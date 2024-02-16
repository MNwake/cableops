import asyncio
import threading
import time

import uvicorn
from bson import ObjectId
from fastapi import FastAPI

from database.base_models import RiderStatsBase, ParkBase
from database.base_models.scorecard_base import ScorecardBase
from database import Rider, Scorecard, Park
from database.base_models import RiderBase
from database.events import RiderStats
from database.utils import custom_json_encoder
from .connection_manager import ConnectionManager
from .routes import StatsRoute, ScorecardRoutes, RiderRoutes
from .routes.parks_route import ParksRoute


class FastAPIApp:
    def __init__(self, database):
        self.app = FastAPI(json_encoders={ObjectId: custom_json_encoder})
        self.database = database
        self.initialized = False
        self.manager = ConnectionManager()
        self.parks_route = ParksRoute(self.manager)
        self.riders_route = RiderRoutes(self.manager)
        self.stats_route = StatsRoute(self.manager)
        self.scorecard_route = ScorecardRoutes(self.manager, self)
        self.rider_base = RiderBase
        self.setup_routes()

    async def initialize(self):
        await self.convert_data()

    def start_fastapi_initialization(self):
        # Function to run the asyncio event loop
        asyncio.run(self.initialize())

    def start_fastapi_server(self):
        fastapi_thread = threading.Thread(target=self.run)
        fastapi_thread.start()
        # Create a thread to run the asyncio initialization
        initialization_thread = threading.Thread(target=self.start_fastapi_initialization)
        initialization_thread.start()

    def setup_routes(self):
        self.app.include_router(self.riders_route.router, prefix="/riders")
        self.app.include_router(self.stats_route.router, prefix="/stats")
        self.app.include_router(self.scorecard_route.router, prefix="/scorecards")
        self.app.include_router(self.parks_route.router, prefix="/parks")

        @self.app.get("/")
        async def read_root():
            return {"Hello": "World"}

        @self.app.get("/ping")
        async def ping():
            return {"status": "OK"}


    def run(self):
        uvicorn.run(self.app, host="0.0.0.0", port=8000)

    async def convert_data(self):
        routes = [
            self.riders_route,
            # self.stats_route,
            # self.scorecard_route,
            # self.parks_route
        ]
        start_time = time.time()

        all_riders_time = time.time()
        all_riders = Rider.objects().all()
        print(f"Time taken to fetch all riders: {time.time() - all_riders_time:.2f} seconds")

        all_stats_time = time.time()
        all_stats = RiderStats.objects().all()
        print(f"Time taken to fetch all stats: {time.time() - all_stats_time:.2f} seconds")

        recent_scorecards_time = time.time()
        recent_scorecards = Scorecard.get_most_recent_cards()
        print(f"Time taken to fetch recent scorecards: {time.time() - recent_scorecards_time:.2f} seconds")

        all_parks_time = time.time()
        all_parks = Park.objects().all()
        print(f"Time taken to fetch all parks: {time.time() - all_parks_time:.2f} seconds")

        print(f"Total time taken: {time.time() - start_time:.2f} seconds")


        all_parks = Park.objects().all()

        # Now pass the awaited statistics to the mongo_to_pydantic method
        print('starting parks conversion')
        self.parks_route.pydantic_parks = ParkBase.mongo_to_pydantic(all_parks)
        print('starting riders conversion')
        self.riders_route.pydantic_riders = RiderBase.mongo_to_pydantic(all_riders)
        print('starting stats conversion')
        self.stats_route.pydantic_stats = RiderStatsBase.mongo_to_pydantic(all_stats)
        print('starting scorecard conversion')
        self.scorecard_route.pydantic_scorecards = ScorecardBase.mongo_to_pydantic(recent_scorecards)

        end_time = time.time()
        execution_time = end_time - start_time
        self.initialized = True
        print(f"Pydantic Conversion time: {execution_time} seconds")

