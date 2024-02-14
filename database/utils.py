from datetime import datetime
from typing import Optional

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


def to_str(obj_id):
    return str(obj_id) if obj_id else None