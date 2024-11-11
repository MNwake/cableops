from mongoengine import Document, ReferenceField


class Team(Document):
    park = ReferenceField('Park')