from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Optional, List

class ParkBase(BaseModel):
    id: str
    name: str
    state: Optional[str] = None
    abbreviation: Optional[str] = None
    team: Optional[str] = None
    cable: Optional[List[str]] = []
    riders_checked_in: Optional[List[str]] = []

    @classmethod
    def mongo_to_pydantic(cls, parks):
        """
        Convert MongoDB Park objects to Pydantic ParkBase models.

        :param parks: List of Park objects.
        :return: Converted Pydantic ParkBase model(s).
        """
        converted_parks = []

        for park in parks:
            pydantic_park = cls(
                id=str(park.id),
                name=park.name,
                state=park.state,
                abbreviation=park.abbreviation,
                team=str(park.team),
                # cable=park.cable,
                # riders_checked_in=[str(rider.id) for rider in park.riders_checked_in]
            )
            converted_parks.append(pydantic_park)

        return converted_parks