from bson import ObjectId
from pydantic import BaseModel, Field


class ForkBase(BaseModel):
    id: str = Field(default_factory=ObjectId, alias="_id")
