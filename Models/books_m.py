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
    title: str
    writers:Optional[list[str]] = []

#Basemodel
class new_book(BaseModel):
    name: str
    title:str

class update_book(BaseModel):
    title: Optional[str] = None

class new_doc(BaseModel):
    title: str
    type: str

class update_doc(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None
    related: Optional[list[str]] = None

class new_cell(BaseModel):
    title: str
    contents: str

class update_cell(BaseModel):
    title: Optional[str] = None
    contents: Optional[str] = None
