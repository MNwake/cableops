import json
from pprint import pprint
from typing import Optional, List

from fastapi import APIRouter, WebSocket

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
            try:
                while True:
                    # Wait for a message containing the rider_id
                    data = await websocket.receive_text()
                    rider_id = json.loads(data).get('rider_id')

                    # Fetch stats for the requested rider
                    if rider_id:
                        rider_stats = await RiderStats.get_rider_stats(rider_id=rider_id)
                        await websocket.send_json(rider_stats)
                    else:
                        # Handle invalid rider_id
                        await websocket.send_text("Invalid rider ID")
            except Exception as e:
                print('Exception in rider stats WebSocket:', e)
            finally:
                self.manager.disconnect(websocket, path)

        @self.router.get("/riders")
        async def get_stats(stat_id: Optional[str] = None, rider_id: Optional[str] = None, year: Optional[int] = None):
            # Filter pydantic_stats based on query parameters
            filtered_stats = self.filter_stats(stat_id, rider_id, year)
            return filtered_stats

    def filter_stats(self, stat_id: Optional[str], rider_id: Optional[str], year: Optional[int]) -> List[
        'RiderStatsBase']:
        # Apply filters to self.pydantic_stats
        if not self.pydantic_stats:
            print('no pydantic stats')
            return []

        return [stat for stat in self.pydantic_stats
                if (not stat_id or stat.id == stat_id)
                and (not rider_id or stat.rider == rider_id)
                and (not year or stat.year == year)]




