from pydantic_settings import BaseSettings
from typing import Optional
from fastapi import HTTPException, status
from database.exception_handler import ExceptionHandler, IndexHandler
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from beanie import init_beanie, PydanticObjectId, Document

from models.books import Book, Role
from models.docs import Doc, Cell
from models.users import User


class Settings(BaseSettings):
    SECRET_KEY: Optional[str] = None
    DB_URL: Optional[str] = None
    DB_NAME: Optional[str] = None

    async def initiate_database(self):
        client = AsyncIOMotorClient(self.DB_URL)
        await init_beanie(database=client[self.DB_NAME], document_models=[User, Book, Doc, Cell, Role])

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
    async def delete_book_and_associated_documents(cls, body: Document) -> None:
        # Find all documents associated with the book
        docs = await DocCol.find_many(DocCol.parent == cls.name)
        # doc_ids = [doc.id for doc in docs]
        doc_ids = docs.project(DocCol.id==1)

        # Find all cells associated with the documents
        cells = await CellCol.find({CellCol.parent: {"$in": doc_ids}})
        await cells.delete_all()
        await docs.delete_all()
        await body.delete()

        return None
    
class DocCol(Doc, ExceptionHandler, IndexHandler):
    pass
    
class CellCol(Cell, ExceptionHandler, IndexHandler):
    pass

class RoleCol(Role, ExceptionHandler):

    @classmethod
    async def check_permission(cls):
        #                         *args, 
        #                         user_name: str,
        #                         project: str = None, 
        #                         obj_type: str,
        #                         **kwargs):
        
        # document: Book = await cls.check_existence_and_return_document(
        #     *args, **kwargs,
        #     obj_type=obj_type,
        #     project=project
        # )
        
        # #여기에 더 추가되야함
        # if document.writer == user_name:
        #     return document
        
        # raise HTTPException(
        #     status_code=status.HTTP_401_UNAUTHORIZED,
        #     detail={
        #         "message": "user with supplied user_name has no permission"
        #     }
        # )
        pass