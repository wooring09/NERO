from fastapi import APIRouter, HTTPException, Depends, status
from authenticate.authenticate import authenticate
from database.exception_handler import ExceptionHandler
from beanie import PydanticObjectId, Document
from pydantic import BaseModel

from database.connection import (
    BookCol,
    DocCol, 
    CellCol,
    UserCol,
    RoleCol
)
from models.books import (
    NewBook
)
from models.docs import (
    NewDoc,
    UpdateDoc
)
from models.docs import (
    NewCell,
    UpdateCell
)

doc_router = APIRouter()

async def check_doc_and_parent_objs(book_name, doc_id):
    #Doc과 Book 불러오기
    book = await BookCol.check_existence_and_return(
        BookCol.name==book_name,
        obj_type="Book"
    )
    doc = await DocCol.check_existence_and_return(
        DocCol.id==doc_id,
        obj_type="Document"
    )

    #위치 확인((Book)에 (Document)가 포함되어 있는가)
    await BookCol.check_directory(
        book.id,
        doc.parent,
        obj_type="Document"
    )

    return {"book": book, "doc": doc}

async def check_cell_and_parent_objs(book_name, doc_id, cell_id):
    #Doc, Book, Cell 불러오기
    book = await BookCol.check_existence_and_return(
        BookCol.name==book_name,
        obj_type="Book"
    )
    doc = await DocCol.check_existence_and_return(
        DocCol.id==doc_id,
        obj_type="Document"
    )
    cell = await CellCol.check_existence_and_return(
        CellCol.id==cell_id,
        obj_type="Cell"
    )
    
    #위치 확인((Book)에 (Document)가 포함되어 있는가)
    await BookCol.check_directory(
        book.id,
        doc.parent,
        obj_type="Document"
    )
    #위치 확인((Document)에 (Cell)이 포함되어 있는가)
    await BookCol.check_directory(
        doc.id,
        cell.parent,
        obj_type="Cell"
    )

    return {"book": book, "doc": doc, "cell": cell}

@doc_router.post("/{book_name}/new")
async def new_doc(book_name: str, 
                  body: NewDoc, 
                  user_name: str = Depends(authenticate)) -> dict:
    #Book 불러오기
    book = await BookCol.check_existence_and_return(
        BookCol.name==book_name,
        obj_type="Book"
    )

    #권한 확인 **미완
    await RoleCol.check_permission()

    # 문서 생성 및 저장
    doc = DocCol(**body.model_dump())
    doc.parent = book.id
    await DocCol.set_index_and_insert(doc)

    return {
        "message": "successfully created document"
    }

@doc_router.get("/{book_name}/{doc_id}")
async def get_doc(book_name:str, 
                  doc_id:PydanticObjectId): #Read
    
    response = await check_doc_and_parent_objs(book_name, doc_id)
    doc = response["doc"]
    
    return doc

@doc_router.put("/{book_name}/{doc_id}/update")
async def update_doc(book_name:str, 
                     doc_id:PydanticObjectId, 
                     body: UpdateDoc, 
                     user_name: str = Depends(authenticate)): #Update
    
    #존재 여부 확인, 위치 확인
    response = await check_doc_and_parent_objs(book_name, doc_id)
    doc = response["doc"]

    #권한 확인 **미완
    await RoleCol.check_permission()

    # 문서 업데이트
    await DocCol.vanish_none_and_update(doc, body)

    return{
        "message": "successfully updated document"
    }

@doc_router.patch("/{book_name}/{doc_id}/set_index")
async def set_doc_index(book_name:str, 
                        doc_id:PydanticObjectId, 
                        newindex: int, 
                        user_name: str = Depends(authenticate)): #Update
    
    response = await check_doc_and_parent_objs(book_name, doc_id)
    doc = response["doc"]

    #권한 확인 **미완
    await RoleCol.check_permission()

    # 문서 업데이트
    await DocCol.switch_index(doc, newindex)

    return{
        "message": "successfully updated index"
    }

