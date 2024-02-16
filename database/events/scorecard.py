from datetime import datetime

import mongoengine as db


class Scorecard(db.Document):
    date = db.DateTimeField(default=datetime.now)
    section = db.StringField()
    division = db.FloatField()
    execution = db.FloatField()
    creativity = db.FloatField()
    difficulty = db.FloatField()
    score = db.FloatField()
    landed = db.BooleanField()
    park = db.ReferenceField("Park")
    rider = db.ReferenceField("User")
    judge = db.ReferenceField("Judge")

    @classmethod
    def get_scorecards_by_rider(cls, rider):
        return cls.objects.filter(rider=rider).order_by('-date').limit(20)

    @classmethod
    def get_most_recent_cards(cls, amount: int = 20):
        return cls.objects.order_by('-date').limit(amount)


