from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import *
from kivy.lang.builder import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel

from files.file_handling import save_new_routine
from files.gym_files.gym_objects import Exercise, SuperSet
from screens.create_screen import GymCard, IntegerInput
from screens.kivy_objects import KivyButton, KivyLabel, L_GREEN

Builder.load_file("Screens/Screens_kv/active_gym_screen.kv")


class ExerciseButton(MDIconButton):
    pressed = False
    reps = None
    moved = False
    long_release = False
    long_release_event = None
    rep_label = None
    icon = "empty"

    def __init__(self, grid, reps, set_row, screen, **kwargs):
        super(ExerciseButton, self).__init__(**kwargs)
        self.max_reps = reps
        self.set_row = set_row
        self.screen = screen
        self.bind(pos=self.update_bg, size=self.update_bg)
        self.normal_ellipse, self.normal_ellipse_border = self.create_ellipse(Color(117 / 255, 1, 133 / 255, 0.5))
        self.pressed_ellipse, self.pressed_ellipse_border = self.create_ellipse(Color(117 / 255, 1, 133 / 255, 1))
        self.canvas.add(self.normal_ellipse)
        self.current_ellipse = self.normal_ellipse_border
        grid.add_widget(self)

    def create_ellipse(self, color):
        ellipse_group = InstructionGroup()
        ellipse_group.add(color)
        ellipse_border = Ellipse()
        ellipse_group.add(ellipse_border)
        return ellipse_group, ellipse_border

    def switch_ellipse(self, new_ellipse_border, new_ellipse, old_ellipse):
        self.canvas.remove(new_ellipse)
        new_ellipse_border.size = [40, 40]
        new_ellipse_border.pos = self.pos[0] + 5, self.pos[1] + 5
        self.canvas.add(new_ellipse)
        self.canvas.remove(old_ellipse)
        return new_ellipse_border

    def create_normal_ellipse(self):
        self.pressed = False
        if self.rep_label is not None:
            self.rep_label.text = ""
        return self.switch_ellipse(self.normal_ellipse_border, self.normal_ellipse, self.pressed_ellipse)

    def create_pressed_ellipse(self):
        self.pressed = True
        with self.canvas.after:
            self.rep_label = MDLabel(text="", size=[50, 50], pos=self.pos, halign="center")
            self.rep_label.font_name = "Geosans"
        return self.switch_ellipse(self.pressed_ellipse_border, self.pressed_ellipse, self.normal_ellipse)

    def update_bg(self, *args):
        self.pressed_ellipse_border.size, self.pressed_ellipse_border.pos = [50, 50], self.pos
        self.normal_ellipse_border.size, self.normal_ellipse_border.pos = [50, 50], self.pos
        if self.pressed:
            self.rep_label.size, self.rep_label.pos = [50, 50], self.pos

    def on_touch_down(self, touch):
        self.long_release_event = None
        self.moved = False
        self.down = True
        self.long_release = False
        if self.x < touch.x < self.x + 50 and self.y < touch.y < self.y + 50 and self.set_row.rep_change and not self.screen.change_weight:
            if self.set_row.show_rest_event is not None:
                self.set_row.show_rest_event.cancel()
            self.long_release_event = Clock.schedule_once(self.on_long_release, 0.275)
            if self.pressed:
                self.current_ellipse = self.pressed_ellipse_border
            else:
                self.current_ellipse = self.normal_ellipse_border
            Animation(size=[40, 40], pos=[self.pos[0] + 5, self.pos[1] + 5], duration=0.15).start(self.current_ellipse)

    def on_touch_up(self, touch):
        if self.long_release_event is not None:
            self.long_release_event.cancel()
        if self.current_ellipse is not None and not self.moved and self.set_row.rep_change and not self.screen.change_weight:
            if self.x < touch.x < self.x + 50 and self.y < touch.y < self.y + 50:
                if not self.long_release:
                    if self.pressed:
                        if self.reps != 0:
                            self.reps -= 1
                            self.set_row.show_rest(self)
                        else:
                            self.reps = None
                            self.current_ellipse = self.create_normal_ellipse()
                    else:
                        self.reps = self.max_reps
                        self.current_ellipse = self.create_pressed_ellipse()
                        self.set_row.show_rest(self)
                else:
                    self.reps = None
                    self.current_ellipse = self.create_normal_ellipse()
                self.set_row.main_grid.rest_complete(None)
                Animation(size=[50, 50], pos=self.pos, duration=0.15).start(self.current_ellipse)
                self.update_text()

    def on_touch_move(self, touch, *args):
        if self.current_ellipse is not None:
            if not self.x < touch.x < self.x + 50 or not self.y < touch.y < self.y + 50:
                self.moved = True
                Animation(size=[50, 50], pos=self.pos, duration=0.15).start(self.current_ellipse)

    def on_long_release(self, *args):
        self.long_release = True

    def update_text(self):
        if self.reps is not None:
            self.rep_label.text = f"{self.reps}"


