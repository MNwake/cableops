from kivy.properties import StringProperty, ObjectProperty, ListProperty
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.list import MDListItem
from kivymd.uix.textfield import MDTextField, MDTextFieldTrailingIcon


class CustomOneLineIconListItem(MDListItem):
    text = StringProperty()

class MyTrailingIcon(MDTextFieldTrailingIcon, ButtonBehavior):
    pass



class RiderSearch(MDTextField):
    rider_on_deck = StringProperty()



