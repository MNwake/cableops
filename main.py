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
import os
from dotenv import load_dotenv
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager

from Utility.sync import sync_files
from View.screens import screens
from database import DataBase
from webserver import FastAPIApp

if 'linux' in sys.platform:
    Window.size = (1000, 900)
    import RPi.GPIO as GPIO
    GPIO.setwarnings(False)
    # Load environment variables from .env file
    load_dotenv()

    # Verify the SOLCX_BINARY variable
    solc_binary = os.getenv("SOLCX_BINARY")
    print(f"Using solc binary at: {solc_binary}")

import logging

# Set the root logger level to WARNING to suppress DEBUG and INFO logs globally
logging.basicConfig(level=logging.WARNING)

# Suppress specific library logs
logging.getLogger('web3').setLevel(logging.WARNING)        # Suppress Web3.py logs
logging.getLogger('urllib3').setLevel(logging.WARNING)     # Suppress urllib3 logs used by Web3.py
logging.getLogger('kivy').setLevel(logging.WARNING)        # Suppress Kivy logs
logging.getLogger('pymongo').setLevel(logging.WARNING)     # Suppress pymongo logs
logging.getLogger('firebase_admin').setLevel(logging.WARNING)  # Suppress Firebase Admin logs


import firebase_admin
from firebase_admin import credentials

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

import os
os.environ["KIVY_LOG_LEVEL"] = "warning"


class CableOps(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_all_kv_files(self.directory)
        self.connection = DataBase()
        self.manager_screens = MDScreenManager()
        self.fastapi = FastAPIApp(self.connection)
        self.fastapi.start_fastapi_server()

    def build(self) -> MDScreenManager:
        self.theme_cls.primary_palette = 'Aliceblue'
        self.theme_cls.theme_style = 'Dark'
        # self.theme_cls.dynamic_color = False
        self.generate_application_screens()
        self.manager_screens.current = 'main screen'


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


    def switch_theme_style(self):
        self.theme_cls.primary_palette = (
            "Blue" if self.theme_cls.primary_palette == "White" else "White"
        )
        self.theme_cls.theme_style = (
            "Dark" if self.theme_cls.theme_style == "Light" else "Light"
        )


if __name__ == '__main__':
    print('Hello World!')
    if 'darwin' in sys.platform:
        print("Test " * 10)
        sync_files()
        from solcx import get_installed_solc_versions

        print("Installed Solidity Versions:", get_installed_solc_versions())

    # Run Kivy application
    CableOps().run()
#