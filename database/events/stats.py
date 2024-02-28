import time
from datetime import datetime

import mongoengine as db
from pandas import DataFrame, to_datetime, concat

from .scorecard import Scorecard


class RiderStats(db.Document):
    rider = db.ReferenceField('Rider', required=True)
    year = db.IntField(default=datetime.now().year)
    overall = db.ListField()  # Field to store overall rankings
    top_10 = db.ListField()  # Field to store riders top 10 scorecards
    cwa = db.ListField()  # CWA score metrics
    attempted = db.ListField()
    best_trick = db.ListField()

    meta = {
        'indexes': [
            {'fields': ['rider', 'year'], 'unique': True}
        ]
    }

    @classmethod
    def get_rider_division(cls, rider_id):
        stat = cls.objects(rider=rider_id).order_by('-year').first()
        if stat and stat.overall:
            overall_stats = stat.cwa

            # Iterate through the overall stats to find the division mean
            for stat_item in overall_stats:
                if 'score' in stat_item:
                    division_mean = stat_item['score'].get('division', {}).get('mean')
                    if division_mean is not None:
                        return division_mean
        return None

    @classmethod
    def get_rider_stats(cls, stat_id=None, rider_id=None, year=None, cursor=None, limit=20):
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
        return rider_stats_query.limit(limit)

    @classmethod
    def get_rider_ranking(cls, rider_id):
        # Fetch the latest stats for all riders
        all_riders_stats = cls.objects().order_by('-year').all()

        # Create a list of tuples (rider_id, division_mean)
        rider_scores = []
        for stats in all_riders_stats:
            for cwa_item in stats.cwa:
                score = cwa_item.get('score', {}).get('division', {}).get('mean')
                if score is not None:
                    rider_scores.append((str(stats.rider.id), score))

        # Sort the list by division_mean in descending order
        sorted_scores = sorted(rider_scores, key=lambda x: x[1], reverse=True)

        # Find the rank of the specified rider
        for rank, (rider_id_iter, _) in enumerate(sorted_scores, start=1):
            if rider_id_iter == str(rider_id):
                return rank

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

    def calculate_stats(self):
        start_time = time.time()  # Start the timer

        # Fetch scorecards for the rider
        df = DataFrame(Scorecard.get_scorecards(rider_ids=self.rider))
        df['_id'] = df['_id'].astype(str)
        df['date'] = to_datetime(df['date'])

        self.overall = self.calculate_overall(df)
        self.top_10 = self.calculate_top_10(df)
        self.cwa = self.calculate_cwa(df)
        self.attempted = self.calculate_attempted(df)
        self.best_trick = self.calculate_best_trick(df)


        end_time = time.time()  # End the timer
        execution_time = end_time - start_time  # Calculate the duration
        print(f"Ranking calculations completed in {execution_time} seconds.")
        return self

    def calculate_overall(self, df):
        # Step 1: Filter out scorecards where landed is False
        landed_df = df[df['landed']]

        # Step 2: Calculate summary statistics for each section
        section_summary = landed_df.groupby('section')['score'].describe()

        # Step 3: Calculate summary statistics for division, execution, difficulty, and creativity
        score_summary = landed_df[['division', 'execution', 'difficulty', 'creativity']].describe()

        # Step 4: Transpose the section_summary DataFrame
        section_summary = section_summary.transpose()

        # Step 5: Return the two DataFrames as a list of dictionaries
        return [{'section': section_summary.to_dict()}, {'score': score_summary.to_dict()}]

    def calculate_top_10(self, df):
        # Step 1: Filter out only landed scorecards
        landed_df = df[df['landed']]

        # Step 2: Calculate top 10 for each section
        top_10_stats_list = []

        # Calculate top 10 for each section
        sections = ['kicker', 'rail', 'air trick']  # Assuming these are your sections, adjust as needed
        for section in sections:
            top_10 = landed_df[landed_df['section'] == section].nlargest(10, 'score')
            top_10_stats_list.append(top_10)

        # Step 3: Concatenate top 10 scorecards for all sections into a single DataFrame
        top_10_df = concat(top_10_stats_list)

        # Step 4: Group the top 10 scorecards by section and describe
        section_summary = top_10_df.groupby('section')['score'].describe()

        # Step 5: Calculate summary statistics for division, execution, difficulty, and creativity
        score_summary = top_10_df[['division', 'execution', 'difficulty', 'creativity']].describe()

        # Step 6: Transpose the section_summary DataFrame
        section_summary = section_summary.transpose()

        # Step 7: Return the two DataFrames as a list of dictionaries
        return [{'section': section_summary.to_dict()}, {'score': score_summary.to_dict()}]

    def calculate_cwa(self, df):
        # Step 1: Filter out scorecards with a score over 50 and where landed is True
        cwa_df = df[(df['score'] > 50) & df['landed']]

        # Step 2: Calculate summary statistics for each section
        section_summary = cwa_df.groupby('section')['score'].describe()

        # Step 3: Calculate summary statistics for division, execution, difficulty, and creativity
        score_summary = cwa_df[['division', 'execution', 'difficulty', 'creativity']].describe()

        # Step 4: Transpose the section_summary DataFrame
        section_summary = section_summary.transpose()

        # Step 5: Return the two DataFrames as a list of dictionaries
        return [{'section': section_summary.to_dict()}, {'score': score_summary.to_dict()}]

    def calculate_attempted(self, df):
        # Step 1: Filter out scorecards where landed is False
        attempted_df = df[~df['landed']]

        # Step 2: Calculate summary statistics for each section
        section_summary = attempted_df.groupby('section')['score'].describe()

        # Step 3: Calculate summary statistics for division, execution, difficulty, and creativity
        score_summary = attempted_df[['division', 'execution', 'difficulty', 'creativity']].describe()

        # Step 4: Transpose the section_summary DataFrame
        section_summary = section_summary.transpose()

        # Step 5: Return the two DataFrames as a list of dictionaries
        return [{'section': section_summary.to_dict()}, {'score': score_summary.to_dict()}]

    def calculate_best_trick(self, df):
        # Step 1: Filter out only landed scorecards
        landed_df = df[df['landed']]

        # Step 2: Get the single best scorecard for each section
        best_trick_df = landed_df.loc[landed_df.groupby('section')['score'].idxmax()]

        # Step 3: Calculate summary statistics for each section
        section_summary = best_trick_df.groupby('section')['score'].describe()

        # Step 4: Calculate summary statistics for division, execution, difficulty, and creativity
        score_summary = best_trick_df[['division', 'execution', 'difficulty', 'creativity']].describe()

        # Step 5: Transpose the section_summary DataFrame
        section_summary = section_summary.transpose()

        # Step 6: Return the two DataFrames as a list of dictionaries
        return [{'section': section_summary.to_dict()}, {'score': score_summary.to_dict()}]



class TeamStats(db.Document):
    pass