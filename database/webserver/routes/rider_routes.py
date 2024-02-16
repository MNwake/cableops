import json
from typing import Optional, List

from fastapi import WebSocket, APIRouter, Query
from starlette.websockets import WebSocketDisconnect

from database.base_models import RiderBase
from database.utils import calculate_age, Stance, Gender, SortRiders


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
        def get_riders(home_park_id: Optional[str] = None,
                       min_age: Optional[int] = None,
                       max_age: Optional[int] = None,
                       gender: Optional[str] = Query(None, enum=['male', 'female']),
                       stance: Optional[str] = Query(None, enum=['regular', 'goofy']),
                       year_started: Optional[str] = None,
                       rider_id: Optional[str] = Query(None,
                                                       description="Comma-separated rider IDs"),
                       name: Optional[str] = Query(None,
                                                   description="Search by first or last name"),
                       sort_by: Optional[SortRiders] = None) -> List[RiderBase]:
            # Filter riders based on query parameters
            filtered_riders = self.filter_riders(home_park_id, min_age, max_age, gender, stance,
                                                 year_started, rider_id, name)

            # Sort filtered riders
            sorted_riders = self.sort_riders(filtered_riders, sort_by)

            return sorted_riders

    def filter_riders(self, home_park_id: Optional[str], min_age: Optional[int],
                      max_age: Optional[int], gender: Optional[str],
                      stance: Optional[str], year_started: Optional[str],
                      rider_id: Optional[str], name: Optional[str]) -> List[RiderBase]:
        # Apply filters to self.pydantic_riders
        if not self.pydantic_riders:
            return []

        filtered_riders = self.pydantic_riders

        # Apply filters
        if home_park_id:
            filtered_riders = [rider for rider in filtered_riders if rider.home_park == home_park_id]
        if rider_id:
            filtered_riders = [rider for rider in filtered_riders if rider.id == rider_id]
        if min_age:
            filtered_riders = [rider for rider in filtered_riders if calculate_age(rider.date_of_birth) >= min_age]
        if max_age:
            filtered_riders = [rider for rider in filtered_riders if calculate_age(rider.date_of_birth) <= max_age]
        if gender:
            filtered_riders = [rider for rider in filtered_riders if rider.gender == gender]
        if stance:
            filtered_riders = [rider for rider in filtered_riders if rider.stance == stance]
        if year_started:
            filtered_riders = [rider for rider in filtered_riders if rider.year_started == year_started]
        if name:
            filtered_riders = [rider for rider in filtered_riders if
                               name.lower() in rider.first_name.lower() or name.lower() in rider.last_name.lower()]

        return filtered_riders

    def sort_riders(self, riders: List[RiderBase], sort_by: Optional[SortRiders]) -> List[RiderBase]:
        if not sort_by:
            return riders

        if sort_by == SortRiders.oldest_to_youngest:
            return sorted(riders, key=lambda x: x.date_of_birth)
        elif sort_by == SortRiders.youngest_to_oldest:
            return sorted(riders, key=lambda x: x.date_of_birth, reverse=True)
        elif sort_by == SortRiders.alphabetical:
            return sorted(riders, key=lambda x: (x.first_name, x.last_name))
        elif sort_by == SortRiders.most_years_experience:
            return sorted(riders, key=lambda x: x.year_started, reverse=True)

        return riders


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
