from sqlmodel import Field, SQLModel
from datetime import datetime

class LinkBase(SQLModel):
    original_url : str

class LinkCreate(LinkBase):
    pass

class LinkPublic(LinkBase):
    id : int | None = None
    short_code : str
    created_at : datetime = Field(default_factory=datetime.now)

class Link(LinkBase, table=True):
    id : int | None = Field(default=None, primary_key=True)
    short_code : str
    created_at : datetime = Field(default_factory=datetime.now)
    user_id : int | None = Field(default = None, foreign_key="user.id")


class Click(SQLModel, table=True):
    id : int | None = Field(default=None, primary_key=True)
    # user : str | None = Field(default=None, foreign_key="user.id")
    link_id : int | None = Field(default=None, foreign_key="link.id")
    clicked_at : datetime = Field(default_factory=datetime.now)


class UserBase(SQLModel):
    username : str
    
class UserCreate(UserBase):
    password : str

class User(UserBase, table=True):
    id : int | None = Field(default = None, primary_key=True)
    hashed_password : str