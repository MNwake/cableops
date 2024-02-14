import json

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
from starlette.websockets import WebSocket, WebSocketDisconnect

from database import Rider, Scorecard, Park
from database.events import RiderStats


class ScorecardModel(BaseModel):
    difficulty: float
    execution: float
    creativity: float
    division: float
    section: str
    rider_id: str
    landed: bool
    park_id: str


class ScorecardRoutes:
    def __init__(self, manager, api):
        self.api = api
        self.router = APIRouter()
        self.manager = manager
        self.define_routes()

    def define_routes(self):

        @self.router.websocket("/ws")
        async def scorecards_websocket(websocket: WebSocket):
            await self.manager.connect(websocket, path="/scorecards/ws")
            while True:
                try:
                    message = await websocket.receive_text()
                    if message:
                        message_data = json.loads(message)
                        print('message data', message_data)
                        if "scorecard" in message_data.key():
                            # Call the new_rider method with appropriate parameters
                            print('do something with the new rider:')
                            # await self.new_rider(message_data["new_rider"])
                except WebSocketDisconnect as e:
                    print('websocketdisconnect', e)
                finally:
                    self.manager.disconnect(websocket, path='/scorecards/ws')

        @self.router.post("/new")
        async def create_scorecard(scorecard_data: ScorecardModel = Body(...)):
            try:
                rider = Rider.objects(id=scorecard_data.rider_id).first()
                park = Park.objects(id=scorecard_data.park_id).first()
                if not rider:
                    raise HTTPException(status_code=404, detail="Rider not found")

                # Create a new Scorecard instance
                scorecard = Scorecard(
                    difficulty=scorecard_data.difficulty,
                    execution=scorecard_data.execution,
                    creativity=scorecard_data.creativity,
                    division=scorecard_data.division,
                    section=scorecard_data.section,
                    landed=scorecard_data.landed,
                    rider=rider,
                    park=park
                )
                scorecard.save()

                # Trigger RiderStats calculation and update
                rider_stats = RiderStats.objects(rider=rider).first()
                if rider_stats:
                    updated_stats_data = rider_stats.calculate_stats()
                else:
                    updated_stats_data = RiderStats(rider=rider)
                    updated_stats_data.calculate_stats()
                    updated_stats_data.save()

                # Return the created scorecard
                return scorecard

            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))