from typing import Optional, List

from fastapi import APIRouter
from pydantic import json
from starlette.websockets import WebSocket

from database.base_models import ParkBase


class ParksRoute:
    def __init__(self, manager):
        self.router = APIRouter()
        self.manager = manager
        self.define_routes()
        self.pydantic_parks = None

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

        @self.router.get('')
        async def get_parks(state: Optional[str] = None,
                            name: Optional[str] = None,
                            team_id: Optional[str] = None,
                            cable_id: Optional[str] = None):
            """
            Fetch parks with optional filtering parameters.
            """
            # Filter pydantic_parks based on query parameters
            filtered_parks = self.filter_parks(state, name, team_id, cable_id)
            return filtered_parks

    def filter_parks(self, state: Optional[str],
                     name: Optional[str],
                     team_id: Optional[str],
                     cable_id: Optional[str]) -> List[ParkBase]:
        # Apply filters to self.pydantic_parks
        if not self.pydantic_parks:
            return []

        return [park for park in self.pydantic_parks
                if (not state or park.state == state)
                and (not name or name.lower() in park.name.lower())
                and (not team_id or park.team == team_id)
                and (not cable_id or cable_id in park.cable)]

