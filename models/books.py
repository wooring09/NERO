from pydantic import BaseModel
from typing import Optional
from beanie import Document, PydanticObjectId

class Book(Document):
    name: str
    display_name: str
    writer: str
    followers: Optional[list[str]] = []
    image: Optional[str] = None

    class Settings:
        name = "books"

class Role(Document):
    name: str
    users: Optional[list[str]] = []
    book_id: PydanticObjectId

    handle_book: bool
    view_book: bool

    handle_doc: bool
    view_doc: bool

    ban_user: bool
    invite_user: bool

    

class NewBook(BaseModel):
    name: str
    display_name:str

class UpdateBook(BaseModel):
    display_name: Optional[str] = None
