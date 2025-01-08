from kivy.properties import BooleanProperty, StringProperty
from kivymd.uix.button import MDButton


class DirectionButton(MDButton):
    is_cable_going_forward = BooleanProperty()
    icon = StringProperty(defaultvalue='fast-forward')
    text = StringProperty(defaultvalue='Forward')

    def on_is_cable_going_forward(self, instance, value):
        if value:
            self.icon = 'fast-forward'
            self.text = 'Forward'
        else:
            self.icon = 'rewind'
            self.text = 'Reverse'
