import time
from datetime import datetime, date
from enum import Enum

import math
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from pandas import DataFrame, to_datetime, concat

from database.CWA_Events import Scorecard

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

div_labels = {
    (-1, 20): 'Beginner',
    (20, 40): 'Novice',
    (40, 60): 'Intermediate',
    (60, 80): 'Advanced',
    (80, 101): 'Pro'
}


def calculate_division(score):
    if score != score:  # This checks for nan
        return 'Beginner'
    for score_range, label in div_labels.items():
        if isinstance(score_range, tuple):
            if score_range[0] <= score < score_range[1]:
                return label
    return 'Undefined'  # Or any other default label


def custom_json_encoder(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, float) and math.isnan(obj):
        return None
    return jsonable_encoder(obj)


def calculate_age_group(dob: date) -> str:
    today = datetime.today().date()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    if age < 11:
        return "Grom"
    elif 11 <= age <= 16:
        return "Juniors"
    elif 17 <= age <= 29:
        return "Adults"
    elif 30 <= age <= 39:
        return "Masters"
    elif age >= 40:
        return "Veterans"
    else:
        return "Unknown"


def get_experience_label(years_experience: int) -> str:
    if years_experience < 0:
        return "Invalid"
    elif years_experience <= 1:
        return "Newbie"
    elif years_experience <= 3:
        return "Rookie"
    elif years_experience <= 5:
        return "Seasoned"
    elif years_experience < 10:
        return "Expert"
    else:
        return "Legend"


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
    kicker = "kicker"
    rail = "rail"
    air_trick = "air trick"


class SortRiders(str, Enum):
    oldest_to_youngest = "oldest_to_youngest"
    youngest_to_oldest = "youngest_to_oldest"
    alphabetical = "alphabetical"
    most_years_experience = "most_years_experience"


class SortScorecards(str, Enum):
    most_recent = "Most Recent"
    score_highest = "Score:Highest"
    score_lowest = "Score: Lowest"


def format_datetime(date):
    default_date = datetime(1900, 1, 1, 11, 59, 59)
    return (date or default_date).strftime("%Y-%m-%dT%H:%M:%S")


def handle_nan_values(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, float) and math.isnan(value):
                data[key] = None
            elif isinstance(value, dict):
                handle_nan_values(value)


def calculate_stats(rider_id):
    start_time = time.time()

    # Fetch scorecards for the rider
    df = DataFrame(Scorecard.get_scorecards_by_rider(rider_id))
    if df.empty:
        print("DataFrame is empty")
        return {}  # Return an empty dict if no scorecards found

    df['_id'] = df['_id'].astype(str)
    df['date'] = to_datetime(df['date'])
    df['date'] = df['date'].dt.strftime("%Y-%m-%dT%H:%M:%S")


    cwa_stats = calculate_cwa(df)
    division_mean = cwa_stats.pop('mean_division_score', None)

    stats_dict = {
        "division": division_mean,  # Example for division, adjust as needed
        "overall": calculate_overall(df),
        "top_10": calculate_top_10(df),
        "cwa": cwa_stats,
        "attempted": calculate_attempted(df),
        "best_trick": calculate_best_trick(df),
        "kicker_stats": calculate_section_stats(df, 'Kicker'),
        "rail_stats": calculate_section_stats(df, 'Rail'),
        "air_trick_stats": calculate_section_stats(df, 'Air Trick')
    }

    end_time = time.time()
    execution_time = end_time - start_time
    print(execution_time)

    return stats_dict


def calculate_overall(df):
    # Step 1: Filter out scorecards where landed is False
    landed_df = df[df['landed']]

    # Step 2: Calculate summary statistics for each section
    section_summary = landed_df.groupby('section')['score'].describe()

    # Step 3: Calculate summary statistics for division, execution, difficulty, and creativity
    score_summary = landed_df[['division', 'execution', 'difficulty', 'creativity']].describe().to_dict()

    # Step 4: Transpose the section_summary DataFrame
    section_summary = section_summary.transpose().to_dict()

    # Step 5: Return the two DataFrames as a list of dictionaries
    return {
        'section': section_summary,
        'score': score_summary
    }


