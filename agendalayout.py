import kivy
kivy.require('1.8.0')

from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget

import datetime
import os

from dbhandler import DBHandler, ActivityModel
from debug import DebugTools
from utils import unix_time

__author__ = 'boisei0'

base_path = os.path.dirname(os.path.abspath(__file__))

debug = DebugTools()
dbh = DBHandler()

background_colour = [.8, 1, 1, 1]


class AgendaLayout(BoxLayout):
    agenda_core = ObjectProperty()

    def __init__(self, **kwargs):
        super(AgendaLayout, self).__init__(**kwargs)

        self.orientation = 'vertical'
        self.widgets = 0  # FIXME: Unused
        self.size_hint_y = None
        self.height = '32cm'
        self.spacing = 0

        draw_background(self)

        self.app = App.get_running_app()
        selected_date = self.app.selected_date
        self.dt = datetime.datetime(selected_date.year, selected_date.month, selected_date.day, 7, 0, 0, 0)

        self._fill_day()

    def _fill_day(self):
        self.clear_widgets()
        sse = int(unix_time(self.dt))
        for i in range(65):
            self.add_widget(AgendaItem(timestamp=(i * 60 * 15) + sse))

    def on_update(self):
        self.clear_widgets()
        selected_date = self.app.selected_date
        self.dt = datetime.datetime(selected_date.year, selected_date.month, selected_date.day, 7, 0, 0, 0)
        self._fill_day()


class AgendaItem(BoxLayout):
    def __init__(self, timestamp, **kwargs):
        super(AgendaItem, self).__init__(**kwargs)

        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = '0.5cm'
        self.spacing = 0

        self.whitespace_path = os.path.join(base_path, 'res', 'whitespace.png')

        time = datetime.datetime.utcfromtimestamp(timestamp).strftime('%H:%M')  # FIXME
        self.label = Label(size_hint_x=.2, markup=True)
        if time[-2:] == '00' or time[-2:] == '30':
            self.label.text = '[color=3b72ff]{}[/color]'.format(time)
        self.label.valign = 'top'  # FIXME
        self.item_button = Button(size_hint_x=.6)
        self.item_button.border = [0, 16, 0, 16]

        self.activity = None

        try:
            self.activity = ActivityModel(dbh.get_activity_id_by_timestamp(timestamp))
            self._display_normal_item()
        except IndexError:
            self._display_empty_item()

        self.add_widget(self.label)
        self.add_widget(self.item_button)
        self.add_widget(Widget(size_hint_x=.2))

    def _display_empty_item(self):
        self.item_button.disabled = True
        self.item_button.background_disabled_normal = self.whitespace_path
        self.item_button.background_disabled_down = self.whitespace_path
        self.item_button.background_color = background_colour

    def _display_normal_item(self):
        if self.activity is not None:
            self.item_button.background_normal = self.whitespace_path
            self.item_button.background_down = self.whitespace_path
            self.item_button.background_color = self.activity.course.colour
            self.item_button.text = self.activity.title


def draw_background(widget):
    widget.canvas.add(Color(background_colour[0], background_colour[1], background_colour[2], background_colour[3]))
    widget.canvas.add(Rectangle(pos=[0, 0], size=[3000, 8000]))