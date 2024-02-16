import time
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class ScorecardBase(BaseModel):
    date: datetime = datetime.now()
    section: Optional[str]
    division: Optional[float]
    execution: Optional[float]
    creativity: Optional[float]
    difficulty: Optional[float]
    score: Optional[float]
    landed: Optional[bool]
    park: Optional[str]  # Assuming reference fields are represented as string IDs
    rider: Optional[str]
    judge: Optional[str]

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
        converted_scorecards = []

        for scorecard in scorecards:
            pydantic_scorecard = cls(
                date=scorecard.date,
                section=scorecard.section,
                division=scorecard.division,
                execution=scorecard.execution,
                creativity=scorecard.creativity,
                difficulty=scorecard.difficulty,
                score=scorecard.score,
                landed=scorecard.landed,
                park=str(scorecard.park.id) if scorecard.park else None,
                rider=str(scorecard.rider.id) if scorecard.rider else None,
                judge=str(scorecard.judge.id) if scorecard.judge else None
            )
            converted_scorecards.append(pydantic_scorecard)

        return converted_scorecards