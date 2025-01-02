from kivy.properties import StringProperty

from View.base_screen import BaseScreenView


class MainScreenView(BaseScreenView):
    title = StringProperty()
    def __init__(self, **kw):
        super().__init__(**kw)

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.

        """

    def on_enter(self):
        self.switch_screen('cable coin')


    def on_settings_callback(self):
        self.app.theme_cls.theme_style_switch_animation = True
        self.app.theme_cls.theme_style_switch_animation_duration = 0.8
        self.app.switch_theme_style()
        print('settings icon')

    def on_menu_callback(self):
        self.ids.nav_drawer.set_state('toggle')

    def switch_screen(self, screen_name):
        """
        Switch to the specified screen.
        """
        if self.ids.screen.children:
            current_screen = self.ids.screen.children[0]
            current_screen.on_leave()
            self.ids.screen.clear_widgets()
        screen = self.manager_screens.get_screen(screen_name)
        self.ids.screen.add_widget(screen)
        self.title = screen.title
        screen.on_enter()
