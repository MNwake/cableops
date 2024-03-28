import uuid
from datetime import datetime

import mongoengine as db

class ContestCarrier(db.Document):
    number = db.IntField(unique=True)
    rider = db.ReferenceField('Rider')
    bib_color = db.StringField()
    session = db.StringField()




