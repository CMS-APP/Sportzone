import re

from kivy.animation import Animation
from kivy.core.window import Window
from kivy.graphics import Rectangle, Color
from kivy.lang.builder import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivymd.uix.button import MDFlatButton
from kivymd.uix.card import MDCard, MDSeparator
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.textfield import MDTextField

from files.file_handling import save_new_routine
from files.gym_files.gym_objects import get_exercises, SuperSetExercise, Exercise, SuperSet
from screens.kivy_objects import KivyButton, KivyLabel, L_GREEN

Builder.load_file("Screens/Screens_kv/create_screen.kv")

""" Before undertaking the task of reviewing this code for the creation screen. 
There is some 'Fitness' related terminology you should understand before moving forward.

Definitions:
    Weight: 
        - The mass in kilograms(kg) or pounds(lb)

    Reps:
        - The number of repetitions of a specific exercise
        - Done one after another without any rest
        - Usually between 1 - 20
        - If using dumbbells (Weights on each arm) the reps are for each arm
        
    Sets:
        - The number of times the reps is executed for each exercise
        - Usually between 2 - 6 
        - Sometimes the number of reps of each set decreases after each set
    
    Rest Time:
        - Between each set the person executing the exercise rests for a certain period of time
        - If the user cannot complete all the reps of a certain set - the user should rest for longer then usual

    Exercise: 
        - Is one repeated form of the same movement using weights or the body
        - Mainly used to build muscle and gain strength of certain areas of the human body
        - All sets are done one after another with rests in between
        - Exercises include:
            - Body-weight
            - Dumbbell
            - Barbell
            - Machine
            - Band
            - Kettle-bell
        - Warning: Before performing any exercise. The user should discuss with a doctor or certified personal trainer
        which exercise should and should not be performed
        
    Super Set:
        - Move from one exercise to a separate exercise without taking a break for rest in between the two exercises.
        - The number of sets remains constant for each exercise
        - Rest is only taken after one set for each exercise is complete
        - Usually between 2 - 3 exercises
        
    Routine:
        - A collection of exercises and super sets
        - Rest is taken between each Exercise/ Super Set

    Progression:
        - After each routine is finished, the next routine needs to change based of the data collected from the previous
        routines and ones before. This will allow the user to progress in the best possible way. Depending on their
        goals. """

sorted_exercises = get_exercises()


class CustomOneLineIconListItem(OneLineIconListItem):
    # Class used for each exercise in the search bar
    def __init__(self, selected_exercise, add_exercise_action, **kwargs):
        super(CustomOneLineIconListItem, self).__init__(**kwargs)
        self.selected_exercise = selected_exercise
        self.add_exercise_action = add_exercise_action
        self.text = selected_exercise.name
        self.size_hint_y = None

    def add_exercise(self):
        self.add_exercise_action(self.selected_exercise)


class MusclePickButton(MDFlatButton):
    # Class used for each muscle group for the muscle selection card
    def __init__(self, muscle, release_action, **kwargs):
        super(MusclePickButton, self).__init__(**kwargs)
        self.size_hint = [1 / 2, 2 / 7]
        self.text_color = (0, 0, 0, 1)
        self.md_bg_color = L_GREEN
        self.font_size = 20
        self.text = muscle
        self.muscle = muscle
        self.release_action = release_action

    def on_release(self):
        self.release_action(self.muscle)


class GymCard(MDCard):
    def __init__(self, **kwargs):
        super(GymCard, self).__init__(**kwargs)
        self.size_hint = [1, None]
        self.orientation = "vertical"
        with self.canvas:
            Color(117 / 255, 1, 133 / 255)
            self.border = Rectangle(rectangle=(0, 0, 200, 200))
            Color(1, 1, 1, 1)
            self.back_rect = Rectangle(rectangle=(0, 0, 200, 200))
        self.bind(pos=self.update_bg, size=self.update_bg)

    def update_bg(self, *args):
        self.border.pos, self.border.size = self.pos, self.size
        self.back_rect.pos, self.back_rect.size = [self.pos[0] + 2, self.pos[1] + 2], [self.size[0] - 4,
                                                                                       self.size[1] - 4]


