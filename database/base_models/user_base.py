from datetime import datetime, date
from typing import Optional

from bson import ObjectId
from pydantic import Field, BaseModel


class UserBase(BaseModel):
    id: str = Field(default_factory=ObjectId, alias="_id")
    email: Optional[str] = None
    first_name: str
    last_name: str
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    date_created: datetime = Field(default_factory=datetime.utcnow)
    profile_image: str = ''

    @property
    def age(self) -> Optional[int]:
        if not self.date_of_birth:
            return None
        today = date.today()
        born = self.date_of_birth.date()
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


