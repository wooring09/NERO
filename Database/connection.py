from pydantic_settings import BaseSettings
from typing import Optional
from fastapi import HTTPException, status

from beanie import init_beanie, PydanticObjectId, Document
from Models.books_m import Book, Doc, Cell
from Models.users_m import User
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

class Settings(BaseSettings):
    SECRET_KEY: Optional[str] = None
    DB_URL: Optional[str] = None

    async def initiate_database(self):
        client = AsyncIOMotorClient(self.DB_URL)
        await init_beanie(database=client.get_default_database(), document_models=[User, Book, Doc, Cell])

    class Config:
        env_file = ".env"
    

class Database:
    def __init__(self, collection):
        self.model = collection

    #Basic Database
    async def insert(self, body:Document):
        await body.insert()
        return
    
    async def get(self, id:PydanticObjectId): #find with ObjectId
        response = await self.model.get(id)
        return response

    async def find(self, query):
        response = await self.model.find_one(query)
        return response
    
    async def findMany(self, query):
        response = await self.model.find_many(query).to_list()
        return response
    
    async def findAll(self):
        response = await self.model.find_many().to_list()
        return response
    
    async def update(self, id:PydanticObjectId, body:BaseModel):
        desbody = body.model_dump()
        newbody = {k: v for k, v in desbody.items() if v is not None} #value가 None이라면 key삭제
        
        mainbody = await self.model.get(id)
        await mainbody.update({"$set":newbody})
        return True
    
    async def delete(self, id:PydanticObjectId):
        body = self.model.get(PydanticObjectId)
        if not body:
            return False
        await body.delete()
        return True
    
    #follow functions
    async def followUser(self, user_id:PydanticObjectId, target_id:PydanticObjectId):
        user = await User.get(user_id)
        target = await User.get(target_id)
        if not user or not target:
            return False

        await user.update({"$push":{"followingUsers":str(target_id)}})
        await target.update({"$push":{"followers":str(user_id)}})
        return True
    
    async def unfollowUser(self, user_id:PydanticObjectId, target_id:PydanticObjectId):
        user = await User.get(user_id)
        target = await User.get(target_id)
        if not user or not target:
            return False

        await user.update({"$pull":{"followingUsers":str(target_id)}})
        await target.update({"$pull":{"followers":str(user_id)}})
        return True
    
    async def followBook(self, user_id:PydanticObjectId, book_id:PydanticObjectId):
        user = await User.get(user_id)
        target = await Book.get(book_id)
        if not user or not target:
            return False

        await user.update({"$push":{"followingBooks":str(book_id)}})
        await target.update({"$push":{"writers":str(user_id)}})
        return True
    
    async def unfollowBook(self, user_id:PydanticObjectId, book_id:PydanticObjectId):
        user = await User.get(user_id)
        target = await Book.get(book_id)
        if not user or not target:
            return False

        await user.update({"$pull":{"followingBooks":str(book_id)}})
        await target.update({"$pull":{"writers":str(user_id)}})
        return True
    
    #Book Database
    # async def deleteBook(self, book_id:PydanticObjectId):
    #     book = Book.get(book_id)
    #     ids = book.documents
    #     Docs_Id = [PydanticObjectId(id) for id in ids]
    #     Document.delete_all({"_id": {"$in": Docs_Id}})
    #     Books_coll.delete_one({"_id":ObjectId(book_id)})
    #     return
    
    #User Database
    # async def deleteUser(self, email):

    #Document Database
    async def insertDoc(self, book_id:PydanticObjectId, document:Doc):
        newdoc = await document.create()
        if not newdoc:
            return False
        doc_id = str(newdoc.id)

        book = await Book.get(book_id)
        if not book:
            return False
        
        await book.update({"$push": {"documents": doc_id}})
        return True
    
    async def deleteDoc(self, book_id:str, doc_id:PydanticObjectId):
        doc = await Doc.get(doc_id)
        if not doc:
            return False
        doc.delete()

        book = await Book.find({"id_": book_id})
        if not book:
            return False
        await book.update({"$pull":{"documents": str(doc_id)}})

    #Cell Database
    async def insertCell(self, doc_id:PydanticObjectId, cell:Cell):
        newcell = await cell.create()
        if not newcell:
            return False
        cell_id = str(newcell.id)

        doc = await Doc.get(doc_id)
        if not doc:
            return False
        
        await doc.update({"$push": {"cells": cell_id}})
        return True
    
    async def deleteCell(self, doc_id:PydanticObjectId, cell_id:PydanticObjectId):
        cell = await Cell.get(cell_id)
        if not cell:
            return False
        await cell.delete()

        doc = await Doc.get(doc_id)
        if not doc:
            return False
        await doc.update({"$pull":{"cells": str(cell_id)}})
        return True