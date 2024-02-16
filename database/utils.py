from datetime import datetime
from enum import Enum
from typing import Optional

from bson import ObjectId
from fastapi.encoders import jsonable_encoder

bib_colors = ['red', 'blue', 'green', 'yellow']
color_dict = {
    "red": [1, 0, 0, 0.2],
    "blue": [0, 0, 1, 0.2],
    "green": [0, 1, 0, 0.2],
    "yellow": [1, 1, 0, 0.2],
    "black": [0, 0, 0, 0.2],
    "orange": [1, 0.5, 0, 0.2],
    "white": [1, 1, 1, 0.2],
}


def build_rider_query(home_park: Optional[str] = None,
                      min_age: Optional[int] = 0,
                      max_age: Optional[int] = 100,
                      gender: Optional[str] = None,
                      stance: Optional[str] = None,
                      year_started: Optional[int] = None
                      ):
    print('rider query')
    query = {}

    current_year = datetime.now().year

    if home_park:
        query["home_park"] = home_park
    if gender:
        query["gender"] = gender
    if stance:
        query["stance"] = stance
    if year_started:
        query["year_started"] = year_started

    min_birth_year = current_year - max_age  # For max_age
    max_birth_year = current_year - min_age  # For min_age
    if min_age or max_age:
        query["date_of_birth"] = {
            "$gte": datetime(min_birth_year, 1, 1),
            "$lte": datetime(max_birth_year, 12, 31)
        }

    print(f"Query: {query}")  # Debugging line
    return query


def custom_json_encoder(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    return jsonable_encoder(obj)

def calculate_age(birth_date: datetime) -> int:
    # Implement age calculation from birth_date
    today = datetime.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


def calculate_birth_date(age: int) -> datetime:
    """
    Calculate the birth date corresponding to the given age.

    :param age: The age for which to calculate the birth date.
    :return: The calculated birth date.
    """
    # Get the current date
    current_date = datetime.utcnow()

    # Subtract the age from the current year to get the birth year
    birth_year = current_date.year - age

    # Construct the birth date using the birth year and January 1st
    birth_date = datetime(birth_year, 1, 1)

    return birth_date

def to_str(obj_id):
    return str(obj_id) if obj_id else None

class Gender(Enum):
    male = "male"
    female = "female"

class Stance(Enum):
    regular = "regular"
    goofy = "goofy"

class Section(str, Enum):
    kicker = "Kicker"
    rail = "Rail"
    air_trick = "Air Trick"

class SortRiders(str, Enum):
    oldest_to_youngest = "oldest_to_youngest"
    youngest_to_oldest = "youngest_to_oldest"
    alphabetical = "alphabetical"
    most_years_experience = "most_years_experience"

class SortScorecards(str, Enum):
    most_recent = "Most Recent"
    score_highest = "Score:Highest"
    score_lowest = "Score: Lowest"