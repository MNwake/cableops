from mongoengine import EmbeddedDocument, BooleanField

from Cable.steppermotor import StepperMotor


class Magazine(EmbeddedDocument):
    loaded = BooleanField()
    engaged = BooleanField(default=False)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.motor = StepperMotor(pulse_pin=21, direction_pin=20)
        self.engaged_callback = None

    def engage(self):
        if self.engaged:
            return
        print('mag engaged')
        steps = 400  # Number of steps for 2 rotations
        self.motor.rotate(steps, clockwise=True, speed=0.001)
        self.engaged = True

    def disengage(self):
        if not self.engaged:
            return
        print('mag disengaged')
        steps = 400  # Number of steps for 2 rotations
        self.motor.rotate(steps, clockwise=False, speed=0.001)
        self.engaged = False