class ExerciseInfoCard(GymCard):
    add = False
    exercise = None

    def __init__(self, grid, routine, **kwargs):
        super(ExerciseInfoCard, self).__init__(**kwargs)
        self.grid = grid
        self.routine = routine
        grid.add_widget(self)

    def add_exercise_info(self, exercise, show_add_button):
        self.clear_widgets()
        self.add = True
        self.exercise = exercise
        self.padding, self.spacing = [10, 10], [0, 5]

        KivyLabel(self, 30, "center", text=f"{exercise.name} info", size_hint=[1, 1 / 10])
        self.add_widget(MDSeparator(height=2))
        KivyLabel(self, 25, "center", text=f"{exercise.name} info coming soon!", size_hint=[1, 8 / 10])

        button_hint = [1, None]
        if show_add_button:
            button_hint = [1 / 2, None]

        grid = GridLayout(cols=2, size_hint=[1, None], spacing=[10, 0])
        KivyButton(grid, L_GREEN, 25, self.remove_card, size_hint=button_hint, text="Cancel")
        if show_add_button:
            KivyButton(grid, L_GREEN, 25, self.add_exercise, button_hint, text="Add Exercise")
        self.add_widget(grid)

    def remove_card(self):
        self.add = False
        Animation(y=self.grid.height + 50, duration=0.2).start(self)

    def add_exercise(self):
        if self.add:
            self.routine.add_exercise(self.exercise)
            self.add = False
            self.remove_card()


class IntegerInput(MDTextField):
    # Class only allows integer values input unless 'point_five' is True
    def __init__(self, grid, name, min_value, max_value, point_five, start_number, routine_grid, **kwargs):
        super(IntegerInput, self).__init__(**kwargs)
        self.min_value, self.max_value, self.point_five = min_value, max_value, point_five
        self.routine_grid, self.text = routine_grid, str(start_number)
        self.size_hint = [1 / 3, None]
        self.font_name = "Geosans"
        self.font_size = 20
        self.color_mode = 'custom'
        self.line_color_focus, self.line_color_normal = (0, 0, 0, 1), (0, 0, 0, 1)
        self.current_hint_text_color = (0, 0, 0, 1)
        self.hint_text = name
        grid.add_widget(self)

    def insert_text(self, substring, from_undo=False):
        prev_text = self.text
        if self.point_five:
            if "." in self.text:
                pattern = re.compile('[05]')
                if self.text.index(".") != len(self.text) - 1:
                    substring = ""
            else:
                pattern = re.compile('[0-9.]')
        else:
            pattern = re.compile('[0-9]')
        if pattern.match(substring) is None:
            substring = ""
        super(IntegerInput, self).insert_text(substring, from_undo=from_undo)
        try:
            float(self.text)
        except ValueError:
            self.text = prev_text
            return
        if not self.min_value <= float(self.text) <= self.max_value:
            self.text = prev_text
        self.routine_grid.check_text_input()

    def do_backspace(self, from_undo=False, mode='bkspc'):
        self.text = self.text[:-1]
        self.routine_grid.check_text_input()


class ExerciseGrid(GymCard):
    # Class used to display the exercise text inputs
    def __init__(self, selected_exercise, routine_grid, exercise_data=None, **kwargs):
        super(ExerciseGrid, self).__init__(**kwargs)
        self.selected_exercise = selected_exercise
        self.routine_grid = routine_grid
        self.height = 175

        # Grid for the exercise name and 'Delete' buttons
        name_grid = GridLayout(cols=2, size_hint_x=1, spacing=[10, 0], padding=[10, 0])
        KivyButton(grid=name_grid, md_bg_color=L_GREEN, on_release_action=self.exercise_info,
                   font_size=20, size_hint=[1 / 2, None], text=selected_exercise.name, height=50)

        KivyButton(grid=name_grid, md_bg_color=L_GREEN, on_release_action=self.delete_exercise,
                   font_size=20, size_hint=[1 / 2, None], text="Delete", height=50)
        self.add_widget(name_grid)

        start_numbers = [8, 1, 20, 4, 0, 90]
        if exercise_data is not None:
            start_numbers = exercise_data

        self.all_text_inputs = []
        # Using the 'IntegerInput' class to represent the text inputs for the different parameters
        text_inputs = [["Reps", "Min Reps", "Max Reps", "Sets", "Weight (kg)", "Rest Time (s)"],
                       [1, 1, 1, 1, 0, 1],
                       [21, 21, 21, 7, 500, 500],
                       [False, False, False, False, True, False],
                       start_numbers]

        input_grid = GridLayout(cols=3, size_hint_x=1, spacing=[25, 0], padding=[10, 0])
        for i in range(len(text_inputs[0])):
            text_input = IntegerInput(input_grid, text_inputs[0][i], text_inputs[1][i], text_inputs[2][i],
                                      text_inputs[3][i], text_inputs[4][i], self.routine_grid)
            self.all_text_inputs.append(text_input)
        self.add_widget(input_grid)

    def exercise_info(self):  # If you press the exercise name button - Future version will include more exercise info
        self.routine_grid.screen.show_exercise_info(self.selected_exercise, False)

    def delete_exercise(self):  # If you press the 'Delete' button, the exercise is removed from the routine
        self.routine_grid.delete_set(self)


