from typing import Optional

import uvicorn
from fastapi import FastAPI

from database.base_models import RiderBase
from database import DataBase, Rider
from database.events import RiderStats
from .connection_manager import ConnectionManager
from .encoder import custom_encoder
from .routes import StatsRoute, ScorecardRoutes, RiderRoutes

# MongoDB connection
DataBase()

class FastAPIApp:
    def __init__(self):
        self.app = FastAPI()
        self.manager = ConnectionManager()
        self.riders_route = RiderRoutes(self.manager)
        self.stats_route = StatsRoute(self.manager)
        self.scorecard_route = ScorecardRoutes(self.manager, self)
        self.rider_base = RiderBase
        self.setup_routes()


    def setup_routes(self):
        self.app.include_router(self.riders_route.router, prefix="/riders")
        self.app.include_router(self.stats_route.router, prefix="/stats")
        self.app.include_router(self.scorecard_route.router, prefix="/scorecards")
        self.app.include_router(self.scorecard_route.router, prefix="/parks")

        @self.app.get("/")
        async def read_root():
            return {"Hello": "World"}

        @self.app.get("/ping")
        async def ping():
            return {"status": "OK"}

        @self.app.get("/all_riders/")
        async def get_riders(home_park: Optional[str] = None, min_age: Optional[int] = None,
                             max_age: Optional[int] = None, gender: Optional[str] = None,
                             stance: Optional[str] = None, year_started: Optional[int] = None):
            # Build query filters based on provided parameters
            query_filters = {}
            if home_park:
                query_filters["home_park"] = home_park
            if min_age:
                query_filters["age__gte"] = min_age
            if max_age:
                query_filters["age__lte"] = max_age
            if gender:
                query_filters["gender"] = gender
            if stance:
                query_filters["stance"] = stance
            if year_started:
                query_filters["year_started"] = year_started

            # Query Riders using MongoEngine with the constructed query filters
            filtered_riders = Rider.objects(**query_filters)

            # Convert the filtered riders to Pydantic models
            pydantic_riders = RiderBase.mongo_to_pydantic(filtered_riders)

            return pydantic_riders

        @self.app.get("/riders")
        async def get_rider_stats():
            try:
                # Fetch stats for all riders
                all_rider_stats = RiderStats.objects().all()

                # Convert each RiderStats object to a dictionary and then apply the custom encoder
                return [custom_encoder(stats.to_mongo().to_dict()) for stats in all_rider_stats]

            except Exception as e:
                print('Error in getting all rider stats:', e)
                return {"error": "Failed to retrieve all rider stats"}, 500


    def run(self):
        uvicorn.run(self.app, host="0.0.0.0", port=8000)

