from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import settings
from .db import Session
from .schemas import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
        user_email: str | None = payload.get("sub")
        if user_email is None:
            raise token_exception
        with Session() as session:
            user: User | None = session.query(User).filter_by(email=user_email).first()
            if user is None:
                raise token_exception
            return user
    except JWTError:
        raise token_exception
