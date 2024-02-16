import mongoengine as db


class Park(db.Document):
    name = db.StringField(required=True)
    state = db.StringField()
    abbreviation = db.StringField()
    team = db.ReferenceField('Team')
    cable = db.ListField(db.ReferenceField('Cable'))
    riders_checked_in = db.ListField(db.ReferenceField('Rider'))


class Team(db.Document):
    name = db.StringField(required=True)
    team_stats = db.ReferenceField('TeamStats')
    riders = db.ListField(db.ReferenceField('Rider'))
