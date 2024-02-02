from kivy.properties import BooleanProperty
from kivymd.uix.button import MDIconButton

class LockButton(MDIconButton):
    is_cable_locked = BooleanProperty(False)

    def on_is_cable_locked(self, widget, value):
        if value:
            self.style = 'filled'
        else:
            self.style = 'outlined'
