from pydantic import BaseModel
from typing import Optional

class Document(BaseModel):
    title: str 
    writers: list[str]
    type: str
    related: list[str]
    parentBook: str
    contents: str
    comments: list[str]

class Doc_in_Book(BaseModel):
    _id: str
    title: str
    type: str

class Book(BaseModel):
    title: str
    writers: list[str]
    documents: list[str]

class updateBook(BaseModel):
    title: Optional[str] = None
    writers: Optional[list[str]] = None
    documents: Optional[list[str]] = None