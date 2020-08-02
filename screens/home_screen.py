from datetime import datetime

from kivy.clock import Clock
from kivy.graphics import Rectangle, Color
from kivy.lang.builder import Builder
from kivy.properties import NumericProperty
from kivy.uix.screenmanager import Screen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel

from files.file_handling import read_file
from screens.kivy_objects import KivyButton, KivyLabel, ORANGE

Builder.load_file("Screens/Screens_kv/home_screen.kv")

# Used so a non-numerical date is displayed
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
SUFFIXES = ["st", "nd", "rd", "th", "th", "th", "th", "th", "th", "th", "th", "th", "th", "th", "th", "th", "th", "th",
            "th", "th", "st", "nd", "rd", "th", "th", "th", "th", "th", "th", "th", "st"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",
          "December"]


class InfoCard(MDCard):
    # Inherits from the MDCard module - Is used to display the different activities available on the home screen.
    orientation = "vertical"
    padding = 10, 10, 10, 10
    height = NumericProperty(100)

    def __init__(self, grid, name, image, on_release_action, **kwargs):
        """ Initial parameters:
        name: text for the main label. Example - "Gym", "Yoga", ...
        image: image used behind the label
        on_release_action: The function called if the card is released
        """
        super(InfoCard, self).__init__(**kwargs)
        self.on_release_action = on_release_action

        with self.canvas:
            # Creates a Border with the image and label infront
            Color(1, 143 / 255, 5 / 255)  # Orange color
            self.border = Rectangle(rectangle=(0, 0, 200, 200))
            Color(1, 1, 1, 1)  # Resets the color to white
            self.image = Rectangle(source=image)
            self.title = MDLabel(text=f"{name}", color=(0, 0, 0, 1))
            self.title.font_name, self.title.font_size = "Geosans", 30

        self.title_text = self.title.text
        # Whenever the position or size of the card changes. The border and image changes position and size too
        self.bind(pos=self.update_bg)
        self.bind(size=self.update_bg)

        grid.add_widget(self)

    def update_bg(self, *args):  # Updates the position and size of the card
        self.border.pos = self.pos
        self.border.size = self.size
        self.image.pos = self.pos[0] + 2, self.pos[1] + 2
        self.image.size = self.size[0] - 4, self.size[1] - 4
        self.title.pos = self.pos[0] + 10, self.pos[1]
        self.title.size = self.size

    def on_release(self):  # The action when the card is released
        self.on_release_action()


class HomeScreen(Screen):
    update_event = None

    def __init__(self, app, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        self.app = app
        if read_file("files/viewed.pkl") is not None and read_file("files/viewed.pkl"):
            self.start()

    def start(self):
        self.update_event = Clock.schedule_interval(self.update, 0)
        self.ids.action_grid.clear_widgets()
        KivyButton(grid=self.ids.action_grid, md_bg_color=ORANGE, font_size=25, on_release_action=self.gym_action,
                   size_hint=[1 / 2, None], height=50, text="Gym")

        KivyLabel(grid=self.ids.action_grid, font_size=25, size_hint=[1 / 2, None], height=50)

    def stop(self):
        self.update_event.cancel()

    def update(self, _):  # Updates the date on the home page
        self.date.text = f"{DAYS[datetime.today().weekday()]} {datetime.now().day}{SUFFIXES[datetime.now().day - 1]} of {MONTHS[datetime.now().month - 1]} {datetime.now().year} "

    def gym_action(self):  # The action when the gym card is pressed
        self.stop()
        self.app.screen_action("gym_screen", "left", "R/T").start()
