from fastapi import APIRouter, HTTPException
from Database.connection import Books_coll, Basic_connection, Docs_connection
import json

book_router = APIRouter()
book_database = Basic_connection(Books_coll)
doc_database = Docs_connection

@book_router.get("/")
async def main():
    cursor = book_database.findOne({})
    books = list(cursor)
    if books is None:
        raise HTTPException(
            status_code=404,
            detail="Books are not found"
        )
    print(books)
    return str(books)