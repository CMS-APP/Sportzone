from kivy.animation import Animation
from kivy.core.window import Window
from kivy.lang.builder import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivymd.uix.card import MDCard, MDSeparator
from kivymd.uix.label import MDLabel

from files.file_handling import read_file, write_file
from files.gym_files.gym_objects import Exercise, SuperSet
from screens.kivy_objects import KivyButton, KivyLabel, L_GREEN

Builder.load_file("Screens/Screens_kv/gym_screen.kv")


def animate_to(widget, position):  # Function used to reduce use of animation code
    anim = Animation(pos_hint=position, duration=0.2)
    anim.start(widget)


class RoutineCard(MDCard):
    def __init__(self, screen, routine, number, grid, **kwargs):
        super(RoutineCard, self).__init__(**kwargs)
        self.screen, self.number, self.routine = screen, number, routine
        self.size_hint = [None, None]
        self.height = 190
        self.orientation = "vertical"

        KivyLabel(grid=self, font_size=25, halign="left", size_hint=[1, None], height=30, text=f"  {routine.name}")
        self.add_widget(MDSeparator(height=2))

        exercise_number, super_set_number = 0, 0
        for exercise_set in routine.exercises:
            if isinstance(exercise_set, SuperSet):
                super_set_number += 1

        if super_set_number != 0:
            super_set_text = f"{super_set_number} Super Sets"
            if super_set_number == 1:
                super_set_text = "1 Super Set"
            KivyLabel(grid=self, font_size=16, halign="left", size_hint=[1, None], height=30,
                      text=f"    {super_set_text}")
            exercise_number += 1

        for exercise_set in routine.exercises:
            if isinstance(exercise_set, Exercise):
                exercise_number += 1
                if exercise_number <= 4:
                    KivyLabel(grid=self, font_size=16, halign="left", size_hint=[1, None], height=30,
                              text=f"    {exercise_set.base_exercise.name}")
            last_exercise = exercise_set

        if exercise_number > 4:
            more_exercises_text = f"{exercise_number - 4} More Exercises"
            if exercise_number - 4 == 1:
                more_exercises_text = last_exercise.base_exercise.name
            KivyLabel(grid=self, font_size=16, halign="left", size_hint=[1, None], height=30,
                      text=f"    {more_exercises_text}")
        self.add_widget(MDLabel())

        grid.add_widget(self)

    def on_touch_down(self, touch):
        if self.x < touch.pos[0] < self.x + self.width and self.y < touch.pos[1] < self.y + self.height:
            if touch.is_double_tap:
                self.screen.show_routine(self.routine)


