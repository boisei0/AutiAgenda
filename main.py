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
from kivy.uix.settings import InterfaceWithSpinner

try:
    import cProfile
    profiler_loaded = True
except ImportError:
    profiler_loaded = False

import datetime
import gettext
from os import path

from datepicker import DatePicker
from dbhandler import DBHandler
from debug import DebugTools
from settings import CustomSettings, JSONData
from strings import TextData, get_locale, list_translations, cap_first_letter

__author__ = 'Rob Derksen (boisei0)'
__appname__ = 'AutiAgenda'
__version__ = '0.2'

base_path = path.dirname(path.abspath(__file__))

debug = DebugTools()

config_settings = ConfigParser()
config_settings.read(path.join(base_path, 'config', 'autiagenda.ini'))
settings = CustomSettings(interface_cls=InterfaceWithSpinner)
# settings.add_json_panel('Date / Time', config, 'datetime.json')
# TODO: Add settings / config later

config_courses = ConfigParser()
config_courses.read(path.join(base_path, 'config', 'courses.ini'))
courses = CustomSettings()

Factory.register('DatePicker', DatePicker)

domain = 'agenda'
locale_directory = base_path + "/locale"
gettext.bindtextdomain(domain, locale_directory)
gettext.textdomain(domain)
gettext.install(domain, localedir=locale_directory, unicode=True)

available_translations = list_translations()
translations = {}
for translation in available_translations:
    if gettext.find(domain, locale_directory, languages=[translation], all=1) is not None:
        translations[translation] = gettext.translation(domain, localedir=locale_directory, languages=[translation])

system_locale = get_locale()
if system_locale != 'en' and system_locale in translations.keys():
    translations[system_locale].install()

strings = TextData()
dbh = DBHandler()
json_data = JSONData()


class AgendaCore(BoxLayout):
    agenda_layout = ObjectProperty(None)

    selected_day_button = Button()
    today = datetime.datetime.today()
    selected_date = datetime.datetime(today.year, today.month, today.day)
    selected_day_text = StringProperty('Today')

    about_popup = Popup(size_hint=(0.6, 0.5), auto_dismiss=False)
    sync_dialog = Popup(size_hint=(0.7, 0.6), auto_dismiss=False)
    settings_popup = Popup(title=_(cap_first_letter(strings.text['settings'])), size_hint=(0.95, 0.7),
                           auto_dismiss=False)
    courses_popup = Popup(title=_(cap_first_letter(strings.text['courses'])), size_hint=(0.95, 0.7), auto_dismiss=False)

    def __init__(self, app, **kwargs):
        super(AgendaCore, self).__init__(**kwargs)

        self.app = app

        self.top_menu_more = AgendaTopMenuDropDown(self)
        self.selected_date_dropdown = SelectedDateDropDown()

        self.about_popup.attach_to = self
        self.about_popup.content = AboutDialog(root=self)

        self.sync_dialog.attach_to = self
        self.sync_dialog.content = SyncDialog(root=self)

        self.settings_popup.attach_to = self
        self.settings = settings
        self.settings_popup.content = self.settings

        self.courses_popup.attach_to = self
        self.courses_settings = courses
        for course_id in range(dbh.get_no_courses()):
            json = '[' + json_data.get_courses_json_by_course_id(course_id) + ']'
            self.courses_settings.add_json_panel(u'{} {}'.format(cap_first_letter(_(strings.text['course'])),
                                                 course_id), config_courses, data=json)
        self.courses_settings.set_interface_text()
        self.courses_popup.content = self.courses_settings

    def open_settings_dialog(self):
        self.settings_popup.open()
        self.top_menu_more.dismiss()

    def sync_all(self):
        print('sync')
        self.sync_dialog.open()
        self.top_menu_more.dismiss()

    def display_courses(self):
        self.courses_popup.open()
        self.top_menu_more.dismiss()

    def display_about(self):
        self.about_popup.title = _(strings.about['title'])
        self.about_popup.content.set_dialog_content(_(strings.about['text']).format(__appname__, __author__))
        self.about_popup.open()
        self.top_menu_more.dismiss()

    def display_next_day(self):
        self.selected_date += datetime.timedelta(days=1)
        self.selected_day_text = self.format_selected_date()

    def display_prev_day(self):
        self.selected_date -= datetime.timedelta(days=1)
        self.selected_day_text = self.format_selected_date()

    def display_schedule(self):
        print('schedule')
        self.top_menu_more.dismiss()

        print('Installing translations...')
        translations['po'].install(unicode=True)

        self._on_translate()

    def _on_translate(self):
        self.selected_date_dropdown.ids['date_picker'].__self__.on_translate()

        # override defaults
        self.courses_popup = Popup(title=cap_first_letter(_(strings.text['courses'])), size_hint=(0.95, 0.7),
                                   auto_dismiss=False)

        self.courses_popup.attach_to = self
        self.courses_settings = CustomSettings(interface_cls=InterfaceWithSpinner)

        for course_id in range(dbh.get_no_courses()):
            json = '[' + json_data.get_courses_json_by_course_id(course_id) + ']'
            self.courses_settings.add_json_panel(u'{} {}'.format(cap_first_letter(_(strings.text['course'])),
                                                 course_id), config_courses, data=json)
        self.courses_settings.set_interface_text()
        self.courses_popup.content = self.courses_settings

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
            month = _(strings.months[int(self.selected_date.strftime('%m'))])
            return self.selected_date.strftime(u'%d {} %Y'.format(month))


