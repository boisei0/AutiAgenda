import kivy
kivy.require('1.8.0')

from kivy.graphics import Color, Rectangle, Line
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

from debug import DebugTools

__author__ = 'boisei0'

debug = DebugTools()


class AgendaLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(AgendaLayout, self).__init__(**kwargs)

        self.orientation = 'vertical'
        self.widgets = 0
        self.size_hint_y = None
        self.height = 1200

        self._draw_background()

        for i in range(30):
            self.add_widget(Button(text=str(i), size_hint_y=None, height=40, size_hint_x=.2))

    def _draw_background(self):
        with self.canvas:
            # col_light_blue = Color(.8, 1, 1)
            # col_dark_blue = Color(.29, .73, 1)
            Color(.8, 1, 1)
            Rectangle(pos=[0, 0], size=[8000, 8000])


class AgendaItem(Button):
    pass