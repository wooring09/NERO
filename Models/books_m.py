from pydantic import BaseModel
from typing import Optional

class Document(BaseModel):
    title: str
    writer: str

class Book(BaseModel):
    title: str
    writers: list[str]
    documents: list[Document]