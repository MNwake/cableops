import json

from fastapi import APIRouter
from starlette.websockets import WebSocket, WebSocketDisconnect


class ParkRoutes:
    def __init__(self, connection_manager, server_memory):
        self.router = APIRouter(tags=["Cable"])
        self.manager = connection_manager
        self.memory = server_memory
        self.define_routes()

    def define_routes(self):

        @self.router.websocket("/ws/park")
        async def get_park_info(websocket: WebSocket):
            path = '/ws/teams/team'
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


    def handle_request(self, websocket, request_type, message_data):
        pass
