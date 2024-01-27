import sys
import threading

if 'linux' in sys.platform:
    import RPi.GPIO as GPIO
from time import sleep, time


class DCMotor:
    def __init__(self, in1_pin, in2_pin, en_pin):
        self.in1_pin = in1_pin
        self.in2_pin = in2_pin
        self.en_pin = en_pin
        self.current_speed = 0

        if 'linux' in sys.platform:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.in1_pin, GPIO.OUT)
            GPIO.setup(self.in2_pin, GPIO.OUT)
            GPIO.setup(self.en_pin, GPIO.OUT)
            GPIO.output(self.in1_pin, GPIO.LOW)
            GPIO.output(self.in2_pin, GPIO.LOW)

            self.pwm = GPIO.PWM(self.en_pin, 1000)
            self.pwm.start(self.current_speed)  # Start with 0 duty cycle for soft start

    def change_speed(self, speed, increment=5, delay=0.1):
        """ Change the motor speed gradually """
        steps = abs(speed - self.current_speed) // increment

        for _ in range(steps):
            if speed > self.current_speed:
                self.current_speed += increment
            else:
                self.current_speed -= increment

            self.pwm.ChangeDutyCycle(self.current_speed)
            sleep(delay)

        # Set to final speed if it's not exactly divisible by increment
        self.current_speed = speed
        self.pwm.ChangeDutyCycle(self.current_speed)

    def forward(self, speed=25):
        if 'linux' in sys.platform:
            GPIO.output(self.in1_pin, GPIO.HIGH)
            GPIO.output(self.in2_pin, GPIO.LOW)
            self.change_speed(speed)

    def reverse(self, speed=25):
        if 'linux' in sys.platform:
            GPIO.output(self.in1_pin, GPIO.LOW)
            GPIO.output(self.in2_pin, GPIO.HIGH)
            self.change_speed(speed)

    def soft_stop(self):
        """ Soft stop the motor """
        self.change_speed(0)

    def emergency_brake(self):
        """ Immediate stop (hard stop) """
        if 'linux' in sys.platform:
            self.pwm.ChangeDutyCycle(0)
            GPIO.output(self.in1_pin, GPIO.LOW)
            GPIO.output(self.in2_pin, GPIO.LOW)

    def cleanup(self):
        if 'linux' in sys.platform:
            self.pwm.stop()
            GPIO.cleanup()

    def start_motor_thread(self, direction, speed=25):
        """Start the motor in a separate thread."""
        if direction == 'Forward':
            motor_thread = threading.Thread(target=self.forward, args=(speed,))
        elif direction == 'Reverse':
            motor_thread = threading.Thread(target=self.reverse, args=(speed,))
        else:
            raise ValueError("Invalid motor direction: " + direction)

        motor_thread.start()

    def stop_motor_thread(self):
        """Stop the motor from the separate thread."""
        self.soft_stop()