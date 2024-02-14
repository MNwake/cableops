import json

from fastapi import WebSocket, APIRouter
from starlette.websockets import WebSocketDisconnect

from database.base_models import RiderBase


class RiderRoutes:
    def __init__(self, manager):
        self.router = APIRouter()
        self.manager = manager
        self.rider_base = RiderBase
        self.define_routes()

    def define_routes(self):
        @self.router.websocket("/ws")
        async def rider_websocket(websocket: WebSocket):
            await self.manager.connect(websocket, path="/riders/ws")
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

    async def handle_request(self, websocket: WebSocket, request_type: str, message_data: dict):
        handlers = {
            "rider_id": self.get_rider_by_id,
            "rider_stats": self.get_rider_stats,
            "create_rider": self.create_rider,
            # Add more request types and corresponding handler methods as needed
        }
        handler = handlers.get(request_type)
        if handler:
            await handler(websocket, message_data)
        else:
            await websocket.send_json({"error": "Unsupported request type"})

    async def get_rider_by_id(self, websocket: WebSocket, message_data: dict):
        rider_id_list = message_data.get("rider_id")
        if rider_id_list:
            riders = [await self.rider_base.fetch_rider_by_id(rider_id) for rider_id in rider_id_list]
            await websocket.send_json([rider.dict() for rider in riders])
        else:
            await websocket.send_json({"error": "Invalid request format for rider_id"})

    async def get_rider_stats(self, websocket: WebSocket, message_data: dict):
        rider_id = message_data.get("rider_id")
        if rider_id:
            rider_stats = await self.fetch_rider_stats(rider_id)
            await websocket.send_json(rider_stats.dict())
        else:
            await websocket.send_json({"error": "Invalid request format for rider_stats"})

    async def create_rider(self, websocket: WebSocket, message_data: dict):
        rider_data_list = message_data.get("rider_data")
        if rider_data_list:
            new_riders = [await self.create_new_rider(rider_data) for rider_data in rider_data_list]
            await self.manager.broadcast_new_riders([rider.dict() for rider in new_riders])
        else:
            await websocket.send_json({"error": "Invalid request format for create_rider"})



