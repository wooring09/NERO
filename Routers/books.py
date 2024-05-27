from fastapi import APIRouter, HTTPException, Depends
from Database.connection import Books_coll, Basic_connection, Docs_connection
from Models.books_m import Book, Document, updateBook
from Authenticate.authenticate import authenticate
from bson.objectid import ObjectId

book_router = APIRouter()
book_database = Basic_connection(Books_coll)
doc_database = Docs_connection

async def check_exist(database, id):
    response = await database.findOne({"_id": ObjectId(id)})
    return str(response)


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
    check = await check_exist(book_database, book_id)
    if check == "None":
        raise HTTPException(
            status_code=404,
            detail="book with supplied id doesn't exist"
        )
    await book_database.updateOne({"_id":ObjectId(book_id)}, book)
    return "successfully updated book"

@book_router.post("{book_id}/new")
async def newDoc(book_id, doc: Document, user: str = Depends(authenticate)):
    await doc_database.insertOne(doc)
    return "successfully created document"

@book_router.post("{book_id}/{doc_id}/update")
async def updateDoc(book_id, doc_id, doc: Document, user: str = Depends(authenticate)):
    await doc_database.updateOne(book_id, doc_id, doc)
    return "successfully updated document"