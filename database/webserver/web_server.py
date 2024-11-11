import asyncio
import os
import threading

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.staticfiles import StaticFiles

from database import ServerMemory
from database.NoteBot.route import NoteBotRoute

from database.utils import custom_json_encoder
from .connection_manager import ConnectionManager
from .routes import StatsRoute, ScorecardRoutes, RiderRoutes
from .routes.contest_routes import ContestRoutes
from .routes.parks_route import ParkRoutes

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_HTML = os.path.join(BASE_DIR, 'website/index.html')
PRIVACY_HTML = os.path.join(BASE_DIR, 'website/privacy_policy.html')


class MaxSizeLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_upload_size: int = 5 * 1024 * 1024):
        super().__init__(app)
        self.max_upload_size = max_upload_size

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get('content-length')
        if content_length and int(content_length) > self.max_upload_size:
            raise HTTPException(status_code=413, detail="Payload Too Large")
        return await call_next(request)

class RouteManager:

    def __init__(self, connection, memory):
        self.connection = connection
        self.parks_route = ParkRoutes(connection, memory)
        self.riders_route = RiderRoutes(connection, memory)
        self.stats_route = StatsRoute(connection, memory)
        self.contest_route = ContestRoutes(connection, memory)
        self.scorecard_route = ScorecardRoutes(connection, memory)
        self.speech2note_route = NoteBotRoute(connection, memory)

    def setup_routes(self, app):
        app.include_router(self.riders_route.router, prefix="/api/riders")
        app.include_router(self.stats_route.router, prefix="/api/stats")
        app.include_router(self.scorecard_route.router, prefix="/api/scorecards")
        app.include_router(self.parks_route.router, prefix="/api/parks")
        app.include_router(self.contest_route.router, prefix="/api/contest")
        app.include_router(self.speech2note_route.router, prefix="/api/notebot")

class FastAPIApp:
    def __init__(self, database):
        self.app = FastAPI(json_encoders={type: custom_json_encoder})
        self.initialized = False
        self.database = database
        self.manager = ConnectionManager()
        self.memory = ServerMemory()
        self.router = RouteManager(self.manager, self.memory)
        self.router.setup_routes(self.app)

        # Add the middleware to limit the request size to 5MB
        self.app.add_middleware(MaxSizeLimitMiddleware)

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

        # @self.app.get("/")
        # async def read_root():
        #     return FileResponse(ROOT_HTML)

        @self.app.get('/api')
        async def api_page():
            # Create a dictionary to hold the API endpoints
            endpoints = {
                "riders": "/api/riders",
                "stats": "/api/stats",
                "scorecards": "/api/scorecards",
                "parks": "/api/parks",
                "contest": "/api/contest",
                "notebot": "/api/notebot",
            }
            return {"api": endpoints}

        @self.app.get("/privacy")
        async def read_root():
            return FileResponse(PRIVACY_HTML)

        @self.app.get("/ping")
        async def ping():
            return {"status": "OK"}

        @self.app.get("/motor_tower")
        async def get_default_photo():
            # Assuming your FastAPI app runs from the "server" directory
            # Construct the correct path from the project root or known base directory
            base_directory = "/home/theokoester/dev/cableops/server"  # Use the correct base directory
            photo_path = os.path.join(base_directory, "assets/images/motor_tower.png")

            if os.path.exists(photo_path):
                print(f"file exists at: {photo_path}")
                return FileResponse(photo_path)
            else:
                raise HTTPException(status_code=404, detail="Default photo not found")
    def run(self):
        uvicorn.run(self.app, host="0.0.0.0", port=8000, log_level="info")
