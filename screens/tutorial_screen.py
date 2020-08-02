from datetime import datetime

from kivy.core.window import Window
from kivy.lang.builder import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

from files.file_handling import write_file
from screens.kivy_objects import KivyButton, KivyLabel

Builder.load_file("Screens/Screens_kv/tutorial_screen.kv")


class AnimationScroll(ScrollView):
    def __init__(self, screen, **kwargs):
        super(AnimationScroll, self).__init__(**kwargs)
        self.screen = screen
        self.do_scroll = [False, True]
        self.grid = GridLayout(cols=1, padding=[10])
        self.add_widget(self.grid)

    def animate_widgets(self, animation_dict):
        def animation(widget, start_scroll, end_scroll):
            widget.x = (Window.size[0] * (self.scroll_y - end_scroll)) / (start_scroll - end_scroll)
            if widget.x < 10:
                widget.x = 10
            if widget.x > Window.size[0]:
                widget.x = Window.size[0]

        for widget, pos_list in animation_dict.items():
            animation(widget, pos_list[0], pos_list[1])


class TutorialScreen(Screen):
    def __init__(self, app, **kwargs):
        super(TutorialScreen, self).__init__(**kwargs)
        self.app = app
        self.all_buttons = []

        self.ids.welcome_label.text = "Good " + self.calculate_time_of_day()

        animation_scroll = AnimationScroll(screen=self, size_hint=[1, None],
                                           size=[Window.size[0], Window.size[1] - 125])
        self.add_widget(animation_scroll)

        KivyLabel(grid=animation_scroll.grid, font_size=30, halign="left", size_hint=[1, None], height=5)
        KivyLabel(grid=animation_scroll.grid, font_size=30, halign="left", text="Why should you use this App?",
                  size_hint=[1, None], height=40)
        KivyLabel(grid=animation_scroll.grid, font_size=20, halign="left",
                  text="  > All features are completely free for everyone.", size_hint=[1, None], height=30)
        KivyLabel(grid=animation_scroll.grid, font_size=20, halign="left",
                  text="  > It integrates all your fitness needs in one place.", size_hint=[1, None], height=30)
        KivyLabel(grid=animation_scroll.grid, font_size=20, halign="left",
                  text="  > You can create any custom routine you want.", size_hint=[1, None], height=30)
        KivyLabel(grid=animation_scroll.grid, font_size=30, halign="left", size_hint=[1, None], height=10)
        KivyLabel(grid=animation_scroll.grid, font_size=30, halign="left", text="What this App offers:",
                  size_hint=[1, None], height=40)
        KivyLabel(grid=animation_scroll.grid, font_size=20, halign="left",
                  text="  > Weight Lifting Routines", size_hint=[1, None], height=30)
        KivyLabel(grid=animation_scroll.grid, font_size=30, halign="left", size_hint=[1, None], height=10)
        KivyLabel(grid=animation_scroll.grid, font_size=25, halign="left",
                  text="What this App will offer in the future:",
                  size_hint=[1, None], height=40)
        KivyLabel(grid=animation_scroll.grid, font_size=20, halign="left",
                  text="  > Yoga", size_hint=[1, None], height=30)
        KivyLabel(grid=animation_scroll.grid, font_size=20, halign="left",
                  text="  > Cardio - Running/Cycling", size_hint=[1, None], height=30)
        KivyLabel(grid=animation_scroll.grid, font_size=30, halign="left", size_hint=[1, None], height=10)
        KivyLabel(grid=animation_scroll.grid, font_size=30, halign="left", text="How should you use this App?",
                  size_hint=[1, None], height=40)
        KivyLabel(grid=animation_scroll.grid, font_size=35, halign="left", text="  [u]Gym[/u] ", markup=True,
                  size_hint=[1, None], height=35)
        KivyLabel(grid=animation_scroll.grid, font_size=19, halign="left",
                  text="Make your way to the gym screen, where you can create any routine you want! As you complete routines the reps for each exercise will increase, decrease or stay the same depending on how many reps you perform. You will want the weight to increase, therefore the minimum and maximum rep values decide how high the reps need to go before increasing the weight. Then the reps will go back to the minimum reps",
                  size_hint=[0.9, None], height=230, pos_hint={"x": 0.1})
        KivyButton(grid=animation_scroll.grid, on_release_action=self.home_action,
                   md_bg_color=(1, 143 / 255, 5 / 255, 1), size_hint=[1, None], text="Continue", height=50)

    def home_action(self):
        viewed = True
        write_file("files/viewed.pkl", viewed)
        self.app.screen_action("home_screen", "left", "R/T").start()

    @staticmethod
    def calculate_time_of_day():
        now = datetime.now()
        current_hour = now.strftime("%H")
        if 12 <= int(current_hour) < 18:
            return "afternoon "
        elif int(current_hour) >= 18:
            return "evening "
        else:
            return "morning "
