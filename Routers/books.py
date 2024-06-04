from fastapi import APIRouter, HTTPException, Depends, status
from Database.connection import Books_coll,Docs_coll, Database, docDatabase
from Models.books_m import Book, Document, updateBook, updateDocument
from Authenticate.authenticate import authenticate
from bson.objectid import ObjectId

book_router = APIRouter()
book_database = Database(Books_coll)
doc_database = docDatabase()

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
    cursor = book_database.findMany({})
    books = list(cursor)
    return str(books)

#BOOK CRUD----------------------------------------------------------------------------------

@book_router.post("/new")
async def newBook(book:Book, user: str = Depends(authenticate)): #Create
    book.writers = [user]
    book.documents = []
    await book_database.insertOne(book)
    return "successfully created book"

@book_router.get("{book_id}")
async def getBook(book_id): #Read
    book = book_database.findOne(book_id)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book with supplied id doesn't exist"
        )
    return str(book)

@book_router.post("{book_id}/update")
async def updatetBook(book_id, book:updateBook, user: str = Depends(authenticate)): #Update
    check = await book_database.findOne({"_id": ObjectId(book_id)})
    if not check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book with supplied id doesn't exist"
        )
    writers = dict(check)["writers"]
    if not user == writers[0]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authority to access"
        )
    await book_database.updateOne({"_id":ObjectId(book_id)}, book)
    return "successfully updated book"

@book_router.delete("{book_id}/delete")
async def deleteBook(book_id, user: str = Depends(authenticate)): #Delete
    check = await book_database.findOne({"_id": ObjectId(book_id)})
    if not check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book with supplied id doesn't exist"
        )
    writers = dict(check)["writers"]
    if not user == writers[0]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authority to access"
        )
    await book_database.deleteBook(book_id)
    return "successfully deleted book"

#DOCUMENT CRUD------------------------------------------------------------------------------

@book_router.post("{book_id}/new")
async def newDoc(book_id, doc: Document, user: str = Depends(authenticate)): #Create
    check = await book_database.findOne({"_id": ObjectId(book_id)})
    if not check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book with supplied id doesn't exist"
        )
    writers = dict(check)["writers"]
    if not user in writers:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authority to access"
        )
    doc.parentBook = book_id
    doc.writers = [user]
    doc.comments = []
    await doc_database.insertOne(book_id, doc)
    return "successfully created document"

@book_router.get("{book_id}/{doc_id}")
async def getBook(book_id, doc_id): #Read
    checkdoc = await doc_database.findOne(doc_id)
    if not checkdoc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document with supplied id doesn't exist"
        )
    
    checkbook = await book_database.findOne({"_id":ObjectId(book_id)})
    if not checkbook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book with supplied id doesn't exist"
        )
    documentsID = dict(checkbook)["documents"]
    if not doc_id in documentsID:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Document with supplied id doesn't belong to Book with supplied id"
        )
    
    return str(checkdoc)

@book_router.post("{book_id}/{doc_id}/update")
async def updateDoc(book_id, doc_id, doc: updateDocument, user: str = Depends(authenticate)): #Update
    checkdoc = await doc_database.findOne(doc_id)
    if not checkdoc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document with supplied id doesn't exist"
        )
    writers = dict(checkdoc)["writers"]
    if not user in writers:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authority to access"
        )
    
    checkbook = await book_database.findOne({"_id":ObjectId(book_id)})
    if not checkbook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book with supplied id doesn't exist"
        )
    documentsID = dict(checkbook)["documents"]
    if not doc_id in documentsID:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Document with supplied id doesn't belong to Book with supplied id"
        )
    
    await doc_database.updateOne(doc_id, doc)
    return "successfully updated document"

@book_router.delete("{book_id}/{doc_id}/delete")
async def deleteDoc(book_id, doc_id, user: str = Depends(authenticate)): #Delete
    checkdoc = await doc_database.findOne(doc_id)
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
    
    checkbook = await book_database.findOne({"_id":ObjectId(book_id)})
    if not checkbook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book with supplied id doesn't exist"
        )
    documentsID = dict(checkbook)["documents"]
    if not doc_id in documentsID:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Document with supplied id doesn't belong to Book with supplied id"
        )
    
    await doc_database.deleteOne(book_id, doc_id)
    return "successfully deleted document"

@book_router.post("/{book_id}/follow")
async def followbook(book_id, user:str = Depends(authenticate)):
    book = await book_database.findOne({"_id":ObjectId(book_id)})
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    writers = dict(book)["writers"]
    if user in writers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already followed"
        )
    await book_database.followBook(user, book_id)
    return "successfully followed"

@book_router.post("/{book_id}/unfollow")
async def unfollowbook(book_id, user:str = Depends(authenticate)):
    book = await book_database.findOne({"_id":ObjectId(book_id)})
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    writers = dict(book)["writers"]
    if not user in writers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already unfollowed"
        )    
    await book_database.unfollowBook(user, book_id)
    return "successfully unfollowed"
