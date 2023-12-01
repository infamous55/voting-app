import json
from typing import Any

from fastapi import WebSocket


class WebSocketsManager:
    def __init__(self):
        self.active_polls: dict[int, set[WebSocket]] = {}

    async def connect(self, poll_id: int, websocket: WebSocket):
        if poll_id not in self.active_polls:
            self.active_polls[poll_id] = set()
        self.active_polls[poll_id].add(websocket)

    async def disconnect(self, poll_id: int, websocket: WebSocket):
        self.active_polls[poll_id].remove(websocket)
        if len(self.active_polls[poll_id]) == 0:
            del self.active_polls[poll_id]

    async def broadcast(self, poll_id: int, message: Any):
        message = json.dumps(message)
        for websocket in self.active_polls[poll_id]:
            await websocket.send_text(message)


ws_manager = WebSocketsManager()
