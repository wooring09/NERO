from pydantic import BaseModel
from typing import Optional
from beanie import Document, PydanticObjectId


class Doc(Document):
    index: Optional[int] = None
    title: str 
    type: str
    parent: Optional[PydanticObjectId] = None
    related: Optional[list[str]] = []

    class Settings:
        collection = "docs"

class Cell(Document):
    index: Optional[int] = None
    title: str
    parent: Optional[PydanticObjectId] = None
    contents: str
    
    class Settings:
        collection = "cells"

    
class UpdateDoc(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None
    related: Optional[list[str]] = None

class NewCell(BaseModel):
    title: str
    contents: str

class NewDoc(BaseModel):
    title: str 
    type: str

class UpdateCell(BaseModel):
    title: Optional[str] = None
    contents: Optional[str] = None
