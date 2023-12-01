from typing import cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app.db import Session
from app.dependencies import get_current_user
from app.models import (OptionResponse, PollCreateInput, PollResponse,
                        PollUpdateInput)
from app.schemas import Option, Poll, User, Vote

router = APIRouter()


# TODO: add pagination
@router.get("/polls", response_model=list[PollResponse])
async def get_polls(current_user: User = Depends(get_current_user)):
    with Session() as session:
        # TODO: add proper typing
        user_polls = (
            session.query(Poll)
            .filter(Poll.user_id == current_user.id)
            .options(joinedload(Poll.options))
            .all()
        )
        polls_response: list[PollResponse] = []
        for poll in user_polls:
            options_response: list[OptionResponse] = []
            for option in poll.options:
                options_response.append(
                    OptionResponse(
                        id=cast(int, option.id),
                        title=cast(str, option.title),
                        description=cast(str, option.description),
                        votes_count=cast(int, option.votes_count),
                    )
                )
            polls_response.append(
                PollResponse(
                    id=cast(int, poll.id),
                    title=cast(str, poll.title),
                    description=cast(str, poll.description),
                    user_id=cast(int, poll.user_id),
                    options=options_response,
                )
            )
        return polls_response


@router.get("/polls/{poll_id}", response_model=PollResponse)
async def get_poll(poll_id: int):
    with Session() as session:
        poll: Poll | None = session.query(Poll).filter_by(id=poll_id).first()
        if not poll:
            raise HTTPException(status_code=404, detail="Poll not found")
        options: list[Option] = session.query(Option).filter_by(poll_id=poll_id).all()
        options_response = []
        for option in options:
            options_response.append(
                OptionResponse(
                    id=cast(int, option.id),
                    title=cast(str, option.title),
                    description=cast(str, option.description),
                    votes_count=cast(int, option.votes_count),
                )
            )
        return PollResponse(
            id=cast(int, poll.id),
            title=cast(str, poll.title),
            description=cast(str, poll.description),
            user_id=cast(int, poll.user_id),
            options=options_response,
        )


@router.post("/polls", status_code=status.HTTP_201_CREATED, response_model=PollResponse)
async def create_poll(
    poll: PollCreateInput, current_user: User = Depends(get_current_user)
):
    with Session() as session:
        new_poll = Poll(
            title=poll.title, description=poll.description, user_id=current_user.id
        )
        session.add(new_poll)
        session.commit()
        session.refresh(new_poll)
        options_response: list[OptionResponse] = []
        for option in poll.options:
            new_option = Option(
                title=option.title,
                description=option.description,
                poll_id=new_poll.id,
                votes_count=0,
            )
            session.add(new_option)
            session.commit()
            session.refresh(new_option)
            options_response.append(
                OptionResponse(
                    id=cast(int, new_option.id),
                    title=cast(str, new_option.title),
                    description=cast(str, new_option.description),
                    votes_count=0,
                )
            )
        return PollResponse(
            id=cast(int, new_poll.id),
            title=cast(str, new_poll.title),
            description=cast(str, new_poll.description),
            user_id=cast(int, new_poll.user_id),
            options=options_response,
        )


@router.put("/polls/{poll_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_poll(
    poll_id: int,
    poll_update: PollUpdateInput,
    current_user: User = Depends(get_current_user),
):
    with Session() as session:
        poll: Poll | None = session.query(Poll).filter_by(id=poll_id).first()
        if not poll:
            raise HTTPException(status_code=404, detail="Poll not found")
        if poll.user_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="You are not authorized to update this poll"
            )
        if poll_update.title is not None:
            session.query(Poll).filter_by(id=poll_id).update(
                {"title": poll_update.title}
            )
        if poll_update.description is not None:
            session.query(Poll).filter_by(id=poll_id).update(
                {"description": poll_update.description}
            )
        session.commit()
        session.refresh(poll)
        return


@router.delete("/polls/{poll_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_poll(poll_id: int, current_user: User = Depends(get_current_user)):
    with Session() as session:
        poll: Poll | None = session.query(Poll).filter_by(id=poll_id).first()
        if not poll:
            raise HTTPException(status_code=404, detail="Poll not found")
        if poll.user_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="You are not authorized to delete this poll"
            )
        session.delete(poll)
        session.commit()
        return
