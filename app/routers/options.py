from typing import cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func

from app.db import Session
from app.dependencies import get_current_user
from app.models import OptionCreateInput, OptionResponse, OptionUpdateInput
from app.schemas import Option, Poll, User, Vote

router = APIRouter()


@router.get("/polls/{poll_id}/options", response_model=list[OptionResponse])
async def get_options(poll_id: int):
    with Session() as session:
        poll: Poll | None = session.query(Poll).filter_by(id=poll_id).first()
        if not poll:
            raise HTTPException(status_code=404, detail="Poll not found")
        options: list[Option] = session.query(Option).filter_by(poll_id=poll_id).all()
        options_response: list[OptionResponse] = []
        for option in options:
            options_response.append(
                OptionResponse(
                    id=cast(int, option.id),
                    title=cast(str, option.title),
                    description=cast(str, option.description),
                    votes_count=cast(int, option.votes_count),
                )
            )
        return options_response


@router.get("/polls/{poll_id}/options/{option_id}", response_model=OptionResponse)
async def get_option(poll_id: int, option_id: int):
    with Session() as session:
        option: Option | None = session.query(Option).filter_by(id=option_id).first()
        if not option:
            raise HTTPException(status_code=404, detail="Option not found")
        poll: Poll | None = session.query(Poll).filter_by(id=poll_id).first()
        if not poll:
            raise HTTPException(status_code=404, detail="Poll not found")
        return OptionResponse(
            id=cast(int, option.id),
            title=cast(str, option.title),
            description=cast(str, option.description),
            votes_count=cast(int, option.votes_count),
        )


@router.post(
    "/polls/{poll_id}/options",
    status_code=status.HTTP_201_CREATED,
    response_model=OptionResponse,
)
async def create_option(
    poll_id: int,
    option: OptionCreateInput,
    current_user: User = Depends(get_current_user),
):
    with Session() as session:
        poll: Poll | None = session.query(Poll).filter_by(id=poll_id).first()
        if not poll:
            raise HTTPException(status_code=404, detail="Poll not found")
        if poll.user_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="You are not authorized to create an option"
            )
        new_option = Option(
            title=option.title,
            description=option.description,
            poll_id=poll_id,
            votes_count=0,
        )
        session.add(new_option)
        session.commit()
        session.refresh(new_option)
        return OptionResponse(
            id=cast(int, new_option.id),
            title=cast(str, new_option.title),
            description=cast(str, new_option.description),
            votes_count=0,
        )


@router.put(
    "/polls/{poll_id}/options/{option_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def update_option(
    poll_id: int,
    option_id: int,
    option_update: OptionUpdateInput,
    current_user: User = Depends(get_current_user),
):
    with Session() as session:
        option: Option | None = session.query(Option).filter_by(id=option_id).first()
        if not option:
            raise HTTPException(status_code=404, detail="Option not found")
        poll: Poll | None = session.query(Poll).filter_by(id=poll_id).first()
        if not poll:
            raise HTTPException(status_code=404, detail="Poll not found")
        if option.poll_id != poll_id or poll.user_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="You are not authorized to update this option"
            )
        if option_update.title is not None:
            session.query(Option).filter_by(id=option_id).update(
                {"title": option_update.title}
            )
        if option_update.description is not None:
            session.query(Option).filter_by(id=option_id).update(
                {"description": option_update.description}
            )
        session.commit()
        session.refresh(option)
        return


@router.delete(
    "/polls/{poll_id}/options/{option_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_option(
    poll_id: int,
    option_id: int,
    current_user: User = Depends(get_current_user),
):
    with Session() as session:
        option: Option | None = session.query(Option).filter_by(id=option_id).first()
        if not option:
            raise HTTPException(status_code=404, detail="Option not found")
        poll: Poll | None = session.query(Poll).filter_by(id=poll_id).first()
        if not poll:
            raise HTTPException(status_code=404, detail="Poll not found")
        if option.poll_id != poll_id or poll.user_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="You are not authorized to delete this option"
            )
        session.delete(option)
        session.commit()
        return
