import sys
import threading

if 'linux' in sys.platform:
    import RPi.GPIO as GPIO
from time import sleep, time


class DCMotor:
    def __init__(self, in1_pin, in2_pin, en_pin):
        self.set_speed = None
        self.in1_pin = in1_pin
        self.in2_pin = in2_pin
        self.en_pin = en_pin
        self.current_speed = int(0)

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
        if 'linux' in sys.platform:
            """ Change the motor speed gradually """
            speed = int(speed)
            absolute = abs(speed - self.current_speed)
            print(absolute)
            steps = absolute // increment
            print(steps)

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

    def forward(self):
        print('forward')
        if 'linux' in sys.platform:
            GPIO.output(self.in1_pin, GPIO.HIGH)
            GPIO.output(self.in2_pin, GPIO.LOW)
            self.change_speed(0)


    def reverse(self):
        if 'linux' in sys.platform:
            GPIO.output(self.in1_pin, GPIO.LOW)
            GPIO.output(self.in2_pin, GPIO.HIGH)
            self.change_speed(0)

    def soft_stop(self):
        """ Soft stop the motor """
        self.change_speed(0)

    def hard_stop(self):
        """ Immediate stop (hard stop) """
        if 'linux' in sys.platform:
            self.pwm.ChangeDutyCycle(0)
            GPIO.output(self.in1_pin, GPIO.LOW)
            GPIO.output(self.in2_pin, GPIO.LOW)

    def cleanup(self):
        if 'linux' in sys.platform:
            self.pwm.stop()
            GPIO.cleanup()

    def start_motor_thread(self, direction):
        print('start_motor_thread')
        """Start the motor in a separate thread."""
        if direction:
            motor_thread = threading.Thread(target=self.forward)
        else:
            motor_thread = threading.Thread(target=self.reverse)

        motor_thread.start()

    def stop_motor_thread(self):
        """Stop the motor from the separate thread."""
        self.soft_stop()