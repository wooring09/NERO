from pydantic import BaseModel
from typing import Optional
from beanie import Document

class User(Document):
    name:str
    password:str
    displayname:str
    email:Optional[str] = None
    followers:Optional[list[str]] = []
    followingBooks:Optional[list[str]] = []
    followingUsers:Optional[list[str]] = []

class sign_up(BaseModel):
    name:str
    password:str
    displayname:str

class update_user(BaseModel):
    password:Optional[str] = None
    displayname:Optional[str] = None
    