def calculate_top_10(df):
    # Step 1: Filter out only landed scorecards
    landed_df = df[df['landed']]

    # Step 2: Calculate top 10 for each section
    top_10_stats_list = []

    # Calculate top 10 for each section
    sections = ['Kicker', 'Rail', 'Air Trick']  # Assuming these are your sections, adjust as needed
    for section in sections:
        top_10 = landed_df[landed_df['section'] == section].nlargest(10, 'score')
        top_10_stats_list.append(top_10)

    # Step 3: Concatenate top 10 scorecards for all sections into a single DataFrame
    top_10_df = concat(top_10_stats_list)

    # Step 4: Group the top 10 scorecards by section and describe
    section_summary = top_10_df.groupby('section')['score'].describe()

    # Step 5: Calculate summary statistics for division, execution, difficulty, and creativity
    score_summary = top_10_df[['division', 'execution', 'difficulty', 'creativity']].describe().to_dict()

    # Step 6: Transpose the section_summary DataFrame
    section_summary = section_summary.transpose().to_dict()

    # Step 7: Return the two DataFrames as a list of dictionaries
    return {
        'section': section_summary,
        'score': score_summary
    }


def calculate_cwa(df):
    cwa_df = df[(df['score'] > 50) & df['landed']]
    section_summary = cwa_df.groupby('section')['score'].describe()
    score_summary = cwa_df[['division', 'execution', 'difficulty', 'creativity']].describe().to_dict()

    section_summary = section_summary.transpose().to_dict()

    # Extracting mean division score
    mean_division_score = score_summary['division']['mean'] if 'division' in score_summary else None

    return {
        'section': section_summary,
        'score': score_summary,
        'mean_division_score': mean_division_score  # Adding mean division score to the return dict
    }


def calculate_attempted(df):
    # Step 1: Filter out scorecards where landed is False
    attempted_df = df[~df['landed']]

    # Step 2: Calculate summary statistics for each section
    section_summary = attempted_df.groupby('section')['score'].describe()

    # Step 3: Calculate summary statistics for division, execution, difficulty, and creativity
    score_summary = attempted_df[['division', 'execution', 'difficulty', 'creativity']].describe().to_dict()

    # Step 4: Transpose the section_summary DataFrame
    section_summary = section_summary.transpose().to_dict()

    # Step 5: Return the two DataFrames as a list of dictionaries
    return {
        'section': section_summary,
        'score': score_summary
    }


def calculate_best_trick(df):
    # Step 1: Filter out only landed scorecards
    landed_df = df[df['landed']]

    # Step 2: Get the single best scorecard for each section
    best_trick_df = landed_df.loc[landed_df.groupby('section')['score'].idxmax()]

    # Step 3: Calculate summary statistics for each section
    section_summary = best_trick_df.groupby('section')['score'].describe()

    # Step 4: Calculate summary statistics for division, execution, difficulty, and creativity
    score_summary = best_trick_df[['division', 'execution', 'difficulty', 'creativity']].describe().to_dict()

    # Step 5: Transpose the section_summary DataFrame and convert to dict
    section_summary = section_summary.transpose().to_dict()

    # The scorecard details have been removed from here

    # Step 6: Return the results
    return {
        'section': section_summary,
        'score': score_summary
    }


def calculate_section_stats(df, section):
    # Step 1: Filter out scorecards for the specified section
    section_df = df[df['section'] == section]

    # Step 2: Calculate summary statistics for division, creativity, execution, and difficulty
    section_summary = section_df[['division', 'creativity', 'execution', 'difficulty']].describe().to_dict()

    # Step 3: Return the section summary statistics
    return section_summary

def replace_nan(data):
    if isinstance(data, dict):
        return {k: replace_nan(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [replace_nan(item) for item in data]
    elif isinstance(data, float) and math.isnan(data):
        return None  # Replace NaN with None
    return data


def calculate_team_stats(df):
    # Ensure the DataFrame is filtered for the desired conditions
    filtered_df = df[(df['score'] > 50) & df['landed']]

    # Section summary
    section_summary = filtered_df.groupby('section')['score'].describe()

    # Descriptive statistics for other metrics
    score_summary = filtered_df[['division', 'execution', 'difficulty', 'creativity']].describe()

    # Convert to dictionary
    section_summary_dict = section_summary.transpose().to_dict()
    score_summary_dict = score_summary.to_dict()


    # Combine the data into a single dictionary
    team_stats = {
        'section': section_summary_dict,
        'score': score_summary_dict,
    }

    return team_stats


def calculate_team_stats_for_park(park_id):
    # Fetch scorecards for the specified park
    scorecards = Scorecard.get_scorecards_by_park(park_id)
    scorecards_df = DataFrame(scorecards)

    # Perform the calculation as in the previous example
    team_stats = calculate_team_stats(scorecards_df)

    return team_stats