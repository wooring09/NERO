from pydantic import BaseModel
from typing import Optional
from bson.objectid import ObjectId

class User(BaseModel):
    name:Optional[str] = None
    email:str
    password:str
    followingBooks:Optional[list[str]] = None
    followingUsers:Optional[list[str]] = None
    