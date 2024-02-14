from datetime import datetime
from typing import Optional, Dict

from pydantic import Field

from database.base_models import MyBaseModel


class RiderStatsBase(MyBaseModel):
    rider: str
    year: int = Field(default=lambda: datetime.now().year)
    overall: Optional[Dict] = None
    top_10: Optional[Dict] = None
    cwa: Optional[Dict] = None
    attempted: Optional[Dict] = None