from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import create_db_and_tables
from app.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="Task API", lifespan=lifespan)
app.include_router(router)


@app.get("/")
def read_root():
    return {"message": "Hello, backend world!"}