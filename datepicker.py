import kivy
kivy.require('1.8.0')

from kivy.graphics import Color, Rectangle
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

import calendar
import datetime
import gettext

from strings import TextData

__author__ = 'Rob Derksen (boisei0)'

strings = TextData()


class DatePicker(BoxLayout):
    root_app = ObjectProperty(None)

    def __init__(self, selected_month=datetime.datetime.today().strftime('%m'),
                 selected_year=datetime.datetime.today().strftime('%Y'),
                 selected_day=datetime.datetime.today().strftime('%d'), **kwargs):
        super(DatePicker, self).__init__(**kwargs)

        self.orientation = 'vertical'
        # self.canvas.add(Color(0.81, 0.81, 0.81))
        # self.canvas.add(Rectangle(pos=[self.center_x, self.center_y], size=[self.width, self.height]))

        top_row = BoxLayout(size_hint_y=None, height=(self.height / 3))

        self.selected_month = int(selected_month)
        self.selected_year = int(selected_year)
        self.selected_day = int(selected_day)

        self.prev_month_button = Button(size_hint_x=0.2, size_hint_y=None, height=(self.width / 3), text='<-', bold=True)
        self.prev_month_button.bind(on_release=self.on_prev_month)
        top_row.add_widget(self.prev_month_button)

        self.selected_month_label = Label(text=u'[color=303030]{} {}[/color]'.format(_(strings.months[self.selected_month]),
                                                                                     self.selected_year),
                                          size_hint_x=0.6, markup=True)
        top_row.add_widget(self.selected_month_label)

        self.next_month_button = Button(size_hint_x=0.2, size_hint_y=None, height=(self.width / 3), text='->', bold=True)
        # self.next_month_button.background_normal = 'res/drawable-mdpi/ic_find_next_holo_dark.png'
        # self.next_month_button.background_down = 'res/drawable-mdpi/ic_find_next_holo_light.png'
        self.next_month_button.bind(on_release=self.on_next_month)
        top_row.add_widget(self.next_month_button)

        self.add_widget(top_row)

        self.day_picker = DayPicker(self.selected_month, self.selected_year, self.selected_day)
        self.add_widget(self.day_picker)

    def on_prev_month(self, instance):
        new_month = self.selected_month - 1
        if new_month == 0:
            new_month = 12
            self.selected_year -= 1
        self.selected_month = new_month

        self._update_view()

    def on_next_month(self, instance):
        new_month = self.selected_month + 1
        if new_month == 13:
            new_month = 1
            self.selected_year += 1
        self.selected_month = new_month

        self._update_view()

    def _update_view(self):
        self.day_picker.set_year(self.selected_year)
        self.day_picker.set_month(self.selected_month)
        self.selected_month_label.text = u'[color=303030]{} {}[/color]'.format(_(strings.months[self.selected_month]),
                                                                               self.selected_year)
        self.day_picker.update()

    def on_translate(self):
        self.remove_widget(self.day_picker)
        self.day_picker = DayPicker(self.selected_month, self.selected_year, self.selected_day)
        self.add_widget(self.day_picker)


class DayPicker(BoxLayout):
    def __init__(self, month, year, day, **kwargs):
        super(DayPicker, self).__init__(**kwargs)

        self.orientation = 'vertical'

        self._month = month
        self._year = year
        self._date = datetime.date(self._year, self._month, day)

        self._cal = calendar.Calendar()

        self.add_widget(self._get_header())

        list_month = self._list_month()
        self._weeks_to_display = len(list_month)
        self._calendar = self._fill_calendar(list_month)

        self.add_widget(self._calendar)

    def set_month(self, month):
        self._month = month

    def set_year(self, year):
        self._year = year

    def _list_month(self):
        return self._cal.monthdatescalendar(self._year, self._month)

    def update(self):
        list_month = self._list_month()
        self._weeks_to_display = len(list_month)

        self.remove_widget(self._calendar)
        del self._calendar
        self._calendar = self._fill_calendar(list_month)
        self.add_widget(self._calendar)

    def _fill_calendar(self, list_month):
        month_start, days_in_month = calendar.monthrange(self._year, self._month)
        for i in range(month_start):
            list_month[0][i] = list_month[0][i].strftime('%d')
        month_end = list_month[-1].index(datetime.date(self._year, self._month, days_in_month))
        for i in range(month_end + 1, 7):
            list_month[-1][i] = list_month[-1][i].strftime('%d')

        bl = BoxLayout(orientation='vertical', spacing=2)
        for i in range(self._weeks_to_display):
            week = BoxLayout(spacing=2)
            for ii in range(7):
                if not isinstance(list_month[i][ii], datetime.date):
                    week.add_widget(Label(text=u'[color=303030]{}[/color]'.format(int(list_month[i][ii])), markup=True))
                else:
                    week.add_widget(Button(text=str(int(list_month[i][ii].strftime('%d'))),
                                           on_release=self._select_date))
            bl.add_widget(week)
        return bl

    def _get_header(self):
        widget = BoxLayout(size_hint_y=None, height=(self.height / 4))
        for i in range(1, 8):
            widget.add_widget(Label(text=u'[color=303030][b]{}[/b][/color]'.format(_(strings.weekdays_abbr[i])), markup=True))
        return widget

    def _select_date(self, instance):
        if instance.text == '':
            return
        day = int(instance.text)
        self._date = datetime.date(self._year, self._month, day)