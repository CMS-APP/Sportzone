import re

from kivy.lang.builder import Builder
from kivymd.uix.navigationdrawer import MDNavigationDrawer
from kivymd.uix.textfield import MDTextField

Builder.load_file("Screens/Screens_kv/navigation_drawer.kv")


class FloatInput(MDTextField):
    """ A numeric input with one decimal place

    """
    pat = re.compile('[^0-9]')  # The only input allowed (numeric values)

    def insert_text(self, substring, from_undo=False):
        """ Function to add a number to the text field. If the input has a decimal point then only one extra number can
        be added to the input. The number must be between zero and one thousand. """

        def isfloat(value):
            # Checks if an input is a float or integer
            try:
                num = float(value)
            except ValueError:
                return False
            return True

        pat = self.pat
        prev_text = self.text
        if '.' in self.text:
            # If the text has a decimal place only include numeric values
            s = re.sub(pat, '', substring)
        else:
            # Otherwise add the decimal place with the text
            s = '.'.join([re.sub(pat, '', s) for s in substring.split('.', 1)])

        super(FloatInput, self).insert_text(s, from_undo=from_undo)
        if isfloat(self.text):  # Check text is a float
            if not 0 < float(self.text) < 1000:
                self.text = prev_text
            if self.text.find('.') != -1 and len(self.text[self.text.find('.'):]) > 2:
                """Checks if there is a decimal point in the text and sees if there is more then one number after the 
                decimal point"""
                self.text = prev_text


class NavigationDrawer(MDNavigationDrawer):
    def button_selected(self, selected_button, btn_options):
        # Changes the color of the button selected to green. All other buttons turn red
        for btn in btn_options:
            if btn == selected_button:
                btn.md_bg_color = (0, 1, 0, 0.4)
            else:
                btn.md_bg_color = (1, 0, 0, 0.4)
