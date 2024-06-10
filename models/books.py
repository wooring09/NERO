from pydantic import BaseModel
from typing import Optional

from beanie import Document, PydanticObjectId

#Document Model
class Cell(Document):
    index: Optional[int] = None
    title: str
    parent: Optional[PydanticObjectId] = None
    contents: str

class Doc(Document):
    index: Optional[int] = None
    title: str 
    type: str
    parent: Optional[PydanticObjectId] = None
    related: Optional[list[str]] = []

class Book(Document):
    name: str
    display_name: str
    writer: str
    followers: Optional[list[str]] = []
    image: Optional[str] = None

    class Settings:
        collection = "books"


#Basemodel
class NewBook(BaseModel):
    name: str
    display_name:str

class UpdateBook(BaseModel):
    display_name: Optional[str] = None

class UpdateDoc(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None
    related: Optional[list[str]] = None

class NewCell(BaseModel):
    title: str
    contents: str

class UpdateCell(BaseModel):
    title: Optional[str] = None
    contents: Optional[str] = None
