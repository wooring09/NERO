from fastapi import APIRouter, HTTPException, Depends, status
from database.connection import Database, BookCol, DocCol, CellCol
from models.books import Book, Doc, Cell, NewBook,UpdateBook, UpdateDoc, NewCell, UpdateCell
from models.users import User
from authenticate.authenticate import authenticate
from database.exception_handler import check_existence, check_authority, check_directory, check_duplicate, check_existence_with_name, ExceptionHandler
from beanie import PydanticObjectId, Document
from pydantic import BaseModel

book_router = APIRouter()
book_database = Database(Book)
doc_database = Database(Doc)
cell_database = Database(Cell)
user_database = Database(User)


@book_router.get("/")
async def get_all() -> list:
    books = await Book.find_all(limit=10).to_list()
    print(books)
    return books

#BOOK CRUD----------------------------------------------------------------------------------

@book_router.post("/new")
async def new_book(body: NewBook,
                   user_name: str = Depends(authenticate))-> dict:

    await BookCol.check_duplicate(
        BookCol.name==body.name,
        message="book with supplied bookname already exists"
    )

    book = BookCol(**body.model_dump(),
                   writer=user_name,
                   followers=[user_name])

    await book.create()

    return {
        "message": "book created successfully"
    }

#
#
#

@book_router.get("/{book_name}")
async def get_book(book_name: str) -> dict:

    book = await BookCol.check_existence_and_return_document(
        BookCol.name==book_name,
        message="book_name with supllied id doesn't exist"
    )

    return book

#
#
#

@book_router.put("/{book_name}/update/overview")
async def updatet_book_overview(book_name: str,
                                body: UpdateBook, 
                                user_name: str = Depends(authenticate)) -> dict:
    
    book = await BookCol.check_existence_and_permission(
        BookCol.name==book_name,
        user_name=user_name,
        message_for_exist_exception="book_name with supllied id doesn't exist",
    )

    await BookCol.vanish_none_update_fields_and_update(
        document=book,
        body=body.model_dump()
    )
    
    return {
        "message": "book updated successfully"
    }

#
#
#

@book_router.patch("/{book_name}/update/permission")
async def update_book_permission():
    return 0

#
#
#

@book_router.delete("/{book_name}/delete")
async def delete_book(book_name: str, 
                      user_name: str = Depends(authenticate)) -> dict:
    
    book = await BookCol.check_existence_and_permission(
        BookCol.name==book_name,
        user_name=user_name,
        message_for_exist_exception="book with supplied book_name doesn't exist"
    )

    await book.delete_book_and_associated_documents()

    return {
        "message": "successfully deleted book"
    }

#DOCUMENT CRUD------------------------------------------------------------------------------

@book_router.post("/{book_name}/new")
async def newDoc(book_name:str, body: str, user: str = Depends(authenticate)): #Create
    book = await check_existence_with_name(book_database, book_name)
    writers = book.writers
    await check_authority(user, writers)
    
    doc = Doc(**body.model_dump())
    doc.parent = book.id
    await doc_database.setIndex_and_insert(doc)
    return "successfully created document"

@book_router.get("/{book_name}/{doc_id}")
async def getDoc(book_name:str, doc_id:PydanticObjectId): #Read
    doc = await check_existence(doc_database, doc_id)
    book = await check_existence_with_name(book_database, book_name)
    await check_directory(book.id, doc.parent)
    
    return doc

@book_router.put("/{book_name}/{doc_id}/update")
async def updateDoc(book_name:str, doc_id:PydanticObjectId, body: UpdateDoc, user: str = Depends(authenticate)): #Update
    doc = await check_existence(doc_database, doc_id)
    book = await check_existence_with_name(book_database, book_name)
    await check_directory(book.id, doc.parent)
    writers = book.writers
    await check_authority(user, writers)
    
    await doc_database.update(doc_id, body)
    return "successfully updated document"

@book_router.put("/{book_name}/{doc_id}/set_index")
async def setBookIndex(book_name:str, doc_id:PydanticObjectId, newindex: int, user: str = Depends(authenticate)): #Update
    doc = await check_existence(doc_database, doc_id)
    book = await check_existence_with_name(book_database, book_name)
    await check_directory(book.id, doc.parent)
    writers = book.writers
    await check_authority(user, writers)
    
    await doc_database.resetIndex(doc_id, newindex)
    return "successfully updated index"

@book_router.delete("/{book_name}/{doc_id}/delete")
async def deleteDoc(book_name:str, doc_id:PydanticObjectId, user: str = Depends(authenticate)): #Delete
    doc = await check_existence(doc_database, doc_id)
    book = await check_existence_with_name(book_database, book_name)
    await check_directory(book.id, doc.parent)
    writers = book.writers
    await check_authority(user, writers)

    await doc_database.setIndex_and_delete(doc_id)
    return "successfully deleted document"

#CELL CRUD------------------------------------------------------------------------------
@book_router.post("/{book_name}/{doc_id}/new")
async def newCell(book_name:str, doc_id:PydanticObjectId, body:NewCell, user:str=Depends(authenticate)):#create
    doc = await check_existence(doc_database, doc_id)
    book = await check_existence_with_name(book_database, book_name)
    await check_directory(book.id, doc.parent)
    writers = book.writers
    await check_authority(user, writers)
    
    cell = Cell(**body.model_dump())
    cell.parent = str(doc_id)
    await cell_database.setIndex_and_insert(cell)
    return "successfully created cell"

@book_router.put("/{book_name}/{doc_id}/{cell_id}")
async def updateCell(book_name:str, doc_id:PydanticObjectId, cell_id:PydanticObjectId, body:UpdateCell, user:str=Depends(authenticate)):#update
    cell = await check_existence(cell_database, cell_id)
    doc = await check_existence(doc_database, doc_id)
    book = await check_existence_with_name(book_database, book_name)
    await check_directory(doc_id, cell.parent)
    await check_directory(book.id, doc.parent)
    writers = book.writers
    await check_authority(user, writers)

    await cell_database.update(cell_id, body)
    return "successfully updated cell"

@book_router.put("/{book_name}/{doc_id}/{cell_id}/set_index")
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

@book_router.delete("/{book_name}/{doc_id}/{cell_id}")
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
@book_router.post("/{book_name}/follow")
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

@book_router.post("/{book_name}/unfollow")
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