# @doc_router.delete("/{book_name}/{doc_id}/delete")
# async def deleteDoc(book_name:str, doc_id:PydanticObjectId, user_name: str = Depends(authenticate)): #Delete
#     doc = await check_existence(doc_database, doc_id)
#     book = await check_existence_with_name(book_database, book_name)
#     await check_directory(book.id, doc.parent)
#     writers = book.writers
#     await check_authority(user_name, writers)

#     await doc_database.setIndex_and_delete(doc_id)
#     return "successfully deleted document"

#CELL CRUD------------------------------------------------------------------------------
@doc_router.post("/{book_name}/{doc_id}/new")
async def newCell(book_name:str, 
                  doc_id:PydanticObjectId, 
                  body:NewCell, 
                  user_name:str=Depends(authenticate)):#create
    
    response = await check_doc_and_parent_objs(book_name, doc_id)
    doc = response["doc"]

    #권한 확인 **미완
    await RoleCol.check_permission()

    # 문서 생성 및 저장
    cell = CellCol(**body.model_dump())
    cell.parent = doc.id
    await CellCol.set_index_and_insert(cell)

    return {
        "message": "successfully created cell"
    }

@doc_router.put("/{book_name}/{doc_id}/{cell_id}")
async def updateCell(book_name:str, 
                     doc_id:PydanticObjectId, 
                     cell_id: PydanticObjectId, 
                     body: UpdateCell, 
                     user_name:str=Depends(authenticate)):#update
    
    response = await check_cell_and_parent_objs(book_name, doc_id, cell_id)
    cell = response["cell"]

    #권한 확인 **미완
    await RoleCol.check_permission()

    # 문서 업데이트
    await CellCol.vanish_none_and_update(cell, body)

    return{
        "message": "successfully updated cell"
    }

@doc_router.patch("/{book_name}/{doc_id}/{cell_id}/set_index")
async def set_cell_index(book_name:str, 
                         doc_id: PydanticObjectId, 
                         cell_id:PydanticObjectId, 
                         newindex: int, 
                         user_name: str = Depends(authenticate)): #Update
    
    response = await check_cell_and_parent_objs(book_name, doc_id, cell_id)
    cell = response["cell"]

    #권한 확인 **미완
    await RoleCol.check_permission()

    # 문서 업데이트
    await CellCol.switch_index(cell, newindex)

    return{
        "message": "successfully updated index"
    }

# @doc_router.delete("/{book_name}/{doc_id}/{cell_id}")
# async def deleteCell(book_name:str, doc_id:PydanticObjectId, cell_id:PydanticObjectId, user_name:str=Depends(authenticate)):#update
#     cell = await check_existence(cell_database, cell_id)
#     doc = await check_existence(doc_database, doc_id)
#     book = await check_existence_with_name(book_database, book_name)
#     await check_directory(doc_id, cell.parent)
#     await check_directory(book.id, doc.parent)
#     writers = book.writers
#     await check_authority(user_name, writers)

#     await cell_database.setIndex_and_delete(cell_id)
#     return "successfully deleted cell"

# #follow
# @doc_router.post("/{book_name}/follow")
# async def followbook(book_name:str, user_name:str = Depends(authenticate)):
#     book = await check_existence_with_name(book_database, book_name)
#     writers = book.writers
#     if user_name in writers:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail="Already followed"
#         )
    
#     await book_database.followBook(user_name, book_name)
#     return "successfully followed"

# @doc_router.post("/{book_name}/unfollow")
# async def unfollowbook(book_name:str, user_name:str = Depends(authenticate)):
#     book = await check_existence_with_name(book_database, book_name)
#     writers = book.writers
#     if not user_name in writers:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail="Already unfollowed"
#         )
    
#     await book_database.unfollowBook(user_name, book_name)
#     return "successfully unfollowed"