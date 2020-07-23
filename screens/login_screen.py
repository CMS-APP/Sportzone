import sys
import os

from kivy.clock import Clock
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import Screen

sys.path.insert(1, os.path.abspath("../") + '/fitness_dev_v0.3/files')

Builder.load_file("Screens/Screens_kv/login_screen.kv")


class LoginScreen(Screen):
    def __init__(self, app, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.app = app
        self.start()

    def start(self):  # Function to be initiated when this screen is selected
        self.raise_event = Clock.schedule_interval(self.raise_button, 0)

    def raise_button(self, _):  # Function the raised buttons raised
        self.login_btn.elevation = 10
        self.signup_btn.elevation = 10

    def stop(self):  # Function to be initiated when a different screen is selected
        self.raise_event.cancel()
