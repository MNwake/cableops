from datetime import datetime
from typing import Optional, Dict

from bson import ObjectId
from pydantic import Field, BaseModel


class RiderStatsBase(BaseModel):
    id: str
    rider: Optional[str] = None
    year: int = Field(default=lambda: datetime.now().year)
    overall: Optional[list] = None
    top_10: Optional[list] = None
    cwa: Optional[list] = None
    attempted: Optional[list] = None
    best_trick: Optional[list] = None

    @classmethod
    def mongo_to_pydantic(cls, stats):
        """
        Convert MongoDB Rider objects to Pydantic RiderBase models synchronously.
        Includes rider statistics in the converted models.

        :param stats: List of RiderStats objects.
        :return: Converted Pydantic RiderBase model(s) with statistics.
        """

        converted_stats = []

        for stat in stats:
            rider_id = str(stat.rider.id)
            stat_id = str(stat.id)

            pydantic_rider = cls(
                id=stat_id,
                rider=rider_id,
                year=stat.year,
                overall=stat.overall,
                top_10=stat.top_10,
                cwa=stat.cwa,
                attempted=stat.attempted
            )
            converted_stats.append(pydantic_rider)

        return converted_stats