class ExerciseRow(GridLayout):
    rep_change = True
    show_rest_event = None
    rest_rectangle = None
    total_rest_time = 0

    def __init__(self, sets, reps, rest_time, main_grid, screen, **kwargs):
        super(ExerciseRow, self).__init__(**kwargs)
        self.cols = sets
        self.sets = sets
        self.reps = reps
        self.rest_time = rest_time
        self.main_grid = main_grid
        self.screen = screen
        self.size_hint = [1, None]
        self.all_buttons = []

        with self.canvas.after:
            Color(192 / 255, 192 / 255, 192 / 255, 1)
            self.rest_rectangle = Rectangle(rectangle=(0, 0, self.width, self.height))
            self.rest_label = MDLabel(text="", pos=[self.pos[0], self.pos[1] + 20 + self.height], size=[self.width, 1])
            self.rest_label.font_name, self.rest_label.font_size, self.rest_label.halign = "Geosans", 20, "center"

        self.bind(pos=self.update_bg, size=self.update_bg)

        for i in range(self.sets):
            set_button = ExerciseButton(self, self.reps, self, self.screen)
            set_button.md_bg_color = (1, 1, 1, 1)
            set_button.size_hint = [None, None]
            self.all_buttons.append(set_button)

    def show_rest(self, pressed_button):
        if self.show_rest_event is not None:
            self.show_rest_event.cancel()
            self.show_rest_event = None

        if self.all_buttons.index(pressed_button) != len(self.all_buttons) - 1:
            if not self.all_buttons[self.all_buttons.index(pressed_button) + 1].pressed:
                self.total_rest_time = self.rest_time + (
                        (pressed_button.max_reps - pressed_button.reps) / pressed_button.max_reps) * self.rest_time
                self.show_rest_event = Clock.schedule_once(self.animate_rest, 2)

    def update_bg(self, *args):
        for button in self.all_buttons:
            button.size = [50, 50]

        space = self.width - 50 * self.sets
        space_a = space / (self.sets * 2)
        self.spacing = [space_a * 2 + 5, 0]
        self.padding = [space_a - 5, 0]

        if self.rest_rectangle is not None:
            self.rest_rectangle.size = [self.width, 1]
            self.rest_rectangle.pos = self.pos[0], self.pos[1] + self.height + 5
            self.rest_label.size = [self.width, 1]
            self.rest_label.pos = self.pos[0], self.pos[1] + self.height + 5

    def animate_rest(self, _):
        Animation(size=[self.width, self.height + 5], pos=[self.pos[0], self.pos[1]], duration=0.25).start(
            self.rest_rectangle)
        Animation(size=[self.width, self.height + 5], pos=[self.pos[0], self.pos[1]], duration=0.25).start(
            self.rest_label)
        Clock.schedule_once(lambda x: self.change_text(f"Nice One. Rest for {round(self.total_rest_time)} seconds!"),
                            0.1)
        Clock.schedule_once(self.reset_rest, 2.75)

    def reset_rest(self, _):
        Animation(size=[self.width, 1], pos=[self.pos[0], self.pos[1] + self.height + 5], duration=0.25).start(
            self.rest_rectangle)
        Animation(size=[self.width, 1], pos=[self.pos[0], self.pos[1] + self.height + 5], duration=0.25).start(
            self.rest_label)
        Clock.schedule_once(lambda x: self.change_text(""), 0.1)
        self.main_grid.start_rest(self.total_rest_time)

    def change_text(self, label_text):
        self.rest_label.text = label_text


