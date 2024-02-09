import sys
import threading
import time


if 'linux' in sys.platform:
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)


class MagneticSensor:

    def __init__(self, pin, callback, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pin = pin
        self.callback = callback
        self.running = False
        self.thread = None
        if 'linux' in sys.platform:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def start(self):
        if 'linux' in sys.platform:
            if not self.running:
                self.running = True
                self.thread = threading.Thread(target=self.monitor_sensor)
                self.thread.start()

    def stop(self):
        self.running = False
        if self.thread is not None:
            self.thread.join()

    def monitor_sensor(self):
        while self.running:
            if GPIO.input(self.pin) == GPIO.LOW:
                self.callback()
                time.sleep(1)  # Debounce delay
