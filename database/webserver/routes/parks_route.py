from fastapi import APIRouter
from pydantic import json
from starlette.websockets import WebSocket

from database import Park, custom_encoder


class ParksRoute:
    def __init__(self, manager):
        self.router = APIRouter()
        self.manager = manager
        self.define_routes()


    def define_routes(self):
        @self.router.websocket("/ws/")
        async def get_parks(websocket: WebSocket):
            path = '/ws/parks'
            await self.manager.connect(websocket, path)
            try:
                while True:
                    # Wait for a message containing the rider_id
                    data = await websocket.receive_text()
                    parks = json.loads(data)
                    print(parks)
                    # Fetch stats for the requested rider
            except Exception as e:
                print('Exception in rider stats WebSocket:', e)
            finally:
                self.manager.disconnect(websocket, path)
        @self.router.get('/')
        async def get_parks():
            parks = Park.objects().all()
            parks_list = [custom_encoder(park.to_mongo()) for park in parks]
            return parks_list