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
    async def followUser(self, user_id:str, target_id:PydanticObjectId):
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
    async def insertBook(self, body:Document):
        newbody = await body.create()
        book_id = str(body.id)
        user_id = body.writers[0]
        user = await User.get(PydanticObjectId(user_id))
        await user.update({"$push": {"followingBooks": book_id}})
        return
    
    async def deleteBook(self, book_id:PydanticObjectId):
        book = await Book.get(book_id)
        docs = Doc.find_many({"parentBook":str(book_id)})
        docs_list = await Doc.find_many({"parentBook":str(book_id)}).to_list()
        docs_id = [str(doc.id) for doc in docs_list]
        cells = Cell.find_many({"parentDoc":{"$in": docs_id}})
        await cells.delete_many()
        await docs.delete_many()
        await book.delete()
        return True
    
    #User Database
    async def deleteUser(self, user_id:PydanticObjectId):
        books = Book.find({"writers": str(user_id)})
        print(books)
        await books.update_many({"$pull": {"writers": str(user_id)}})
        user = await User.get(user_id)
        await user.delete()
        return True


    #Index functions
    async def setIndex_and_insert(self, body:Document):
        max_index = await self.model.find_many({"parent": body.parent}).sort("-index").first_or_none()
        if max_index:
            body.index = max_index.index + 1
        else:
            body.index = 1
        await body.create()
        return True
    
    async def setIndex_and_delete(self, id:PydanticObjectId):
        body = await self.model.get(id)
        index = body.index
        others = self.model.find_many({"parent": body.parent, "index": {"$gte":index}})
        await others.update_many({"$inc": {"index":-1}})
        await body.delete()
        return True
    
    async def resetIndex(self, id:PydanticObjectId, new_index:int):
        body = await self.model.get(id)
        index = body.index
        others = self.model.find_many({"parent": body.parent, "index": {"$gte":new_index}})
        await others.update_many({"$inc": {"index":1}})
        await body.update({"$set":{"index":new_index}})
        return True

    #Cell Database
    # async def insertCell(self, doc_id:PydanticObjectId, cell:Cell):
    #     newcell = await cell.create()
    #     if not newcell:
    #         return False
    #     cell_id = str(newcell.id)

    #     doc = await Doc.get(doc_id)
    #     if not doc:
    #         return False
        
    #     await doc.update({"$add": {"cells": cell_id}})
    #     return True
    
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