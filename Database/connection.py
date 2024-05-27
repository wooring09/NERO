from pymongo import MongoClient
from pydantic_settings import BaseSettings
from typing import Optional
from fastapi import HTTPException, status
from bson.objectid import ObjectId

client = MongoClient("mongodb://localhost:30000/")
db = client["NERO"]
Books_coll = db["Books"]
Docs_coll = db["Docs"]
Users_coll = db["Users"]
Docs_projection = {"title":1, "type":1}

class Settings(BaseSettings):
    SECRET_KEY: Optional[str]

    class Config:
        env_file = ".env"

class Basic_connection:
    def __init__(self, collection):
        self.model = collection

    async def insertOne(self, document):
        self.model.insert_one(dict(document))
        return
    
    async def insertMany(self, documents):
        self.model.insert_many(dict(documents))
        return
    
    async def findOne(self, query):
        response = self.model.find_one(query)
        return response
    
    async def findMany(self, query):
        response = self.model.find(query)
        return response
    
    async def updateOne(self, query, document):
        self.model.update_one(query, {"$set":dict(document)})
        return

class Docs_connection:    #Docs(collection) 변경 & Books(collection)의 documents값 변경
    async def insertOne(book_id, document):
        Docs_coll.insert_one(document)
        newDoc = Docs_coll.find_one(dict(document), Docs_projection)
        Books_coll.update_one(
            {"_id":book_id},
            {"$set": {"documents": {"$push": newDoc}}}
        )
        
    async def updateOne(book_id, doc_id, document):
        Doc = dict(document)
        Docs_coll.update_one({"_id":doc_id}, {"$set":Doc})
        existDoc = Docs_coll.find_one({"_id":ObjectId(doc_id)}, Docs_projection)   #새 Doc 불러오기
        newDoc = dict(map(lambda key: (key, Doc[key]), Docs_projection))
        existDoc.update(newDoc)  #최신 Doc으로 덮어씌우기
        Books_coll.update_one(
            {"_id":ObjectId(book_id)},
            {"$set":{"documents.$": existDoc}}
        )

