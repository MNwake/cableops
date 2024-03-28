import time
from datetime import datetime
from typing import List, Optional

from database.base_models import RiderBase, RiderStatsBase, ScorecardBase, ParkBase, ContestCarrierBase, \
    RiderProfileBase
from database.base_models.rider_base import calculate_cwa_rank, calculate_age_rank, calculate_experience_rank, \
    calculate_division_rank
from database.database_converter import DatabaseConverter
from database.events import Scorecard
from database.utils import calculate_age_group, calculate_division


class ServerMemory:

    def __init__(self):
        self.riders: List[RiderBase] = []
        self.stats: List[RiderStatsBase] = []
        self.scorecards: List[ScorecardBase] = []
        self.parks: List[ParkBase] = []
        self.carriers: List[ContestCarrierBase] = []
        self.rider_profiles: List[RiderProfileBase] = []
        self.arider_profiles_map: dict[str, RiderProfileBase] = {}  # New attribute

    async def load_data(self):
        # Start timing
        converter = DatabaseConverter()
        total_start_time = time.time()
        self.riders = await converter.fetch_and_convert_riders()
        self.stats = await converter.fetch_and_convert_stats()
        self.scorecards = await converter.fetch_and_convert_scorecards()
        self.carriers = await converter.fetch_and_convert_carriers()
        self.parks = await converter.fetch_and_convert_parks()
        self.rider_profiles = await converter.fetch_and_convert_profiles(self)
        self.rider_profiles_map = {profile.rider.id: profile for profile in self.rider_profiles}
        print(f"Total load and conversion time: {time.time() - total_start_time:.2f} seconds")

    def add_scorecard(self, scorecard: ScorecardBase):
        self.scorecards.append(scorecard)

    def update_carriers(self, carrier):

        pydantic_carrier = ContestCarrierBase.from_orm(carrier).dict()

        carrier_to_update = None
        for c in self.carriers:
            if c.number == pydantic_carrier['number']:
                carrier_to_update = c
                break

        if carrier_to_update:
            # Update the carrier_to_update with pydantic_carrier data
            for key, value in pydantic_carrier.items():
                setattr(carrier_to_update, key, value)
        else:
            # Convert dict back to Pydantic model before appending
            new_carrier = ContestCarrierBase(**pydantic_carrier)
            self.carriers.append(new_carrier)


        return pydantic_carrier

    async def update_stats(self, new_stats: RiderStatsBase):
        # Find the index of the existing stats for the rider, if it exists
        existing_stats_index = next((index for index, stat in enumerate(self.stats) if stat.rider == new_stats.rider),
                                    None)

        print(f"Total number of stats entries: {len(self.stats)}")
        if existing_stats_index is not None:
            # Update the existing stats object with the new data
            existing_stats = self.stats[existing_stats_index]
            for key, value in new_stats.dict().items():
                setattr(existing_stats, key, value)

        else:
            # If no existing stats found, append the new stats and create a new profile
            self.stats.append(new_stats)

        print(f"Total number of stats entries: {len(self.stats)}")

        self.create_or_update_rider_profile(new_stats)
        # For debug purposes, print the length of the stats list
        print(f"Total number of stats entries: {len(self.stats)}")

    def get_rider_cwa_division_score(self, rider_id: str) -> float:
        # This function should retrieve the relevant statistic for the rider.
        # Assuming here that you have a method or way to get the cwa.score.division.mean statistic for a rider.
        # You would replace this implementation with your actual logic.
        # For example:
        for stats in self.stats:
            if stats.rider == rider_id and stats.cwa and 'score' in stats.cwa and 'division' in stats.cwa[
                'score'] and 'mean' in stats.cwa['score']['division']:
                return stats.cwa['score']['division']['mean']
        return 0.0

    @property
    def rider_rankings_cwa(self):
        print(f"Rider rankings property: Total number of stats entries: {len(self.stats)}")
        # Filter out stats entries without a valid division score mean
        # valid_stats = [stat for stat in self.stats if
        #                stat.cwa and 'score' in stat.cwa and 'division' in stat.cwa['score'] and 'mean' in
        #                stat.cwa['score']['division']]

        # Create a list of tuples containing rider ID and score
        rider_scores = [(stat.rider, self.get_rider_cwa_division_score(stat.rider)) for stat in self.stats]

        # Sort the list by score in descending order
        sorted_rider_scores = sorted(rider_scores, key=lambda x: x[1], reverse=True)

        print("sorted rider scores")
        print(len(sorted_rider_scores))
        return sorted_rider_scores

    @property
    def rider_rankings_by_experience(self):
        # Define experience brackets and initialize the dictionary
        experience_brackets = {
            'Newbie': [],
            'Rookie': [],
            'Seasoned': [],
            'Expert': [],
            'Legend': []
        }

        # Iterate over each rider
        for stat in self.stats:
            rider = None
            for r in self.riders:
                if r.id == stat.rider:
                    rider = r
                    break
            # Calculate the number of years of experience for the rider
            years_experience = datetime.now().year - rider.year_started

            # Get the rider's score
            score = self.get_rider_cwa_division_score(rider.id)

            # Determine the experience bracket for the rider
            if years_experience < 1:
                bracket = 'Newbie'
            elif 1 <= years_experience < 3:
                bracket = 'Rookie'
            elif 3 <= years_experience < 5:
                bracket = 'Seasoned'
            elif 5 <= years_experience < 10:
                bracket = 'Expert'
            else:
                bracket = 'Legend'

            # Append the rider and their score to the corresponding bracket
            experience_brackets[bracket].append({'rider_id': rider.id, 'score': score})

        for bracket in experience_brackets:
            experience_brackets[bracket].sort(key=lambda x: x['score'], reverse=True)

        return experience_brackets

    @property
    def rider_rankings_by_division(self):
        division_rankings = {'Beginner': [], 'Novice': [], 'Intermediate': [], 'Advanced': [], 'Pro': []}

        for stat in self.stats:
            rider = None
            for r in self.riders:
                if r.id == stat.rider:
                    rider = r
                    break
            score = self.get_rider_cwa_division_score(rider.id)
            division = calculate_division(score)
            division_rankings[division].append((rider.id, score))

        # Sorting riders within each division by score in descending order
        for division in division_rankings:
            division_rankings[division].sort(key=lambda x: x[1], reverse=True)

        return division_rankings

    @property
    def rider_rankings_by_age_group(self):
        # Define age group categories
        age_groups = {
            'Grom': [],
            'Juniors': [],
            'Adults': [],
            'Masters': [],
            'Veterans': []
        }

        # Iterate over all riders
        for stat in self.stats:
            # TODO Get the self.riders object that matches stat.rider
            rider = None

            for r in self.riders:
                if r.id == stat.rider:
                    rider = r
                    break

            age_group = calculate_age_group(rider.date_of_birth)
            if age_group in age_groups:
                age_groups[age_group].append(rider.id)
            else:
                age_groups['Unknown'].append(rider.id)

        # Sort riders within each age group by rank based on CWA division score mean
        for age_group, rider_ids in age_groups.items():
            rider_ids.sort(key=lambda rider_id: self.get_rider_cwa_division_score(rider_id), reverse=True)

        return age_groups

    def create_or_update_rider_profile(self, rider_stat: RiderStatsBase):
        rider = None
        for r in self.riders:
            if r.id == rider_stat.rider:
                rider = r

        rider.division = self.get_rider_cwa_division_score(rider.id)
        print("getting existing profile")
        existing_profile = self.rider_profiles_map.get(rider.id)
        overall_count, cwa_count, attempted_count = Scorecard.calculate_score_counts(rider.id)

        if existing_profile:
            print("found existing profile")
            # Update the existing profile
            existing_profile.statistics = rider_stat
            existing_profile.trick_count = int(overall_count)
            existing_profile.scored_count = int(cwa_count)
            existing_profile.attempted_count = int(attempted_count)
            existing_profile.rider = rider
            existing_profile.cwa_rank = calculate_cwa_rank(rider.id, self.rider_rankings_cwa)
            existing_profile.age_rank = calculate_age_rank(rider.id, self.rider_rankings_by_age_group)
            existing_profile.experience_rank = calculate_experience_rank(rider.id, self.rider_rankings_by_experience)
            existing_profile.division_rank = calculate_division_rank(rider.id, self.rider_rankings_by_division,
                                                                     self.get_rider_cwa_division_score(
                                                                         rider_stat.rider))
            existing_profile.tricks = Scorecard.get_trick_statistics(rider.id)
            return existing_profile
        else:
            print("creating new profile")
            # Create a new profile
            new_profile = RiderProfileBase(
                rider=rider,
                statistics=rider_stat,
                trick_count=int(overall_count),
                scored_count=int(cwa_count),
                attempted_count=int(attempted_count),
                cwa_rank=calculate_cwa_rank(rider.id, self.rider_rankings_cwa),
                age_rank=calculate_age_rank(rider.id, self.rider_rankings_by_age_group),
                division_rank=calculate_division_rank(rider.id, self.rider_rankings_by_division,
                                                      self.get_rider_cwa_division_score(rider_stat.rider)),
                experience_rank=calculate_experience_rank(rider.id, self.rider_rankings_by_experience),
                tricks=Scorecard.get_trick_statistics(rider.id)
            )
            self.rider_profiles.append(new_profile)

            # Update rider_profiles_map with the new profile
            self.rider_profiles_map[new_profile.rider.id] = new_profile

            print("length of rider profiles in memory")
            print(len(self.rider_profiles))
            return new_profile

    # Method to fetch a rider profile
    def get_rider_profile(self, rider_id: str) -> Optional[RiderProfileBase]:
        for profile in self.rider_profiles:
            if profile.rider and profile.rider.id == rider_id:
                return profile
        return None
