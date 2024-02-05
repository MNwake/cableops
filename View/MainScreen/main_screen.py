import cv2
import time
from kivy.graphics.texture import Texture

from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, Clock
from kivymd.uix.menu import MDDropdownMenu

from View.MainScreen.components import PowerButton, EmergencyBrake, SpeedControl, DirectionButton, MyTopAppBar, RiderSearch, CustomOneLineIconListItem # NOQA
from View.MainScreen.components.carrier_card import CarrierCard
from View.MainScreen.components.nav_drawer.nav_drawer import MyNavDrawer, DrawerItem
from View.base_screen import BaseScreenView


class MainScreenView(BaseScreenView):
    status = StringProperty()
    direction = StringProperty()
    speed = StringProperty()
    carrier_number = StringProperty()
    rider_on_deck = StringProperty(defaultvalue='Select Rider')
    magazine = BooleanProperty()
    fork = BooleanProperty()
    active_carrier = ObjectProperty()
    active_rider_name = StringProperty(defaultvalue="Empty")
    fork_camera = StringProperty(defaultvalue='Off')
    park_name = StringProperty(defaultvalue='Test Park')
    preset_speeds = ObjectProperty(allownone=True)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.nav_drawer = MyNavDrawer()
        self.ids.nav_layout.add_widget(self.nav_drawer)
        self.nav_drawer.set_state('close')
        self.riders_list_menu = MDDropdownMenu(
            caller=self.ids.rider_search,
            position='bottom'

        )
        self.riders_list_menu_is_open = False  # Flag to track if the menu is open

        self.set_carriers()

        Clock.schedule_interval(self.update_video, 1/24)


    def model_is_changed(self):
        print('model is changed')
        self.speed = str(self.model.cable.speed)
        self.ids.power_button.is_cable_on = self.model.cable.running
        self.ids.direction_button.is_cable_going_forward = self.model.cable.forward
        if self.model.rider_on_deck:
            self.rider_on_deck = self.model.rider_on_deck.full_name
        else:
            self.rider_on_deck = 'Select Rider'
        self.update_riders_dropdown(self.model.riders_checked_in)

        self.status = 'On' if self.model.cable.running else 'Off'
        self.magazine = self.model.cable.magazine.engaged
        self.fork = self.model.cable.fork.engaged
        # self.set_checkin_riders
        self.update_carriers()
        self.active_carrier = self.model.cable.active_carrier

    def update_video(self, dt):

        def frame_to_texture(frame):
            buf = cv2.flip(frame, 0).tostring()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            return texture

        frame = self.model.cable.fork.camera.get_frame()
        if frame is not None:
            texture = frame_to_texture(frame)
            self.ids.fork_camera.texture = texture
    def on_active_carrier(self, instance, value):
        if value.rider:
            self.active_rider_name = value.rider.full_name
            self.ids.fork_button.disabled = False
        else:
            self.active_rider_name = 'Empty'
            self.ids.fork_button.disabled = True

    def update_carriers(self):
        reversed_children = reversed(self.ids.carrier_grid.children)

        for index, carrier_card in enumerate(reversed_children):
            if index < len(self.model.cable.carriers):
                carrier_card.carrier = None
                carrier_card.carrier = self.model.cable.carriers[index]
            else:
                carrier_card.carrier = None

    def set_carriers(self):
        for carrier in self.model.cable.carriers:
            self.ids.carrier_grid.add_widget(CarrierCard(carrier=carrier))


    def focus_rider_search(self, instance, focus):
        if focus and instance.text == 'Select Rider':
            instance.text = ''
        elif not focus and instance.text == '':
            instance.text = 'Select Rider'
        if focus:
            self.open_riders_list_menu()
        if not focus:
            self.close_riders_list_menu()

    def open_riders_list_menu(self):
        if not self.riders_list_menu_is_open:
            self.riders_list_menu.position = 'bottom'
            self.riders_list_menu.open()
            self.riders_list_menu_is_open = True

    def close_riders_list_menu(self):
        if self.riders_list_menu_is_open:
            self.riders_list_menu.dismiss()
            self.riders_list_menu_is_open = False

    def on_settings_callback(self):
        print('settings icon')

    def on_menu_callback(self):
        self.nav_drawer.set_state('toggle')

    def update_riders_dropdown(self, riders):

        def add_rider_item(rider):
            self.riders_list_menu.items.append(
                {
                    "text": rider.full_name,
                    "on_release": lambda x=rider: self.controller.rider_on_deck(x),
                }
            )

        self.riders_list_menu.items = []
        for rider in riders:
            add_rider_item(rider)


    def on_enter(self, *args):
        self.model_is_changed()
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

    def fork_pressed(self):
        if not self.model.cable.running:
            return
        self.controller.engage_fork()

    def send_pressed(self):
        if not self.model.cable.running or not self.model.rider_on_deck:
            print('returned')
            return

        self.controller.send_rope()
