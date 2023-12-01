from typing import cast

from fastapi import (APIRouter, Depends, HTTPException, WebSocket,
                     WebSocketDisconnect, status)

from app.db import Session
from app.dependencies import get_current_user
from app.models import OptionResponse, PollResponse, VoteResponse
from app.schemas import Option, Poll, User, Vote
from app.ws import ws_manager

router = APIRouter()


@router.post(
    "/polls/{poll_id}/options/{option_id}/vote",
    status_code=status.HTTP_201_CREATED,
    response_model=VoteResponse,
)
async def vote(
    poll_id: int, option_id: int, current_user: User = Depends(get_current_user)
):
    with Session() as session:
        poll: Poll | None = session.query(Poll).filter_by(id=poll_id).first()
        if not poll:
            raise HTTPException(status_code=404, detail="Poll not found")
        option: Option | None = session.query(Option).filter_by(id=option_id).first()
        if not option or option.poll_id != poll_id:
            raise HTTPException(status_code=404, detail="Option not found")
        new_vote = Vote(user_id=current_user.id, poll_id=poll_id, option_id=option_id)
        session.add(new_vote)
        session.query(Option).filter_by(id=option_id).update(
            {"votes_count": cast(int, option.votes_count) + 1}
        )
        session.commit()
        session.refresh(new_vote)
        session.refresh(option)
        vote_response = VoteResponse(
            id=cast(int, new_vote.id),
            user_id=cast(int, new_vote.user_id),
            poll_id=cast(int, new_vote.poll_id),
            option_id=cast(int, new_vote.option_id),
        )
        option_response = OptionResponse(
            id=cast(int, option.id),
            title=cast(str, option.title),
            description=cast(str, option.description),
            votes_count=cast(int, option.votes_count),
        )
        user_response = {
            "id": cast(int, current_user.id),
            "username": cast(str, current_user.username),
        }
        await ws_manager.broadcast(
            poll_id,
            {
                "event": "vote",
                "data": {
                    "vote": vote_response,
                    "option": option_response,
                    "user": user_response,
                },
            },
        )
        return vote_response


@router.delete(
    "/polls/{poll_id}/options/{option_id}/vote", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_vote(
    poll_id: int, option_id: int, current_user: User = Depends(get_current_user)
):
    with Session() as session:
        poll: Poll | None = session.query(Poll).filter_by(id=poll_id).first()
        if not poll:
            raise HTTPException(status_code=404, detail="Poll not found")
        option: Option | None = session.query(Option).filter_by(id=option_id).first()
        if not option:
            raise HTTPException(status_code=404, detail="Option not found")
        vote: Vote | None = (
            session.query(Vote)
            .filter_by(user_id=current_user.id, poll_id=poll_id, option_id=option_id)
            .first()
        )
        if not vote:
            raise HTTPException(status_code=404, detail="Vote not found")
        session.delete(vote)
        session.query(Option).filter_by(id=option_id).update(
            {"votes_count": cast(int, option.votes_count) - 1}
        )
        session.commit()
        session.refresh(option)
        vote_response = VoteResponse(
            id=cast(int, vote.id),
            user_id=cast(int, vote.user_id),
            poll_id=cast(int, vote.poll_id),
            option_id=cast(int, vote.option_id),
        )
        option_response = OptionResponse(
            id=cast(int, option.id),
            title=cast(str, option.title),
            description=cast(str, option.description),
            votes_count=cast(int, option.votes_count),
        )
        user_response = {
            "id": cast(int, current_user.id),
            "username": cast(str, current_user.username),
        }
        await ws_manager.broadcast(
            poll_id,
            {
                "event": "delete",
                "data": {
                    "vote": vote_response,
                    "option": option_response,
                    "user": user_response,
                },
            },
        )
        return


@router.websocket("/polls/{poll_id}")
async def vote_websocket(
    websocket: WebSocket,
    poll_id: int,
    _: User = Depends(get_current_user),
):
    poll: Poll | None = None
    options: list[Option] = []
    with Session() as session:
        poll = session.query(Poll).filter_by(id=poll_id).first()
        if not poll:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        options = session.query(Option).filter_by(poll_id=poll_id).all()
    await websocket.accept()
    await ws_manager.connect(poll_id, websocket)
    poll_response = PollResponse(
        id=cast(int, poll.id),
        title=cast(str, poll.title),
        description=cast(str, poll.description),
        user_id=cast(int, poll.user_id),
        options=[
            OptionResponse(
                id=cast(int, option.id),
                title=cast(str, option.title),
                description=cast(str, option.description),
                votes_count=cast(int, option.votes_count),
            )
            for option in options
        ],
    )
    try:
        await ws_manager.broadcast(
            poll_id,
            {
                "event": "connect",
                "data": {
                    "poll": poll_response,
                },
            },
        )
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await ws_manager.disconnect(poll_id, websocket)
