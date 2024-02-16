import json
from datetime import datetime
from pprint import pprint
from typing import Optional, List

from fastapi import APIRouter, Body, HTTPException, Query, Depends
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
        self.pydantic_scorecards = None

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
        async def get_scorecards(sort_by: Optional[str] = Query(None, description="Sort by attribute",
                                                                enum=["Most Recent", "Score:Highest", "Score: Lowest"]),
                                 cursor: Optional[str] = Query(None, description="Cursor"),
                                 rider_id: Optional[List[str]] = Query(None,
                                                                       description="Rider IDs separated by comma"),
                                 date: Optional[datetime] = Query(None, description="Date (mm/dd/yyyy)"),
                                 section: Optional[str] = Query(None, description="Section",
                                                                enum=["Kicker", "Rail", "Air Trick"]),
                                 landed: Optional[bool] = Query(None, description="Landed", enum=[True, False]),
                                 park_id: Optional[List[str]] = Query(None,
                                                                      description="Park IDs separated by comma"),
                                 range_start: Optional[int] = None,
                                 range_end: Optional[int] = None,
                                 ):
            # Filter scorecards based on query parameters
            print(self.pydantic_scorecards)
            limit = 10

            filtered_scorecards = self.filter_scorecards(rider_id, date, section,
                                                         landed, park_id)

            # Sort scorecards based on query parameters
            sorted_scorecards = self.sort_scorecards(filtered_scorecards, sort_by)

            # Apply cursor pagination
            if cursor:
                # Find the index of the cursor in the sorted list
                try:
                    cursor_index = next(i for i, scorecard in enumerate(sorted_scorecards)
                                        if str(scorecard.id) == cursor)
                    sorted_scorecards = sorted_scorecards[cursor_index:]
                except StopIteration:
                    return []

            # Apply range pagination
            paginated_scorecards = sorted_scorecards[range_start:range_end]

            return paginated_scorecards

    def filter_scorecards(self,
                          rider_id: Optional[List[str]], date: Optional[str],
                          section: Optional[str], landed: Optional[bool],
                          park_id: Optional[List[str]]):
        # Apply filters to self.pydantic_scorecards
        if not self.pydantic_scorecards:
            return []

        filtered_scorecards = self.pydantic_scorecards

        # Apply remaining filters
        if rider_id:
            filtered_scorecards = [scorecard for scorecard in filtered_scorecards
                                   if scorecard.rider_id in rider_id]
        if date:
            try:
                # Convert the date string to a datetime object
                date_obj = datetime.strptime(date, "%m/%d/%Y")
                # Filter scorecards by date
                filtered_scorecards = [scorecard for scorecard in filtered_scorecards
                                       if scorecard.date == date_obj]
            except ValueError:
                # Handle invalid date format
                pass
        if section:
            filtered_scorecards = [scorecard for scorecard in filtered_scorecards
                                   if scorecard.section == section.lower()]
        if landed is not None:
            filtered_scorecards = [scorecard for scorecard in filtered_scorecards
                                   if scorecard.landed == landed]
        if park_id:
            filtered_scorecards = [scorecard for scorecard in filtered_scorecards
                                   if scorecard.park_id in park_id]

        return filtered_scorecards

    def sort_scorecards(self, scorecards, sort_by: Optional[str]):
        # Apply sorting
        if sort_by:
            if sort_by == "Most Recent":
                scorecards = sorted(scorecards,
                                    key=lambda x: x.date or datetime.min, reverse=True)
            elif sort_by == "Score:Highest":
                scorecards = sorted(scorecards,
                                    key=lambda x: x.score or 0, reverse=True)
            elif sort_by == "Score: Lowest":
                scorecards = sorted(scorecards,
                                    key=lambda x: x.score or 0)
            else:
                print(f"Invalid sort_by attribute: {sort_by}. Sorting skipped.")

        return scorecards

    def max_scorecards_limit(self, cursor: Optional[bool] = Query(None)):
        if cursor:
            return Query(20, description="Max number of scorecards to get", le=100)
        else:
            return None