class SuperSetExerciseGrid(GridLayout):
    # Class to represent the exercise inside a super set grid
    def __init__(self, selected_exercise, super_set_grid, exercise_data=None, **kwargs):
        super(SuperSetExerciseGrid, self).__init__(**kwargs)
        self.selected_exercise = selected_exercise
        self.super_set_grid = super_set_grid
        self.cols, self.size_hint_x = 1, 1
        self.spacing, self.all_text_inputs = [25, 0], []
        self.exercise_grid = GridLayout(cols=2, size_hint_x=1, spacing=[10, 0])
        KivyButton(grid=self.exercise_grid, md_bg_color=L_GREEN, font_size=20,
                   on_release_action=self.exercise_info, size_hint=[1 / 2, None], text=selected_exercise.name)
        KivyButton(grid=self.exercise_grid, md_bg_color=L_GREEN, font_size=20,
                   on_release_action=self.delete_exercise, size_hint=[1 / 2, None], text="Delete Exercise")
        self.add_widget(self.exercise_grid)
        if exercise_data is not None:
            exercise_numbers = exercise_data
        else:
            exercise_numbers = [8, 1, 20, 0]

        # Add the non initial parameters to the exercise grid
        text_inputs_data = [["Reps", "Min Reps", "Max Reps", "Weight (kg)"],
                            [1, 1, 1, 0],
                            [21, 21, 21, 500],
                            [False, False, False, True],
                            exercise_numbers]
        self.text_input_grid = GridLayout(cols=2, size_hint_x=1, spacing=[10, 5], padding=[10, 5])
        for i in range(4):
            text_input = IntegerInput(self.text_input_grid, text_inputs_data[0][i], text_inputs_data[1][i],
                                      text_inputs_data[2][i], text_inputs_data[3][i],
                                      text_inputs_data[4][i], self.super_set_grid)
            self.all_text_inputs.append(text_input)
        self.add_widget(self.text_input_grid)

    def exercise_info(self):
        # Display the exercise info to the user
        self.super_set_grid.routine_grid.screen.show_exercise_info(self.selected_exercise, False)

    def delete_exercise(self):
        # Delete the exercise from the super set
        self.super_set_grid.delete_exercise(self)


