import time
from datetime import datetime

import mongoengine as db
from pandas import DataFrame, to_datetime, concat

from .scorecard import Scorecard


class RiderStats(db.Document):
    rider = db.ReferenceField('Rider', required=True)
    year = db.IntField(default=datetime.now().year)
    overall = db.DictField()  # Field to store overall rankings
    top_10 = db.DictField()  # Field to store riders top 10 scorecards
    cwa = db.DictField()  # CWA score metrics
    attempted = db.DictField()

    meta = {
        'indexes': [
            {'fields': ['rider', 'year'], 'unique': True}
        ]
    }

    @classmethod
    async def get_rider_stats(cls, rider_id=None):
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

        # Perform various calculations
        self.overall = self.calculate_overall(df).to_dict()
        self.top_10 = self.calculate_top_10(df).to_dict()
        self.cwa = self.calculate_cwa(df).to_dict()
        self.attempted = self.calculate_attempted(df).to_dict()

        # Save or update rankings
        self.save()

        end_time = time.time()  # End the timer
        execution_time = end_time - start_time  # Calculate the duration
        print(f"Ranking calculations completed in {execution_time} seconds.")
        return self

    def calculate_overall(self, df):
        # Calculate total and landed counts for each section
        total_count = df.groupby('section').size().rename('total_count')
        landed_count = df[df['landed']].groupby('section').size().rename('landed_count')

        # Calculate landing percentage and rename it to land_rate
        land_rate_sections = (landed_count / total_count).rename('land_rate').fillna(0) * 100

        # Calculate summary statistics for landed scorecards in each section
        landed_df = df[df['landed'] == True]
        grouped = landed_df.groupby('section')
        section_summary = grouped['score'].describe()

        # Add land_rate to the section summary
        section_summary = section_summary.join(land_rate_sections, how='left')

        # Calculate summary statistics for all landed scorecards combined
        overall_summary = landed_df['score'].describe().to_frame().T
        overall_summary.index = ['all_sections']

        # Calculate land_rate for all sections combined
        overall_landed_percentage = (df['landed'].sum() / len(df)) * 100
        overall_summary['land_rate'] = overall_landed_percentage

        # Concatenate overall summary with section summary
        combined_summary = concat([section_summary, overall_summary])

        return combined_summary

    def calculate_top_10(self, df):
        # Filter out only landed scorecards
        landed_df = df[df['landed'] == True]

        # Get unique sections
        sections = landed_df['section'].unique()
        top_10_stats_list = []

        # Calculate top 10 for each section
        for section in sections:
            top_10 = landed_df[landed_df['section'] == section].nlargest(10, 'score')
            section_stats = top_10['score'].describe().rename(section)
            top_10_stats_list.append(section_stats)

        # Calculate top 10 across all sections
        top_10_overall = landed_df.nlargest(10, 'score')
        overall_stats = top_10_overall['score'].describe().rename('all_sections')
        top_10_stats_list.append(overall_stats)

        # Concatenate all statistics into a single DataFrame
        top_10_stats = concat(top_10_stats_list, axis=1)

        return top_10_stats.transpose()

    def calculate_cwa(self, df):
        # Filter out scorecards with a score over 50
        score_over_50_df = df[df['score'] > 50]

        # Calculate total and landed counts for scorecards over 50
        total_count_over_50 = score_over_50_df.groupby('section').size().rename('total_count_over_50')
        landed_count_over_50 = score_over_50_df[score_over_50_df['landed']].groupby('section').size().rename(
            'landed_count_over_50')
        land_rate = (landed_count_over_50 / total_count_over_50).rename('land_rate').fillna(0) * 100

        # Get unique sections
        sections = score_over_50_df['section'].unique()
        cwa_stats_list = []

        # Calculate stats for each section
        for section in sections:
            section_stats = score_over_50_df[score_over_50_df['section'] == section]['score'].describe().rename(
                section)
            section_stats['land_rate'] = land_rate.get(section, 0)
            cwa_stats_list.append(section_stats)

        # Calculate stats across all sections
        overall_stats = score_over_50_df['score'].describe().rename('all_sections')
        overall_landed_percentage = (score_over_50_df['landed'].sum() / len(score_over_50_df)) * 100
        overall_stats['land_rate'] = overall_landed_percentage
        cwa_stats_list.append(overall_stats)

        # Concatenate all statistics into a single DataFrame
        cwa_stats = concat(cwa_stats_list, axis=1)

        return cwa_stats.transpose()

    def calculate_attempted(self, df):
        # Filter out only attempted (landed is False) scorecards
        attempted_df = df[df['landed'] == False]

        # Get unique sections
        sections = attempted_df['section'].unique()
        attempted_stats_list = []

        # Calculate stats for each section
        for section in sections:
            section_stats = attempted_df[attempted_df['section'] == section]['score'].describe().rename(section)
            attempted_stats_list.append(section_stats)

        # Concatenate all statistics into a single DataFrame
        attempted_stats = concat(attempted_stats_list, axis=1)

        return attempted_stats.transpose()


class TeamRankings(db.Document):
    pass