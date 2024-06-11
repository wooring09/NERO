from pydantic_settings import BaseSettings
from typing import Optional
from fastapi import HTTPException, status
from database.exception_handler import ExceptionHandler
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from beanie import init_beanie, PydanticObjectId, Document

from models.books import Book
from models.docs import Doc, Cell
from models.users import User


class Settings(BaseSettings):
    SECRET_KEY: Optional[str] = None
    DB_URL: Optional[str] = None
    DB_NAME: Optional[str] = None

    async def initiate_database(self):
        client = AsyncIOMotorClient(self.DB_URL)
        await init_beanie(database=client[self.DB_NAME], document_models=[User, Book, Doc, Cell])

    class Config:
        env_file = ".env"

#
#
#
    
class UserCol(User, ExceptionHandler):
    pass

class BookCol(Book, ExceptionHandler):

    @classmethod
    async def add_to_user_follower_list(cls, book_id: PydanticObjectId, user_name: str):
        
        await cls.update(
            {cls.id: book_id},
            {"$addToSet":{cls.followers: user_name}}
        )

        return True
    
    @classmethod
    async def check_existence_and_permission(cls,
                                             *args, 
                                             user_name: str,
                                             project: str = None, 
                                             message_for_exist_exception: str="no message",
                                             **kwargs):
        
        document: BookCol = await cls.check_existence_and_return_document(
            *args, **kwargs,
            message=message_for_exist_exception,
            project=project
        )
        
        #여기에 더 추가되야함
        if document.writer == user_name:
            return document
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": "user with supplied user_name has no permission"
            }
        )
    
    async def delete_book_and_associated_documents(self) -> None:
        # Find all documents associated with the book
        docs = await DocCol.find_many(DocCol.parent == self.name)
        doc_ids = [doc.id for doc in docs]

        # Find all cells associated with the documents
        cells = await CellCol.find({CellCol.parent: {"$in": doc_ids}})
        await cells.delete_all()
        await docs.delete_all()
        await self.delete()

        return None
    
class DocCol(Doc, ExceptionHandler):
    pass

class CellCol(Cell, ExceptionHandler):
    pass

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
        # docs = Doc.find_many({"parentBook":str(book_id)})
        docs = Doc.find_many(Doc.parent_book==book_id)
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

        book = await Book.find({"name": book_id})
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
        
        await doc.update({"$add": {"cells": cell_id}})
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