import mongoengine as db


class ContestResults(db.Document):
    contest = db.ReferenceField('Contest')
    overall = db.DynamicField()