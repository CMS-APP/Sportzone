import os
import re
import sys

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang.builder import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivymd.uix.button import MDFlatButton
from kivymd.uix.card import MDCard, MDSeparator
from kivymd.uix.label import MDLabel, Label
from kivymd.uix.textfield import MDTextField

sys.path.insert(1, os.path.abspath("../") + '/fitness_dev_v0.3/files')
Builder.load_file("Screens/Screens_kv/signup_screen.kv")

from file_handling import write_file


class CurrentUser:
    def __init__(self, username, email, password, units, gender, height, weight, age, experience, goals, equipment,
                 frequency, tutorial_complete):
        self.username = username
        self.email = email
        self.password = password
        self.units = units
        self.gender = gender
        self.height = height
        self.weight = weight
        self.age = age
        self.experience = experience
        self.goals = goals
        self.equipment = equipment
        self.frequency = frequency
        self.tutorial_complete = tutorial_complete


class UsernameInput(MDTextField):
    def __init__(self, **kwargs):
        super(UsernameInput, self).__init__(**kwargs)
        self.hint_text = "Username"
        self.icon_right = "account"
        self.color_mode = "custom"
        self.font_size = 25
        self.line_color_focus = (0, 0, 0, 1)
        self.line_color_normal = (0, 0, 0, 1)
        self.helper_text_mode = "persistent"
        self.valid = False

    def on_text(self, *args):
        self.text = self.text.replace(" ", "")
        alphanum = re.compile('[^0-9a-zA-Z]+')

        if len(self.text) == 0:
            self.helper_text = "Please enter a username"
            self.current_hint_text_color = (0, 0, 0, 1)
            self.line_color_focus = (0, 0, 0, 1)
            self.line_color_normal = (0, 0, 0, 1)
            init = False
        else:
            init = True

        if init:
            if len(self.text) < 6:
                self.helper_text, self.valid = "Needs to be 6 or more characters long", False
            elif len(self.text) > 20:
                self.helper_text, self.valid = "Needs to be 20 or less characters long", False
            elif alphanum.search(self.text):
                self.helper_text, self.valid = "Needs to include no special characters", False
            # elif not self.app.firebase.check_username(self.text):
            # self.helper_text = "Username taken", False
            else:
                self.valid = True

            if not self.valid:
                self.current_hint_text_color = (0, 0, 0, 1)
                self.line_color_focus = (1, 0, 0, 1)
                self.line_color_normal = (1, 0, 0, 1)
            else:
                self.helper_text = ""
                self.current_hint_text_color = (0, 0, 0, 1)
                self.line_color_focus = (0, 1, 0, 1)
                self.line_color_normal = (0, 1, 0, 1)


class EmailInput(MDTextField):
    def __init__(self, **kwargs):
        super(EmailInput, self).__init__(**kwargs)
        self.hint_text = "Email"
        self.icon_right = "email"
        self.color_mode = "custom"
        self.font_size = 25
        self.line_color_focus = (0, 0, 0, 1)
        self.line_color_normal = (0, 0, 0, 1)
        self.helper_text_mode = "persistent"
        self.valid = False

    def on_text(self, *args):
        self.text = self.text.replace(" ", "")
        if len(self.text) == 0:
            self.helper_text = "Please enter your email"
            self.current_hint_text_color = (0, 0, 0, 1)
            self.line_color_focus = (0, 0, 0, 1)
            self.line_color_normal = (0, 0, 0, 1)
            init = False
        else:
            init = True

        if init:
            regex_1 = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w'
            regex_2 = '^[a-z0-9]+[@]\w+[.]\w'
            if not re.search(regex_1, self.text) and not re.search(regex_2, self.text):
                self.helper_text, self.valid = "Please enter a valid email", False
            # elif not self.app.firebase.check_email(self.text):
            # self.helper_text, self.valid = "Email taken", False
            else:
                self.valid = True

            if not self.valid:
                self.current_hint_text_color = (0, 0, 0, 1)
                self.line_color_focus = (1, 0, 0, 1)
                self.line_color_normal = (1, 0, 0, 1)
            else:
                self.helper_text = ""
                self.current_hint_text_color = (0, 0, 0, 1)
                self.line_color_focus = (0, 1, 0, 1)
                self.line_color_normal = (0, 1, 0, 1)


