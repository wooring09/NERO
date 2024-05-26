from pymongo import MongoClient
from pydantic_settings import BaseSettings
from typing import Optional
from fastapi import HTTPException, status

client = MongoClient("mongodb://localhost:30000/")
db = client["NERO"]
Books_coll = db["Books"]
Docs_coll = db["Docs"]
Users_coll = db["Users"]
Docs_projection = {"title":1, "type":1, "parentBook":1}

class Settings(BaseSettings):
    SECRET_KEY: Optional[str]

    class Config:
        env_file = ".env"

class Basic_connection:
    def __init__(self, collection):
        self.model = collection

    async def insertOne(self, document) -> None:
        self.model.insert_one(dict(document))
        return
    
    async def insertMany(self, documents) -> None:
        self.model.insert_many(dict(documents))
        return
    
    async def findOne(self, query) -> None:
        response = self.model.find_one(query)
        return response
    
    async def findMany(self, query) -> None:
        response = self.model.find(query)
        return response

class Docs_connection:    #Docs(collection) 변경 & Books(collection)의 documents값 변경
    async def insertOne(document):
        Docs_coll.insert_one(document)
        newDoc = Docs_coll.find_one(dict(document), Docs_projection)
        Books_coll.update_one(
            {"title": newDoc["parentBook"]},
            {"$set": {"documents": {"$push": newDoc.pop("parentBook")}}}
        )
        
    async def updateOne(query, document):
        existDoc = Docs_coll.find_one(query, Docs_projection)   #이전 Doc 불러오기
        Docs_coll.update_one(query, dict(document))
        updatedDoc = existDoc.update(existDoc)  #최신 Doc으로 덮어씌우기
        Books_coll.update_one(
            {"title": existDoc["parentBook"]},
            {"$set":{"documents.$": updatedDoc}}
        )

