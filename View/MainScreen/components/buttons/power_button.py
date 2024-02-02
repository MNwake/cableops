from kivy.properties import BooleanProperty, StringProperty
from kivymd.uix.button import MDButton


class PowerButton(MDButton):
    is_cable_on = BooleanProperty(False)
    icon = StringProperty(defaultvalue='power-off')
    text = StringProperty(defaultvalue='Power Off')

    def on_is_cable_on(self, instance, value):
        if value:
            self.style = 'filled'
            self.text = 'Power On'
            self.icon = 'power-on'

        else:
            self.style = 'elevated'
            self.text = 'Power Off'
            self.icon = 'power-off'



