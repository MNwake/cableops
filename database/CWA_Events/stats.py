from datetime import datetime

from mongoengine import DictField, ReferenceField, IntField, Document, FloatField


class RiderCompStats(Document):
    rider = ReferenceField('Rider', required=True)
    year = IntField(default=datetime.now().year)

    division = FloatField()
    overall = DictField()  # Field to store overall rankings
    top_10 = DictField()  # Field to store riders top 10 scorecards
    cwa = DictField()  # CWA score metrics

    attempted = DictField()
    best_trick = DictField()
    kicker_stats = DictField()
    rail_stats = DictField()
    air_trick_stats = DictField()

    meta = {
        'indexes': [
            {'fields': ['rider', 'year'], 'unique': True}
        ],
        'db_alias': 'cable'
    }


    # def to_dict(self):
    #     """Convert MongoDB document to a dictionary with formatted dates."""
    #     data = self.to_mongo().to_dict()
    #     for field in ['date_of_birth', 'date_created', 'waiver_date']:
    #         if data.get(field):
    #             data[field] = data[field].strftime("%Y-%m-%dT%H:%M:%S")
    #     return data

    @classmethod
    def get_rider_division(cls, rider_id):
        stat = cls.objects(rider=rider_id).order_by('-year').first()
        if stat and stat.overall:
            # Access 'score' directly as it's now part of the 'overall' dictionary
            score = stat.overall.get('score', {})

            # Get the 'division' mean
            division_mean = score.get('division', {}).get('mean')
            return division_mean

        return None

    @classmethod
    def get_stats_by_rider(cls, stat_id=None, rider_id=None, year=None, cursor=None, limit=None):
        query_params = {}

        # Default to the current year if 'year' is not provided
        if year is None:
            year = datetime.now().year

        # Add query parameters based on provided arguments
        if stat_id is not None:
            query_params['id'] = stat_id  # Assuming 'id' is the field for stat ID
        if rider_id is not None:
            query_params['rider'] = rider_id
        if year is not None:
            query_params['year'] = year

        # Create the initial query with the parameters
        rider_stats_query = cls.objects(**query_params).order_by('id')

        # Apply cursor for pagination
        if cursor:
            rider_stats_query = rider_stats_query.filter(id__gt=cursor)

        # Return the query results limited by the batch size
        if limit:
            return rider_stats_query.limit(limit)

        return rider_stats_query

    @classmethod
    def get_rider_ranking(cls, rider_id):
        current_year = datetime.now().year

        # Fetch the stats for the current year
        current_year_stats = cls.objects(year=current_year)

        # Create a list of tuples (rider_id, division_mean) and filter out any entries without a valid score
        rider_scores = []
        for stats in current_year_stats:
            division_mean = stats.cwa.get('score', {}).get('division', {}).get('mean')
            if division_mean is not None:
                rider_scores.append((str(stats.rider.id), division_mean))

        # Sort the list by division_mean in descending order
        sorted_scores = sorted(rider_scores, key=lambda x: x[1], reverse=True)

        # Find the index (rank) of the specified rider
        for index, (rider_id_iter, _) in enumerate(sorted_scores):
            if rider_id_iter == str(rider_id):
                return index + 1  # Adding 1 because rank should start from 1, not 0

        return None

    @classmethod
    def get_mean_score(cls, rider_id, stat_type):
        stat = cls.objects(rider=rider_id).order_by('-year').first()
        if not stat:
            return None

        if stat_type not in ['overall', 'top_10', 'cwa', 'best_trick']:
            return None

        stat_list = getattr(stat, stat_type)
        if not stat_list:
            return None

        scores = {}
        for stat_item in stat_list:
            for section, values in stat_item.items():
                for key, value in values.items():
                    if 'mean' in value:
                        scores[f"{section}_{key}"] = value['mean']

        return scores

    @classmethod
    def get_cwa_score(cls, rider_id):
        return cls.get_mean_score(rider_id, 'cwa')

    @classmethod
    def get_overall_score(cls, rider_id):
        return cls.get_mean_score(rider_id, 'overall')

    @classmethod
    def get_top_ten_score(cls, rider_id):
        return cls.get_mean_score(rider_id, 'top_10')

    @classmethod
    def get_best_trick_score(cls, rider_id):
        return cls.get_mean_score(rider_id, 'best_trick')

    @classmethod
    def get_rider_ranking_by_age_group(cls, rider_id):
        from database.events import Rider
        from database.utils import calculate_age_group

        rider = Rider.objects(id=rider_id).first()
        if not rider:
            return None

        # Calculate the age group of the rider
        rider_age_group = calculate_age_group(rider.date_of_birth)

        # Fetch all stats and filter by age group
        all_rider_stats = cls.objects()
        filtered_stats = []

        for stat in all_rider_stats:
            if calculate_age_group(stat.rider.date_of_birth) == rider_age_group:
                filtered_stats.append(stat)

        # Sort the filtered stats by cwa score
        sorted_stats = sorted(filtered_stats, key=lambda x: x.cwa.get('score', {}).get('division', {}).get('mean', 0),
                              reverse=True)

        # Determine the ranking of the rider
        for rank, stat in enumerate(sorted_stats, start=1):
            if stat.rider.id == rider_id:
                # Return the rider's age group and their rank within that age group
                return rider_age_group, rank

        return None

    @classmethod
    def get_rider_ranking_by_division_group(cls, rider_id):

        # Retrieve the division of the current rider
        current_rider_division = cls.get_rider_division(rider_id)
        if current_rider_division is None:
            return None

        # Fetch all rider stats
        all_rider_stats = cls.objects()
        filtered_stats = []

        for stat in all_rider_stats:
            # Get division of each rider
            division = cls.get_rider_division(str(stat.rider.id))
            if division == current_rider_division:
                filtered_stats.append(stat)

        # Sort the filtered stats by cwa score
        sorted_stats = sorted(filtered_stats, key=lambda x: x.cwa.get('score', {}).get('division', {}).get('mean', 0),
                              reverse=True)

        # Determine the ranking of the rider within the division group
        for rank, stat in enumerate(sorted_stats, start=1):
            if stat.rider.id == rider_id:
                # Return the rider's division and their rank within that division group
                return current_rider_division, rank

        return None

    @classmethod
    def get_rider_ranking_by_experience(cls, rider_id):
        from database.events import Rider

        # Get the current rider's experience
        current_rider = Rider.objects(id=rider_id).first()
        if not current_rider or not current_rider.year_started:
            return None

        current_rider_experience = datetime.now().year - current_rider.start_year

        # Define experience categories
        categories = {
            'Newbie': (0, 1),  # 0-1 year of experience
            'Rookie': (1, 3),  # 1-3 years of experience
            'Seasoned': (3, 5),  # 3-5 years of experience
            'Expert': (5, 10),  # 5-10 years of experience
            'Legend': (10, float('inf'))  # 10+ years of experience
        }

        # Determine the category of the current rider
        current_rider_category = None
        for category, (min_year, max_year) in categories.items():
            if min_year <= current_rider_experience <= max_year:
                current_rider_category = category
                break
        else:
            # Rider falls outside the defined categories
            return None

        # Fetch all riders and filter by experience category
        all_riders = Rider.objects()
        category_riders = []

        for rider in all_riders:
            rider_experience = datetime.now().year - rider.start_year
            if categories[current_rider_category][0] <= rider_experience <= categories[current_rider_category][1]:
                rider_stat = cls.objects(rider=rider.id).order_by('-year').first()
                if rider_stat:
                    score = rider_stat.cwa.get('score', {}).get('division', {}).get('mean', 0)
                    category_riders.append((rider.id, score))

        # Sort the riders in the category by score
        sorted_riders = sorted(category_riders, key=lambda x: x[1], reverse=True)

        # Find the rank of the current rider
        for rank, (rider_id_iter, _) in enumerate(sorted_riders, start=1):
            if rider_id_iter == str(rider_id):
                # Return the rider's experience category and their rank within that category
                return current_rider_category, rank

        return None

class RidingStats(Document):
    """

    Keep track of days checked in,
    sessions per day
    # laps per session
    lap count per day
    total lap count

    """

class TeamStats(Document):
    pass