class RoutineScroll(ScrollView):
    check_new_pos = None
    displayed_routines = []
    current_button = None

    def __init__(self, screen, grid, **kwargs):
        super(RoutineScroll, self).__init__(**kwargs)
        self.screen = screen
        self.do_scroll = [True, False]
        self.size_hint_x = 1
        self.grid = GridLayout(rows=1, size_hint=[None, None], height=200, spacing=(10, 0), padding=(10, 5))
        self.grid.bind(minimum_width=self.grid.setter('width'))
        self.add_widget(self.grid)
        grid.add_widget(self)

    def add_routines(self, routines):
        self.grid.clear_widgets()
        self.displayed_routines = []
        for i, routine in enumerate(routines):
            self.displayed_routines.append(RoutineCard(screen=self.screen, routine=routine, number=i, grid=self.grid))
        if len(routines) != 0:
            self.current_button = self.displayed_routines[0]
            if len(routines) == 1:
                self.screen.ids.swipe_right_label.text = ""
        self.scroll_label_change()
        self.bind(size=self.update_size)

    def update_size(self, *args):
        for routine_card in self.displayed_routines:
            routine_card.size = [Window.size[0] - 40, 190]

    def on_scroll_stop(self, touch, check_children=True):
        # Function to snap the scroll view to the next routine on the list.
        if self.x < touch.opos[0] < self.x + self.width and self.y < touch.opos[1] < self.y + self.height and len(
                self.displayed_routines) > 1 and self.screen.selected_routine is None:
            # Checks the initial press is the scroll view location
            dx = touch.x - touch.opos[0]  # Finds the direction the release is done in
            if dx < 0 and self.current_button != self.displayed_routines[len(self.displayed_routines) - 1]:
                self.scroll_to(self.displayed_routines[self.displayed_routines.index(self.current_button) + 1])
                self.current_button = self.displayed_routines[self.displayed_routines.index(self.current_button) + 1]
            elif dx > 0 and self.current_button != self.displayed_routines[0]:
                self.scroll_to(self.displayed_routines[self.displayed_routines.index(self.current_button) - 1])
                self.current_button = self.displayed_routines[self.displayed_routines.index(self.current_button) - 1]
            self.scroll_label_change()

    def scroll_label_change(self):
        self.screen.ids.swipe_right_label.text, self.screen.ids.swipe_left_label.text = "", ""
        if len(self.displayed_routines) > 1:
            self.screen.ids.swipe_right_label.text = "Swipe for ->\nmore routines!"
            self.screen.ids.swipe_left_label.text = "<- Swipe for\n  more routines!"
            if self.current_button == self.displayed_routines[-1]:
                self.screen.ids.swipe_right_label.text = ""
            if self.current_button == self.displayed_routines[0]:
                self.screen.ids.swipe_left_label.text = ""

    def on_scroll_move(self, touch):  # Stops the movement of the scroll view during press
        pass


