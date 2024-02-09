"""
The entry point to the application.

The application uses the MVC template. Adhering to the principles of clean
architecture means ensuring that your application is easy to test, maintain,
and modernize.

You can read more about this template at the links below:

https://github.com/HeaTTheatR/LoginAppMVC
https://en.wikipedia.org/wiki/Model–view–controller
"""
import sys
import threading

from database import DataBase


from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from View.screens import screens
from web.web_server import FastAPIApp

if 'linux' in sys.platform:
    import RPi.GPIO as gpio
    Window.size = (1000, 900)

import subprocess

import firebase_admin
from firebase_admin import credentials, storage

if sys.platform == 'linux':
    cred = credentials.Certificate('/home/theokoester/dev/cableops/server/database/the-cwa-4df1775855c1.json')
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'the-cwa.appspot.com'
    })
else:
    cred = credentials.Certificate('database/the-cwa-4df1775855c1.json')
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'the-cwa.appspot.com'
    })


def sync_files():
    rsync_command = [
        "rsync",
        "-avz",
        "/Users/theokoester/dev/projects/python/CWA/cableops/",
        "theokoester@raspi:/home/theokoester/dev/cableops/"
    ]
    try:
        print('rsync')
        result = subprocess.run(rsync_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Rsync completed successfully")
        print(result.stdout.decode())
    except subprocess.CalledProcessError as e:
        print("Error occurred while running rsync")
        print(e.stderr.decode())



class CableOps(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_all_kv_files(self.directory)
        # This is the screen manager that will contain all the screens of your
        # application.
        self.connection = DataBase()
        self.manager_screens = MDScreenManager()
        print(sys.platform)
        if 'darwin' in sys.platform:
            sync_files()
        
    def build(self) -> MDScreenManager:
        self.theme_cls.primary_palette = 'Aliceblue'
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.dynamic_color = True
        self.generate_application_screens()
        if 'linux' in sys.platform:
            self.start_fastapi_server()
        return self.manager_screens

    def generate_application_screens(self) -> None:
        """
        Creating and adding screens to the screen manager.
        You should not change this cycle unnecessarily. He is self-sufficient.

        If you need to add any screen, open the `View.screens.py` module and
        see how new screens are added according to the given application
        architecture.
        """

        for i, name_screen in enumerate(screens.keys()):
            model = screens[name_screen]["model"]()
            controller = screens[name_screen]["controller"](model)
            view = controller.get_view()
            view.manager_screens = self.manager_screens
            view.name = name_screen
            self.manager_screens.add_widget(view)

    def start_fastapi_server(self):
        self.fastapi_app = FastAPIApp()
        self.fastapi_thread = threading.Thread(target=self.fastapi_app.run)
        self.fastapi_thread.start()

    def on_stop(self):
        if 'linux' in sys.platform:
            print('gpio cleanup')
            gpio.cleanup()

    def switch_theme_style(self):
        self.theme_cls.primary_palette = (
            "Blue" if self.theme_cls.primary_palette == "White" else "White"
        )
        self.theme_cls.theme_style = (
            "Dark" if self.theme_cls.theme_style == "Light" else "Light"
        )

CableOps().run()
