from fastapi import APIRouter, HTTPException, Depends
from Database.connection import Books_coll, Basic_connection, Docs_connection
from Models.books_m import Book, Document, updateBook
from Authenticate.authenticate import authenticate
from bson.objectid import ObjectId

book_router = APIRouter()
book_database = Basic_connection(Books_coll)
doc_database = Docs_connection

async def check(database, id):
    check = await book_database.findOne({"_id": ObjectId(id)})
    if not check:
        return False
    return True

@book_router.get("/")
async def getAll():
    cursor = book_database.findMany({})
    books = list(cursor)
    return str(books)

@book_router.get("{book_id}")
async def getBook(book_id):
    book = book_database.findOne(book_id)
    if book is None:
        raise HTTPException(
            status_code=404,
            detail="Book with supplied id doesn't exist"
        )
    return str(book)

@book_router.post("/new")
async def newBook(book:Book, user: str = Depends(authenticate)):
    await book_database.insertOne(book)
    return "successfully created book"

@book_router.post("{book_id}/update")
async def updatetBook(book_id, book:updateBook, user: str = Depends(authenticate)):
    if(not check(book_database, book_id)):
        raise HTTPException(
            status_code=404,
            detail="Book with supplied id doesn't exist"
        )
    await book_database.updateOne({"_id":ObjectId(book_id)}, book)
    return "successfully updated book"

@book_router.post("{book_id}/new")
async def newDoc(book_id, doc: Document, user: str = Depends(authenticate)):
    if(not check(book_database, book_id)):
        raise HTTPException(
            status_code=404,
            detail="Book with supplied id doesn't exist"
        )
    await doc_database.insertOne(book_id, doc)
    return "successfully created document"

@book_router.post("{book_id}/{doc_id}/update")
async def updateDoc(book_id, doc_id, doc: Document, user: str = Depends(authenticate)):
    await doc_database.updateOne(book_id, doc_id, doc)
    return "successfully updated document"