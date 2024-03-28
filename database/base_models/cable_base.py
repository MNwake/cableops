from typing import Optional, List

from bson import ObjectId
from pydantic import BaseModel, Field, validator


class CableBase(BaseModel):
    id: str
    park: Optional[str]
    name: str
    _speed: float = 0
    num_carriers: int = 8
    lap_time: int = 90
    e_brake: bool = False
    fork: Optional['ForkBase'] = None
    magazine: Optional['MagazineBase'] = None
    carriers: List['CarrierBase'] = []

    @validator('id', pre=True)
    def validate_id(cls, value):
        if isinstance(value, ObjectId):
            return str(value)
        return value

    @validator('park', 'fork', 'magazine', pre=True)
    def validate_object_references(cls, value):
        if hasattr(value, 'id'):
            return str(value.id)
        return value

    @validator('carriers', each_item=True, pre=True)
    def validate_carriers(cls, value):
        if hasattr(value, 'id'):
            return str(value.id)
        return value

    class Config:
        from_attributes = True