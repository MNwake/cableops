from typing import Optional

from database.base_models import MyBaseModel


class ParkBase(MyBaseModel):
    name: str
    state: Optional[str] = None
    abbreviation: Optional[str] = None
    team_name: Optional[str] = None
