from typing import Optional, List

from database.base_models import MyBaseModel


class CableBase(MyBaseModel):
    park: Optional[str]  # Assuming this will be the ObjectId of the Park as a string
    name: str
    _speed: float = 0
    num_carriers: int = 8
    lap_time: int = 90
    e_brake: bool = False
    fork: Optional['ForkBase'] = None
    magazine: Optional['MagazineBase'] = None
    carriers: List['CarrierBase'] = []