class PasswordInput(MDTextField):
    def __init__(self, **kwargs):
        super(PasswordInput, self).__init__(**kwargs)
        self.hint_text = "Password"
        self.icon_right = "key"
        self.color_mode = "custom"
        self.password = True
        self.font_size = 25
        self.line_color_focus = (0, 0, 0, 1)
        self.line_color_normal = (0, 0, 0, 1)
        self.helper_text_mode = "persistent"
        self.valid = False

    def on_text(self, *args):
        self.text = self.text.replace(" ", "")
        if len(self.text) == 0:
            self.helper_text = "Please enter a password"
            self.current_hint_text_color = (0, 0, 0, 1)
            self.line_color_focus = (0, 0, 0, 1)
            self.line_color_normal = (0, 0, 0, 1)
            init = False
        else:
            init = True

        if init:
            numbers = re.compile('[0-9]')
            l_letters = re.compile('[a-z]')
            u_letters = re.compile('[A-Z]')
            if len(self.text) < 8:
                self.helper_text, self.valid = "Needs to be at least 8 characters long", False
            elif len(self.text) > 254:
                self.helper_text, self.valid = "Needs to be shorter", False
            elif not l_letters.search(self.text):
                self.helper_text, self.valid = "Needs to include at least one lowercase letter", False
            elif not u_letters.search(self.text):
                self.helper_text, self.valid = "Needs to include at least one uppercase letter", False
            elif not numbers.search(self.text):
                self.helper_text, self.valid = "Needs to include at least one number", False
            else:
                self.valid = True

            if not self.valid:
                self.current_hint_text_color = (0, 0, 0, 1)
                self.line_color_focus = (1, 0, 0, 1)
                self.line_color_normal = (1, 0, 0, 1)
            else:
                self.helper_text = ""
                self.current_hint_text_color = (0, 0, 0, 1)
                self.line_color_focus = (0, 1, 0, 1)
                self.line_color_normal = (0, 1, 0, 1)


class HealthInput(MDTextField):
    init = True
    valid = False

    def __init__(self, text, icon, decimal, upper_limit, **kwargs):
        super(HealthInput, self).__init__(**kwargs)
        self.hint_text = text
        self.normal_text = text.lower()
        self.icon_right = icon
        self.decimal = decimal
        self.upper_limit = upper_limit
        self.color_mode = "custom"
        self.helper_text_mode = "persistent"
        self.current_hint_text_color = (0, 0, 0, 1)
        self.line_color_focus = (0, 0, 0, 1)
        self.line_color_normal = (0, 0, 0, 1)

    def on_text(self, instance, text):
        self.init = True
        if len(self.text) == 0:
            self.helper_text = f"Please enter your {self.normal_text}"
            self.current_hint_text_color = (0, 0, 0, 1)
            self.line_color_focus = (0, 0, 0, 1)
            self.line_color_normal = (0, 0, 0, 1)
            self.init = False
            self.valid = False

        if self.init:
            self.valid = True
            try:
                float(self.text)
                if not float(self.text) <= self.upper_limit:
                    self.valid = False
                    self.helper_text = f"Please input a number less then {self.upper_limit}"
                elif float(self.text) == 0:
                    self.valid = False
                    self.helper_text = f"Please input a number larger then 0"
                elif not self.decimal and '.' in self.text:
                    self.valid = False
                    self.helper_text = f"Please input a whole number"
                elif self.normal_text == "age" and float(self.text) < 16:
                    self.valid = False
                    self.helper_text = f"You need to be at least 16 years old"
            except ValueError:
                self.helper_text = "Please input a number"
                self.valid = False

            self.current_hint_text_color = (1, 0, 0, 1)
            self.line_color_focus = (1, 0, 0, 1)
            self.line_color_normal = (1, 0, 0, 1)
            if self.valid:
                self.helper_text = ""
                self.current_hint_text_color = (0, 1, 0, 1)
                self.line_color_focus = (0, 1, 0, 1)
                self.line_color_normal = (0, 1, 0, 1)