class ExerciseGrid(GymCard):
    rest_rectangle = None
    rest_animation = None
    total_rest_time = 0

    def __init__(self, active_exercise, screen, **kwargs):
        super(ExerciseGrid, self).__init__(**kwargs)
        self.active_exercise = active_exercise
        self.base_exercise = active_exercise.base_exercise
        self.reps = active_exercise.reps
        self.sets = active_exercise.sets
        self.weight = active_exercise.weight
        self.rest_time = active_exercise.rest_time
        self.main_grid = GridLayout(cols=1)
        self.screen = screen
        self.height = 190
        grid = GridLayout(cols=1, padding=[10, 10], spacing=[0, 10], size_hint=[1, None])

        title_grid = GridLayout(cols=2, size_hint=[1, None], height=40)
        grid.add_widget(title_grid)
        KivyButton(grid=title_grid, md_bg_color=L_GREEN, font_size=15, on_release_action=None, size_hint=[1 / 2, None],
                   height=40, text=f"{self.base_exercise.name}")
        self.rest_title = KivyLabel(title_grid, font_size=25, halign="right", size_hint=[1 / 2, None], height=40)

        exercise_info_grid = GridLayout(cols=2, size_hint=[1, None], height=40)

        rep_text = f"{self.sets} sets of {self.reps} reps"

        if self.base_exercise.each_side:
            rep_text += " each side"

        weight_button = KivyButton(grid=exercise_info_grid, md_bg_color=L_GREEN, font_size=15, on_release_action=None,
                                   size_hint=[1 / 2, None], height=40, text=f"{self.weight} kg")
        weight_button.bind(on_release=lambda weight_button: screen.change_weight_action(weight_button))

        KivyLabel(grid=exercise_info_grid, font_size=30, halign="center", size_hint=[1 / 2, None], height=40,
                  text=rep_text)

        grid.add_widget(exercise_info_grid)

        self.exercise_row = ExerciseRow(self.sets, self.reps, self.rest_time, self, self.screen)
        grid.add_widget(self.exercise_row)

        self.add_widget(grid)

    def start_rest(self, total_rest_time):
        self.total_rest_time = total_rest_time
        self.rest_animation = Animation(duration=self.total_rest_time)
        self.rest_animation.bind(on_progress=self.rest_progress, on_complete=self.rest_complete)
        self.rest_animation.start(self)

    def rest_progress(self, *args):
        # While the animation is going the rest timer is shown to the user
        prog = args[2]
        if self.total_rest_time != 0:
            self.rest_title.text = f"Rest: {str(round((1 - prog) * self.total_rest_time))}s"

    def rest_complete(self, *args):
        # After the animation finished the next button shows the current reps again
        if self.rest_animation is not None:
            self.rest_title.text = ""


