import kivy
kivy.require('1.8.0')

from kivy.app import App
from kivy.metrics import dp
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.settings import SettingSpacer

from dbhandler import DBHandler
from strings import TextData, cap_first_letter

__author__ = 'boisei0'

strings = TextData()
dbh = DBHandler()


class Schedule(BoxLayout):
    def __init__(self, **kwargs):
        super(Schedule, self).__init__(**kwargs)

        self.app = App.get_running_app()
        self.rows = self.app.config_settings.getint('schedule', 'coursesaday')

        self.orientation = 'vertical'

        self.schedule_buttons = dict()
        self.size = self.parent.size
        self.schedule_scroll_view = ScrollView(size_hint_x=1, size_hint_y=None,
                                               size=(self.size[0], self.size[1] - dp(55)),
                                               do_scroll_x=False)

        # self.schedule = GridLayout(col_default_width='55dp', col_force_default=True, cols=7, row_default_height='1cm',
        #                            row_force_default_height=True)
        self.schedule = BoxLayout(orientation='vertical')
        self._fill_schedule()
        self.schedule_scroll_view.add_widget(self.schedule)

        self.add_widget(self.schedule_scroll_view)
        self.add_widget(SettingSpacer())

        button_box = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        button_box.add_widget(Button(text=u'Add {}'.format(_(strings.text['course'])), on_release=self.on_add_course))
        button_box.add_widget(Button(text=cap_first_letter(_(strings.text['close'])), on_release=self.on_close))

        self.add_widget(button_box)

    def on_add_course(self, instance):
        pass  # TODO

    def _fill_schedule(self):
        for i in range(self.rows):
            for ii in range(7):
                btn = Button(disabled=False, text='hi')
                self.schedule.add_widget(btn)


class ScheduleDialog(BoxLayout):
    app = App.get_running_app()
    rows = NumericProperty(10)
    add_course_button_text = StringProperty(u'Add {}'.format(_(strings.text['course'])))
    close_button_text = StringProperty(cap_first_letter(_(strings.text['close'])))

    def __init__(self, **kwargs):
        super(ScheduleDialog, self).__init__(**kwargs)

    def on_translate(self):
        self.add_course_button_text = u'Add {}'.format(_(strings.text['course']))  # FIXME: Translation
        self.close_button_text = cap_first_letter(_(strings.text['close']))  # FIXME: Translation

    def on_close(self, instance):
        # TODO: Save handling
        self.parent.parent.parent.dismiss()