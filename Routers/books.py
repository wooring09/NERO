from fastapi import APIRouter, HTTPException, Depends, status
from Database.connection import Database
from Models.books_m import Book, Doc, Cell, new_book,update_book, new_doc, update_doc, new_cell, update_cell
from Models.users_m import User
from Authenticate.authenticate import authenticate
from Authenticate.check_exception import check_existence, check_authority, check_directory, check_duplicate, check_existence_with_name
from beanie import PydanticObjectId, Document
from pydantic import BaseModel

book_router = APIRouter()
book_database = Database(Book)
doc_database = Database(Doc)
cell_database = Database(Cell)
user_database = Database(User)

@book_router.get("/")
async def getAll():
    cursor = await book_database.findAll()
    books = list(cursor)
    return books

#BOOK CRUD----------------------------------------------------------------------------------

@book_router.post("/new")
async def newBook(body:new_book, user: str = Depends(authenticate)): #Create
    await check_duplicate(book_database, "name", body.name)

    book = Book(**body.model_dump())
    await book_database.insert(book)
    await book_database.followBook(user, book.name)
    return "successfully created book"

@book_router.get("/{book_name}")
async def getBook(book_name:str): #Read
    book = await check_existence_with_name(book_database, book_name)
    return book


@book_router.put("/{book_name}/update")
async def updatetBook(book_name:str, body:update_book, user: str = Depends(authenticate)): #Update
    book = await check_existence_with_name(book_database, book_name)
    writers = book.writers
    await check_authority(user, writers)

    await book_database.update(book.id, body)
    return "successfully updated book"

@book_router.delete("/{book_name}/delete")
async def deleteBook(book_name:str, user: str = Depends(authenticate)): #Delete
    book = await check_existence_with_name(book_database, book_name)
    writers = book.writers
    await check_authority(user, writers)

    await book_database.deleteBook(book.id)
    return "successfully deleted book"

#DOCUMENT CRUD------------------------------------------------------------------------------

@book_router.post("/{book_name}/new")
async def newDoc(book_name:str, body: new_doc, user: str = Depends(authenticate)): #Create
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
async def updateDoc(book_name:str, doc_id:PydanticObjectId, body: update_doc, user: str = Depends(authenticate)): #Update
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
async def newCell(book_name:str, doc_id:PydanticObjectId, body:new_cell, user:str=Depends(authenticate)):#create
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
async def updateCell(book_name:str, doc_id:PydanticObjectId, cell_id:PydanticObjectId, body:update_cell, user:str=Depends(authenticate)):#update
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