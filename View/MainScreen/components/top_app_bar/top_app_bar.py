from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty, StringProperty
from kivymd.uix.appbar import MDTopAppBar




class MyTopAppBar(MDTopAppBar, EventDispatcher):
    park_name = StringProperty()
    menu_icon = ObjectProperty(None)
    settings_icon = ObjectProperty(None)

    def menu_icon_press(self):
        if self.menu_icon:
            self.menu_icon()

    def settings_icon_press(self):
        if self.settings_icon:
            self.settings_icon()