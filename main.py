import kivy
kivy.require('1.8.0')

from kivy.app import App
from kivy.config import ConfigParser
from kivy.factory import Factory
from kivy.properties import ObjectProperty, StringProperty

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.popup import Popup
from kivy.uix.settings import InterfaceWithSidebar
from kivy.uix.widget import Widget

try:
    import cProfile
    profiler_loaded = True
except ImportError:
    profiler_loaded = False

import datetime
import gettext
from os import path

from datepicker import DatePicker
from settings import CustomSettings
from strings import TextData, get_locale, list_translations, cap_first_letter

__author__ = 'Rob Derksen (boisei0)'
__appname__ = 'AutiAgenda'

base_path = path.dirname(__file__)

config_settings = ConfigParser()
config_settings.read(path.join(path.join(base_path, 'config'), 'autiagenda.ini'))
settings = CustomSettings(interface_cls=InterfaceWithSidebar)
# settings.add_json_panel('Date / Time', config, 'datetime.json')
# TODO: Add settings / config later

config_courses = ConfigParser()
config_courses.read(path.join(path.join(base_path, 'config'), 'courses.ini'))
courses = CustomSettings(interface_cls=InterfaceWithSidebar)
courses.add_json_panel('Course 1', config_courses, path.join(path.join(base_path, 'config'), 'courses.json'))

Factory.register('DatePicker', DatePicker)

domain = 'agenda'
locale_directory = path.dirname(path.abspath(__file__)) + "/locale"
gettext.bindtextdomain(domain, locale_directory)
gettext.textdomain(domain)
gettext.install(domain, localedir=locale_directory, unicode=True)

available_translations = list_translations()
translations = {}
for translation in available_translations:
    if gettext.find(domain, locale_directory, languages=[translation], all=1) is not None:
        print(gettext.find(domain, locale_directory, languages=[translation], all=1))
        translations[translation] = gettext.translation(domain, localedir=locale_directory, languages=[translation])
print(translations)

strings = TextData()


class Agenda(Widget):
    selected_day_button = Button()
    selected_date = datetime.datetime(datetime.datetime.today().year, datetime.datetime.today().month,
                                      datetime.datetime.today().day)  # TODO: Reformat this... :+
    selected_day_text = StringProperty('Today')

    about_popup = Popup(size_hint=(0.3, 0.5), auto_dismiss=False)
    settings_popup = Popup(title=_(cap_first_letter(strings.text['settings'])), size_hint=(0.8, 0.7), auto_dismiss=False)
    courses_popup = Popup(title=_(cap_first_letter(strings.text['courses'])), size_hint=(0.8, 0.7), content=courses,
                          auto_dismiss=False)

    def __init__(self, app, **kwargs):
        super(Agenda, self).__init__(**kwargs)

        self.app = app

        self.top_menu_more = AgendaTopMenuDropDown(self)
        self.selected_date_dropdown = SelectedDateDropDown(self)

        self.about_popup.attach_to = self
        self.about_popup.content = AboutDialog(root=self)

        self.settings_popup.attach_to = self
        self.settings = settings
        self.settings.set_self_awareness(self.settings_popup)
        self.settings_popup.content = self.settings

        self.courses_popup.attach_to = self
        self.courses_settings = courses
        self.courses_settings.set_self_awareness(self.courses_popup)
        self.courses_popup.content = self.courses_settings

    def open_settings_dialog(self):
        self.settings_popup.open()
        self.top_menu_more.dismiss()

    def sync_all(self):
        print('sync')
        self.top_menu_more.dismiss()

    def display_courses(self):
        self.courses_popup.open()
        self.top_menu_more.dismiss()

    def display_schedule(self):
        print('schedule')
        self.top_menu_more.dismiss()

    def display_about(self):
        self.about_popup.title = _(strings.about['title'])
        self.about_popup.content.set_dialog_content(_(strings.about['text']).format(__appname__, __author__))
        self.about_popup.open()
        self.top_menu_more.dismiss()

    def display_next_day(self):
        self.selected_date += datetime.timedelta(days=1)
        self.selected_day_button.text = self.format_selected_date()

    def display_prev_day(self):
        self.selected_date -= datetime.timedelta(days=1)
        self.selected_day_button.text = self.format_selected_date()

    def new_activity(self):
        print('Installing translations...')
        translations['nl'].install(unicode=True)

    def open_top_menu_more(self, root):
        self.top_menu_more.on_translation()
        self.top_menu_more.open(root)

    def format_selected_date(self):
        today_full = datetime.datetime.today()
        today = datetime.datetime(year=today_full.year, month=today_full.month, day=today_full.day)
        yesterday_full = today - datetime.timedelta(days=1)
        yesterday = datetime.datetime(year=yesterday_full.year, month=yesterday_full.month, day=yesterday_full.day)
        tomorrow_full = today + datetime.timedelta(days=1)
        tomorrow = datetime.datetime(year=tomorrow_full.year, month=tomorrow_full.month, day=tomorrow_full.day)
        if self.selected_date == today:
            return _(strings.date_name['today'])
        elif self.selected_date == yesterday:
            return _(strings.date_name['yesterday'])
        elif self.selected_date == tomorrow:
            return _(strings.date_name['tomorrow'])
        else:
            return self.selected_date.strftime('%d-%m %Y')


