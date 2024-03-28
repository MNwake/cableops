import asyncio
import os
import threading

import uvicorn
from bson import ObjectId
from fastapi import FastAPI
from fastapi.responses import FileResponse
from starlette.staticfiles import StaticFiles

from database import ServerMemory
from database.database_converter import DatabaseConverter

from database.utils import custom_json_encoder
from .connection_manager import ConnectionManager
from .routes import StatsRoute, ScorecardRoutes, RiderRoutes
from .routes.contest_routes import ContestRoutes
from .routes.parks_route import ParkRoutes

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_HTML = os.path.join(BASE_DIR, 'website/index.html')
PRIVACY_HTML = os.path.join(BASE_DIR, 'website/privacy_policy.html')


class RouteManager:

    def __init__(self, connection, memory):
        self.connection = connection
        self.parks_route = ParkRoutes(connection, memory)
        self.riders_route = RiderRoutes(connection, memory)
        self.stats_route = StatsRoute(connection, memory)
        self.contest_route = ContestRoutes(connection, memory)
        self.scorecard_route = ScorecardRoutes(connection, memory)

    def setup_routes(self, app):
        app.include_router(self.riders_route.router, prefix="/riders")
        app.include_router(self.stats_route.router, prefix="/stats")
        app.include_router(self.scorecard_route.router, prefix="/scorecards")
        app.include_router(self.parks_route.router, prefix="/parks")
        app.include_router(self.contest_route.router, prefix="/contest")


class FastAPIApp:
    def __init__(self, database):
        self.app = FastAPI(json_encoders={type: custom_json_encoder})
        self.initialized = False
        self.database = database
        self.manager = ConnectionManager()
        self.memory = ServerMemory()
        self.router = RouteManager(self.manager, self.memory)
        self.router.setup_routes(self.app)
        self.app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "website", "static")), name="static")

    async def initialize(self):

        await self.memory.load_data()

    def start_fastapi_initialization(self):
        # Function to run the asyncio event loop
        asyncio.run(self.initialize())

    def start_fastapi_server(self):
        fastapi_thread = threading.Thread(target=self.run)
        fastapi_thread.start()
        # Create a thread to run the asyncio initialization
        initialization_thread = threading.Thread(target=self.start_fastapi_initialization)
        initialization_thread.start()

        @self.app.get("/")
        async def read_root():
            return FileResponse(ROOT_HTML)

        @self.app.get("/privacy")
        async def read_root():
            return FileResponse(PRIVACY_HTML)

        @self.app.get("/ping")
        async def ping():
            return {"status": "OK"}

    def run(self):
        uvicorn.run(self.app, host="0.0.0.0", port=8000, log_level="debug")
