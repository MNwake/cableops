from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, ListProperty

from View.MainScreen.components import PowerButton, EmergencyBrake, SpeedControl  # NOQA
# from kivymd.uix.segmentedcontrol import MDSegmentedControl, MDSegmentedControlItem
from View.base_screen import BaseScreenView

# from kivymd.uix.button import MDFlatButton

class MainScreenView(BaseScreenView):
    status = StringProperty()
    direction = StringProperty()
    speed = StringProperty()
    carrier_number = StringProperty()
    rider_on_deck = StringProperty(defaultvalue='Rider on Deck')
    magazine = BooleanProperty()
    fork = BooleanProperty()
    active_carrier = ObjectProperty()
    active_rider_name = StringProperty(defaultvalue="Empty")
    fork_camera = StringProperty(defaultvalue='Off')
    park_name = StringProperty(defaultvalue='Test Park')
    preset_speeds = ListProperty()

    def __init__(self, **kw):
        super().__init__(**kw)

    def on_enter(self, *args):
        self.model_is_changed()

    def model_is_changed(self):
        print('model is changed')
        self.speed = str(self.model.cable.speed)
        self.ids.power_button.is_cable_on = self.model.cable.running
        self.preset_speeds = self.model.cable.speed_settings

    def emergency_brake_error(self):
        print('ebrake is active')
        return

    def lock_controls(self, widget):
        self.ids.power_button.disabled = True
        self.ids.speed_control.disabled = True
        widget.is_cable_locked = True

    def unlock_controls(self, widget):
        self.ids.power_button.disabled = False
        self.ids.speed_control.disabled = False
        widget.is_cable_locked = False
        # TODO open notification for user to enter pin, then clear
        self.controller.clear_emergency_brake()