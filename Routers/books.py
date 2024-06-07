from fastapi import APIRouter, HTTPException, Depends, status
from Database.connection import Database
from Models.books_m import Book, Doc, Cell, new_book,update_book, new_doc, update_doc
from Models.users_m import User
from Authenticate.authenticate import authenticate
from beanie import PydanticObjectId, Document
from pydantic import BaseModel

book_router = APIRouter()
book_database = Database(Book)
doc_database = Database(Doc)
cell_database = Database(Cell)
user_database = Database(User)

# async def check(database, id):
#     check = await book_database.findOne({"_id": ObjectId(id)})
#     if not check:
#         return False
#     return check

# async def checkExist(database, query):
#     return
# async def checkAuthority()

@book_router.get("/")
async def getAll():
    cursor = await book_database.findAll()
    books = list(cursor)
    return books

#BOOK CRUD----------------------------------------------------------------------------------

@book_router.post("/new")
async def newBook(body:new_book, user: str = Depends(authenticate)): #Create
    user_objid = await user_database.id_to_OBJid(user)
    if await book_database.find({"id_":body.id_}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Book with supplied id already exists"
        )
    book = Book(**body.model_dump())
    book.writers = [str(user_objid)]
    await book_database.insert(book)
    return "successfully created book"

@book_router.get("/{book_id}")
async def getBook(book_id:str): #Read
    book_objid = await book_database.id_to_OBJid(book_id)
    if not book_objid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book with supplied id doesn't exist"
        )
    
    book = await book_database.get(book_objid)
    return book

@book_router.put("/{book_id}/update")
async def updatetBook(book_id:str, body:update_book, user: str = Depends(authenticate)): #Update
    book_objid = await book_database.id_to_OBJid(book_id)
    book = await book_database.get(book_objid)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book with supplied id doesn't exist"
        )
    writers = book.writers
    if not user == writers[0]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authority to access"
        )
    await book_database.update(book_objid, body)
    return "successfully updated book"

@book_router.delete("/{book_id}/delete")
async def deleteBook(book_id:str, user: str = Depends(authenticate)): #Delete
    book_objid = await book_database.id_to_OBJid(book_id)

    book = await book_database.get(book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book with supplied id doesn't exist"
        )
    
    writers = book.writers
    if not user == writers[0]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authority to access"
        )
    await book_database.delete(book_objid)
    return "successfully deleted book"

#DOCUMENT CRUD------------------------------------------------------------------------------

@book_router.post("/{book_id}/new")
async def newDoc(book_id:str, body: new_doc, user: str = Depends(authenticate)): #Create
    book_objid = await book_database.id_to_OBJid(book_id)
    user_objid = await user_database.id_to_OBJid(user)
    if not book_objid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book with supplied id doesn't exist"
        )
    
    book = await book_database.get(book_objid)
    writers = book.writers
    if not str(user_objid) in writers:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authority to access"
        )
    
    doc = Doc(**body.model_dump())
    doc.parentBook = str(book_objid)
    doc.writers = [user]
    
    await doc_database.insertDoc(book_objid, doc)
    return "successfully created document"

@book_router.get("/{book_id}/{doc_id}")
async def getDoc(book_id:str, doc_id:PydanticObjectId): #Read
    book_objid = await book_database.id_to_OBJid(book_id)
    if not book_objid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book with supplied id doesn't exist"
        )
    
    checkdoc = await doc_database.get(doc_id)
    if not checkdoc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document with supplied id doesn't exist"
        )
    
    checkbook = await book_database.get(book_objid)
    if not str(doc_id) in checkbook.documents:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Document with supplied id doesn't belong to Book with supplied id"
        )
    
    return str(checkdoc)

@book_router.put("/{book_id}/{doc_id}/update")
async def updateDoc(book_id:str, doc_id:PydanticObjectId, body: update_doc, user: str = Depends(authenticate)): #Update
    book_objid = await book_database.id_to_OBJid(book_id)
    if not book_objid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book with supplied id doesn't exist"
        )

    checkdoc = await doc_database.get(doc_id)
    if not checkdoc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document with supplied id doesn't exist"
        )
    writers = checkdoc.writers
    if not user in writers:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authority to access"
        )
    
    checkbook = await book_database.get(book_objid)
    if not str(doc_id) in checkbook.documents:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Document with supplied id doesn't belong to Book with supplied id"
        )
    
    await doc_database.update(doc_id, body)
    return "successfully updated document"

@book_router.delete("/{book_id}/{doc_id}/delete")
async def deleteDoc(book_id, doc_id, user: str = Depends(authenticate)): #Delete
    book_objid = await book_database.id_to_OBJid(book_id)
    if not book_objid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book with supplied id doesn't exist"
        )

    checkdoc = await doc_database.get(doc_id)
    if not checkdoc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document with supplied id doesn't exist"
        )
    writers = dict(checkdoc)["writers"]
    if not user == writers[0]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authority to access"
        )
    
    checkbook = await book_database.get(book_objid)
    documentsID = dict(checkbook)["documents"]
    if not doc_id in documentsID:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Document with supplied id doesn't belong to Book with supplied id"
        )
    
    await doc_database.deleteDoc(book_objid, doc_id)
    return "successfully deleted document"

@book_router.post("/{book_id}/follow")
async def followbook(book_id, user:str = Depends(authenticate)):
    book_objid = await book_database.id_to_OBJid(book_id)
    user_objid = await user_database.id_to_OBJid(user)

    if not book_objid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    book = await book_database.get(book_objid)
    writers = book.writers
    if str(user_objid) in writers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already followed"
        )
    
    await book_database.followBook(user_objid, book_objid)
    return "successfully followed"

@book_router.post("/{book_id}/unfollow")
async def unfollowbook(book_id, user:str = Depends(authenticate)):
    book_objid = await book_database.id_to_OBJid(book_id)
    user_objid = await user_database.id_to_OBJid(user)

    book = await book_database.get(book_objid)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    writers = dict(book)["writers"]
    if not str(user_objid) in writers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already unfollowed"
        )
    await book_database.unfollowBook(user_objid, book_objid)
    return "successfully unfollowed"