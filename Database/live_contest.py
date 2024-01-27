from datetime import datetime

import mongoengine as db
from mongoengine import ListField, EmbeddedDocumentField


class Carrier(db.EmbeddedDocument):
    number = db.IntField(required=True)
    bib_color = db.StringField()
    rider = db.ReferenceField('Rider')


class LiveContest(db.Document):
    contest = db.ReferenceField("Contest", required=True)
    start_time = db.DateTimeField(default=datetime.now())
    scorecards = db.ListField(db.ReferenceField("Scorecard"))
    rankings = db.DynamicField()
    carriers = ListField(EmbeddedDocumentField('Carrier'))

    def __init__(self, *args, **kwargs):
        super(LiveContest, self).__init__(*args, **kwargs)
        # If carriers list is empty and contest.num_riders_on_water exists
        if not self.carriers and getattr(self.contest, 'num_riders_on_water', None):
            for i in range(2, 2 * self.contest.num_riders_on_water + 1, 2):  # Generate even numbers
                self.carriers.append(Carrier(number=i))
            # You might also want to save the document here. Depends on your application logic.
            # self.save()

    def get_carrier(self, number):
        return next((c for c in self.carriers if c.number == number), None)

    def remove_rider_from_carrier(self, carrier_number):
        carrier = self.get_carrier(carrier_number)
        carrier.rider = None
        carrier.bib_color = None
        self.save()

    def set_rider_on_carrier(self, rider, carrier_number):
        carrier = self.get_carrier(carrier_number)
        if not carrier:  # If no carrier exists with the given number
            carrier = Carrier(number=carrier_number)  # Create a new Carrier instance
            self.carriers.append(carrier)  # Append it to the carriers list

        carrier.rider = rider
        carrier.bib_color = rider.bib_color
        self.save()

    @property
    def riders_on_water(self):
        return [carrier.rider for carrier in self.carriers if carrier.rider is not None]
