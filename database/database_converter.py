from database.cable.park import Park
from database.base_models.rider_base import calculate_cwa_rank, calculate_age_rank, calculate_experience_rank, \
    calculate_division_rank, RiderProfileBase
from database.base_models import RiderBase, RiderStatsBase, ParkBase, ScorecardBase, ContestCarrierBase
from database.events import Rider, Scorecard
from database.events import RiderCompStats, ContestCarrier


class DatabaseConverter:

    async def fetch_and_convert_riders(self):
        all_riders = Rider.objects().all()
        return [RiderBase.from_orm(item) for item in all_riders]


    async def fetch_and_convert_stats(self):
        all_stats = RiderCompStats.objects().all()
        return [RiderStatsBase.from_orm(item) for item in all_stats]


    async def fetch_and_convert_parks(self):
        all_parks = Park.objects().all()
        return [ParkBase.from_orm(item) for item in all_parks]


    async def fetch_and_convert_scorecards(self):
        recent_scorecards = Scorecard.objects().order_by('-date').limit(100)
        return [ScorecardBase.from_orm(item) for item in recent_scorecards]


    async def fetch_and_convert_carriers(self):
        carriers = ContestCarrier.objects().order_by('number')
        return [ContestCarrierBase.from_orm(item) for item in carriers]

    async def fetch_and_convert_profiles(self, memory):
        profiles = []
        riders_mapping = {rider.id: rider for rider in memory.riders}

        for stat in memory.stats:
            rider = riders_mapping.get(stat.rider)
            if not rider:
                continue

            cwa_rank = calculate_cwa_rank(rider.id, memory.rider_rankings_cwa) or 0
            age_rank = calculate_age_rank(rider.id, memory.rider_rankings_by_age_group)
            experience_rank = calculate_experience_rank(rider.id, memory.rider_rankings_by_experience)
            division_score = memory.get_rider_cwa_division_score(rider.id)
            division_rank = calculate_division_rank(rider.id, memory.rider_rankings_by_division, division_score)
            tricks = Scorecard.get_trick_statistics(rider.id) or {}

            mongo_rider = Rider.objects(id=rider.id).first()
            mongo_rider.division = division_score
            mongo_rider.save()

            # Calculate trick counts
            overall_count, cwa_count, attempted_count = Scorecard.calculate_score_counts(rider.id)
            profile = RiderProfileBase(
                rider=rider,
                statistics=stat,
                cwa_rank=cwa_rank,
                age_rank=age_rank,  # Guaranteed tuple
                division_rank=division_rank,  # Guaranteed tuple
                experience_rank=experience_rank,  # Guaranteed tuple
                tricks=tricks,
                trick_count=int(overall_count),
                scored_count=int(cwa_count),
                attempted_count=int(attempted_count)
            )
            profiles.append(profile)
        return profiles





