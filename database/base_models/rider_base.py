from datetime import datetime
from typing import Optional, Union, List

from bson import ObjectId
from pydantic import Field

from database.base_models import MyBaseModel
from database import Rider
from database.events import RiderStats


class RiderBase(MyBaseModel):
    email: Optional[str] = None
    first_name: str
    last_name: str
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    date_created: datetime = Field(default_factory=datetime.utcnow)
    profile_image: str = ''
    stance: Optional[str] = None
    year_started: Optional[int] = None
    home_park: Optional['ParkBase'] = None
    statistics: Optional['RiderStatsBase'] = None

    @classmethod
    def mongo_to_pydantic(cls, riders: Union[List[Rider], Rider]) -> Union[List['RiderBase'], 'RiderBase']:
        """
        Convert MongoDB Rider objects to Pydantic RiderBase models.

        :param riders: List of MongoDB Rider objects or a single Rider object.
        :return: Converted Pydantic RiderBase model(s).
        """
        if isinstance(riders, list):
            return [cls.mongo_to_pydantic(rider) for rider in riders]
        else:
            print('mongo to pydantic not a list need to call .all() on endpoint')
            return cls(
                id=str(riders.id),
                email=riders.email,
                first_name=riders.first_name,
                last_name=riders.last_name,
                date_of_birth=riders.date_of_birth,
                gender=riders.gender,
                date_created=riders.date_created,
                profile_image=riders.profile_image,
                stance=riders.stance,
                year_started=riders.year_started,
                home_park=riders.home_park,
                statistics=riders.statistics
            )
    async def fetch_rider_by_id(self, rider_id: str):
        rider = Rider.objects(id=ObjectId(rider_id)).first()
        if rider:
            return RiderBase(
                id=str(rider.id),
                email=rider.email,
                first_name=rider.first_name,
                last_name=rider.last_name,
                date_of_birth=rider.date_of_birth,
                gender=rider.gender,
                date_created=rider.date_created,
                profile_image=rider.profile_image,
                stance=rider.stance,
                year_started=rider.year_started,
                home_park=rider.home_park,
                statistics=rider.statistics
            )
        else:
            return None

    async def fetch_rider_stats_by_id(self, rider_id: str):
        rider_stats = RiderStats.objects(rider=ObjectId(rider_id)).first()
        if rider_stats:
            return RiderBase(
                id=str(rider_stats.id),
                # Populate other fields accordingly based on the RiderStats model
                year=rider_stats.year,
                overall=rider_stats.overall,
                top_10=rider_stats.top_10,
                cwa=rider_stats.cwa,
                attempted=rider_stats.attempted
            )
        else:
            return None

    async def create_new_rider(self, rider_data: dict):
        new_rider = Rider(
            email=rider_data.get('email'),
            first_name=rider_data.get('first_name'),
            last_name=rider_data.get('last_name'),
            date_of_birth=rider_data.get('date_of_birth'),
            gender=rider_data.get('gender'),
            profile_image=rider_data.get('profile_image'),
            stance=rider_data.get('stance'),
            year_started=rider_data.get('year_started'),
            home_park=rider_data.get('home_park'),
            statistics=rider_data.get('statistics')
        )
        new_rider.save()
        return new_rider

