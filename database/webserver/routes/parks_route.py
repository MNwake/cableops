from http.client import HTTPException
from typing import Optional, List, Tuple

from fastapi import APIRouter
from pydantic import json
from starlette.websockets import WebSocket, WebSocketDisconnect

from database import Park
from database.base_models import ParkBase

class ParksRoute:
    def __init__(self, manager):
        self.router = APIRouter()
        self.manager = manager
        self.define_routes()
        self.pydantic_parks = None  # Assuming this holds a list of Pydantic models

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
        async def get_parks(cursor: Optional[str] = None,
                            park_id: Optional[str] = None,
                            name: Optional[str] = None,

                            batch_size: Optional[int] = 20) -> Tuple[List[ParkBase], str | None]:
            try:
                print('****params****')
                print('cursor', 'park_id', 'name', 'batch_size', cursor, park_id, name, batch_size)
                # Retrieve parks with pagination
                parks = Park.get_parks(cursor=cursor, park_id=park_id, name=name, limit=batch_size)
                print('parks from mongo', parks)
                # Extract the IDs and convert them to strings
                park_ids = [str(park.id) for park in parks]

                # Match Pydantic parks with the retrieved IDs
                matched_parks = [park for park in self.pydantic_parks if str(park.id) in park_ids]

                # Determine the next cursor
                next_cursor = str(matched_parks[-1].id) if matched_parks else None

                print(f"Sending batch of {len(matched_parks)} matched parks and next cursor: {next_cursor}")

                return matched_parks, next_cursor

            except Exception as e:
                raise HTTPException()

    def handle_request(self, websocket, request_type, message_data):
        print('websocket', 'request_type', 'message_data')
        print(websocket, request_type, message_data)

