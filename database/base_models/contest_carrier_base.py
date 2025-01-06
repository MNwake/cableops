from pydantic import BaseModel, Field, parse_obj_as, validator
from typing import Optional, List
from bson import ObjectId



class ContestCarrierBase(BaseModel):
    id: str
    number: int
    rider_id: Optional[str] = None
    bib_color: Optional[str] = None
    session: Optional[str] = None

    @validator('id', pre=True)
    def validate_id(cls, value):
        if isinstance(value, ObjectId):
            return str(value)
        return value

    @validator('rider_id', pre=True)
    def validate_rider_id(cls, value):
        if isinstance(value, ObjectId):
            return str(value)
        return value

    @validator('session', pre=True, always=True)
    def validate_session(cls, value):
        if isinstance(value, ObjectId):
            return str(value)
        elif isinstance(value, str):
            # Additional checks for string format can be added here if needed
            return value
        elif value is None:
            return value
        raise ValueError(f"Invalid session format: {value}")

    # @validator('session', pre=True, each_item=True)
    # def validate_session(cls, value):
    #     if value is not None:
    #         return SessionBase(**session_dict)
    #     return value

    class Config:
        from_attributes = True


