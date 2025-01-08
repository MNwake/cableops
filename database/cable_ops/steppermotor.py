import sys
import threading
from time import sleep
from mongoengine import EmbeddedDocument, BinaryField, FloatField

class StepperMotor(EmbeddedDocument):
    def __init__(self, pulse_pin, direction_pin):
        self._pulse_pin = pulse_pin
        self._direction_pin = direction_pin

        if 'linux' in sys.platform:
            import RPi.GPIO as GPIO
            self.GPIO = GPIO
            self.GPIO.setmode(self.GPIO.BCM)
            self.GPIO.setup(self._direction_pin, self.GPIO.OUT)
            self.GPIO.setup(self._pulse_pin, self.GPIO.OUT)

    def _generate_pulse(self, steps, sleep_time):
        if 'linux' in sys.platform:
            for _ in range(steps):
                self.GPIO.output(self._pulse_pin, self.GPIO.HIGH)
                sleep(sleep_time)
                self.GPIO.output(self._pulse_pin, self.GPIO.LOW)
                sleep(sleep_time)

    def rotate(self, steps, clockwise=True, speed=0.01):
        print('rotate')
        if 'linux' in sys.platform:
            direction = self.GPIO.HIGH if clockwise else self.GPIO.LOW
            self.GPIO.output(self._direction_pin, direction)
            threading.Thread(target=self._generate_pulse, args=(steps, speed)).start()

    def cleanup(self):
        if 'linux' in sys.platform:
            self.GPIO.cleanup()