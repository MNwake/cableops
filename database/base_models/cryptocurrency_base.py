from pydantic import BaseModel, Field
from typing import Optional

class Cryptocurrency(BaseModel):
    id: int
    name: str
    symbol: str
    price: float
    market_cap: float
    volume_24h: float
    percent_change_24h: float
    icon_url: str
    class Config:
        from_attributes = True