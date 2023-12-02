from typing import cast

from fastapi import APIRouter, Depends, HTTPException, status

from app.db import Session
from app.dependencies import get_current_user, pwd_context
from app.models import Profile, UserResponse, UserUpdateInput
from app.schemas import User

router = APIRouter()


@router.get(
    "/users/{user_id}",
    response_model=Profile,
    status_code=status.HTTP_200_OK,
    summary="Get user profile",
    tags=["users"],
)
async def get_user_profile(user_id: int):
    with Session() as session:
        user: User | None = session.query(User).filter_by(id=user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return Profile(
            name=cast(str, user.name),
        )


@router.get(
    "/users/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    tags=["users"],
)
async def get_user(current_user: User = Depends(get_current_user)):
    db_user = current_user
    return UserResponse(
        id=cast(int, db_user.id),
        name=cast(str, db_user.name),
        email=cast(str, db_user.email),
    )


@router.put(
    "/users/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Update current user",
    tags=["users"],
)
async def update_user(
    user_update: UserUpdateInput,
    current_user: User = Depends(get_current_user),
):
    with Session() as session:
        if user_update.name is not None:
            session.query(User).filter_by(id=current_user.id).update(
                {"name": user_update.name}
            )
        if user_update.email is not None:
            session.query(User).filter_by(id=current_user.id).update(
                {"email": user_update.email}
            )
        if user_update.password is not None:
            hashed_password = pwd_context.hash(user_update.password)
            session.query(User).filter_by(id=current_user.id).update(
                {"hashed_password": hashed_password}
            )
        session.commit()
        return


@router.delete(
    "/users/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete current user",
    tags=["users"],
)
async def delete_user(
    current_user: User = Depends(get_current_user),
):
    with Session() as session:
        session.query(User).filter_by(id=current_user.id).delete()
        session.commit()
        return
