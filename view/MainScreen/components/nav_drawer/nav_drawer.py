from kivy.properties import StringProperty, ColorProperty, ObjectProperty, ListProperty
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.behaviors import RectangularRippleBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.navigationdrawer import MDNavigationDrawer, MDNavigationDrawerItem


class DrawerLabel(MDBoxLayout, ButtonBehavior, RectangularRippleBehavior):
    icon = StringProperty()
    text = StringProperty()



class DrawerItem(MDNavigationDrawerItem):
    icon = StringProperty()
    text = StringProperty()

    def __init__(self, **kwargs):
        super(DrawerItem, self).__init__(**kwargs)

    # def on_text(self, instance, value):
    #     print('on_text:', value)

class MyNavDrawer(MDNavigationDrawer):
    switch_screen = ObjectProperty()