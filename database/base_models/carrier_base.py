from bson import ObjectId
from pydantic import BaseModel, Field


class CarrierBase(BaseModel):
    id: str = Field(default_factory=ObjectId, alias="_id")