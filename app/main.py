from contextlib import asynccontextmanager

from fastapi import FastAPI

from .db import init_db, session
from .models import User


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return session.query(User).all()
