import os

import sys
from datetime import datetime
from pprint import pprint
from typing import Optional

from bson import ObjectId
from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from database import DataBase
from database.Events import Rider, Park


app = FastAPI()
if sys.platform == 'linux':
    app.mount("/static", StaticFiles(directory="/home/theokoester/dev/cableops/server/assets/images"), name="static")
def custom_encoder(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, (list, set)):
        return [custom_encoder(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: custom_encoder(value) for key, value in obj.items()}
    return obj

# MongoDB connection up\dsyr
DataBase()
import uvicorn

class FastAPIApp:
    def __init__(self):
        self.app = FastAPI()
        self.setup_routes()

    def setup_routes(self):
        @self.app.get("/")
        async def read_root():
            return {"Hello": "World"}

        @self.app.get("/riders/")
        async def get_riders(
                home_park: Optional[str] = None,
                min_age: Optional[int] = None,
                max_age: Optional[int] = None,
                gender: Optional[str] = None,
                stance: Optional[str] = None,
                year_started: Optional[int] = None
        ):
            query = {}
            if home_park:
                query["home_park"] = home_park
            if gender:
                query["gender"] = gender
            if stance:
                query["stance"] = stance
            if year_started:
                query["year_started"] = year_started
            if min_age or max_age:
                current_year = datetime.now().year
                if min_age:
                    min_birth_year = current_year - min_age
                    query["date_of_birth__lte"] = datetime(min_birth_year, 1, 1)
                if max_age:
                    max_birth_year = current_year - max_age
                    query["date_of_birth__gte"] = datetime(max_birth_year, 1, 1)

            riders = Rider.objects(__raw__=query).all()
            riders_list = [custom_encoder(rider.to_mongo().to_dict()) for rider in riders]
            return riders_list

        @self.app.get('/parks/')
        async def get_parks():
            parks = Park.objects().all()
            parks_list = [custom_encoder(park.to_mongo()) for park in parks]
            pprint(parks_list)
            return parks_list


    def run(self):
        uvicorn.run(self.app, host="0.0.0.0", port=8000)