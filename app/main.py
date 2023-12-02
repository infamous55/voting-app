from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routers import votes

from .db import init_db
from .routers import auth, options, polls, users


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(polls.router)
app.include_router(options.router)
app.include_router(votes.router)


# the following functions are used for testing purposes
# TODO: delete them
#
# @app.get("/users")
# def get_users():
#     with Session() as session:
#         users = session.query(User).all()
#         return users
#
#
# @app.delete("/users")
# def delete_users():
#     with Session() as session:
#         session.query(User).delete()
#         session.commit()
#         return {"message": "All users deleted"}
