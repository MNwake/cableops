from datetime import datetime
from typing import Optional, Dict, Any

from bson import ObjectId
from pydantic import BaseModel, validator


class RiderStatsBase(BaseModel):
    id: str
    rider: str
    year: int
    division: Optional[float] = None
    overall: Optional[Dict] = None
    top_10: Optional[Dict] = None
    cwa: Optional[Dict] = None
    attempted: Optional[Dict] = None
    best_trick: Optional[Dict] = None
    kicker_stats: Optional[Dict] = None
    rail_stats: Optional[Dict] = None
    air_trick_stats: Optional[Dict] = None

    @validator('id', pre=True)
    def validate_objectid_to_string(cls, value):
        if isinstance(value, ObjectId):
            return str(value)
        return value
    @validator('rider', pre=True)
    def validate_rider(cls, value):
        if hasattr(value, 'id'):
            # Convert the Rider object reference to a string ID
            return str(value.id)
        return value

    @validator('best_trick', pre=True, each_item=True)
    def convert_objectid_in_dict(cls, value):
        if isinstance(value, dict):
            return {k: (str(v) if isinstance(v, ObjectId) else v) for k, v in value.items()}
        return value

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%S")
        }
