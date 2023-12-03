from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from app.routers import votes

from .db import init_db
from .routers import auth, options, polls, users

description = """
Voting App API documentation

## Authentication
- Register a new user account
- Login to your account

You can authorize requests with your JSON Web Token (JWT) in the `Authorization` header by using the value `Bearer <token>`.

## Users
- See your profile and the profiles of other users
- Update your account information
- Delete your account and all associated data

## Polls
- Create/Read/Update/Delete polls

## Options
- Create/Read/Update/Delete options of a poll

## Votes
- Vote for an option or withdraw your vote
- See real-time vote counts for each poll via WebSockets at the `/polls/<poll_id>` endpoint
"""

tags_metadata = [
    {
        "name": "auth",
        "description": "Register and login endpoints",
    },
    {
        "name": "users",
        "description": "Account information management endpoints",
    },
    {
        "name": "polls",
        "description": "Polls CRUD endpoints",
    },
    {
        "name": "options",
        "description": "Options CRUD endpoints",
    },
    {
        "name": "votes",
        "description": "Voting and vote withdrawal endpoints",
    },
]


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Voting App",
    description=description,
    openapi_tags=tags_metadata,
    version="1.0.0",
    license_info={"name": "MIT", "url": "https://opensource.org/license/mit/"},
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(polls.router)
app.include_router(options.router)
app.include_router(votes.router)

Instrumentator().instrument(app).expose(app)
