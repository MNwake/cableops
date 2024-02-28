from datetime import datetime
from typing import Optional, Dict, List

from bson import ObjectId
from pydantic import Field, BaseModel, parse_obj_as


class RiderStatsBase(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    rider: str = Field(default_factory=lambda: str(ObjectId()))
    year: int = Field(default_factory=lambda: datetime.now().year)
    overall: Optional[list] = None
    top_10: Optional[list] = None
    cwa: Optional[list] = None
    attempted: Optional[list] = None
    best_trick: Optional[list] = None

    @classmethod
    def mongo_to_pydantic(cls, stats):
        """
        Convert MongoDB RiderStats objects to Pydantic RiderStatsBase models synchronously.
        Includes rider statistics in the converted models.

        :param stats: List of RiderStats objects.
        :return: Converted Pydantic RiderStatsBase model(s) with statistics.
        """

        # Convert MongoDB RiderStats objects to dictionaries
        stat_dicts = [
            {
                'id': str(stat.id),
                'rider': str(stat.rider.id) if stat.rider else None,
                'year': stat.year,
                'overall': stat.overall,
                'top_10': stat.top_10,
                'cwa': stat.cwa,
                'attempted': stat.attempted,
                'best_trick': stat.best_trick
            }
            for stat in stats
        ]

        # Parse the list of dictionaries into a list of Pydantic models
        converted_stats = parse_obj_as(List[cls], stat_dicts)

        return converted_stats
