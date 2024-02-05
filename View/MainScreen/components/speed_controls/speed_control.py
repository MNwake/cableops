from kivy.properties import StringProperty, NumericProperty, ListProperty, BooleanProperty, ObjectProperty
from kivy.uix.behaviors import ToggleButtonBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton

from View.MainScreen.components.buttons.direction_button import DirectionButton


class MyToggleButton(ToggleButtonBehavior, MDButton):
    text = StringProperty()
    value = NumericProperty()
    speed_control = ObjectProperty()

    def on_state(self, widget, value):
        # Call the set_speed method of SpeedControl
        if self.speed_control:
            self.speed_control(self)

class SpeedControl(MDBoxLayout):
    speed = NumericProperty(allownone=True)
    disabled = BooleanProperty(False)
    speed_presets = ObjectProperty(allownone=True)
    direction = StringProperty(defaultvalue='forward')



    def on_speed_presets(self, instance, value):
        print('on speed presets')
        if self.ids.speed_box.children:
            self.ids.speed_box.clear_widgets()
        if not value:
            return

        for label, speed in value.items():
            button = MyToggleButton(
                text=label,
                value=speed,
                group='speed',
                speed_control=self.set_speed
            )

            if label == 'Zero':
                button.state = 'down'
            self.ids.speed_box.add_widget(button)

    def on_disabled(self, instance, value):
        for child in self.ids.speed_box.children:
            child.disabled = value

    def set_speed(self, instance):
        print(f'state: {instance.state}')
        if instance.state == 'down':
            print('Button pressed:', instance.text)
            instance.style = 'filled'
            self.speed = instance.value
        else:
            instance.style = 'outlined'

