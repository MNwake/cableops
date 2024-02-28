import json
from pprint import pprint
from typing import Optional, List, Tuple

from fastapi import APIRouter, WebSocket, HTTPException
from starlette.websockets import WebSocketDisconnect

from database.base_models import RiderStatsBase
from database.events import RiderStats
from database.webserver.encoder import custom_encoder


class StatsRoute:
    def __init__(self, manager):
        self.router = APIRouter()
        self.manager = manager
        self.define_routes()
        self.pydantic_stats = None

    def define_routes(self):
        @self.router.websocket("/ws/rider")
        async def get_rider_stats(websocket: WebSocket):
            path = '/ws/stats/rider'
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

        @self.router.get("/riders")
        async def get_stats(cursor: Optional[str] = None,
                            stat_id: Optional[str] = None,
                            rider_id: Optional[str] = None,
                            year: Optional[int] = None,
                            batch_size: Optional[int] = 20) -> Tuple[List[RiderStatsBase], str | None]:
            try:
                # Retrieve matching rider stats based on query parameters
                stats = RiderStats.get_rider_stats(stat_id=stat_id, rider_id=rider_id, year=year, cursor=cursor,
                                                   limit=batch_size)

                # Extract the IDs and convert them to strings
                stat_ids = [str(stat.id) for stat in stats]

                # Match Pydantic stats with the retrieved IDs
                matched_stats = [stat for stat in self.pydantic_stats if str(stat.id) in stat_ids]

                # Determine the next cursor
                next_cursor = str(matched_stats[-1].id) if matched_stats else None

                return matched_stats, next_cursor

            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

    def handle_request(self, websocket, request_type, message_data):
        pass
