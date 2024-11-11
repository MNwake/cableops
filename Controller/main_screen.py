import cv2
import time
from kivy.clock import Clock
from kivy.graphics.texture import Texture

from View.MainScreen.main_screen import CableMainScreen


class MainScreenController:
    """
    The `MainScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    def __init__(self, model):
        self.model = model  # Model.main_screen.MainScreenModel
        self.view = CableMainScreen(controller=self, model=self.model)
        self.model.update_rider_list()



    def get_view(self) -> CableMainScreen:
        return self.view
    def start_cable(self, dt=None):
        print('start cable controller')
        if self.model.cable.e_brake:
            self.view.emergency_brake_error()
            return
        self.model.cable.start()
        self.model.notify_observers('main screen')

    def stop_cable(self):
        print('stop cable')
        self.model.cable.stop()
        self.view.ids.speed_control.set_speed_to_zero()
        self.model.notify_observers('main screen')

    def adjust_speed(self, value):
        self.model.cable.speed = value
        self.model.notify_observers('main screen')

    def change_direction(self, instance):
        self.stop_cable()
        if instance.is_cable_going_forward:
            print('change direction to false')
            self.model.cable.forward = False
        else:
            print('change direction to true')
            self.model.cable.forward = True

        self.model.notify_observers('main screen')

    def send_rope(self):
        self.model.cable.toggle_magazine()
        self.model.notify_observers('main screen')


    def rider_on_deck(self, rider):
        print('rider on deck')
        self.model.rider_on_deck = rider

    def clear_on_deck(self):
        self.model.cable.rider_on_deck = None

    def engage_fork(self):
        self.model.cable.toggle_fork()
        self.model.notify_observers('main screen')


    def simulate_carrier(self):
        print('simulate carrier')
        self.model.cable.carrier_pass_motor()


    def emergency_brake(self, root):
        self.model.cable.emergency_stop()
        self.stop_cable()
        self.model.notify_observers('main screen')
        self.view.lock_controls(root.ids.lock_button)

    def clear_emergency_brake(self):
        self.model.cable.e_brake = False

    def update_checked_in_riders(self, text):
        if text == 'Select Rider':
            text = ''
        self.model.update_rider_list(text)