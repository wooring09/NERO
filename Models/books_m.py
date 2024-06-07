from pydantic import BaseModel
from typing import Optional

from beanie import Document

#Document Model
class Cell(Document):
    title: str
    parentDoc: str
    contents: str

class Doc(Document):
    title: str 
    writers: Optional[list[str]] = []
    type: str
    parentBook: Optional[str] = None
    related: Optional[list[str]] = []
    cells: Optional[list[str]] = []

class Book(Document):
    id_: str
    title: str
    writers:Optional[list[str]] = []
    documents:Optional[list[str]] = []


#Basemodel
class new_book(BaseModel):
    id_: str
    title:str

class update_book(BaseModel):
    id_: Optional[str] = None
    title: Optional[str] = None

class new_doc(BaseModel):
    title: str
    type: str

class update_doc(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None
    related: Optional[list[str]] = None