class SignupLabel(MDLabel):
    def __init__(self, text, font_size, color=None, halign="center", **kwargs):
        super(SignupLabel, self).__init__(**kwargs)
        self.text = text
        self.size_hint = [1, None]
        self.font_name = "Geosans"
        self.font_size = font_size
        self.valign = "middle"
        self.halign = halign
        if color is not None:
            self.color = color


class SignupButton(MDFlatButton):
    selected = False

    def __init__(self, text, on_release_action, **kwargs):
        super(SignupButton, self).__init__(**kwargs)
        self.text = text
        self.font_size = 20
        self.text_color = (0, 0, 0, 1)
        self.md_bg_color = (1, 143 / 255, 5 / 255, 1)
        self.on_release_action = on_release_action

    def on_release(self):
        if self.on_release_action is not None:
            self.on_release_action()


class SignupButtonList(GridLayout):
    def __init__(self, names, action=None, label=None, selected_button=None, button_height=50, **kwargs):
        super(SignupButtonList, self).__init__(**kwargs)
        self.size_hint = [1, None]
        self.height = button_height
        self.cols = len(names)
        self.spacing = [10, 0]
        self.all_buttons = []
        if label is not None:
            self.cols += 1
            text_label = Label(text=label, font_size=20, size_hint=[1 / self.cols, None], height=button_height,
                               halign="center",
                               valign="center")
            text_label.color = (0, 0, 0, 1)
            self.add_widget(text_label)

        for i in range(len(names)):
            button = SignupButton(names[i], action)
            button.size_hint, button.height = [1 / self.cols, None], button_height
            button.bind(on_release=lambda button: self.button_selected(button))
            self.add_widget(button)
            self.all_buttons.append(button)

        if selected_button is not None:
            self.button_selected(self.all_buttons[selected_button])

    def button_selected(self, selected_button):
        for button in self.all_buttons:
            button.md_bg_color = (1, 143 / 255, 5 / 255, 1)
            if button == selected_button:
                self.selected_button = button
                button.selected = True
                button.md_bg_color = (0, 1, 0, 0.5)
            else:
                button.selected = False


class MultiButtonListSelect(GridLayout):
    def __init__(self, buttons, **kwargs):
        super(MultiButtonListSelect, self).__init__(**kwargs)
        self.buttons = buttons
        self.cols = 3
        self.rows = 2
        self.spacing = [10, 10]
        self.displayed_buttons = []
        self.selected_buttons = []
        self.valid = False
        for name in self.buttons:
            button = SignupButton(name, None, size_hint=[1 / 3, None])
            button.font_size = 16
            button.name = self.buttons[name]
            button.bind(on_release=lambda button: self.button_selected(button))
            self.displayed_buttons.append(button)
            self.add_widget(button)

    def button_selected(self, selected_button):
        if selected_button not in self.selected_buttons:
            selected_button.md_bg_color = (0, 1, 0, 0.5)
            self.selected_buttons.append(selected_button)
        else:
            selected_button.md_bg_color = (1, 143 / 255, 5 / 255, 1)
            self.selected_buttons.remove(selected_button)

        if len(self.selected_buttons) > 2:
            self.selected_buttons[0].md_bg_color = (1, 143 / 255, 5 / 255, 1)
            self.selected_buttons.remove(self.selected_buttons[0])

        if len(self.selected_buttons) == 2:
            self.valid = True