class SuperSetRow(GridLayout):
    show_rest_event = None
    rep_change = True
    total_rest_time = 0

    def __init__(self, grid, rep_data, rest_time, main_grid, number, **kwargs):
        super(SuperSetRow, self).__init__(**kwargs)
        self.cols = 2
        self.number = number
        self.rep_data = rep_data
        self.rest_time = rest_time
        self.main_grid = main_grid
        self.size_hint = [1, None]
        self.height = 70
        self.all_buttons = []
        print(rep_data)
        for i in range(len(rep_data)):
            set_button = ExerciseButton(self, rep_data[i], self, main_grid.screen)
            set_button.md_bg_color = (1, 1, 1, 1)
            set_button.size_hint = [None, None]
            self.all_buttons.append(set_button)

        with self.canvas.after:
            Color(192 / 255, 192 / 255, 192 / 255, 1)
            self.rest_rectangle = Rectangle(rectangle=(0, 0, self.width, self.height))
            self.rest_label = MDLabel(text="", pos=[self.pos[0], self.pos[1] + 20 + self.height], size=[self.width, 1])
            self.rest_label.font_name, self.rest_label.font_size, self.rest_label.halign = "Geosans", 20, "center"

        self.bind(pos=self.update_bg, size=self.update_bg)
        grid.add_widget(self)

    def update_bg(self, *args):
        space = self.width - 50 * len(self.rep_data)
        space_a = space / (len(self.rep_data) * 2)
        self.spacing = [space_a * 2 + 5, 0]
        self.padding = [space_a - 5, 0]
        for i in range(len(self.all_buttons)):
            self.all_buttons[i].size = [50, 50]
        self.rest_rectangle.size = [self.width, 1]
        self.rest_rectangle.pos = self.pos[0], self.pos[1] + self.height + 5
        self.rest_label.size = [self.width, 1]
        self.rest_label.pos = self.pos[0], self.pos[1] + self.height + 5

    def show_rest(self, pressed_button):
        if self.show_rest_event is not None:
            self.show_rest_event.cancel()

        self.finish = True
        for button in self.all_buttons:
            if not button.pressed:
                self.finish = False
                break
        if self.finish and self.number != (self.main_grid.sets - 1):
            self.show_rest_event = Clock.schedule_once(self.animate_rest, 2)

    def animate_rest(self, _):
        self.rep_change = False
        self.total_rest_time = self.rest_time
        for button in self.all_buttons:
            self.total_rest_time += (((button.max_reps - button.reps) / button.max_reps) * self.rest_time)
        Animation(size=[self.width, self.height + 10], pos=[self.pos[0], self.pos[1] - 5], duration=0.25).start(
            self.rest_rectangle)
        Animation(size=[self.width, self.height + 10], pos=[self.pos[0], self.pos[1] - 5], duration=0.25).start(
            self.rest_label)
        Clock.schedule_once(lambda x: self.change_text(f"Nice One. Rest for {round(self.total_rest_time)} seconds!"),
                            0.1)
        Clock.schedule_once(self.reset_rest, 2.75)

    def reset_rest(self, _):
        self.rep_change = True
        Animation(size=[self.width, 1], pos=[self.pos[0], self.pos[1] + self.height + 5], duration=0.25).start(
            self.rest_rectangle)
        Animation(size=[self.width, 1], pos=[self.pos[0], self.pos[1] + self.height + 5], duration=0.25).start(
            self.rest_label)
        Clock.schedule_once(lambda x: self.change_text(""), 0.1)
        self.main_grid.start_rest(self.total_rest_time)

    def change_text(self, label_text):
        self.rest_label.text = label_text


