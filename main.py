from fastapi import FastAPI
from Routers.books import book_router
from Routers.users import user_router
from pymongo.mongo_client import MongoClient

app = FastAPI()

#메인으로 이동
@app.get("/")
async def main():
    return "hi"

app.include_router(book_router, prefix="/books")
app.include_router(user_router, prefix="/users")