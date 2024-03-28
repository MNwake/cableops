from bson import ObjectId
from pydantic import BaseModel, Field, validator
from typing import Optional, List

from database.cable import Cable
from database.events import Rider


class ParkBase(BaseModel):
    id: str
    name: str
    state: Optional[str] = None
    abbreviation: Optional[str] = None
    team: Optional[str] = None
    # cable: Optional[List[str]] = []
    riders_checked_in: Optional[List[str]] = []

    @validator('id', pre=True)
    def validate_id(cls, value):
        if isinstance(value, ObjectId):
            return str(value)
        return value

    @validator('riders_checked_in', each_item=True, pre=True)
    def validate_lists(cls, value):
        if isinstance(value, (Cable, Rider)):  # Assuming Cable and Rider are your MongoEngine models
            return str(value.id)  # Replace with appropriate attribute if different
        return value

    class Config:
        from_attributes = True
