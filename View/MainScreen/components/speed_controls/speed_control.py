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

    def set_speed_to_zero(self):
        # Iterate through the children of the speed_box to find the 'Zero' button
        print('set speed to zero')
        for child in self.ids.speed_box.children:
            if child.text == 'Zero':
                # Set the state of the 'Zero' button to 'down'
                child.state = 'down'
                # Call set_speed to apply the speed change
                self.set_speed(child)
            else:
                child.state = 'normal'

    def on_disabled(self, instance, value):
        for child in self.ids.speed_box.children:
            child.disabled = value

    def set_speed(self, instance):
        if instance.state == 'down':
            instance.style = 'filled'
            self.speed = instance.value
        else:
            instance.style = 'outlined'