class AgendaTopMenuDropDown(DropDown):
    courses_text = StringProperty(cap_first_letter(_(strings.text['courses'])))
    schedule_text = StringProperty(cap_first_letter(_(strings.text['schedule'])))
    sync_text = StringProperty(cap_first_letter(_(strings.text['sync'])))
    about_text = StringProperty(cap_first_letter(_(strings.about['title'])))
    settings_text = StringProperty(cap_first_letter(_(strings.text['settings'])))

    def __init__(self, app):
        super(AgendaTopMenuDropDown, self).__init__()

        self.auto_width = False

        self.app = app

    def on_translation(self):
        self.courses_text = cap_first_letter(_(strings.text['courses']))
        self.schedule_text = cap_first_letter(_(strings.text['schedule']))
        self.sync_text = cap_first_letter(_(strings.text['sync']))
        self.about_text = cap_first_letter(_(strings.about['title']))
        self.settings_text = cap_first_letter(_(strings.text['settings']))


class SelectedDateDropDown(DropDown):
    def __init__(self, app):
        super(SelectedDateDropDown, self).__init__()

        self.auto_width = False

        self.app = app


class AboutDialog(BoxLayout):
    root = ObjectProperty(None)
    dialog_content = StringProperty('')

    def __init__(self, **kwargs):
        super(AboutDialog, self).__init__(**kwargs)

    def dismiss_dialog(self):
        self.root.about_popup.dismiss()

    def set_dialog_content(self, dialog_content):
        self.dialog_content = dialog_content


class AgendaApp(App):
    def __init__(self, debug=False):
        super(AgendaApp, self).__init__()

        self.window = None
        self.profile = None
        self.debug = debug

        self.strings = strings

    def build(self):
        from kivy.base import EventLoop
        EventLoop.ensure_window()

        self.window = EventLoop.window
        self.title = __appname__

        return Agenda(self)

    def on_start(self):
        if self.debug and profiler_loaded:
            self.profile = cProfile.Profile()
            self.profile.enable()

    def on_stop(self):
        if self.debug and profiler_loaded:
            self.profile.disable()
            self.profile.dump_stats(path.join(self.user_data_dir, '{}.profile'.format(__appname__)))

    def on_pause(self):
        if self.debug and profiler_loaded:
            self.profile.dump_stats(path.join(self.user_data_dir, '{}.profile'.format(__appname__)))
        return True

    def on_resume(self):
        pass


if __name__ == '__main__':
    AgendaApp().run()