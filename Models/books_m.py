from pydantic import BaseModel
from typing import Optional
from bson.objectid import ObjectId

class Document(BaseModel):
    title: str 
    writers: list[str]
    type: str
    related: list[str]
    parentBook: str
    contents: str
    comments: list[str]

class Doc_in_Book(BaseModel):
    id: ObjectId
    title: str
    type: str

class Book(BaseModel):
    title: str
    writers: list[str]
    documents: list[Doc_in_Book]