class EquipmentSelectList(GridLayout):
    def __init__(self, **kwargs):
        super(EquipmentSelectList, self).__init__(**kwargs)
        self.rows = 2
        self.spacing = [0, 10]

        self.all_other_buttons = []

        self.gym_button = SignupButton("Full Gym", self.gym_select, size_hint=[1, None])
        self.gym_button.selected = False
        self.add_widget(self.gym_button)

        self.non_gym_grid = GridLayout(cols=4, spacing=[10, 0])
        self.add_widget(self.non_gym_grid)
        non_gym_names = ["Dumbbell", "Resistance\nBands", "Barbell", "Cable Machine"]
        for name in non_gym_names:
            button = SignupButton(name, None, size_hint=[1 / 4, None])
            button.selected = False
            button.bind(on_release=lambda button: self.non_gym_select(button))
            self.all_other_buttons.append(button)
            self.non_gym_grid.add_widget(button)

    def gym_select(self):
        if not self.gym_button.selected:
            self.gym_button.md_bg_color = (0, 1, 0, 0.5)
            self.gym_button.selected = True
            for button in self.all_other_buttons:
                button.md_bg_color = (0, 1, 0, 0.5)
                button.selected = True
        else:
            self.gym_button.selected = False
            self.gym_button.md_bg_color = (1, 143 / 255, 5 / 255, 1)
            for button in self.all_other_buttons:
                button.selected = False
                button.md_bg_color = (1, 143 / 255, 5 / 255, 1)

        self.equipment = []

        if self.gym_button.selected:
            self.equipment.append("Full Gym")
        else:
            for button in self.all_other_buttons:
                if button.selected:
                    self.equipment.append(button.text)

    def non_gym_select(self, button):
        if button.selected:
            self.gym_button.selected = False
            self.gym_button.md_bg_color = (1, 143 / 255, 5 / 255, 1)
            button.selected = False
            button.md_bg_color = (1, 143 / 255, 5 / 255, 1)
        else:
            button.selected = True
            button.md_bg_color = (0, 1, 0, 0.5)


class PersonalCard(MDCard):
    def __init__(self, screen, **kwargs):
        super(PersonalCard, self).__init__(**kwargs)
        self.screen = screen
        self.size_hint = [1, 0.79]
        self.orientation = "vertical"
        self.padding = [30, 0]
        self.elevation = 0

        self.grid = GridLayout(cols=1, spacing=0, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))

        self.grid.add_widget(SignupLabel("Let's get physical,", 28, halign="left", size_hint=[1, None], height=25))
        self.grid.add_widget(
            SignupLabel("Sign up to continue!", 24, (129, 129, 129, 1), halign="left", size_hint=[1, None], height=25))
        self.grid.add_widget(MDSeparator(height=2))

        self.main_grid = GridLayout(cols=1, spacing=[0, 12], padding=[20, 10])
        self.grid.add_widget(self.main_grid)

        self.username_input = UsernameInput(size_hint=[1, None], height=150)
        self.main_grid.add_widget(self.username_input)
        self.email_input = EmailInput(size_hint=[1, None], height=150)
        self.main_grid.add_widget(self.email_input)
        self.password_input = PasswordInput(size_hint=[1, None], height=150)
        self.main_grid.add_widget(self.password_input)
        self.all_inputs = [self.username_input, self.email_input, self.password_input]

        self.main_grid.add_widget(MDSeparator(height=2))

        button_grid = GridLayout(cols=2, size_hint=[1, None], height=100, spacing=[10, 0])
        button_grid.add_widget(SignupButton("Back", self.back_action, size_hint=[1, None], height=50))
        button_grid.add_widget(SignupButton("Continue", self.continue_action, size_hint=[1, None], height=50))
        self.main_grid.add_widget(button_grid)

        self.grid.add_widget(MDLabel())

        scroll = ScrollView(size_hint=(1, 0.79), size=(Window.width, Window.height))
        scroll.add_widget(self.grid)

        self.add_widget(scroll)

    def continue_action(self):
        if self.screen.check_input(self.all_inputs):
            self.screen.save_data([self.username_input.text, self.email_input.text, self.password_input.text],
                                  "personal")
            self.screen.animate_card(self, [-Window.size[0], 0], 33)
            self.screen.animate_card(self.screen.health_card, [0, 0])

    def back_action(self):
        Clock.schedule_once(self.screen.stop, 0.3)
        self.screen.app.screen_action("login_screen", "down")