class AgendaTopMenuDropDown(DropDown):
    courses_text = StringProperty(cap_first_letter(_(strings.text['courses'])))
    schedule_text = StringProperty(cap_first_letter(_(strings.text['schedule'])))
    sync_text = StringProperty(cap_first_letter(_(strings.text['sync'])))
    about_text = StringProperty(cap_first_letter(_(strings.about['title'])))
    settings_text = StringProperty(cap_first_letter(_(strings.text['settings'])))

    def __init__(self, core):
        super(AgendaTopMenuDropDown, self).__init__()

        self.auto_width = False

        self.core = core

    def on_translation(self):
        self.courses_text = cap_first_letter(_(strings.text['courses']))
        self.schedule_text = cap_first_letter(_(strings.text['schedule']))
        self.sync_text = cap_first_letter(_(strings.text['sync']))
        self.about_text = cap_first_letter(_(strings.about['title']))
        self.settings_text = cap_first_letter(_(strings.text['settings']))


class SelectedDateDropDown(DropDown):
    def __init__(self):
        super(SelectedDateDropDown, self).__init__()

        self.auto_width = False


class AboutDialog(BoxLayout):
    root = ObjectProperty(None)
    dialog_content = StringProperty('')

    def __init__(self, **kwargs):
        super(AboutDialog, self).__init__(**kwargs)

    def dismiss_dialog(self):
        self.root.about_popup.dismiss()

    def set_dialog_content(self, dialog_content):
        self.dialog_content = dialog_content


class SyncDialog(BoxLayout):
    root = ObjectProperty(None)
    instruction_text = StringProperty('')
    token_text = StringProperty('')
    close_button_text = StringProperty('')

    def __init__(self, **kwargs):
        super(SyncDialog, self).__init__(**kwargs)

    def dismiss_dialog(self):
        self.root.sync_dialog.dismiss()


class AgendaApp(App):
    def __init__(self, debug_mode=False):
        super(AgendaApp, self).__init__()

        self.window = None
        self.profile = None
        self.debug = debug_mode

        self.strings = strings

    def build(self):
        from kivy.base import EventLoop
        EventLoop.ensure_window()

        self.window = EventLoop.window
        self.title = __appname__

        return AgendaCore(self)

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
    AgendaApp(debug_mode=True).run()
