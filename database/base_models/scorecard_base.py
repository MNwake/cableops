import time
from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, Field, parse_obj_as
from typing import Optional, List


class ScorecardBase(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    date: datetime = datetime.now()
    section: Optional[str]
    division: Optional[float]
    execution: Optional[float]
    creativity: Optional[float]
    difficulty: Optional[float]
    score: Optional[float]
    landed: Optional[bool]
    park: Optional[str] = Field(default_factory=lambda: str(ObjectId())) # Assuming reference fields are represented as string IDs
    rider: Optional[str] = Field(default_factory=lambda: str(ObjectId()))
    judge: Optional[str] = Field(default_factory=lambda: str(ObjectId()))

    class Config:
        arbitrary_types_allowed = True
        # Additional configurations like ORM mode can be added here if needed

    @classmethod
    def mongo_to_pydantic(cls, scorecards):
        """
        Convert MongoDB Scorecard objects to Pydantic ScorecardBase models.

        :param scorecards: List of Scorecard objects.
        :return: Converted Pydantic ScorecardBase model(s).
        """
        # Convert MongoDB Scorecard objects to dictionaries
        scorecard_dicts = [
            {
                'id': str(scorecard.id),
                'date': scorecard.date,
                'section': scorecard.section,
                'division': scorecard.division,
                'execution': scorecard.execution,
                'creativity': scorecard.creativity,
                'difficulty': scorecard.difficulty,
                'score': scorecard.score,
                'landed': scorecard.landed,
                'park': str(scorecard.park.id) if scorecard.park else None,
                'rider': str(scorecard.rider.id) if scorecard.rider else None,
                'judge': str(scorecard.judge.id) if scorecard.judge else None
            }
            for scorecard in scorecards
        ]

        # Parse the list of dictionaries into a list of Pydantic models
        converted_scorecards = parse_obj_as(List[cls], scorecard_dicts)

        return converted_scorecards