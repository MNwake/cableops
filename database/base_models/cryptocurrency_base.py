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


class CryptoToken(BaseModel):
    id: str
    symbol: str
    name: str
    price: float
    logo: str
    address: Optional[str] = None  # Add address field



class TransactionDetails(BaseModel):
    estimatedAmount: float
    networkFee: float
    totalCost: float
    pricePerToken: float
    inputCurrency: str