class SuperSetGrid(GymCard):
    rest_animation = None

    def __init__(self, active_super_set, screen, **kwargs):
        super(SuperSetGrid, self).__init__(**kwargs)
        self.active_exercises = active_super_set.super_set_exercises
        self.sets = active_super_set.sets
        self.rest_time = active_super_set.rest_time
        self.screen = screen
        self.height = 225 + 60 * self.sets
        self.all_rows = []
        grid = GridLayout(cols=1, size_hint=[1, None], height=250 + 60 * self.sets, spacing=[0, 10], padding=[10, 10])

        title_grid = GridLayout(cols=2, size_hint=[1, None], height=40)

        KivyLabel(grid=title_grid, font_size=30, halign="center", size_hint=[1 / 2, None], text="Super-Set", height=40)
        self.rest_title = KivyLabel(grid=title_grid, font_size=30, halign="right", size_hint=[1 / 2, None], height=40)
        grid.add_widget(title_grid)

        exercise_button_grid = GridLayout(rows=1, cols=len(self.active_exercises), size_hint=[1, None],
                                          height=50, spacing=[10, 0])

        exercise_weight = GridLayout(rows=1, cols=len(self.active_exercises), size_hint=[1, None],
                                     height=30, spacing=[10, 0])

        exercise_reps = GridLayout(rows=1, cols=len(self.active_exercises), size_hint=[1, None],
                                   height=30, spacing=[10, 0])

        rep_data = []
        weight_data = []

        for exercise in self.active_exercises:
            rep_data.append(exercise.reps)
            weight_data.append(exercise.weight)

            new_name = []
            for word in exercise.base_exercise.name.split(" "):
                new_name.append(word.capitalize())

            button = KivyButton(grid=exercise_button_grid, md_bg_color=L_GREEN, font_size=15,
                                size_hint=[1 / len(self.active_exercises), None], text="\n".join(new_name), height=30)
            button.bind(on_release=lambda exercise_button: self.exercise_info(exercise_button.exercise))

            button = KivyButton(grid=exercise_weight, md_bg_color=L_GREEN, font_size=15,
                                size_hint=[1 / len(self.active_exercises), None], text=f"{exercise.weight} kg",
                                height=30)
            button.exercise = exercise
            button.bind(on_release=lambda weight_button: screen.change_weight_action(weight_button))

            rep_text = f"{exercise.reps} reps"
            if exercise.base_exercise.each_side:
                rep_text += " each side"

            KivyLabel(grid=exercise_reps, font_size=20, halign="center",
                      size_hint=[1 / len(self.active_exercises), None], height=30, text=rep_text)

        grid.add_widget(exercise_button_grid)
        grid.add_widget(exercise_weight)
        grid.add_widget(exercise_reps)
        self.add_widget(grid)
        active_set_grid = GridLayout(rows=self.sets * 2, size_hint=[1, None], padding=[0, 0])
        grid.add_widget(active_set_grid)

        for i in range(self.sets):
            KivyLabel(grid=active_set_grid, halign="center", size_hint=[1, None], height=10)
            row = SuperSetRow(active_set_grid, rep_data, self.rest_time, self, i)
            self.all_rows.append(row)

    def exercise_info(self, exercise):
        if not self.screen.change_weight:
            print(exercise.name)

    def start_rest(self, total_rest_time):
        self.total_rest_time = total_rest_time
        self.rest_animation = Animation(duration=self.total_rest_time)
        self.rest_animation.bind(on_progress=self.rest_progress, on_complete=self.rest_complete)
        self.rest_animation.start(self)

    def rest_progress(self, *args):
        # While the animation is going the rest timer is shown to the user
        prog = args[2]
        if self.total_rest_time != 0:
            self.rest_title.text = f"Rest: {str(round((1 - prog) * self.total_rest_time))}s"

    def rest_complete(self, *args):
        # After the animation finished the next button shows the current reps again
        if self.rest_animation is not None:
            self.rest_title.text = ""
            self.rest_animation.stop_all(self)
            self.rest_animation = None


