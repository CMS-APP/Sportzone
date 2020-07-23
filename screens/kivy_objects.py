from kivymd.uix.button import MDFlatButton
from kivymd.uix.label import MDLabel

L_GREEN = (117 / 255, 1, 133 / 255, 1)
ORANGE = (1, 143 / 255, 5 / 255, 1)

class KivyLabel(MDLabel):
    font_name = "Geosans"

    def __init__(self, grid, font_size=25, halign="center", **kwargs):
        super(KivyLabel, self).__init__(**kwargs)
        self.font_size = font_size
        self.halign = halign
        grid.add_widget(self)


class KivyButton(MDFlatButton):
    font_name = "Geosans"

    def __init__(self, grid, md_bg_color, font_size=25, on_release_action=None, size_hint=None, **kwargs):
        super(KivyButton, self).__init__(**kwargs)
        if size_hint is None:
            size_hint = [1, None]
        self.md_bg_color = md_bg_color
        self.font_size = font_size
        self.on_release_action = on_release_action
        self.size_hint = size_hint
        self.text_color = (0, 0, 0, 1)
        self.height = 50
        grid.add_widget(self)

    def on_release(self):
        if self.on_release_action is not None:
            self.on_release_action()
