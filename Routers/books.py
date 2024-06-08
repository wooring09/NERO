from fastapi import APIRouter, HTTPException, Depends, status
from Database.connection import Database
from Models.books_m import Book, Doc, Cell, new_book,update_book, new_doc, update_doc, new_cell, update_cell
from Models.users_m import User
from Authenticate.authenticate import authenticate
from Authenticate.check_exception import check_existence, check_authority, check_directory, convert_id, check_duplicate
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
    user_objid = await convert_id(user_database, user)
    await check_duplicate(book_database, "name", body.name)

    book = Book(**body.model_dump())
    book.writers = [str(user_objid)]
    await book_database.insertBook(book)
    return "successfully created book"

@book_router.get("/{book_name}")
async def getBook(book_name:str): #Read
    book_objid = await convert_id(book_database,book_name)
    book = await check_existence(book_database, book_objid)
    return book


@book_router.put("/{book_name}/update")
async def updatetBook(book_name:str, body:update_book, user: str = Depends(authenticate)): #Update
    book_objid = await convert_id(book_database, book_name)
    user_objid = await convert_id(user_database, user)
    book = await check_existence(book_database, book_objid)
    writers = book.writers
    await check_authority(user_objid, writers)

    await book_database.update(book_objid, body)
    return "successfully updated book"

@book_router.delete("/{book_name}/delete")
async def deleteBook(book_name:str, user: str = Depends(authenticate)): #Delete
    book_objid = await convert_id(book_database, book_name)
    user_objid = await convert_id(user_database, user)
    book = await check_existence(book_database, book_objid)
    writers = book.writers
    await check_authority(user_objid, writers)

    await book_database.deleteBook(book_objid)
    return "successfully deleted book"

#DOCUMENT CRUD------------------------------------------------------------------------------

@book_router.post("/{book_name}/new")
async def newDoc(book_name:str, body: new_doc, user: str = Depends(authenticate)): #Create
    book_objid = await convert_id(book_database, book_name)
    user_objid = await convert_id(user_database, user)
    book = await check_existence(book_database, book_objid)
    writers = book.writers
    await check_authority(user_objid, writers)
    
    doc = Doc(**body.model_dump())
    doc.parentBook = str(book_objid)
    await doc_database.insertDoc(book_objid, doc)
    return "successfully created document"

@book_router.get("/{book_name}/{doc_id}")
async def getDoc(book_name:str, doc_id:PydanticObjectId): #Read
    book_objid = await convert_id(book_database, book_name)
    doc = await check_existence(doc_database, doc_id)
    book = await check_existence(book_database, book_objid)
    documents = book.documents
    await check_directory(doc_id, documents)
    
    return doc

@book_router.put("/{book_name}/{doc_id}/update")
async def updateDoc(book_name:str, doc_id:PydanticObjectId, body: update_doc, user: str = Depends(authenticate)): #Update
    book_objid = await convert_id(book_database, book_name)
    user_objid = await convert_id(user_database, user)
    await check_existence(doc_database, doc_id)
    book = await check_existence(book_database, book_objid)
    documents = book.documents
    await check_directory(doc_id, documents)
    writers = book.writers
    await check_authority(user_objid, writers)
    
    await doc_database.update(doc_id, body)
    return "successfully updated document"

@book_router.delete("/{book_name}/{doc_id}/delete")
async def deleteDoc(book_name, doc_id, user: str = Depends(authenticate)): #Delete
    book_objid = await convert_id(book_database, book_name)
    doc = await check_existence(doc_database, doc_id)
    writers = doc.writers
    await check_authority(user, writers)  
    book = await check_existence(book_database, book_objid)
    documents = book.documents
    check_directory(doc_id, documents)
    
    await doc_database.deleteDoc(book_objid, doc_id)
    return "successfully deleted document"

#CELL CRUD------------------------------------------------------------------------------
@book_router.post("/{book_name}/{doc_id}/new")
async def newCell(book_name:str, doc_id:PydanticObjectId, body:new_cell, user:str=Depends(authenticate)):#create
    book_objid = await convert_id(book_database, book_name)
    user_objid = await convert_id(user_database, user)
    doc = await check_existence(doc_database, doc_id)
    book = await check_existence(book_database, book_objid)
    writers = book.writers
    await check_authority(user_objid, writers)
    documents = book.documents
    await check_directory(doc_id, documents)
    
    cell = Cell(**body.model_dump())
    cell.parentDoc = str(doc_id)
    await cell_database.insertCell(doc_id, cell)
    return "successfully created cell"

@book_router.put("/{book_name}/{doc_id}/{cell_id}")
async def updateCell(book_name:str, doc_id:PydanticObjectId, cell_id:PydanticObjectId, body:update_cell, user:str=Depends(authenticate)):#update
    book_objid = await convert_id(book_database, book_name)
    user_objid = await convert_id(user_database, user)
    doc = await check_existence(doc_database, doc_id)
    book = await check_existence(book_database, book_objid)
    await check_existence(cell_database, cell_id)
    writers = book.writers
    await check_authority(user_objid, writers)
    documents = book.documents
    await check_directory(doc_id, documents)
    cells = doc.cells
    await check_directory(cell_id, cells)
        
    await cell_database.update(cell_id, body)
    return "successfully updated cell"

@book_router.delete("/{book_name}/{doc_id}/{cell_id}")
async def deleteCell(book_name:str, doc_id:PydanticObjectId, cell_id:PydanticObjectId, user:str=Depends(authenticate)):#update
    book_objid = await convert_id(book_database, book_name)
    user_objid = await convert_id(user_database, user)
    doc = await check_existence(doc_database, doc_id)
    book = await check_existence(book_database, book_objid)
    await check_existence(cell_database, cell_id)
    writers = book.writers
    await check_authority(user_objid, writers)
    documents = book.documents
    await check_directory(doc_id, documents)
    cells = doc.cells
    await check_directory(cell_id, cells)

    await cell_database.deleteCell(doc_id, cell_id)
    return "successfully deleted cell"

#follow
@book_router.post("/{book_name}/follow")
async def followbook(book_name, user:str = Depends(authenticate)):
    book_objid = await convert_id(book_database, book_name)
    user_objid = await convert_id(user_database, user)
    book = await book_database.get(book_objid)
    writers = book.writers
    if str(user_objid) in writers:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already followed"
        )
    
    await book_database.followBook(user_objid, book_objid)
    return "successfully followed"

@book_router.post("/{book_name}/unfollow")
async def unfollowbook(book_name, user:str = Depends(authenticate)):
    book_objid = await convert_id(book_database, book_name)
    user_objid = await convert_id(user_database, user)
    book = await book_database.get(book_objid)
    writers = book.writers
    if not str(user_objid) in writers:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already unfollowed"
        )
    
    await book_database.unfollowBook(user_objid, book_objid)
    return "successfully unfollowed"