class HealthCard(MDCard):
    def __init__(self, screen, **kwargs):
        super(HealthCard, self).__init__(**kwargs)
        self.screen = screen
        self.size_hint = [1, 0.79]
        self.orientation = "vertical"
        self.padding = [30, 0]
        self.spacing = [0, 10]
        self.elevation = 0

        self.grid = GridLayout(cols=1, spacing=0, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))

        self.grid.add_widget(
            SignupLabel("We need some information about you,", 28, halign="left", size_hint=[1, None], height=25))
        self.grid.add_widget(
            SignupLabel("Please type them in below!", 24, (129, 129, 129, 1), halign="left", size_hint=[1, None],
                        height=25))
        self.grid.add_widget(MDSeparator(height=2))

        self.main_grid = GridLayout(cols=1, spacing=[0, 12], padding=[20, 10])
        self.grid.add_widget(self.main_grid)

        self.unit_select = SignupButtonList(["Metric (kg)", "Imperial (lb)"], self.change_units, "Weight Units", 0)
        self.main_grid.add_widget(self.unit_select)
        self.gender_select = SignupButtonList(["Male", "Female", "Other"], label="Gender")
        self.main_grid.add_widget(self.gender_select)
        self.weight_input = HealthInput("weight", "weight", True, 500)
        self.main_grid.add_widget(self.weight_input)
        self.height_input = HealthInput("height", "human-male-height", True, 300)
        self.main_grid.add_widget(self.height_input)
        self.age_input = HealthInput("Age", "calendar-today", False, 100)
        self.main_grid.add_widget(self.age_input)

        self.all_inputs = [self.weight_input, self.height_input, self.age_input]

        self.grid.add_widget(MDSeparator(height=2))

        button_grid = GridLayout(cols=2, size_hint=[1, None], height=100, spacing=[10, 0])
        button_grid.add_widget(SignupButton("Back", self.back_action, size_hint=[1, None], height=50))
        button_grid.add_widget(SignupButton("Continue", self.continue_action, size_hint=[1, None], height=50))
        self.main_grid.add_widget(button_grid)

        self.grid.add_widget(MDLabel())

        scroll = ScrollView(size_hint=(1, 0.79), size=(Window.width, Window.height))
        scroll.add_widget(self.grid)

        self.add_widget(scroll)

        self.change_units()

    def change_units(self):
        self.weight_input.hint_text = "Weight (kg)"
        self.height_input.hint_text = "Height (cm)"
        if self.unit_select.selected_button.text == "Imperial (lb)":
            self.weight_input.hint_text = "Weight (lb)"
            self.height_input.hint_text = "Height (in)"

    def continue_action(self):
        if self.screen.check_input(self.all_inputs) and self.screen.check_button_select(
                self.unit_select.all_buttons) and self.screen.check_button_select(self.gender_select.all_buttons):
            self.screen.save_data(
                [self.unit_select.selected_button.text, self.gender_select.selected_button.text, self.weight_input.text,
                 self.height_input.text, self.age_input.text], "health")
            self.screen.animate_card(self, [-Window.size[0], 0], 66)
            self.screen.animate_card(self.screen.experience_card, [0, 0])

    def back_action(self):
        self.screen.animate_card(self, [Window.size[0], 0], 0)
        self.screen.animate_card(self.screen.personal_card, [0, 0])


