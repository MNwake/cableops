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
    async def get_rider_stats(cls, rider_id=None):

        print('get_rider_stats - rider id:', rider_id)
        if rider_id:
            return await cls.objects(rider_id=rider_id).first()
        else:
            return await cls.objects().all()


    def calculate_stats(self):
        start_time = time.time()  # Start the timer

        # Fetch scorecards for the rider
        df = DataFrame(Scorecard.get_scorecards_by_rider(self.rider))
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