class SuperSetGrid(GymCard):
    add_exercise_button = None
    initial_text_input_grid = None
    exercise_grid = None

    # Class which shows the super set on the create routine screen
    def __init__(self, routine_grid, **kwargs):
        super(SuperSetGrid, self).__init__(**kwargs)
        self.routine_grid = routine_grid
        self.height = 70
        self.main_grid = GridLayout(cols=1, size_hint_x=1, padding=[10, 10], spacing=[0, 10])
        self.all_text_inputs, self.all_exercises = [], []

        name_grid = GridLayout(cols=2, size_hint_x=1, spacing=[10, 0])
        KivyLabel(grid=name_grid, font_size=30, size_hint=[1 / 2, None], text="Super-Set", height=50)
        KivyButton(grid=name_grid, md_bg_color=L_GREEN, font_size=20,
                   on_release_action=self.delete_super_set, size_hint=[1 / 2, None],
                   text="Delete Super Set")

        self.main_grid.add_widget(name_grid)
        self.insert_add_exercise_button()
        self.add_widget(self.main_grid)

    def insert_add_exercise_button(self):
        # Function to add the 'Add Exercise' button to the super set grid
        if len(self.all_exercises) < 3 and self.add_exercise_button is None:
            self.height += 60
            self.add_exercise_button = KivyButton(grid=self.main_grid, md_bg_color=L_GREEN, font_size=25,
                                                  on_release_action=self.insert_muscle_pick, size_hint=[1 / 2, None],
                                                  text="Add Exercise")

    def remove_add_exercise_button(self):
        # Function to remove the 'Add Exercise' button to the super set grid
        if self.add_exercise_button is not None:
            self.height -= 60
            self.main_grid.remove_widget(self.add_exercise_button)
            self.add_exercise_button = None

    def insert_muscle_pick(self):
        # If the user presses the 'Add Exercise' on the super set grid
        self.routine_grid.screen.insert_muscle_pick(self)

    def add_exercise(self, selected_exercise, super_set_data=None, exercise_data=None):
        # Adds the selected exercise to the routine
        self.remove_add_exercise_button()
        self.height += 190
        if self.initial_text_input_grid is None:
            super_set_numbers = [4, 90]
            if super_set_data is not None:
                super_set_numbers = super_set_data
            # If the initial parameters have not been added
            self.initial_text_input_grid = GridLayout(cols=2, size_hint_x=1, spacing=[25, 5], padding=[10, 5])
            text_inputs_data = [["Sets", "Rest Time(s)"], [1, 1], [7, 500], [False, False], super_set_numbers]

            for i in range(2):
                text_input = IntegerInput(self.initial_text_input_grid, text_inputs_data[0][i], text_inputs_data[1][i],
                                          text_inputs_data[2][i], text_inputs_data[3][i],
                                          text_inputs_data[4][i], self.routine_grid)
                self.all_text_inputs.append(text_input)

            self.main_grid.add_widget(self.initial_text_input_grid)
            self.height += 85
        self.exercise_grid = SuperSetExerciseGrid(selected_exercise, self, exercise_data)
        self.all_exercises.append(self.exercise_grid)
        self.main_grid.add_widget(self.exercise_grid)
        self.insert_add_exercise_button()
        if super_set_data is None:
            self.routine_grid.check_text_input()

    def delete_exercise(self, exercise_grid):
        # Removes the selected exercise from the routine
        self.main_grid.remove_widget(exercise_grid)
        self.all_exercises.remove(exercise_grid)
        self.height -= 175
        if len(self.all_exercises) == 0:
            # If the number of exercises is zero then remove the initial parameter grid
            self.main_grid.remove_widget(self.initial_text_input_grid)
            self.initial_text_input_grid = None
            self.all_text_inputs = []
            self.height -= 70
        self.routine_grid.check_text_input()

    def delete_super_set(self):
        # Remove super set from the routine grid
        self.routine_grid.delete_set(self)

    def check_text_input(self):
        # Check the text inputs of the routine grid
        self.routine_grid.check_text_input()


