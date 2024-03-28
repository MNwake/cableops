import json
from typing import Optional, List

from fastapi import APIRouter, Body, HTTPException, Query
from starlette.websockets import WebSocket, WebSocketDisconnect

from database.base_models.scorecard_base import ScorecardBase
from database.events import RiderStats, Rider, Park, Scorecard


class ScorecardRoutes:
    def __init__(self, connection_manager, server_memory):
        self.router = APIRouter()
        self.manager = connection_manager
        self.define_routes()
        self.memory = server_memory

    def define_routes(self):
        # Your existing FastAPI route...
        @self.router.get("")
        async def get_scorecards(cursor: Optional[str] = Query(None),
                                 sort_by: Optional[str] = Query('Most Recent'),
                                 rider_ids: Optional[List[str]] = Query(None)):

            try:
                # Decide the source of scorecards based on the presence of rider_ids
                if rider_ids:
                    scorecards = Scorecard.get_scorecards(rider_ids=rider_ids, sort_by=sort_by, cursor=cursor)
                else:
                    scorecards = Scorecard.get_scorecards(sort_by=sort_by, cursor=cursor)

                pydantic_scorecards = [ScorecardBase.from_orm(scorecard) for scorecard in scorecards]

                if pydantic_scorecards:
                    # Sort by date assuming the date field is available in the Pydantic model
                    oldest_scorecard = sorted(pydantic_scorecards, key=lambda x: x.date)[0]
                    next_cursor = oldest_scorecard.id
                else:
                    next_cursor = None

                return {'data': pydantic_scorecards, "cursor": next_cursor}
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))


