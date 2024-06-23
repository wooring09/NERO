from beanie import PydanticObjectId, Document
from pydantic import BaseModel
from fastapi import HTTPException, status

from typing import Type, TypeVar, Union
from dataclasses import dataclass

class IdProjection(BaseModel):
    _id: str

class ExceptionHandler(Document):

    @classmethod
    async def vanish_none_and_update(cls,
                                    document: Type[Document], 
                                    body: Type[BaseModel]) -> None:
        

        body = body.model_dump()

        filtered_body =  {k: v for k, v in body.items() if v is not None}

        if not filtered_body:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "No fields to update"
                }
            )
        
        await document.update({"$set": filtered_body})

        return None
    
    @classmethod
    async def check_existence_and_return(cls,
                                        *args,
                                        project: Type[BaseModel] = None, 
                                        obj_type: str = None, 
                                        **kwargs) -> type[Document]:

        query = cls.find_one(*args, **kwargs)
        if project:
            query = query.project(project)
        
        body = await query

        if not body:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": f"{obj_type} with supplied query doesn't exist"
                }
            )
        
        return body
    
    @classmethod
    async def check_directory(cls, 
                              parent_id: PydanticObjectId, 
                              body_id: PydanticObjectId, 
                              obj_type: str = None) -> type[Document]:
        
        if not body_id == parent_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": f"{obj_type} with supplied query is in a wrong directory"
                }
            )
        
        return True

    @classmethod
    async def check_duplicate(cls,
                              *args, 
                              project: Type[BaseModel] = None, 
                              obj_type: str = None, 
                              **kwargs) -> type[Document]:
        
        if not project:
            project = IdProjection

        query = cls.find_one(*args, **kwargs).project(project)
        if project:
            query = query.project(project)
        
        existing_document = await query
        
        if existing_document:
            
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": f"{obj_type} with supplied query doesn't exist"
                }
            )
        
        return existing_document

class IndexHandler(Document):

    @classmethod
    async def set_index_and_insert(cls, body:Document):
        max_index = await cls.find_many({"parent": body.parent}).sort("-index").first_or_none()
        if max_index:
            body.index = max_index.index + 1
        else:
            body.index = 1
        await body.create()
        return True

    @classmethod
    async def set_index_and_delete(cls, body:Document):
        index = body.index
        others = cls.find_many({"parent": body.parent, "index": {"$gte":index}})
        await others.update_many({"$inc": {"index":-1}})
        await body.delete()
        return True

    @classmethod
    async def switch_index(cls, body:Document, new_index:int):
        index = body.index

        if new_index == index:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": "already in the supplied index"
                }
            )
        
        others_gte_index = cls.find_many({"parent": body.parent, "index": {"$gt":index}})
        others_gte_new_index = cls.find_many({"parent": body.parent, "index": {"$gte":new_index}})

        #new_index에 해당하는 도큐먼트(몽고DB의)가 없을 경우
        if not others_gte_new_index:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": "index is out of range"
                }
            )
        
        await others_gte_index.update_many({"$inc": {"index":-1}})
        await others_gte_new_index.update_many({"$inc": {"index":1}})
        await body.update({"$set":{"index":new_index}})
        return True