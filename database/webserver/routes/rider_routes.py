import json
from typing import Optional, List

from fastapi import WebSocket, APIRouter
from starlette.websockets import WebSocketDisconnect

from database.base_models import RiderBase
from database.utils import calculate_age



class RiderRoutes:
    def __init__(self, manager):
        self.router = APIRouter()
        self.manager = manager
        self.rider_base = RiderBase
        self.define_routes()
        self.pydantic_riders = None

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

        @self.router.get("")
        async def get_riders(home_park_id: Optional[str] = None, min_age: Optional[int] = None,
                             max_age: Optional[int] = None, gender: Optional[str] = None,
                             stance: Optional[str] = None, year_started: Optional[int] = None,
                             rider_id: Optional[str] = None, name: Optional[str] = None):
            # Filter pydantic_riders based on query parameters
            filtered_riders = self.filter_riders(home_park_id, min_age, max_age, gender, stance,
                                                 year_started, rider_id, name)
            return filtered_riders

    def filter_riders(self, home_park_id: Optional[str], min_age: Optional[int],
                      max_age: Optional[int], gender: Optional[str],
                      stance: Optional[str], year_started: Optional[int],
                      rider_id: Optional[str], name: Optional[str]) -> List[RiderBase]:
        # Apply filters to self.pydantic_riders
        if not self.pydantic_riders:
            return []

        return [rider for rider in self.pydantic_riders
                if (not home_park_id or rider.home_park == home_park_id)
                and (not rider_id or rider.id == rider_id)
                and (not min_age or calculate_age(rider.date_of_birth) >= min_age)
                and (not max_age or calculate_age(rider.date_of_birth) <= max_age)
                and (not gender or rider.gender == gender.lower())
                and (not stance or rider.stance == stance.lower())
                and (not year_started or rider.year_started == year_started)
                and (not name or name.lower() in rider.first_name.lower()
                     or name.lower() in rider.last_name.lower())]


    async def handle_request(self, websocket: WebSocket, request_type: str, message_data: dict):
        handlers = {
            "rider_id": self.get_rider_by_id,
            # "rider_stats": self.get_rider_stats,
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

    # TODO move to stats route
    # async def get_rider_stats(self, websocket: WebSocket, message_data: dict):
    #     rider_id = message_data.get("rider_id")
    #     if rider_id:
    #         rider_stats = await self.rider_base.fetch_rider_stats(rider_id)
    #         await websocket.send_json(rider_stats.dict())
    #     else:
    #         await websocket.send_json({"error": "Invalid request format for rider_stats"})

    async def create_rider(self, websocket: WebSocket, message_data: dict):
        rider_data_list = message_data.get("rider_data")
        if rider_data_list:
            new_riders = [await self.rider_base.create_new_rider(rider_data) for rider_data in rider_data_list]
            await self.manager.broadcast_new_riders([rider.dict() for rider in new_riders])
        else:
            await websocket.send_json({"error": "Invalid request format for create_rider"})



