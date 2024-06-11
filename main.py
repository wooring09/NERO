from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
import uvicorn

from database.connection import Settings
from routers.books import book_router
from routers.users import user_router
from routers.docs import doc_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 데이터베이스 초기화
    await settings.initiate_database()
    yield


app = FastAPI(lifespan=lifespan)
settings = Settings()


@app.get("/")
async def main():
    return RedirectResponse(url="/docs")


app.include_router(book_router, prefix="/books")
app.include_router(user_router, prefix="/users")
app.include_router(doc_router, prefix="/docs")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)