class RoutineGrid(GridLayout):
    add_button_grid = None
    finish_button = None
    previous_routine = None
    valid = False
    all_sets = []

    def __init__(self, screen, previous_routine=None, **kwargs):
        super(RoutineGrid, self).__init__(**kwargs)
        self.screen = screen
        self.padding = [10, 10]

        if previous_routine is not None:
            self.edit_routine(previous_routine)
        else:
            self.all_sets = []
            self.insert_add_buttons()
        self.screen.ids.routine_scroll.add_widget(self)

    def edit_routine(self, previous_routine):
        self.all_sets = []
        self.previous_routine = previous_routine
        for exercise_set in previous_routine.exercises:
            if isinstance(exercise_set, SuperSet):
                all_exercise_data = []
                for exercise in exercise_set.super_set_exercises:
                    exercise_data = [exercise.base_exercise, exercise.reps, exercise.min_reps, exercise.max_reps,
                                     exercise.weight]
                    all_exercise_data.append(exercise_data)
                self.add_superset_from_data([exercise_set.sets, exercise_set.rest_time], all_exercise_data)
            elif isinstance(exercise_set, Exercise):
                self.add_exercise_from_data(exercise_set.base_exercise,
                                            [exercise_set.reps, exercise_set.min_reps, exercise_set.max_reps,
                                             exercise_set.sets, exercise_set.weight, exercise_set.rest_time])
        self.check_text_input()

    def insert_add_buttons(self):
        if self.add_button_grid is None and len(self.all_sets) < 10:
            button_info = [["Add Exercise", "Add Superset"], [self.screen.insert_muscle_pick, self.add_superset]]
            self.add_button_grid = GridLayout(cols=2, size_hint=[1, None], height=50, spacing=[10, 0])
            self.add_widget(self.add_button_grid)
            for text, action in zip(button_info[0], button_info[1]):
                KivyButton(self.add_button_grid, L_GREEN, 25, action, [1 / 2, None], text=text)
        if self.finish_button is None and len(self.all_sets) > 0:
            self.finish_button = KivyButton(self, L_GREEN, 25, self.finish_routine, [1, None],
                                            text="Finish Routine")
        elif self.finish_button is not None and len(self.all_sets) == 0:
            self.remove_widget(self.finish_button)
            self.finish_button = None

    def remove_add_buttons(self):
        if self.add_button_grid is not None:
            self.remove_widget(self.add_button_grid)
            self.add_button_grid = None
        if self.finish_button is not None:
            self.remove_widget(self.finish_button)
            self.finish_button = None

    def add_exercise(self, selected_exercise):
        if self.screen.superset is None:
            exercise = ExerciseGrid(selected_exercise, self)
            self.add_widget(exercise)
            self.all_sets.append(exercise)
            self.remove_add_buttons()
        else:
            self.screen.superset.add_exercise(selected_exercise)
        self.screen.remove_muscle_pick()
        self.screen.remove_exercise_pick()
        self.check_text_input()

    def add_superset(self):
        self.remove_add_buttons()
        superset = SuperSetGrid(self)
        self.add_widget(superset)
        self.all_sets.append(superset)

    def delete_set(self, set_card):
        self.remove_widget(set_card)
        self.all_sets.remove(set_card)
        self.check_text_input()

    def add_superset_from_data(self, superset_data, exercise_data):
        superset = SuperSetGrid(self)
        self.add_widget(superset)
        self.all_sets.append(superset)
        for exercise in exercise_data:
            superset.add_exercise(exercise[0], superset_data, [exercise[1], exercise[2], exercise[3], exercise[4]])

    def add_exercise_from_data(self, prev_exercise, exercise_data):
        exercise = ExerciseGrid(prev_exercise, self, exercise_data)
        self.add_widget(exercise)
        self.all_sets.append(exercise)

    def check_text_input(self):  # Called when needing to check if the text inputs have values and are correct
        def valid(all_sets):
            def text_valid(all_text_inputs, rep_check=True):
                min_reps = max_reps = reps = None
                for text_input in all_text_inputs:
                    if text_input.text == "":
                        return False
                    else:
                        if rep_check:
                            if text_input.hint_text == "Reps":
                                reps = text_input.text
                            elif text_input.hint_text == "Min Reps":
                                min_reps = text_input.text
                            elif text_input.hint_text == "Max Reps":
                                max_reps = text_input.text

                if rep_check:
                    if int(min_reps) < int(max_reps):
                        if int(min_reps) <= int(reps) <= int(max_reps):
                            return True
                        else:
                            return False
                    else:
                        return False
                return True

            for ex_grid in all_sets:  # Loops through each grid. Either super set or exercise set
                if isinstance(ex_grid, SuperSetGrid):  # If the grid is a super set
                    if not text_valid(ex_grid.all_text_inputs, False):  # Check the initial super set parameters
                        return False
                    if len(ex_grid.all_exercises) != 0:
                        for selected_exercise in ex_grid.all_exercises:
                            if not text_valid(selected_exercise.all_text_inputs):  # Check the exercise parameters
                                return False
                    else:
                        return False
                else:
                    if not text_valid(ex_grid.all_text_inputs):  # Check the exercise parameters
                        return False
            return True

        if valid(self.all_sets):  # If valid inputs. Insert 'Add Exercise', 'Add Super Set' and 'Finish Routine' Buttons
            for grid in self.all_sets:
                if isinstance(grid, SuperSetGrid):
                    grid.insert_add_exercise_button()
            self.insert_add_buttons()
        else:  # If not valid inputs. Remove all 'Add Exercise', 'Add Super Set' and 'Finish Routine' Buttons
            for grid in self.all_sets:
                if isinstance(grid, SuperSetGrid):
                    grid.remove_add_exercise_button()
            self.remove_add_buttons()

    def finish_routine(self):
        """ Function collects all the text inputs from the routine and creates a routine to be used on a different
                screen """
        routine_name = self.screen.ids.routine_name.text[:20]
        if routine_name.replace(" ", "") == "":  # Check if the routine name is filled
            return
        all_routine_sets = []
        for grid in self.all_sets:  # For each grid in the routine
            if isinstance(grid, SuperSetGrid):  # The current grid is a super set
                super_set_data = []
                for initial_text_input in grid.all_text_inputs:  # Collects all the initial parameters of the super set
                    super_set_data.append(int(initial_text_input.text))
                if len(grid.all_exercises) > 1:
                    super_set_exercises = []
                    for exercise_grid in grid.all_exercises:  # Goes through each exercise and collects the data
                        text_inputs = exercise_grid.all_text_inputs
                        exercise_data = [int(text_inputs[0].text), int(text_inputs[1].text), int(text_inputs[2].text),
                                         float(text_inputs[3].text)]
                        # Adds each super set exercise to the list
                        super_set_exercises.append(
                            SuperSetExercise(exercise_grid.selected_exercise, exercise_data))
                    # Appends the super set onto the active routine class
                    all_routine_sets.append(SuperSet(super_set_exercises, super_set_data))
                elif len(grid.all_exercises) == 1:
                    # If the number of exercises in the super is one then converts the super set to an exercise
                    text_inputs = grid.all_exercises[0].all_text_inputs
                    exercise_data = [int(text_inputs[0].text), int(text_inputs[1].text), int(text_inputs[2].text),
                                     int(super_set_data[0]), float(text_inputs[3].text), int(super_set_data[1])]
                    all_routine_sets.append(Exercise(grid.all_exercises[0].selected_exercise, exercise_data))
            else:  # If the grid is an exercise
                text_inputs = grid.all_text_inputs
                exercise_data = [int(text_inputs[0].text), int(text_inputs[1].text), int(text_inputs[2].text),
                                 int(text_inputs[3].text), float(text_inputs[4].text), int(text_inputs[5].text)]
                # Adds the exercise onto the active routine class
                all_routine_sets.append(Exercise(grid.selected_exercise, exercise_data))
        save_new_routine("files/gym_files/saved_routines.pkl", [routine_name, all_routine_sets], self.previous_routine)
        self.screen.app.screen_action("gym_screen", "right", "R/T").start()


