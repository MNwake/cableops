import sys
from pprint import pprint
from typing import Optional, List

from bson import ObjectId
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

from database import DataBase
from database.Events import Rider, Park
from utils import build_rider_query
import uvicorn

app = FastAPI()
# MongoDB connection
DataBase()
if sys.platform == 'linux':
    app.mount("/static", StaticFiles(directory="/home/theokoester/dev/cableops/server/assets/images"), name="static")


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, data: str):
        for connection in self.active_connections:
            await connection.send_text(data)


def custom_encoder(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, (list, set)):
        return [custom_encoder(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: custom_encoder(value) for key, value in obj.items()}
    return obj


class FastAPIApp:
    def __init__(self):
        self.app = FastAPI()
        self.setup_routes()

    def setup_routes(self):
        @self.app.get("/")
        async def read_root():
            return {"Hello": "World"}

        @self.app.get("/ping")
        async def ping():
            return {"status": "OK"}

        @self.app.get("/riders/")
        async def get_riders(
                home_park: Optional[str] = None,
                min_age: Optional[int] = 0,
                max_age: Optional[int] = 100,
                gender: Optional[str] = None,
                stance: Optional[str] = None,
                year_started: Optional[int] = None
        ):
            query = build_rider_query(home_park=home_park, min_age=min_age, max_age=max_age, gender=gender,
                                      stance=stance, year_started=year_started)

            riders = Rider.objects(__raw__=query).all()

            riders_list = [custom_encoder(rider.to_mongo().to_dict()) for rider in riders]
            print(riders_list)
            return riders_list

        @self.app.get('/parks/')
        async def get_parks():
            parks = Park.objects().all()
            parks_list = [custom_encoder(park.to_mongo()) for park in parks]
            pprint(parks_list)
            return parks_list

    def run(self):
        uvicorn.run(self.app, host="0.0.0.0", port=8000)
