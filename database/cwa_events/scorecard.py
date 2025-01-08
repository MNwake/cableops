from datetime import datetime

import pandas as pd
from bson import ObjectId
from mongoengine import Document, DateTimeField, StringField, FloatField, BooleanField, ListField, ReferenceField



class Scorecard(Document):
    date = DateTimeField(default=datetime.now)
    section = StringField()
    division = FloatField()
    execution = FloatField()
    creativity = FloatField()
    difficulty = FloatField()
    score = FloatField()
    landed = BooleanField()
    approach = StringField()
    trick_type = StringField()
    spin = StringField()
    spin_direction = StringField()
    modifiers = ListField(StringField())
    session = StringField()
    rider = ReferenceField("User")
    park = ReferenceField("Park")
    judge = ReferenceField("Judge")

    meta = {'db_alias': 'cable'}

    def to_dict(self):
        """Convert MongoDB document to a dictionary with formatted dates."""
        data = self.to_mongo().to_dict()
        for field in ['date_of_birth', 'date_created', 'waiver_date']:
            if data.get(field):
                data[field] = data[field].strftime("%Y-%m-%dT%H:%M:%S")
        return data

    @classmethod
    def get_scorecards(cls, rider_ids=None, sort_by='Most Recent', cursor=None, batch_size=10):
        all_scorecards = []

        if rider_ids:
            for rider_id in rider_ids:
                query_params = {'rider': rider_id}

                query = cls.objects(**query_params)

                if sort_by == 'Most Recent':
                    query = query.order_by('-date')
                elif sort_by == 'Score: Highest':
                    query = query.order_by('-score')
                elif sort_by == 'Score: Lowest':
                    query = query.order_by('score')

                if cursor:
                    if isinstance(cursor, str):
                        cursor_date = datetime.fromisoformat(cursor)
                    else:
                        cursor_date = cursor
                    query = query.filter(date__lt=cursor_date)

                rider_scorecards = query.limit(batch_size)
                all_scorecards.extend(rider_scorecards)

        else:
            # Handle case where no rider_ids are provided
            query = cls.objects()

            if sort_by == 'Most Recent':
                query = query.order_by('-date')
            elif sort_by == 'Score: Highest':
                query = query.order_by('-score')
            elif sort_by == 'Score: Lowest':
                query = query.order_by('score')

            if cursor:
                if isinstance(cursor, str):
                    cursor_date = datetime.fromisoformat(cursor)
                else:
                    cursor_date = cursor
                query = query.filter(date__lt=cursor_date)

            all_scorecards = query.limit(batch_size)

        return all_scorecards

    @classmethod
    def get_scorecards_by_rider(cls, rider):
        scorecards = cls.objects.filter(rider=rider)
        return [scorecard.to_mongo().to_dict() for scorecard in scorecards]

    @classmethod
    def get_all_scorecards(cls):
        scorecards = cls.objects.all()
        return [scorecard.to_mongo().to_dict() for scorecard in scorecards]

    @classmethod
    def get_scorecards_by_park(cls, park_id):
        all_scorecards = []
        from events import Rider
        riders = Rider.objects(home_park=park_id)
        for rider in riders:
            scorecards = cls.objects.filter(rider=rider)
            all_scorecards.extend(scorecards)
        return [scorecard.to_mongo().to_dict() for scorecard in all_scorecards]

    @classmethod
    def get_trick_statistics(cls, rider_id):
        # Fetch all scorecards for the rider
        scorecards = cls.objects.filter(rider=rider_id)

        # Check if scorecards are empty
        if not scorecards:
            return

        # Convert scorecards to a list of dictionaries
        scorecards_data = []
        for scorecard in scorecards:
            scorecard_dict = scorecard.to_mongo().to_dict()
            scorecard_dict['_id'] = str(scorecard_dict['_id'])
            scorecards_data.append(cls.convert_objectids(scorecard_dict))

        # Create a DataFrame
        df = pd.DataFrame(scorecards_data)

        # Construct the 'trick name'
        df['trick_name'] = df['section'] + ' ' + df['approach'] + ' ' + df['trick_type'] + ' ' + df[
            'spin_direction'] + ' ' + df['spin']

        # Group by 'trick name'
        grouped = df.groupby('trick_name')

        # Initialize a dictionary to store the results
        trick_stats = {}

        # Loop through each group
        for name, group in grouped:
            # Compute statistics using describe()
            stats = group['score'].describe().to_dict()

            # Find the scorecard with the highest score
            highest_scorecard = group.loc[group['score'].idxmax()].to_dict()
            highest_scorecard['_id'] = str(highest_scorecard['_id'])

            score = group[['division', 'execution', 'difficulty', 'creativity']].describe().to_dict()

            # Add overall and highest scorecard to the result dictionary
            trick_stats[name] = {
                'stats': stats,
                'highest_scorecard': highest_scorecard,
                'scores': score
            }

        return trick_stats

    @classmethod
    def calculate_overall(self, df):
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

    @classmethod
    def calculate_score_counts(cls, rider_id):
        # Calculate total count
        total = cls.objects(rider=rider_id).count()

        # Calculate scored count
        scored = cls.objects(rider=rider_id, score__gte=50).count()

        # Calculate attempted count
        attempted = cls.objects(rider=rider_id, landed=False).count()

        return total, scored, attempted

    @classmethod
    def convert_objectids(cls, data):
        """Recursively convert ObjectId to str in nested dictionaries."""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, ObjectId):
                    data[key] = str(value)
                elif isinstance(value, dict) or isinstance(value, list):
                    data[key] = cls.convert_objectids(value)
        elif isinstance(data, list):
            return [cls.convert_objectids(item) for item in data]
        return data