class CreateScreen(Screen):
    muscles = ["Abs", "Arms", "Back", "Chest", "Legs", "Shoulders"]
    muscle_selected = None
    routine_grid = None
    exercise_info_card = None
    superset = None

    def __init__(self, app, **kwargs):
        super(CreateScreen, self).__init__(**kwargs)
        self.app = app

        for muscle in self.muscles:
            KivyButton(self.ids.muscle_pick_grid, L_GREEN, 25, None, [1 / 2, 1 / 3],
                       text=muscle).bind(on_release=lambda button: self.insert_exercise_pick(button))

    def create_routine(self):
        self.reset()
        self.routine_grid = RoutineGrid(self)
        self.exercise_info_card = ExerciseInfoCard(self, self.routine_grid, size_hint=[1, None],
                                                   height=Window.size[1] - 205, y=Window.size[1] + 50)

    def edit_routine(self, selected_routine):
        self.reset()
        self.ids.routine_name.text = selected_routine.name
        self.routine_grid = RoutineGrid(self, selected_routine)
        self.exercise_info_card = ExerciseInfoCard(self, self.routine_grid, size_hint=[1, None],
                                                   height=Window.size[1] - 205, y=Window.size[1] + 50)

    def reset(self):
        self.ids.routine_scroll.remove_widget(self.routine_grid)
        self.ids.routine_scroll.scroll_y = 1
        self.routine_grid = None
        self.ids.routine_name.text = ""
        self.muscle_selected = None

    def insert_muscle_pick(self, super_set=None):
        self.superset = super_set
        Animation(x=0, duration=0.2).start(self.ids.muscle_pick)

    def remove_muscle_pick(self):
        Animation(x=self.width + 50, duration=0.2).start(self.ids.muscle_pick)

    def insert_exercise_pick(self, muscle_button):
        self.muscle_selected = muscle_button.text
        self.exercise_search()
        Animation(x=0, duration=0.2).start(self.ids.exercise_pick)

    def remove_exercise_pick(self):
        self.muscle_selected = None
        Animation(x=-(self.width + 50), duration=0.2).start(self.ids.exercise_pick)

    def insert_exercise_info(self):
        Animation(y=80, duration=0.2).start(self.exercise_info_card)

    def exercise_search(self, search_text="", search=False):
        def add_exercise_item(new_exercise):
            if self.routine_grid is not None:
                item = CustomOneLineIconListItem(new_exercise, self.routine_grid.add_exercise)
                item.bind(on_release=lambda item: self.show_exercise_info(item.selected_exercise, True))
                self.ids.container.add_widget(item)

        self.ids.container.clear_widgets()
        for selected_exercise in sorted_exercises:
            if selected_exercise.muscle == self.muscle_selected or self.muscle_selected is None:
                # Checks the muscle selected is the exercise's muscle group
                if search:
                    if search_text in selected_exercise.name.lower():
                        add_exercise_item(selected_exercise)
                else:
                    add_exercise_item(selected_exercise)

    def show_exercise_info(self, exercise, show_add_button):
        self.exercise_info_card.add_exercise_info(exercise, show_add_button)
        self.insert_exercise_info()