class GymScreen(Screen):
    selected_routine = None
    padding_animation_event = None
    today_routine = None
    all_routines_scroll = None

    def __init__(self, app, **kwargs):
        super(GymScreen, self).__init__(**kwargs)
        self.app = app

    def start(self):  # Function called when gym screen is selected
        routines = read_file("files/gym_files/saved_routines.pkl")
        self.ids.main_scroll.do_scroll_y = True
        self.ids.all_routines_grid.clear_widgets()
        self.ids.routine_label.text, self.ids.routine_label.height = "", 0
        self.ids.double_tap_label.text, self.ids.double_tap_label.height = "", 0
        self.ids.swipe_right_label.text = ""
        self.ids.all_routines_grid.height = 0
        self.ids.scroll_grid.spacing = [0, 0]
        if routines is not None and len(routines) != 0:
            self.all_routines_scroll = RoutineScroll(screen=self, grid=self.ids.all_routines_grid)
            self.all_routines_scroll.add_routines(routines=routines)
            self.ids.all_routines_grid.height = 200
            self.bind(size=self.update_size)
            self.update_size()
            self.ids.routine_label.text, self.ids.routine_label.height = "All available routines", 40
            self.ids.double_tap_label.text, self.ids.double_tap_label.height = "Double tap routine to select!", 10
            self.ids.scroll_grid.spacing = [0, 10]

    def update_size(self, *args):
        for routine_card in self.all_routines_scroll.displayed_routines:
            routine_card.size = [(Window.size[0] * (7 / 8)) - 20, 190]

    def show_routine(self, routine):
        self.ids.routine_display_grid.clear_widgets()
        self.selected_routine = routine

        spare_height = Window.size[1] - 330

        title_grid = GridLayout(cols=2)
        self.ids.routine_display_grid.add_widget(title_grid)
        KivyLabel(grid=title_grid, font_size=(45 - len(routine.name)), halign="left", text=routine.name,
                  size_hint=[1 / 2, None], height=50)
        KivyLabel(grid=title_grid, font_size=(45 - len(routine.name)), halign="left", text=routine.name, size_hint=[1 / 2, None], height=50)
        KivyButton(grid=title_grid, md_bg_color=L_GREEN, font_size=15,
                   on_release_action=self.hide_routine, size_hint=[1 / 2, None], text="Back", height=50)

        set_number, exercise_number = 0, 0

        for exercise_set in routine.exercises:
            if isinstance(exercise_set, SuperSet):
                set_number += 1
            elif isinstance(exercise_set, Exercise):
                exercise_number += 1

        for exercise_set in routine.exercises:

            spare_height -= 11
            if spare_height < 80:
                break
            self.ids.routine_display_grid.add_widget(MDSeparator(height=1, size_hint=[1, None]))
            if isinstance(exercise_set, SuperSet):
                set_text = "set"
                if exercise_set.sets != 1:
                    set_text += "s"
                KivyLabel(grid=self.ids.routine_display_grid, font_size=20, halign="left",
                          text=f"Super Set - {exercise_set.sets} {set_text} for each exercise:", height=20,
                          size_hint=[1, None])
                spare_height -= 40
                set_number -= 1
                for exercise in exercise_set.super_set_exercises:
                    if spare_height < 40:
                        break
                    rep_text = "rep"
                    if exercise.reps != 1:
                        rep_text += "s"
                    KivyLabel(grid=self.ids.routine_display_grid, font_size=20, halign="left", size_hint=[1, None],
                              text=f"    {exercise.base_exercise.name} - {exercise.reps} {rep_text}", height=20)
                    spare_height -= 30
            elif isinstance(exercise_set, Exercise):
                set_text = "set"
                if exercise_set.sets != 1:
                    set_text += "s"
                rep_text = "rep"
                if exercise_set.reps != 1:
                    rep_text += "s"
                KivyLabel(grid=self.ids.routine_display_grid, font_size=20, halign="left", height=20,
                          size_hint=[1, None],
                          text=f"{exercise_set.base_exercise.name} - {exercise_set.sets} {set_text} of {exercise_set.reps} {rep_text}")
                spare_height -= 30
                exercise_number -= 1

        if set_number != 0:
            self.ids.routine_display_grid.add_widget(MDSeparator(height=1, size_hint=[1, None]))
            KivyLabel(grid=self.ids.routine_display_grid, font_size=20, halign="left", height=20,
                      text=f"+{set_number} more super-set")

        if exercise_number != 0:
            self.ids.routine_display_grid.add_widget(MDSeparator(height=1, size_hint=[1, None]))
            exercise_remain_text = "more exercise"
            if exercise_number > 1:
                exercise_remain_text += "s"
            KivyLabel(grid=self.ids.routine_display_grid, font_size=20, halign="left", height=20, size_hint=[1, None],
                      text=f"+{exercise_number} {exercise_remain_text}")

        self.ids.routine_display_grid.add_widget(MDSeparator(height=1))

        action_grid = GridLayout(cols=3, size_hint=[1, None], spacing=[10, 0], height=50)
        self.ids.routine_display_grid.add_widget(action_grid)
        action_button_dict = {"Start Routine": self.start_routine, "Edit Routine": self.edit_routine,
                              "Delete Routine": self.delete_routine}

        for button_text, action in action_button_dict.items():
            KivyButton(grid=action_grid, md_bg_color=L_GREEN, font_size=15,
                       on_release_action=action, size_hint=[1 / 3, None], text=button_text)

        KivyLabel(self.ids.routine_display_grid)

        Animation(x=0, duration=0.2).start(self.ids.routine_display)

    def hide_routine(self):
        Animation(x=self.width + 50, duration=0.2).start(self.ids.routine_display)
        self.selected_routine, self.ids.main_scroll.do_scroll_y = None, True

    def start_routine(self):
        self.app.screen_action("active_gym_screen", "up", action="R/T").start_routine(self.selected_routine)
        self.hide_routine()

    def edit_routine(self):
        self.app.screen_action("create_screen", "left", action="R/T").edit_routine(self.selected_routine)
        self.hide_routine()

    def delete_routine(self):
        routines = read_file("files/gym_files/saved_routines.pkl")
        for routine in routines:
            if self.selected_routine.number == routine.number:
                routines.remove(routine)
                break
        write_file("files/gym_files/saved_routines.pkl", routines)
        self.hide_routine()
        self.start()
