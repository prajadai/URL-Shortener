from sqlmodel import Session, select
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from database import create_db_and_tables, engine
from models import Link, LinkBase, LinkCreate, LinkPublic
import secrets

app = FastAPI()

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
    
@app.get('/{short_code}')
def view_shorten_url(short_code: str):
    with Session(engine) as session:
        link = session.exec(select(Link).where(Link.short_code == short_code)).first()
        if not link:
            raise HTTPException(status_code=404, detail="Code not found.")
        return RedirectResponse(url=link.original_url)