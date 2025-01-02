import json
from typing import Dict, Tuple, Any

from fastapi import WebSocket
from icecream import ic


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Tuple[WebSocket, str]] = {}
        self.total_connections: int = 0

    async def connect(self, websocket: WebSocket):
        await websocket.accept()

    async def disconnect(self, user_uuid: str):
        if user_uuid in self.active_connections:
            del self.active_connections[user_uuid]
            self.total_connections -= 1
            print(f"Disconnected: {user_uuid}. Total connections: {self.total_connections}")

    async def broadcast(self, type: str, data: Any):
        serialized_data = json.dumps(data) if isinstance(data, dict) else data
        formatted_message = json.dumps({"type": type, "data": serialized_data})
        for websocket, _ in self.active_connections.values():
            try:
                await websocket.send_text(formatted_message)
                if type == "stats":
                    print("broadcast", formatted_message)

            except Exception as e:
                print(f"Error sending message: {e}")

    async def register(self, websocket: WebSocket, user_uuid: str, path: str):
        if user_uuid:
            self.active_connections[user_uuid] = (websocket, path)
            self.total_connections += 1  # Increment total connections
            print(f"Registered {user_uuid} on path {path}. Total connections: {self.total_connections}")
        else:
            print("User UUID not provided for registration")

