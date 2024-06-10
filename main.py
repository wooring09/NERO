from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from routers.books import book_router
from routers.users import user_router
from pymongo.mongo_client import MongoClient
from database.connection import Settings
from contextlib import asynccontextmanager
import uvicorn
from models.books import Book

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 데이터베이스 초기화
    await settings.initiate_database()
    yield


app = FastAPI(lifespan=lifespan)
settings = Settings()



#메인으로 이동
@app.get("/")
async def main():
    return RedirectResponse(url="/docs")


app.include_router(book_router, prefix="/books")
app.include_router(user_router, prefix="/users")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)