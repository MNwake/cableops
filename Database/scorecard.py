import json
from datetime import datetime

import mongoengine as db
# import pandas as pd


class Scorecard(db.Document):
    date = db.DateTimeField(default=datetime.now)
    section = db.StringField()
    division = db.FloatField()
    execution = db.FloatField()
    creativity = db.FloatField()
    difficulty = db.FloatField()
    landed = db.BooleanField()
    contest = db.ReferenceField("Contest")
    rider = db.ReferenceField("User")
    judge = db.ReferenceField("Judge")
    average = db.FloatField()

    @classmethod
    def get_scorecards_by_rider(cls, rider):
        return cls.objects.filter(rider=rider)

    # def save(self, *args, **kwargs):
    #     self.average = self.calculate_average
    #     super(Scorecard, self).save(*args, **kwargs)

    # @classmethod
    # def to_dataframe(cls, landed=None, start_date=None, end_date=None, contest_id=None, rider_id=None):
    #     query_args = {}
    #
    #     if landed is not None:
    #         query_args['landed'] = landed
    #     if contest_id is not None:
    #         query_args['contest'] = contest_id
    #     if rider_id is not None:
    #         query_args['rider'] = rider_id
    #
    #     if start_date is not None and end_date is not None:
    #         query_args['date__gte'] = start_date
    #         query_args['date__lte'] = end_date
    #
    #     scorecards = cls.objects(**query_args)
    #     df = pd.json_normalize(json.loads(scorecards.to_json()))
    #
    #
    #     df = df.drop(columns=['date.$date'], errors='ignore')
    #     return df

