from mongoengine import Document, StringField, IntField, BooleanField, EmbeddedDocumentField, ListField, \
    FloatField, ReferenceField

from database.CableOps import Carrier, DCMotor, Fork, Magazine, MagneticSensor


class Cable(Document):
    park = ReferenceField('Park')
    name = StringField(required=True)
    _speed = FloatField(default=0)
    num_carriers = IntField(default=8)
    lap_time = IntField(default=90)
    e_brake = BooleanField()

    fork = EmbeddedDocumentField('Fork')
    magazine = EmbeddedDocumentField('Magazine')
    carriers = ListField(EmbeddedDocumentField('Carrier'))

    meta = {'db_alias': 'cable'}

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
        self.forward = True

        # Initialize carriers list
        self.carriers = []  # Reset the carriers list

        # Add carriers up to num_carriers
        for i in range(self.num_carriers):
            carrier = Carrier(number=i + 1)
            self.carriers.append(carrier)

        self.speed_settings = {
            'Zero': 0,
            'Idle': 5,
            '1': 50,
            '2': 75,
            '3': 100
        }

    def toggle_fork(self):
        # Check if the direction is forward before toggling the fork
        if self.forward:
            if not self.fork.engaged:
                self.fork.engage()
            else:
                self.fork.disengage()
        else:
            print("Fork cannot be toggled when the direction is not forward.")

    def toggle_magazine(self):
        # Check if the direction is forward before engaging the magazine
        if self.forward:
            if not self.magazine.engaged:
                self.magazine.engage()
            else:
                self.magazine.disengage()
        else:
            print("Magazine cannot be engaged when the direction is not forward.")
    @property
    def riders_on_water(self):
        riders = []
        for carrier in self.carriers:
            if carrier.rider:
                riders.append((carrier.number, carrier.rider))
        return riders

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
        self._speed = value
        # Set the speed of the motor
        if self.running:  # Check if the system is running before changing the speed
            self.motor.change_speed(speed=value)

    def start(self):
        print('start')
        if self.e_brake:
            return "Error: Emergency brake is active."

        if not any(carrier.active for carrier in self.carriers):
            self.carriers[0].active = True

        self.motor.start_motor_thread(self.forward)
        print('passed start motor thread')
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
        # self.carrier_pass_callback()

    def emergency_stop(self):
        self.e_brake = True
        self.motor.hard_stop()
        self.running = False

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
