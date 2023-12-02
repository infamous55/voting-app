from datetime import datetime, timedelta
from typing import cast

from fastapi import APIRouter, HTTPException, status
from jose import jwt

from app.config import settings
from app.db import Session
from app.dependencies import pwd_context
from app.models import Credentials, LoginResponse, NewUser
from app.schemas import User

router = APIRouter()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=LoginResponse,
    summary="Register new user",
    tags=["auth"],
)
async def register(new_user: NewUser):
    with Session() as session:
        hashed_password = pwd_context.hash(new_user.password)
        user = User(
            name=new_user.name, email=new_user.email, hashed_password=hashed_password
        )
        session.add(user)
        session.commit()
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=timedelta(days=1)
        )
        return LoginResponse(access_token=access_token)


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm="HS256")
    return encoded_jwt


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=LoginResponse,
    summary="Login user",
    tags=["auth"],
)
async def authenticate_user(credentials: Credentials):
    with Session() as session:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
        )
        user: User | None = (
            session.query(User).filter_by(email=credentials.email).first()
        )
        if not user:
            raise credentials_exception
        hashed_password = cast(str, user.hashed_password)
        if not pwd_context.verify(credentials.password, hashed_password):
            raise credentials_exception
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=timedelta(days=1)
        )
        return LoginResponse(access_token=access_token)
