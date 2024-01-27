from mongoengine import EmbeddedDocument, BooleanField

from Cable.camera import DSLRCamera


class Fork(EmbeddedDocument):
    engaged = BooleanField(default=False)
    callback = None  # Reference to the callback method

    def __init__(self, **kw):
        super().__init__(**kw)
        self.camera = DSLRCamera()

    def set_model_callback(self, callback):
        self.callback = callback

    def engage(self):
        self.engaged = True
        if self.callback:
            self.callback('engaged')

    def disengage(self):
        self.engaged = False
        if self.callback:
            self.callback('disengaged')

    def remove_rider(self, carrier):
        if not self.engaged:
            return
        carrier.release()
        self.disengage()

