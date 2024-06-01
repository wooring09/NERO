from pydantic import BaseModel
from typing import Optional
from bson.objectid import ObjectId

class Document(BaseModel):
    title: str 
    writers: Optional[list[str]] = None
    type: str
    parentBook: str
    related: Optional[list[str]] = None
    contents: str
    comments: Optional[list[str]] = None

# class Doc_in_Book(BaseModel):
#     _id: ObjectId
#     title: str
#     type: str

class Book(BaseModel):
    title: str
    writers: list[str]
    documents: list[str]

class updateBook(BaseModel):
    title: Optional[str] = None

class updateDocument(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None
    related: Optional[list[str]] = None
    contents: Optional[str] = None
