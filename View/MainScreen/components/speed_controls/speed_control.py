from kivy.properties import StringProperty, NumericProperty, ListProperty, BooleanProperty
from kivy.uix.behaviors import ToggleButtonBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton




class MyToggleButton(MDButton, ToggleButtonBehavior):
    text = StringProperty()
    value = NumericProperty()


class SpeedControl(MDBoxLayout):
    speed = StringProperty(allownone=True)
    disabled = BooleanProperty(False)
    speed_preset = ListProperty()

    def on_kv_post(self, base_widget):
        self.ids.zero.state = 'down'

    def on_disabled(self, instance, value):
        if value:
            for child in self.children:
                child.disabled = True
        else:
            for child in self.children:
                child.disabled = False
    def set_speed(self, instance, value):
        print(value)
        if value == 'down':
            print('Button pressed:', instance.text)
            instance.style = 'filled'
            # Update the speed property here if needed
            self.speed = instance.text
        else:
            instance.style = 'outlined'

