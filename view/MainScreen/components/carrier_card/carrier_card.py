from kivy.properties import StringProperty, ObjectProperty, BooleanProperty
from kivymd.uix.card import MDCard


class CarrierCard(MDCard):
    number = StringProperty()
    name = StringProperty()
    lap_count = StringProperty(defaultvalue='0')
    active = BooleanProperty(defaultvalue=False)
    carrier = ObjectProperty(allownone=True)
    active_thread = ObjectProperty(allownone=True)

    def __init__(self, **kw):
        super().__init__(**kw)


    def on_carrier(self, instance, value):
        if value is None:
            self.name = 'Empty'
            self.lap_count = ''
            return

        self.number = str(value.number)
        if value.rider:
            self.name = value.rider.full_name
            self.lap_count = str(value.lap_count)
            if value.lap_count > 5: # TODO implement lap limit
                self.md_bg_color = [1,0,0,.5]

        if value.active:
            self.active = True
            self.activate_card()
        else:
            self.active = False
            self.deactivate_card()

    def deactivate_card(self):
        self.style = 'filled'
        self.md_bg_color = 'white'

    def activate_card(self):
        self.style = 'outlined'
        self.md_bg_color = [0,1,0,.5]
