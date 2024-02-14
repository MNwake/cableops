from bson import ObjectId
from pydantic import BaseModel, Field

from database.utils import to_str


class MyBaseModel(BaseModel):
    id: str = Field(default_factory=ObjectId, alias="_id")

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: to_str}
        from_attributes = True



















