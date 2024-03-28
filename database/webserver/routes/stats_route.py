import json
from typing import Optional, List

from fastapi import APIRouter, WebSocket, HTTPException
from starlette.websockets import WebSocketDisconnect

from database.base_models import RiderStatsBase


# Will print all messages from debug and above



class StatsRoute:
    def __init__(self, connection_manager, server_memory):
        self.router = APIRouter()
        self.manager = connection_manager
        self.memory = server_memory
        self.define_routes()

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
                            batch_size: Optional[int] = None) -> dict[str, List[RiderStatsBase] | str | None]:
            try:
                # Filter the stats from memory based on query parameters
                filtered_stats = [stat for stat in self.memory.stats if
                                  (not stat_id or str(stat.id) == stat_id) and
                                  (not rider_id or stat.rider == rider_id) and
                                  (not year or stat.year == year)]

                # Apply pagination if needed
                if cursor:
                    cursor_index = next((index for index, stat in enumerate(filtered_stats) if str(stat.id) == cursor),
                                        -1)
                    filtered_stats = filtered_stats[cursor_index + 1:]  # Skip past the cursor
                if batch_size:
                    filtered_stats = filtered_stats[:batch_size]

                # Prepare next cursor
                next_cursor = str(filtered_stats[-1].id) if filtered_stats else None

                return {'data': filtered_stats, 'cursor': next_cursor}

            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))


    def handle_request(self, websocket, request_type, message_data):
        pass