class ExperienceCard(MDCard):
    def __init__(self, screen, **kwargs):
        super(ExperienceCard, self).__init__(**kwargs)
        self.screen = screen
        self.size_hint = [1, 0.79]
        self.orientation = "vertical"
        self.padding = [30, 0]
        self.spacing = [0, 10]
        self.elevation = 0

        self.grid = GridLayout(cols=1, spacing=0, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))

        self.grid.add_widget(
            SignupLabel("What are your fitness goals?", 28, halign="left", size_hint=[1, None], height=25))
        self.grid.add_widget(
            SignupLabel("We need this to produce the best routines for you!", 20, (129, 129, 129, 1), halign="left",
                        size_hint=[1, None], height=25))
        self.grid.add_widget(MDSeparator(height=2))

        self.main_grid = GridLayout(cols=1, spacing=[0, 12], padding=[20, 10])
        self.grid.add_widget(self.main_grid)

        self.main_grid.add_widget(SignupLabel("Experience?", 25, height=25))

        self.experience_list = SignupButtonList(
            ["Beginner\n(New to fitness)", "Intermediate\n(Been to the gym\na couple times)",
             "Advanced\n(Know my way\nround the gym)"], button_height=100)
        self.main_grid.add_widget(self.experience_list)

        self.main_grid.add_widget(MDSeparator(height=2))

        self.main_grid.add_widget(SignupLabel("Goals? - Pick the Two Main Ones", 25, height=25))
        self.multi_goal_select = MultiButtonListSelect(
            {"Lose Weight/Fat": "Lose Fat", "Gain Muscle": "M", "Increase Strength": "Strength",
             "More Endurance": "Endurance",
             "Grow Athletic Skill": "Athletic", "Expand Joint Flexibility": "Flexibility"})
        self.main_grid.add_widget(self.multi_goal_select)

        self.main_grid.add_widget(MDSeparator(height=2))

        self.main_grid.add_widget(SignupLabel("What equipment do you have available?", 25, height=25))
        self.equipment_list = EquipmentSelectList()
        self.main_grid.add_widget(self.equipment_list)

        self.main_grid.add_widget(MDSeparator(height=2))

        self.main_grid.add_widget(SignupLabel("How often do want to work out per week?", 20, height=25))
        self.frequency = HealthInput("Workout Frequency", "calendar-week", False, 7)
        self.main_grid.add_widget(self.frequency)

        self.main_grid.add_widget(MDSeparator(height=2))

        button_grid = GridLayout(cols=2, size_hint=[1, None], height=100, spacing=[10, 0])
        button_grid.add_widget(SignupButton("Back", self.back_action, size_hint=[1, None], height=50))
        button_grid.add_widget(SignupButton("Continue", self.continue_action, size_hint=[1, None], height=50))
        self.main_grid.add_widget(button_grid)

        self.grid.add_widget(MDLabel())

        scroll = ScrollView(size_hint=(1, 0.79), size=(Window.width, Window.height))
        scroll.add_widget(self.grid)

        self.add_widget(scroll)

    def continue_action(self):
        if self.screen.check_button_select(self.experience_list.all_buttons) and len(
                self.multi_goal_select.selected_buttons) != 0 and self.screen.check_input([self.frequency]):
            goals = []
            for button in self.multi_goal_select.selected_buttons:
                goals.append(button.text)
            self.screen.save_data(
                [self.experience_list.selected_button.text.split("\n")[0], goals, self.equipment_list.equipment,
                 self.frequency.text], "experience")
            self.screen.animate_card(self, [-Window.size[0], 0], 100)

    def back_action(self):
        self.screen.animate_card(self, [Window.size[0], 0], 33)
        self.screen.animate_card(self.screen.health_card, [0, 0])


class SignupScreen(Screen):
    pb_event = None
    personal_data = []
    health_data = []
    experience_data = []

    def __init__(self, app, **kwargs):
        super(SignupScreen, self).__init__(**kwargs)
        self.app = app

    def start(self):
        self.personal_card = PersonalCard(self, pos=[0, 0])
        self.add_widget(self.personal_card)

        self.health_card = HealthCard(self, pos=[Window.size[0], 0])
        self.add_widget(self.health_card)

        self.experience_card = ExperienceCard(self, pos=[Window.size[0], 0])
        self.add_widget(self.experience_card)

    def stop(self, *args):
        self.remove_widget(self.personal_card)
        self.remove_widget(self.health_card)
        self.remove_widget(self.experience_card)

    def animate_card(self, card, position, pb_value=None):
        if pb_value is not None:
            if self.pb_event is not None:
                self.pb_event.cancel()
                self.pb_event = None
            self.pb_event = Clock.schedule_interval(
                lambda _: self.progress_bar_change(pb_value, (pb_value - self.ids.progress_bar.value) / 20), 0.01)
        Animation(pos=position, duration=0.2).start(card)

    def progress_bar_change(self, target, change):
        if round(self.ids.progress_bar.value, 1) == target:
            self.pb_event.cancel()
            self.pb_event = None
        self.ids.progress_bar.value += change

    def check_input(self, inputs):
        for text_input in inputs:
            if not text_input.valid:
                return False
        return True

    def check_button_select(self, buttons):
        for button in buttons:
            if button.selected:
                return True
        return False

    def save_data(self, data, data_type):
        if data_type == "personal":
            self.personal_data = data
            self.health_data = []
            self.experience_data = []
        elif data_type == "health":
            self.health_data = data
            self.experience_data = []
        elif data_type == "experience":
            self.experience_data = data
            write_file("files/gym_files/saved_user.pkl",
                       CurrentUser(self.personal_data[0], self.personal_data[1], self.personal_data[2],
                                   self.health_data[0], self.health_data[1], self.health_data[2], self.health_data[3],
                                   self.health_data[4], self.experience_data[0], self.experience_data[1],
                                   self.experience_data[2], self.experience_data[3], False))
