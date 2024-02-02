import time

from View.MainScreen.main_screen import MainScreenView


class MainScreenController:
    """
    The `MainScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    def __init__(self, model):
        self.model = model  # Model.main_screen.MainScreenModel
        self.view = MainScreenView(controller=self, model=self.model)
        self.model.cable.carrier_pass_callback = self.on_carrier_pass

    def get_view(self) -> MainScreenView:
        return self.view

    def start_cable(self):
        if self.model.cable.e_brake:
            self.view.emergency_brake_error()
            return
        self.model.cable.start()
        self.model.notify_observers('main screen')

    def stop_cable(self):
        print('stop cable')
        self.model.cable.stop()
        self.model.notify_observers('main screen')

    def adjust_speed(self, value):
        self.model.cable.speed = value
        self.model.notify_observers('main screen')

    def change_direction(self, value):
        print('change direction')
        self.model.cable.stop()
        self.model.cable.direction = value
        self.model.notify_observers('main screen')

    def send_rope(self):
        self.model.cable.magazine.engage()
        self.model.notify_observers('main screen')

    def on_carrier_pass(self):
        self.model.rider_on_deck = self.model.cable.rider_on_deck

        self.view.ids.send_button.disabled = False
        self.view.menu.disabled = False

        self.model.update_rider_list()

        self.model.notify_observers('main screen')

    def rider_on_deck(self, rider):
        self.model.rider_on_deck = rider

    def clear_on_deck(self):
        self.model.cable.rider_on_deck = None

    def engage_fork(self):
        self.model.cable.fork.engage()

    def simulate_carrier(self):
        print('simulate carrier')
        self.model.cable.carrier_pass_motor()

    def emergency_brake(self, root):
        self.model.cable.emergency_stop()
        self.model.notify_observers('main screen')
        self.view.lock_controls(root.ids.lock_button)

    def clear_emergency_brake(self):
        self.model.cable.e_brake = False
