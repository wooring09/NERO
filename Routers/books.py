from fastapi import APIRouter, HTTPException
from Database.connection import Books_coll
import json

book_router = APIRouter()

@book_router.get("/")
async def main():
    cursor = Books_coll.find({})
    books = list(cursor)
    if books is None:
        raise HTTPException(
            status_code=404,
            detail="Books are not found"
        )
    print(books)
    return str(books)