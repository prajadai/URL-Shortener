import secrets
from sqlmodel import Session, select
from fastapi import FastAPI, HTTPException, Depends, Request
from database import create_db_and_tables, engine
from models import Link, LinkCreate, LinkPublic, Click, User, UserCreate, LinkUpdate, PaginatedLinks
from auth import pwd_context, create_access_token, get_current_user
from fastapi.responses import RedirectResponse
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from jose import jwt, JWTError
from auth import SECRET_KEY, ALGORITHM

def get_user_id_key(request: Request):
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return get_remote_address(request)  # fallback: no token, limit by IP

        token = auth_header.split(" ")[1]  # "Bearer <token>" -> take the token part
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            return get_remote_address(request)

        with Session(engine) as session:
            existing_user = session.exec(select(User).where(User.username == username)).first()
            if not existing_user:
                return get_remote_address(request)
            return str(existing_user.id)  # key must be a string

    except (JWTError, IndexError):
        return get_remote_address(request)  # any decoding failure -> fallback to IP

limiter = Limiter(key_func=get_user_id_key)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == username)).first()
        if not user:
            return False
        if not verify_password(password, user.hashed_password):
            return False
        return user

def get_user_by_username(current_user : str = Depends(get_current_user)):
    with Session(engine) as session:
        existing_user = session.exec(select(User).where(User.username == current_user)).first()
        if not existing_user:
            raise HTTPException(status_code=401, detail="Authentication failed.")
        return existing_user.id


@app.on_event("startup")
def On_startup():
    create_db_and_tables()


@app.get("/", include_in_schema=False)
def root_redirect():
    return RedirectResponse(url="/home", status_code=307)


@app.get("/home", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {})


@app.get("/app", response_class=HTMLResponse)
def app_page(request: Request):
    return templates.TemplateResponse(request, "index.html", {})


@app.post('/shorten_url', response_model=LinkPublic)
@limiter.limit('5/minute')
def create_shorten_url(request: Request, link : LinkCreate, existing_user_id : int = Depends(get_user_by_username)):
    short_code = secrets.token_urlsafe(6)
    if not link.original_url.startswith("http"):
        link.original_url = "https://" + link.original_url
    with Session(engine) as session:
        db_url = Link(short_code=short_code, **link.model_dump(), user_id=existing_user_id)
        session.add(db_url)
        session.commit()
        session.refresh(db_url)
        return db_url
    

@app.get('/links', response_model=PaginatedLinks)
def get_all_links(limit: int = 10, offset : int = 0, existing_user_id : int = Depends(get_user_by_username)):
    with Session(engine) as session:
        link = session.exec(select(Link).where(Link.user_id == existing_user_id).offset(offset).limit(limit)).all()
        total_count = len(session.exec(select(Link).where(Link.user_id == existing_user_id)).all())
        return PaginatedLinks(total=total_count, limit=limit, offset=offset, results=link)
    

@app.get('/{short_code}/stats')
def get_stats(short_code: str, existing_user_id : int = Depends(get_user_by_username)):
    with Session(engine) as session:
        link = session.exec(select(Link).where((Link.short_code == short_code) & (Link.user_id==existing_user_id))).first()
        if not link:
            raise HTTPException(status_code=404, detail="Code not found.")
        stat = len(list(session.exec(select(Click).where(Click.link_id == link.id))))
        if stat == 0:
            return {"clicks": 0}
        return {"clicks": stat}
    

@app.post('/register')
def register_user(user: UserCreate):
    with Session(engine) as session:
        existing_user = session.exec(select(User).where(User.username == user.username)).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists.")
        hashed_password = pwd_context.hash(user.password)
        db_user = User(username = user.username, hashed_password= hashed_password)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user
    
@app.post('/login')
def login(form_data: OAuth2PasswordRequestForm = Depends()):
        login_status = authenticate_user(form_data.username, form_data.password)
        if not login_status:
            raise HTTPException (status_code=401, detail="Incorrect username or password.")
        token = create_access_token(form_data.username)
        return {"access_token": token, "token_type": "bearer"}
        

@app.delete('/{short_code}')
def delete_link(short_code: str, existing_user_id : int = Depends(get_user_by_username)):
    with Session(engine) as session:
        link = session.exec(select(Link).where((Link.short_code == short_code) & (Link.user_id==existing_user_id))).first()
        if not link:
            raise HTTPException(status_code=404, detail="Code not found.")
        clicks = session.exec(select(Click).where(Click.link_id==link.id)).all()
        for click in clicks:
            session.delete(click)
        session.delete(link)
        session.commit()
        return {"message":f"Successsfully deleted the link: {short_code} ."}
    
@app.patch('/{short_code}', response_model=LinkPublic)
def update_link(short_code: str, update_data: LinkUpdate , existing_user_id: int = Depends(get_user_by_username)):
    with Session(engine) as session:
        link = session.exec(select(Link).where((Link.short_code == short_code) & (Link.user_id==existing_user_id))).first()
        if not link:
            raise HTTPException(status_code=404, detail="Code not found.")
        if not update_data.original_url.startswith("http"):
            update_data.original_url = "https://" + update_data.original_url
        link.original_url = update_data.original_url
        session.commit()
        session.refresh(link)
        return link


@app.get('/{short_code}')
def view_shorten_url(short_code: str):
    with Session(engine) as session:
        link = session.exec(select(Link).where(Link.short_code == short_code)).first()
        if not link:
            raise HTTPException(status_code=404, detail="Code not found.")
        db_click = Click(link_id=link.id)
        session.add(db_click)
        session.commit()
        return RedirectResponse(url=link.original_url)