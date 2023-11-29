from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Annotated, cast

from fastapi import Depends, FastAPI, Header, HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import settings
from .db import Session, init_db
from .models import Credentials, NewUser, UserResponse
from .schemas import User


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@app.post("/register", status_code=201)
async def register(new_user: NewUser):
    with Session() as session:
        hashed_password = pwd_context.hash(new_user.password)
        user = User(
            name=new_user.name, email=new_user.email, hashed_password=hashed_password
        )
        session.add(user)
        session.commit()
        return {"message": "User registered successfully"}


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm="HS256")
    return encoded_jwt


@app.post("/login")
async def authenticate_user(credentials: Credentials):
    with Session() as session:
        user = session.query(User).filter_by(email=credentials.email).first()
        if not user or not pwd_context.verify(
            credentials.password, user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=timedelta(days=1)
        )
        return {"access_token": access_token}


async def get_authorization(authorization: Annotated[str | None, Header()] = None):
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
        )
    return authorization


async def get_token(authorization: str = Depends(get_authorization)):
    scheme, token = authorization.split()
    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
        )
    return token


async def get_current_user(token: str = Depends(get_token)):
    token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid access token",
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms="HS256")
        user_email = payload.get("sub")
        if user_email is None:
            raise token_exception
        with Session() as session:
            user = session.query(User).filter_by(email=user_email).first()
            if user is None:
                raise token_exception
            return user
    except JWTError:
        raise token_exception


@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    db_user = current_user
    return UserResponse(
        id=cast(int, db_user.id),
        name=cast(str, db_user.name),
        email=cast(str, db_user.email),
    )


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
