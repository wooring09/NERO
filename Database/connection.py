from pymongo import MongoClient
from pydantic_settings import BaseSettings
from typing import Optional

client = MongoClient("mongodb://localhost:30000/")
db = client["NERO"]
Books_coll = db["Books"]
Users_coll = db["Users"]

class Settings(BaseSettings):
    SECRET_KEY: Optional[str]

    class Config:
        env_file = ".env"

class connection:
    def __init__(self, collection):
        self.model = collection
    async def insertOne(self, document) -> None:
        self.model.insert_one(dict(document))
        return
    async def insertMany(self, documents) -> None:
        self.model.insert_many(dict(documents))
        return
    async def findOne(self, document) -> None:
        response = self.model.find_one(document)
        return response