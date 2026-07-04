import secrets
from sqlmodel import Session, select
from fastapi import FastAPI, HTTPException, Depends
from database import create_db_and_tables, engine
from models import Link, LinkCreate, LinkPublic, Click, User, UserCreate, UserBase
from auth import pwd_context, create_access_token, get_current_user
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm


app = FastAPI()


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


@app.on_event("startup")
def On_startup():
    create_db_and_tables()


@app.post('/shorten_url', response_model=LinkPublic)
def create_shorten_url(link : LinkCreate):
    short_code = secrets.token_urlsafe(6)
    if not link.original_url.startswith("http"):
        link.original_url = "https://" + link.original_url
    with Session(engine) as session:
        db_url = Link(short_code=short_code, **link.model_dump())
        session.add(db_url)
        session.commit()
        session.refresh(db_url)
        return db_url
    

@app.get('/links', response_model=list[LinkPublic])
def get_all_links(current_user: str = Depends(get_current_user)):
    with Session(engine) as session:
        link = session.exec(select(Link)).all()
        if link is None:
            raise HTTPException(status_code=404, detail="No links found.")
        return link
    

@app.get('/{short_code}/stats')
def get_stats(short_code: str):
    with Session(engine) as session:
        link = session.exec(select(Link).where(Link.short_code == short_code)).first()
        if not link:
            raise HTTPException(status_code=404, detail="Code not found.")
        stat = len(list(session.exec(select(Click).where(Click.link_id == link.id))))
        if stat == 0:
            return {"clicks": 0}
        return {"clicks": stat}
    

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
        

