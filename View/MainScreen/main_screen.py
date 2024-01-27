import cv2
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.properties import StringProperty, BooleanProperty, ListProperty, ObjectProperty
from kivymd.uix.behaviors.toggle_behavior import MDToggleButton
from kivymd.uix.button import MDFlatButton
from kivymd.uix.chip import MDChip
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.segmentedcontrol import MDSegmentedControl, MDSegmentedControlItem

from View.MainScreen.components.carrier_card import CarrierCard
from View.base_screen import BaseScreenView

CarrierCard


class MyToggleButton(MDFlatButton, MDToggleButton):
    grouped = BooleanProperty(defaultvalue=True)

    def __init__(self, **kw):
        super().__init__(**kw)

    def on_touch_down(self, touch):
        # If the button is already in 'down' state, ignore the touch
        if self.state == 'down' and self.grouped:
            return False
        return super(MyToggleButton, self).on_touch_down(touch)


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

    def __init__(self, **kw):
        super().__init__(**kw)
        self._initialize_ui()
        Clock.schedule_interval(self.update_video, 1.0 / 30.0)  # Update at the rate of 30 FPS

    def _initialize_ui(self):
        self.menu = MDDropdownMenu(caller=self.ids.field, position="bottom")
        for carrier in self.model.cable.carriers:
            self.ids.carrier_grid.add_widget(CarrierCard(carrier=carrier))

    def model_is_changed(self):
        self._update_ui_from_model()

    def _update_ui_from_model(self):
        if self.model.cable.running:
            self.status = "Cable On"
        else:
            self.status = "Cable Off"

        self.speed = str(self.model.cable.speed)
        self.direction = self.model.cable.direction
        self.magazine = str(self.model.cable.magazine.engaged)
        self.fork = self.model.fork_status
        self.rider_on_deck = self.model.rider_on_deck.full_name if self.model.rider_on_deck else 'Rider on Deck'
        self.active_carrier = self.model.cable.active_carrier
        if self.active_carrier:
            self.carrier_number = str(self.active_carrier.number)
        self._update_riders_menu()
        self._update_carriers()
        if self.model.cable.fork.camera.is_running:
            self.fork_camera = 'Recording'
        else:
            self.fork_camera = 'Off'

    def update_video(self, dt):
        frame = self.model.cable.fork.camera.get_frame()
        if frame is not None:
            texture = self.frame_to_texture(frame)
            self.ids.fork_video.texture = texture

    @staticmethod
    def frame_to_texture(frame):
        buf = cv2.flip(frame, 0).tostring()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        return texture

    def on_fork(self, instance, value):
        print(f'on fork {value}')

    def _update_carriers(self):
        # Reverse the order of children for correct assignment
        reversed_children = reversed(self.ids.carrier_grid.children)

        for index, carrier_card in enumerate(reversed_children):
            # Make sure the index is within the range of available carriers
            if index < len(self.model.cable.carriers):
                carrier_card.carrier = None
                carrier_card.carrier = self.model.cable.carriers[index]
            else:
                # Handle cases where there are more carrier cards than carriers
                carrier_card.carrier = None  # Or some default value

    def _update_riders_menu(self):
        riders_list = [{"text": rider.full_name, "on_release": lambda x=rider: self.menu_callback(x)} for rider in
                       self.model.riders_list]
        self.menu.items = riders_list

    def menu_callback(self, rider):
        self.menu.dismiss()
        self.controller.rider_on_deck(rider)

    def _set_initial_button_states(self):
        self.ids.power_button.state = 'normal'
        self.ids.forward_toggle.state = 'down'
        # self.ids.idle.state = 'down'

    def on_enter(self, *args):
        self.model_is_changed()
        self._set_initial_button_states()

    def on_active_carrier(self, instance, value):
        if value.rider:
            self.active_rider_name = value.rider.full_name
            self.ids.fork_button.disabled = False
        else:
            self.active_rider_name = 'Empty'
            self.ids.fork_button.disabled = True

    def send_pressed(self):
        if self.status == 'Off' or self.rider_on_deck == 'Rider on Deck':
            return
        self.controller.send_rope()
        self.ids.send_button.disabled = True
        self.menu.disabled = True

    def fork_pressed(self):
        self.controller.engage_fork()
        self.ids.fork_button.disabled = True
