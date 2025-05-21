from typing import Dict
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    def connect(self, task_id: str, websocket: WebSocket):
        self.active_connections[task_id] = websocket

    def disconnect(self, task_id: str):
        self.active_connections.pop(task_id, None)

    async def send_json(self, task_id: str, data: dict):
        websocket = self.active_connections.get(task_id)
        if websocket:
            await websocket.send_json(data)

manager = ConnectionManager()
