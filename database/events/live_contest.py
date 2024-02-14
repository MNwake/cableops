from datetime import datetime

import mongoengine as db
from mongoengine import ListField, EmbeddedDocumentField

class LiveContest(db.Document):
    contest = db.ReferenceField("Contest", required=True)
    start_time = db.DateTimeField(default=datetime.now())
    scorecards = db.ListField(db.ReferenceField("Scorecard"))
    rankings = db.DynamicField()
    carriers = ListField(EmbeddedDocumentField('Carrier'))

