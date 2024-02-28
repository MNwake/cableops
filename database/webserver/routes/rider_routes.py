import json
from typing import Optional, Dict, Any, List

from fastapi import WebSocket, APIRouter, Query, HTTPException
from starlette.websockets import WebSocketDisconnect

from database import Rider
from database.base_models import RiderBase


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
        async def get_riders(cursor: Optional[str] = None,
                             home_park_id: Optional[str] = None,
                             min_age: Optional[int] = None,
                             max_age: Optional[int] = None,
                             gender: Optional[str] = Query(None, enum=['male', 'female']),
                             stance: Optional[str] = Query(None, enum=['regular', 'goofy']),
                             year_started: Optional[str] = None,
                             rider_id: Optional[str] = Query(None, description="Comma-separated rider IDs"),
                             name: Optional[str] = Query(None, description="Search by first or last name"),
                             ) -> str | dict[str, list[Any] | str | None]:
            try:
                if not self.pydantic_riders:
                    return 'database not loaded'

                # Retrieve matching rider IDs based on query parameters
                riders = Rider.get_riders(home_park_id=home_park_id, min_age=min_age, max_age=max_age,
                                          gender=gender, stance=stance, year_started=year_started,
                                          rider_id=rider_id, name=name, cursor=cursor)
                print('rider id', riders[0].id)
                # Extract the IDs and convert them to strings
                rider_ids = [str(rider.id) for rider in riders]

                # Match Pydantic riders with the retrieved IDs
                matched_riders = [rider for rider in self.pydantic_riders if str(rider.id) in rider_ids]

                print(f"Sending batch of {len(matched_riders)} matched riders")

                # Determine the next cursor
                next_cursor = str(matched_riders[-1].id) if matched_riders else None

                # Return a dictionary with data and cursor
                return {"data": matched_riders, "cursor": next_cursor}

            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

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
