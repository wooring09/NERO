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

class Database:
    def __init__(self, collection):
        self.model = collection

    async def insertOne(self, document):
        self.model.insert_one(document.dict())
        return
    
    async def insertMany(self, documents):
        self.model.insert_many(documents.dict())
        return
    
    async def findOne(self, query):
        response = self.model.find_one(query)
        return response
    
    async def findMany(self, query):
        response = self.model.find(query)
        return response
    
    async def updateOne(self, query, document):
        updatedDoc = {k: v for k, v in document.dict().items() if v is not None} #value가 None이라면 key삭제
        self.model.update_one(query, {"$set":updatedDoc})
        return
    
    async def deleteOne(self, query):
        self.model.delete_one(query)
        return
    
    async def deleteBook(self, book_id):
        Docs_str = dict(Books_coll.find_one({"_id":ObjectId(book_id)}))["documents"]
        Docs_Id = [ObjectId(id) for id in Docs_str]
        Docs_coll.delete_many({"_id": {"$in": Docs_Id}})
        Books_coll.delete_one({"_id":ObjectId(book_id)})
        return
    
    # async def deleteUser(self, email):
        

    async def followUser(self, user, target):
        Users_coll.update_one(
            {"email":user},
            {"$push":{"followingUsers":target}}
        )
        Users_coll.update_one(
            {"email":target},
            {"$push":{"followers":user}}
        )
        return
    
    async def unfollowUser(self, user, target):
        Users_coll.update_one(
            {"email":user},
            {"$pull":{"followingUsers":target}}
        )
        Users_coll.update_one(
            {"email":target},
            {"$pull":{"followers":user}}
        )
        return
    
    async def followBook(self, user, book_id):
        Users_coll.update_one(
            {"email":user},
            {"$push":{"followingBooks":book_id}}
        )
        Books_coll.update_one(
            {"_id":ObjectId(book_id)},
            {"$push":{"writers":user}}
        )
        return
    
    async def unfollowBook(self, user, book_id):
        Users_coll.update_one(
            {"email":user},
            {"$pull":{"followingBooks":book_id}}
        )
        Books_coll.update_one(
            {"_id":ObjectId(book_id)},
            {"$pull":{"writers":user}}
        )
        return


class docDatabase:    #Docs(collection) 변경 & Books(collection)의 documents값 변경
    async def findOne(self, doc_id):
        response = Docs_coll.find_one({"_id":ObjectId(doc_id)})
        return response

    async def insertOne(self, book_id, document):
        Doc = document.dict()
        Docs_coll.insert_one(Doc)
        doc_id = Docs_coll.find_one(Doc, Docs_projection)["_id"]
        Books_coll.update_one(
            {"_id":ObjectId(book_id)},
            {"$push": {"documents": str(doc_id)}}
        )
        return
        
    async def updateOne(self, doc_id, document):
        Doc = document.dict()
        updatedDoc = {k: v for k, v in Doc.items() if v is not None}
        Docs_coll.update_one({"_id":ObjectId(doc_id)}, {"$set":updatedDoc})
        return

    async def setArray(self, book_id, doc_id, array):
        Docs_coll.update_one(   #삭제
            {"_id":book_id},
            {"$pop":{"documents":doc_id}}
        )
        Docs_coll.update_one(   #특정위치에 생성
            {"_id":book_id},
            {"$push":{"documents":doc_id, "$position": array}}
        )
        return

    async def deleteOne(self, book_id, doc_id):
        Docs_coll.delete_one({"_id": ObjectId(doc_id)})
        Books_coll.update_one({"_id": ObjectId(book_id)}, {"$pull":{"documents":doc_id}})
        return




