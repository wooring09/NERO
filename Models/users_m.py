from pydantic import BaseModel
from typing import Optional
from beanie import Document

class User(Document):
    id_:str
    password:str
    name:str
    email:Optional[str] = None
    followers:Optional[list[str]] = []
    followingBooks:Optional[list[str]] = []
    followingUsers:Optional[list[str]] = []

class sign_up(BaseModel):
    id_:str
    password:str
    name:str

class update_user(BaseModel):
    id_:Optional[str] = None
    password:Optional[str] = None
    name:Optional[str] = None
    