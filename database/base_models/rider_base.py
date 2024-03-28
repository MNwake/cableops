from datetime import datetime
from typing import Optional, Tuple

from bson import ObjectId
from pydantic import BaseModel, validator

from database.base_models import RiderStatsBase
from database.events import Rider
from database.utils import calculate_division


class RiderBase(BaseModel):
    id: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    date_created: Optional[datetime] = datetime.now()
    profile_image: str = ''
    stance: Optional[str] = None
    year_started: Optional[int] = None
    division: Optional[float] = None
    home_park: Optional[str]
    statistics: Optional[str]
    is_registered: Optional[bool] = False
    waiver_date: Optional[datetime] = None

    @validator('id', 'home_park', 'statistics', pre=True)
    def convert_objectid_to_string(cls, value):
        if isinstance(value, ObjectId):
            return str(value)
        return value

    @validator('home_park', 'statistics', pre=True)
    def validate_object_references(cls, value):
        if hasattr(value, 'id'):
            # Convert the MongoEngine document reference to a string ID
            return str(value.id)
        return value

    @validator('date_of_birth', 'date_created', 'waiver_date', pre=True, always=True)
    def format_datetime(cls, value):
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        for fmt in ('%Y-%m-%dT%H:%M:%S', '%Y-%m-%d', '%d/%m/%Y'):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        raise ValueError(f"Invalid date format for {value}")
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%S")
        }

    @classmethod
    def update_or_create_rider(cls, rider_data: dict):
        rider_id = rider_data.get('id')
        rider = Rider.objects(id=ObjectId(rider_id)).first() if rider_id else None

        if not rider:
            print("Creating new rider")  # Debugging line
            rider = Rider()
        else:
            print("rider found, updating existing")

        rider.update_fields(rider_data)
        rider.save()  # Save the rider to the database
        print("rider Saved")
        return rider


class RiderProfileBase(BaseModel):
    rider: Optional[RiderBase] = None
    cwa_rank: Optional[int] = 0
    age_rank: Optional[int] = 0
    division_rank: Optional[int] = 0
    experience_rank: Optional[int] = 0
    trick_count: Optional[int] = 0
    scored_count: Optional[int] = 0
    attempted_count: Optional[int] = 0
    statistics: Optional[RiderStatsBase] = None
    tricks: Optional[dict] = {}

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%S")
        }



def calculate_cwa_rank(rider_id, rider_rankings_cwa):
    for index, (ranking_id, score) in enumerate(rider_rankings_cwa):
        if ranking_id == rider_id:
            return index + 1
    return 0


def calculate_age_rank(rider_id, rider_rankings_by_age_group):
    for age_group, rider_ids in rider_rankings_by_age_group.items():
        if rider_id in rider_ids:

            return rider_ids.index(rider_id) + 1
    return 0

def calculate_experience_rank(rider_id, rider_rankings_by_experience):
    for bracket, riders in rider_rankings_by_experience.items():
        if rider_id in [r['rider_id'] for r in riders]:
            return list(r['rider_id'] for r in riders).index(rider_id) + 1
    return 0

def calculate_division_rank(rider_id, rider_rankings_by_division, division_score):
    division = calculate_division(division_score)
    for rank, (ranking_rider_id, score) in enumerate(rider_rankings_by_division.get(division, [])):
        if ranking_rider_id == rider_id:
            return rank + 1
    return 0