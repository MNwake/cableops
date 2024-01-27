import threading
import time

from mongoengine import Document, StringField, IntField, BinaryField, BooleanField, EmbeddedDocumentField, ListField, \
    FloatField

from Cable.carrier import Carrier
from Cable.dc_motor import DCMotor
from Cable.fork import Fork
from Cable.magazine import Magazine
from Cable.sensor import MagneticSensor


class Cable(Document):
    name = StringField(required=True)
    _speed = FloatField(default=0)
    num_carriers = IntField(default=8)
    lap_time = IntField(default=90)
    e_brake = BooleanField()

    fork = EmbeddedDocumentField(Fork)
    magazine = EmbeddedDocumentField(Magazine)
    carriers = ListField(EmbeddedDocumentField(Carrier))

    meta = {'db_alias': 'ops'}

    def __init__(self, *args, **values):
        super(Cable, self).__init__(*args, **values)
        # Initialize the embedded documents
        self.rider_on_deck = None
        self.fork = Fork()  # Assuming Fork has no required arguments
        self.magazine = Magazine()  # Assuming Magazine has no required arguments
        self.motor = DCMotor(in1_pin=24, in2_pin=23, en_pin=25)
        self.carrier_sensor = MagneticSensor(pin=17, callback=self.carrier_pass_motor)
        self.running = False
        self.carrier_pass_callback = None
        self.direction = 'Forward'

        for i in range(self.num_carriers):
            carrier = Carrier(number=i + 1)
            self.carriers.append(carrier)
        # Initialize the carriers list based on num_carriers

        self.speed_settings = {
            0: 0,
            1: 5,
            2: 25,
            3: 50,
            4: 70
        }

    @property
    def active_carrier(self):
        """Returns the currently active carrier."""
        for carrier in self.carriers:
            if carrier.active:
                return carrier
        return None  # No active carrier found

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        if value in self.speed_settings:
            self._speed = value
            # Set the speed of the motor
            if self.running:  # Check if the system is running before changing the speed
                if self.direction == 'Forward':
                    self.motor.forward(speed=self.speed_settings[value])
                elif self.direction == 'Reverse':
                    self.motor.reverse(speed=self.speed_settings[value])

    def start(self):
        print('start')
        if self.e_brake:
            return "Error: Emergency brake is active."

        if not any(carrier.active for carrier in self.carriers):
            self.carriers[0].active = True

        self.speed = 'Idle'

        self.motor.start_motor_thread(self.direction, speed=self.speed_settings[self.speed])

        self.carrier_sensor.start()
        self.fork.camera.start_camera()
        self.running = True


    def stop(self):
        print('stop')
        self.running = False
        self.motor.soft_stop()
        self.carrier_sensor.stop()
        self.fork.disengage()
        self.fork.camera.stop_camera()
        self.magazine.disengage()
        self.rider_on_deck = None
        self.carrier_pass_callback()

    def elevator_start(self):
        pass

    def carrier_pass_motor(self):
        print('carrier pass')
        current_index = self.get_current_index()
        if current_index is None:
            return

        carrier = self.carriers[current_index]
        carrier.lap()

        self.fork.remove_rider(carrier)

        if self.magazine.engaged:
            carrier.rider = self.rider_on_deck
            self.magazine.disengage()
            self.rider_on_deck = None

        self.update_active_carrier()

    def update_active_carrier(self):
        """Updates the active carrier to the next in sequence."""
        current_index = self.get_current_index()
        if current_index is not None:
            next_index = (current_index + 1) % len(self.carriers)
            carrier = self.carriers[next_index]
            carrier.active = True  # Set the next carrier as active
            self.carriers[current_index].active = False  # Deactivate the current carrier
            self.carrier_pass_callback()

    def get_current_index(self):
        return next((i for i, carrier in enumerate(self.carriers) if carrier.active), None)
