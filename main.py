from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp

from files.file_handling import read_file
# Import new font
LabelBase.register(name="Geosans", fn_regular="fonts/GeosansLight.ttf", fn_italic="fonts/GeosansLight-Oblique.ttf")
# Change screen size to match phone size
Window.size = [300, 600]
# Import all screens used inside the add
from screens.active_gym_screen import ActiveGymScreen
from screens.create_screen import CreateScreen
from screens.gym_screen import GymScreen
from screens.home_screen import HomeScreen
from screens.tutorial_screen import TutorialScreen

# Import new font
LabelBase.register(name="Geosans", fn_regular="fonts/GeosansLight.ttf", fn_italic="fonts/GeosansLight-Oblique.ttf")
# Change screen size to match phone size
Window.size = [500, 800]

all_screens = [HomeScreen, GymScreen, ActiveGymScreen, CreateScreen]
screen_manager = ScreenManager()

if read_file("files/viewed.pkl") is None:
    all_screens.insert(0, TutorialScreen)


class SportifyApp(MDApp):
    all_active_screens = []

    def __init__(self, **kwargs):
        super(SportifyApp, self).__init__(**kwargs)
        for screen_class in all_screens:  # Create a local version for each screen for the application
            screen = screen_class(self)
            self.all_active_screens.append(screen)
            screen_manager.add_widget(screen)

    def screen_action(self, selected_screen_name, direction, action=None):
        """ Function which can be accessed at any time to move between different screens.
        Parameters:
            selected_screen_name: The name of the selected screen. Example - "home_screen"

            direction: The direction of the animation. Example - "right", "left", "up", "down"

            action: Transfer to and(or) perform a function for a different screen. Example - "T", "R/T"

        If the "R/T" action is selected the screen is returned - mainly used for accessing functions in different
        screens """

        screen_manager.transition.direction = direction  # Select direction for the screen manager to go to
        for screen in self.all_active_screens:
            if screen.name == selected_screen_name:
                selected_screen = screen
                break
        if action is None or action == "T":
            screen_manager.current = selected_screen_name
        elif action == "R/T":
            screen_manager.current = selected_screen_name
            return selected_screen

    def build(self):  # Main loop for the whole application.
        return screen_manager


if __name__ == "__main__":
    sportify_app = SportifyApp()
    sportify_app.run()
