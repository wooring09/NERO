from beanie import PydanticObjectId, Document
from fastapi import HTTPException, status

from typing import Type, TypeVar
from dataclasses import dataclass

def check_existence():
    pass
def check_authority():
    pass
def check_directory():
    pass
def check_duplicate():
    pass
def check_existence_with_name():
    pass 

class ExceptionHandler(Document):

    # async def check_existence(database, obj_id:PydanticObjectId):
    #     obj = await database.get(obj_id)
    #     if not obj:
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND,
    #             detail="Object with supplied id doesn't exist"
    #         )
    #     return obj

    # async def check_directory(Cobj_id:PydanticObjectId, Pobj_ids):
    #     if str(Cobj_id) not in Pobj_ids:
    #         raise HTTPException(
    #             status_code=status.HTTP_401_UNAUTHORIZED,
    #             detail="wrong directory"
    #         )
    #     return True

    # async def check_authority(id: PydanticObjectId, array):
    #     if str(id) not in array:
    #         raise HTTPException(
    #             status_code=status.HTTP_401_UNAUTHORIZED,
    #             detail="No authority to access"
    #         )
    #     return True
    @classmethod
    async def vanish_none_update_fields_and_update(cls,
                                                   document: Type[Document], 
                                                   body: dict) -> None:

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
    async def check_existence_and_return_document(cls,
                                                  *args,
                                                  project: str = None, 
                                                  message: str = "no message", 
                                                  **kwargs) -> type[Document]:
        
        query = cls.find_one(*args, **kwargs)
        if project:
            query = query.project(project)
    
        document = await query

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": message
                }
            )
        
        return document


    @classmethod
    async def check_duplicate(cls,
                              *args, 
                              message: str = "no message", 
                              project: str = None, 
                              **kwargs):
        
        if not project:
            project = cls._id
        
        # 중복 문서 검색
        existing_document = await cls.find_one(*args, **kwargs).project(project)
        
        if existing_document:
            # 중복이 있을 경우 예외 발생
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": message
                }
            )
        
        return existing_document


    # async def convert_id(database, name:str):
    #     body = await database.find({"name":name})
    #     if not body:
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND,
    #             detail="Can't find object"
    #         )
    #     objid = body.id
    #     return objid
