import mongoengine as db


class Park(db.Document):
    name = db.StringField(required=True)
    state = db.StringField()
    abbreviation = db.StringField()
    team_name = db.StringField()
    cable = db.ListField(db.ReferenceField('Cable'))
    riders_checked_in = db.ListField(db.ReferenceField('Rider'))


