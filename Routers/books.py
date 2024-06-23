from fastapi import APIRouter, Depends
from authenticate.authenticate import authenticate

from database.connection import (
    BookCol,
    DocCol, 
    CellCol,
    UserCol,
    RoleCol
)
from models.books import (
    NewBook,
    UpdateBook, 
)


book_router = APIRouter()

@book_router.get("/")
async def get_all() -> list:
    books = await BookCol.find_all(limit=10).to_list()
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
    
    #권한 체크
    await RoleCol.check_permission()

    await book.create()

    return {
        "message": "book created successfully"
    }

#
#
#

@book_router.get("/{book_name}")
async def get_book(book_name: str) -> dict:

    book = await BookCol.check_existence_and_return(
        BookCol.name==book_name,
        message="book_name with supllied id doesn't exist"
    )

    #권한 체크
    await RoleCol.check_permission()

    return book.model_dump()

#
#
#

@book_router.put("/{book_name}/update/overview")
async def updatet_book_overview(book_name: str,
                                body: UpdateBook, 
                                user_name: str = Depends(authenticate)) -> dict:
    
    book = await BookCol.check_existence_and_return(
        BookCol.name==book_name,
        user_name=user_name,
        obj_type="book",
    )

    await BookCol.vanish_none_and_update(
        document=book,
        body=body
    )
    
    #권한 체크
    await RoleCol.check_permission()
    
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
    
    book = await BookCol.check_existence_and_return(
        BookCol.name==book_name,
        user_name=user_name,
        obj_type="book",
    )

    #권한 체크
    await RoleCol.check_permission()

    await BookCol.delete_book_and_associated_documents()

    return {
        "message": "successfully deleted book"
    }

#
#
#