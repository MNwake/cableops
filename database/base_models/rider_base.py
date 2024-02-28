from datetime import datetime
from typing import Optional, List

from bson import ObjectId
from pydantic import Field, BaseModel, parse_obj_as

from database import Rider


class RiderBase(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    email: Optional[str] = None
    first_name: str
    last_name: str
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    date_created: datetime = Field(default_factory=lambda: datetime.utcnow().replace(second=0))
    profile_image: str = ''
    stance: Optional[str] = None
    year_started: Optional[int] = None
    division: Optional[float] = None
    home_park: Optional[str] = Field(default_factory=lambda: str(ObjectId()))
    statistics: Optional[str] = Field(default_factory=lambda: str(ObjectId()))

    @classmethod
    def mongo_to_pydantic(cls, riders):
        """
        Convert MongoDB Rider objects to Pydantic RiderBase models synchronously.
        Includes rider statistics in the converted models.

        :param riders: List of MongoDB Rider objects or a single Rider object.
        :return: Converted Pydantic RiderBase model(s) with statistics.
        """
        # Convert MongoDB Rider objects to dictionaries
        rider_dicts = []
        count = 1
        for rider in riders:
            rider_dict = {
                'id': str(rider.id),
                'email': rider.email,
                'first_name': rider.first_name,
                'last_name': rider.last_name,
                'date_of_birth': rider.date_of_birth.strftime("%Y-%m-%d %H:%M:%S"),  # Format date_of_birth
                'gender': rider.gender,
                'date_created': rider.date_created.strftime("%Y-%m-%d %H:%M:%S"),  # Format date_created
                'profile_image': rider.profile_image,
                'stance': rider.stance,
                'year_started': rider.year_started,
                'home_park': str(rider.home_park.id) if rider.home_park else None,
                'statistics': str(rider.statistics.id) if rider.statistics else None
            }
            rider_dicts.append(rider_dict)
            count += 1

        # Parse the list of dictionaries into a list of Pydantic models
        converted_riders = parse_obj_as(List[cls], rider_dicts)
        return converted_riders

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

