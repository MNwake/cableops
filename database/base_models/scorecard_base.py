from datetime import datetime
from typing import Optional, List

from bson import ObjectId
from pydantic import BaseModel, validator

from database.CWA_Events import Scorecard


class ScorecardBase(BaseModel):
    id: Optional[str] = None
    date: Optional[datetime] = datetime.now()
    section: Optional[str]
    division: Optional[float]
    execution: Optional[float]
    creativity: Optional[float]
    difficulty: Optional[float]
    score: Optional[float]
    landed: Optional[bool]
    approach: Optional[str]
    trick_type: Optional[str]
    spin: Optional[str]
    spin_direction: Optional[str]
    modifiers: List[str]
    session: Optional[str]
    park: Optional[str] = None
    rider: Optional[str]
    judge: Optional[str] = None

    @validator('id', pre=True)
    def validate_id(cls, value):
        if isinstance(value, ObjectId):
            return str(value)
        return value

    # Assuming `park` and `rider` fields should store just the ID of the related objects
    @validator('park', 'rider', pre=True)
    def validate_related_objects(cls, value):
        if hasattr(value, 'id'):
            return str(value.id)
        return value

    @validator('date', pre=True)
    def format_incoming_date(cls, value):
        if isinstance(value, datetime):
            return value
        elif isinstance(value, str):
            try:
                return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                raise ValueError(f"Invalid date format for {value}")
        else:
            raise TypeError("Invalid type for date field")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%S")
        }

    def save(self):
        # Convert this Pydantic model to a MongoDB Document and save it
        scorecard_data = self.dict(exclude_unset=True)

        new_scorecard = Scorecard(**scorecard_data)
        new_scorecard.save()
        return new_scorecard.id
