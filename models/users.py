from pydantic import BaseModel
from typing import Optional
from beanie import Document

class User(Document):
    name:str
    password:str
    display_name:str
    email:Optional[str] = None
    followers:Optional[list[str]] = []
    following_books:Optional[list[str]] = []
    following_users:Optional[list[str]] = []

class sign_up(BaseModel):
    name:str
    password:str
    display_name:str

class update_user(BaseModel):
    password:Optional[str] = None
    display_name:Optional[str] = None
    