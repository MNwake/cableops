import json
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Body, HTTPException, Query
from starlette.websockets import WebSocket, WebSocketDisconnect

from database import Rider, Scorecard, Park
from database.base_models.scorecard_base import ScorecardBase
from database.events import RiderStats


class ScorecardRoutes:
    def __init__(self, manager, api):
        self.api = api
        self.router = APIRouter()
        self.manager = manager
        self.define_routes()
        self.pydantic_scorecards = []

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

        @self.router.post("/create")
        async def create_scorecard(scorecard_data: ScorecardBase = Body(...)):
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

        @self.router.get("")
        async def get_scorecards(cursor: Optional[str] = Query(None, description="Cursor for pagination"),
                                 batch_size: Optional[int] = Query(10, description="Number of scorecards per batch"),
                                 sort_by: Optional[str] = Query('Most Recent', description="Sort by attribute",
                                                                enum=["Most Recent", "Score: Highest",
                                                                      "Score: Lowest"])):
            try:
                scorecards_query = Scorecard.get_scorecards(sort_by=sort_by, cursor=cursor)
                scorecards = scorecards_query.limit(batch_size)

                # Process scorecards and determine next cursor
                processed_scorecards, next_cursor = self.process_scorecards(scorecards)

                return processed_scorecards, next_cursor

            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

        @self.router.get("/rider/{rider_id}")
        async def get_rider_scorecards(rider_id: str,
                                       cursor: Optional[str] = Query(None, description="Cursor for pagination"),
                                       batch_size: Optional[int] = Query(10,
                                                                         description="Number of scorecards per batch"),
                                       sort_by: Optional[str] = Query('Most Recent', description="Sort by attribute",
                                                                      enum=["Most Recent", "Score: Highest",
                                                                            "Score: Lowest"])):
            try:
                scorecards_query = Scorecard.get_scorecards(rider_id=rider_id, sort_by=sort_by, cursor=cursor)
                scorecards = scorecards_query.limit(batch_size)

                # Process scorecards and determine next cursor
                processed_scorecards, next_cursor = self.process_scorecards(scorecards)

                return processed_scorecards, next_cursor

            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

    def process_scorecards(self, scorecards):
        final_scorecards = []
        next_cursor = None

        for scorecard in scorecards:
            scorecard_id = str(scorecard.id)
            cached_model = self.find_in_cache(scorecard_id)

            if cached_model:
                pydantic_model = cached_model
            else:
                pydantic_model = ScorecardBase.mongo_to_pydantic([scorecard])[0]
                self.pydantic_scorecards.append(pydantic_model)

            final_scorecards.append(pydantic_model)

        if final_scorecards:
            # Set next_cursor as the ISO format string of the date of the last scorecard
            next_cursor = final_scorecards[-1].date.isoformat()

        return final_scorecards, next_cursor

    def find_in_cache(self, scorecard_id):
        for scorecard in self.pydantic_scorecards:
            if scorecard.id == scorecard_id:
                return scorecard
        return None

