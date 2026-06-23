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