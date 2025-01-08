from mongoengine import EmbeddedDocument, IntField, BooleanField, ReferenceField




class Carrier(EmbeddedDocument):
    number = IntField()
    _occupied = BooleanField(default=False)
    lap_count = IntField(default=0)
    _rider = ReferenceField('Rider')
    active = BooleanField(default=False)

    meta = {'db_alias': 'cable'}

    def __init__(self, **kw):
        super().__init__(**kw)

    @property
    def rider(self):
        return self._rider

    @rider.setter
    def rider(self, value):
        self._rider = value
        self.lap_count = 0
        self._occupied = True if value else False

    def receive(self, rider):
        self._occupied = True
        self.rider = rider
        self.lap_count = 1

    def release(self):
        self._occupied = False
        self.rider = None
        self.lap_count = 0

    def lap(self):
        if self.rider:
            self.rider.lap_count += 1
            self.lap_count += 1
