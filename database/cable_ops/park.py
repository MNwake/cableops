import mongoengine as db

from mongoengine import Document, StringField, ReferenceField, ListField, EmbeddedDocument, EmbeddedDocumentField, \
    EmailField



class Address(EmbeddedDocument):
    street = StringField()
    city = StringField()
    state = StringField()
    zip = StringField()
    country = StringField()


class Contact(EmbeddedDocument):
    phone_number = StringField()
    name = StringField(default="")
    position = StringField()
    email = EmailField()


class Park(Document):
    name = StringField(required=True)
    abbreviation = StringField(required=False)
    address = EmbeddedDocumentField(Address, default=None)

    # New fields to match the Swift model
    cover_photo = StringField(required=False)  # Optional
    logo = StringField(required=False)  # Optional

    maintenance = ReferenceField('Maintenance', default=None)
    contacts = ListField(EmbeddedDocumentField(Contact, default=None))

    team = ReferenceField('Team', default=None)
    riders_checked_in = ListField(ReferenceField('Rider'))

    cables = ListField(ReferenceField('Cable', default=None))
    meta = {'db_alias': 'cable'}

class Team(db.Document):
    name = db.StringField(required=True)
    team_stats = db.ReferenceField('TeamStats')
    riders = db.ListField(db.ReferenceField('Rider'))


