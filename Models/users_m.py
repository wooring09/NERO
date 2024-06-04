from pydantic import BaseModel
from typing import Optional
from bson.objectid import ObjectId

class User(BaseModel):
    name:Optional[str] = None
    email:str
    password:str
    followers:Optional[list[str]] = None
    followingBooks:Optional[list[str]] = None
    followingUsers:Optional[list[str]] = None

class updateUser(BaseModel):
    name:Optional[str] = None
    