from typing import Any

from fastapi import APIRouter
from pydantic import json
from starlette.websockets import WebSocket, WebSocketDisconnect

from database.webserver import ResponseHandler


class ParkRoutes:
    def __init__(self, connection_manager, server_memory):
        self.router = APIRouter()
        self.manager = connection_manager
        self.memory = server_memory
        self.define_routes()

    def define_routes(self):
        @self.router.websocket("/ws/park")
        async def get_park_info(websocket: WebSocket):
            path = '/ws/parks/park'
            await self.manager.connect(websocket, path)
            while True:
                try:
                    message = await websocket.receive_text()
                    if message:
                        message_data = json.loads(message)
                        request_type = message_data.get("request_type")
                        if request_type:
                            await self.handle_request(websocket, request_type, message_data)
                        else:
                            await websocket.send_json({"error": "Invalid request format"})
                except WebSocketDisconnect as e:
                    print('websocketdisconnect', e)
                finally:
                    pass

        @self.router.get("")
        async def get_parks() -> dict[str, Any]:
            try:
                return {'data': self.memory.parks}
            except Exception as e:
                return ResponseHandler.error('Failed to delivery parks')

    async def handle_request(self, websocket, request_type, message_data):
        print('websocket', 'request_type', 'message_data')
        print(websocket, request_type, message_data)
