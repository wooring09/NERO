from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from Routers.books import book_router
from Routers.users import user_router
from pymongo.mongo_client import MongoClient
from Database.connection import Settings
import uvicorn

app = FastAPI()
settings = Settings()

@app.on_event("startup")
async def on_startup():
    # 데이터베이스 초기화
    await settings.initiate_database()

#메인으로 이동
@app.get("/")
async def main():
    return RedirectResponse(url="/books")

app.include_router(book_router, prefix="/books")
app.include_router(user_router, prefix="/users")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)