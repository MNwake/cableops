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