class ActiveGymScreen(Screen):
    change_weight = False
    weight_canvas = None
    selected_exercise = None
    weight_input = None
    info_label = None
    save_button = None
    routine_changed = False
    previous_routine = None

    def __init__(self, app, **kwargs):
        super(ActiveGymScreen, self).__init__(**kwargs)
        self.app = app

    def start_routine(self, routine):
        self.ids.active_routine_grid.clear_widgets()
        self.ids.title.text = routine.name
        self.all_grids = []
        self.routine = routine

        if self.weight_canvas is not None:
            self.canvas.remove(self.weight_canvas)

        for set in self.routine.exercises:
            if isinstance(set, SuperSet):
                grid = SuperSetGrid(set, self)
                self.all_grids.append(grid)
                self.ids.active_routine_grid.add_widget(grid)
            elif isinstance(set, Exercise):
                grid = ExerciseGrid(set, self)
                self.all_grids.append(grid)
                self.ids.active_routine_grid.add_widget(grid)

        KivyButton(grid=self.ids.active_routine_grid, md_bg_color=L_GREEN, font_size=15,
                   on_release_action=self.finish_routine, size_hint=[1, None], height=100, text="Finish Routine")

    def change_weight_action(self, exercise_button, *args):
        if not self.change_weight:
            self.ids.main_scroll.do_scroll_y = False
            self.change_weight = True
            self.weight_canvas = InstructionGroup()
            self.weight_canvas.add(Color(0, 0, 0, 0.4))
            self.background = Rectangle(rectangle=(0, 0, 0, 0))
            self.weight_canvas.add(self.background)
            self.weight_canvas.add(Color(1, 1, 1, 1))
            self.weight_rect = Rectangle(rectangle=(0, 0, 0, 0))
            self.weight_canvas.add(self.weight_rect)
            self.canvas.add(self.weight_canvas)
            self.weight_input = IntegerInput(self, "Weight(kg)", 0, 500, True, exercise_button.exercise.weight, None,
                                             size_hint=[1 / 3, None], height=100,
                                             pos_hint={"x": 1 / 3, "center_y": 4 / 9})
            label_text = ""
            if exercise_button.exercise.base_exercise.equipment == "Dumbbell":
                label_text = "The weight for each dumbbell. "
            elif exercise_button.exercise.base_exercise.equipment == "Barbell":
                label_text = "The total weight of the barbell (usually 20kg/45lb) and the plates on either side"

            self.info_label = KivyLabel(grid=self, font_size=20, halign="center", size_hint=[3 / 4, 1 / 3],
                                        pos_hint={"center_x": 1 / 2, "top": 3 / 4}, color=(0, 0, 0, 1), text=label_text)

            self.save_button = KivyButton(grid=self, md_bg_color=L_GREEN, font_size=25, on_release_action=None,
                                          size_hint=[9 / 20, 1 / 10],
                                          pos_hint={"x": 11 / 40, "y": 11 / 40}, text="Save Weight")
            self.save_button.bind(on_release=lambda _: self.save_weight(self.weight_input.text, exercise_button))
            self.update_bg()
            self.bind(size=self.update_bg, pos=self.update_bg)
            self.bind(on_touch_up=self.weight_touch_up)

    def update_bg(self, *args):
        self.background.size, self.background.pos = [self.width, self.height], [0, 0]
        self.weight_rect.size, self.weight_rect.pos = [self.width * 3 / 4, self.height / 2], [self.width / 8,
                                                                                              self.height / 4]

    def weight_touch_up(self, *args):
        if not self.width / 4 < args[1].x < self.width * (3 / 4) or not self.height / 4 < args[1].y < self.height * (
                3 / 4):
            self.unbind(on_touch_up=self.weight_touch_up)

    def change_weight_bool(self, *args):
        self.ids.main_scroll.do_scroll_y = True
        self.change_weight = False

    def save_weight(self, exercise_text, exercise_button):
        self.hide_weight_change()
        try:
            float(exercise_text)
        except ValueError:
            return
        exercise_button.text = f"{float(exercise_text)} kg"

        self.previous_routine = self.routine

        for exercise_set in self.routine.exercises:
            if isinstance(exercise_set, SuperSet):
                for exercise in exercise_set.super_set_exercises:
                    if exercise.base_exercise.number == exercise_button.exercise.base_exercise.number:
                        pass
                        exercise.weight = float(exercise_text)
            elif isinstance(exercise_set, Exercise):
                if exercise_set.base_exercise.number == exercise_button.exercise.base_exercise.number:
                    pass
                    exercise_set.weight = float(exercise_text)

        save_new_routine("files/gym_files/saved_routines.pkl", [self.routine.name, self.routine.exercises],
                         self.previous_routine)
        self.routine_changed = True

    def finish_routine(self):
        self.previous_routine = self.routine
        all_data = []
        for set_of_exercises in self.all_grids:
            if isinstance(set_of_exercises, SuperSetGrid):
                superset_data = ["Superset", [set_of_exercises.sets, set_of_exercises.rest_time], []]
                for active_exercise in set_of_exercises.active_exercises:
                    superset_data[2].append([active_exercise, []])
                for row in set_of_exercises.all_rows:
                    for i in range(len(row.all_buttons)):
                        superset_data[2][i][1].append(row.all_buttons[i].reps)
                all_data.append(superset_data)
            elif isinstance(set_of_exercises, ExerciseGrid):
                exercise_data = ["Exercise", set_of_exercises.active_exercise, []]
                for button in set_of_exercises.exercise_row.all_buttons:
                    exercise_data[2].append(button.reps)
                all_data.append(exercise_data)

        def progression_calculator(exercise, reps_completed, total_reps):
            def weight_calculator(weight, progression):
                if 0.0 <= float(weight) < 10.0:
                    weight = round(weight) + progression * 1
                    if weight < 0.0:
                        weight = 0.0
                    elif weight > 10.0:
                        weight = 10.0

                elif 10.0 <= float(weight) < 20.0:
                    weight = round(weight) + progression * 2
                    if weight < 10.0:
                        weight = 10.0
                    elif weight > 20.0:
                        weight = 20.0

                elif float(weight) >= 20.0:
                    if exercise.base_exercise.equipment == "Dumbbell":
                        weight += 2.0
                    elif exercise.base_exercise.equipment == "Barbell" or "Body-weight":
                        weight += 2.5
                return float(weight)

            progress = 0

            if (reps_completed / total_reps) * 100 == 100.0:
                progress = 1
            elif 75.0 <= (reps_completed / total_reps) * 100 < 100.0:
                progress = 0
            elif 0.0 <= (reps_completed / total_reps) * 100 < 75.0:
                progress = -1

            exercise.reps = exercise.reps + progress

            if exercise.reps > exercise.max_reps:
                exercise.weight = weight_calculator(exercise.weight, 1)
                exercise.reps = exercise.min_reps
            elif exercise.reps < exercise.min_reps:
                exercise.weight = weight_calculator(exercise.weight, -1)
                exercise.reps = exercise.max_reps
            return exercise

        new_routine_exercises = []
        for data in all_data:
            if data[0] == "Superset":
                new_exercises = []
                for exercise in data[2]:
                    reps_completed = 0
                    for active_reps in exercise[1]:
                        if active_reps is None:
                            active_reps = 0
                        reps_completed += active_reps
                    new_exercises.append(
                        progression_calculator(exercise[0], reps_completed, exercise[0].reps * data[1][0]))
                new_routine_exercises.append(SuperSet(new_exercises, [data[1][0], data[1][1]]))

            elif data[0] == "Exercise":
                reps_completed = 0
                for active_reps in data[2]:
                    if active_reps is None:
                        active_reps = 0
                    reps_completed += active_reps
                new_routine_exercises.append(
                    progression_calculator(data[1], reps_completed, data[1].reps * data[1].sets))
        save_new_routine("files/gym_files/saved_routines.pkl", [self.routine.name, new_routine_exercises],
                         self.previous_routine)

        screen = self.app.screen_action("gym_screen", "down", "R/T")
        screen.start()

    def hide_weight_change(self):
        self.unbind(size=self.update_bg, pos=self.update_bg)
        if self.weight_canvas is not None:
            self.canvas.remove(self.weight_canvas)
            self.weight_canvas = None
        self.change_weight = False
        if self.weight_input is not None:
            self.remove_widget(self.weight_input)
        if self.info_label is not None:
            self.remove_widget(self.info_label)
        if self.save_button is not None:
            self.remove_widget(self.save_button)
        Clock.schedule_once(self.change_weight_bool, 0.5)

    def gym_screen(self):
        if not self.change_weight:
            screen = self.app.screen_action("gym_screen", "down", "R/T")
            screen.start()

    def home_screen(self):
        if not self.change_weight:
            self.app.screen_action(selected_screen_name="home_screen", direction="down", action="R/T").start()

    def open_nav_drawer(self):
        if not self.change_weight:
            self.ids.nav_drawer.set_state()


def progression(all_grids):
    pass
