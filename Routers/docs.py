from fastapi import APIRouter, HTTPException, Depends, status
from authenticate.authenticate import authenticate
from database.exception_handler import check_existence, check_authority, check_directory, check_duplicate, check_existence_with_name, ExceptionHandler
from beanie import PydanticObjectId, Document
from pydantic import BaseModel

from database.connection import (
    BookCol,
    DocCol, 
    CellCol,
    UserCol,
    Database
)
from models.books import (
    NewBook
)
from models.docs import (
    UpdateDoc
)
from models.docs import (
    NewCell,
    UpdateCell
)


doc_router = APIRouter()
book_database = Database(BookCol)
doc_database = Database(DocCol)
cell_database = Database(CellCol)
user_database = Database(UserCol)


@doc_router.post("/{book_name}/new")
async def new_doc(book_name: str, 
                  body: NewBook,
                  user: str = Depends(authenticate)) -> dict[str, str]:
    # 책의 존재 여부를 확인하고 반환
    book = await BookCol.check_existence_and_return_document(
        BookCol.name == book_name,
        message="book_name with supplied id doesn't exist"
    )

    # 작성자가 맞는지 확인
    writers = book.writers
    if user not in writers:
        raise HTTPException(status_code=403, detail="You do not have permission to add documents to this book.")

    # 문서 생성 및 저장
    doc = DocCol(**body.model_dump())
    doc.parent = book.id
    await doc_database.set_index_and_insert(doc)

    return {
        "message": "successfully created document"
    }

@doc_router.get("/{book_name}/{doc_id}")
async def getDoc(book_name:str, doc_id:PydanticObjectId): #Read
    doc = await check_existence(doc_database, doc_id)
    book = await check_existence_with_name(book_database, book_name)
    await check_directory(book.id, doc.parent)
    
    return doc

@doc_router.put("/{book_name}/{doc_id}/update")
async def updateDoc(book_name:str, doc_id:PydanticObjectId, body: UpdateDoc, user: str = Depends(authenticate)): #Update
    doc = await check_existence(doc_database, doc_id)
    book = await check_existence_with_name(book_database, book_name)
    await check_directory(book.id, doc.parent)
    writers = book.writers
    await check_authority(user, writers)
    
    await doc_database.update(doc_id, body)
    return "successfully updated document"

@doc_router.put("/{book_name}/{doc_id}/set_index")
async def setBookIndex(book_name:str, doc_id:PydanticObjectId, newindex: int, user: str = Depends(authenticate)): #Update
    doc = await check_existence(doc_database, doc_id)
    book = await check_existence_with_name(book_database, book_name)
    await check_directory(book.id, doc.parent)
    writers = book.writers
    await check_authority(user, writers)
    
    await doc_database.resetIndex(doc_id, newindex)
    return "successfully updated index"

@doc_router.delete("/{book_name}/{doc_id}/delete")
async def deleteDoc(book_name:str, doc_id:PydanticObjectId, user: str = Depends(authenticate)): #Delete
    doc = await check_existence(doc_database, doc_id)
    book = await check_existence_with_name(book_database, book_name)
    await check_directory(book.id, doc.parent)
    writers = book.writers
    await check_authority(user, writers)

    await doc_database.setIndex_and_delete(doc_id)
    return "successfully deleted document"

#CELL CRUD------------------------------------------------------------------------------
@doc_router.post("/{book_name}/{doc_id}/new")
async def newCell(book_name:str, doc_id:PydanticObjectId, body:NewCell, user:str=Depends(authenticate)):#create
    doc = await check_existence(doc_database, doc_id)
    book = await check_existence_with_name(book_database, book_name)
    await check_directory(book.id, doc.parent)
    writers = book.writers
    await check_authority(user, writers)
    
    cell = CellCol(**body.model_dump())
    cell.parent = str(doc_id)
    await cell_database.setIndex_and_insert(cell)
    return "successfully created cell"

@doc_router.put("/{book_name}/{doc_id}/{cell_id}")
async def updateCell(book_name:str, doc_id:PydanticObjectId, cell_id: PydanticObjectId, body: UpdateCell, user:str=Depends(authenticate)):#update
    cell = await check_existence(cell_database, cell_id)
    doc = await check_existence(doc_database, doc_id)
    book = await check_existence_with_name(book_database, book_name)
    await check_directory(doc_id, cell.parent)
    await check_directory(book.id, doc.parent)
    writers = book.writers
    await check_authority(user, writers)

    await cell_database.update(cell_id, body)
    return "successfully updated cell"

@doc_router.put("/{book_name}/{doc_id}/{cell_id}/set_index")
async def setCellIndex(book_name:str, doc_id: PydanticObjectId, cell_id:PydanticObjectId, newindex: int, user: str = Depends(authenticate)): #Update
    cell = await check_existence(cell_database, cell_id)
    doc = await check_existence(doc_database, doc_id)
    book = await check_existence_with_name(book_database, book_name)
    await check_directory(doc_id, cell.parent)
    await check_directory(book.id, doc.parent)
    writers = book.writers
    await check_authority(user, writers)

    
    await doc_database.resetIndex(doc_id, newindex)
    return "successfully updated index"

@doc_router.delete("/{book_name}/{doc_id}/{cell_id}")
async def deleteCell(book_name:str, doc_id:PydanticObjectId, cell_id:PydanticObjectId, user:str=Depends(authenticate)):#update
    cell = await check_existence(cell_database, cell_id)
    doc = await check_existence(doc_database, doc_id)
    book = await check_existence_with_name(book_database, book_name)
    await check_directory(doc_id, cell.parent)
    await check_directory(book.id, doc.parent)
    writers = book.writers
    await check_authority(user, writers)

    await cell_database.setIndex_and_delete(cell_id)
    return "successfully deleted cell"

#follow
@doc_router.post("/{book_name}/follow")
async def followbook(book_name:str, user:str = Depends(authenticate)):
    book = await check_existence_with_name(book_database, book_name)
    writers = book.writers
    if user in writers:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already followed"
        )
    
    await book_database.followBook(user, book_name)
    return "successfully followed"

@doc_router.post("/{book_name}/unfollow")
async def unfollowbook(book_name:str, user:str = Depends(authenticate)):
    book = await check_existence_with_name(book_database, book_name)
    writers = book.writers
    if not user in writers:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already unfollowed"
        )
    
    await book_database.unfollowBook(user, book_name)
    return "successfully unfollowed"