from mongoengine import EmbeddedDocument, BooleanField

from database.CableOps import StepperMotor


class Magazine(EmbeddedDocument):
    loaded = BooleanField()
    engaged = BooleanField(default=False)

    # meta = {'db_alias': 'cable'}

    def __init__(self, **kw):
        super().__init__(**kw)
        self.motor = StepperMotor(pulse_pin=21, direction_pin=20)
        self.servo = None # TODO
        self.sensor = None # TODO
        self.engaged_callback = None


    def go_home(self):
        """
        while sensor is open,
            rotate motor reverse

        """

    def load_ball_rope(self):
        """
        if self.sensor is closed:
            open servo motor
            close servo motor
        """

    def engage(self):
        if self.engaged:
            return
        print('mag engaged')
        steps = 400  # Number of steps for 2 rotations
        self.motor.rotate(steps, clockwise=True, speed=0.001)
        self.engaged = True

    def disengage(self, rider_sent: bool = True):
        if not self.engaged:
            return
        self.go_home()
        self.engaged = False
        if rider_sent:
            self.load_ball_rope()


