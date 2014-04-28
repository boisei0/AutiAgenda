import kivy
kivy.require('1.8.0')

from kivy.app import App
from kivy.config import ConfigParser
from kivy.factory import Factory
from kivy.properties import ObjectProperty

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.popup import Popup
from kivy.uix.settings import InterfaceWithSidebar
from kivy.uix.widget import Widget

from datepicker import DatePicker
from settings import CustomSettings

__author__ = 'Rob Derksen (boisei0)'
__appname__ = 'AutiAgenda'

config_settings = ConfigParser()
config_settings.read('config/autiagenda.ini')
settings = CustomSettings(interface_cls=InterfaceWithSidebar)
# settings.add_json_panel('Date / Time', config, 'datetime.json')
# TODO: Add settings / config later

config_courses = ConfigParser()
config_courses.read('config/courses.ini')
courses = CustomSettings(interface_cls=InterfaceWithSidebar)
courses.add_json_panel('Course 1', config_courses, 'config/courses.json')

Factory.register('DatePicker', DatePicker)


class Agenda(Widget):
    selected_date = 'Today'
    about_popup = Popup(title='About...', size_hint=(0.3, 0.5), auto_dismiss=False)
    settings_popup = Popup(title='Settings', size_hint=(0.8, 0.7), auto_dismiss=False)
    courses_popup = Popup(title='Courses', size_hint=(0.8, 0.7), content=courses, auto_dismiss=False)

    def __init__(self, **kwargs):
        super(Agenda, self).__init__(**kwargs)

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
        self.about_popup.open()
        self.top_menu_more.dismiss()

    def display_next_day(self):
        pass

    def display_prev_day(self):
        pass

    def new_activity(self):
        pass


class AgendaTopMenuDropDown(DropDown):
    def __init__(self, app):
        super(AgendaTopMenuDropDown, self).__init__()

        self.auto_width = False

        self.app = app


class SelectedDateDropDown(DropDown):
    def __init__(self, app):
        super(SelectedDateDropDown, self).__init__()

        self.auto_width = False

        self.app = app


class AboutDialog(BoxLayout):
    root = ObjectProperty(None)
    dialog_content = '{} was made by {} for the Kivy App Contest 2014.'.format(__appname__, __author__)

    def __init__(self, **kwargs):
        super(AboutDialog, self).__init__(**kwargs)

    def dismiss_dialog(self):
        self.root.about_popup.dismiss()


class AgendaApp(App):
    def __init__(self):
        super(AgendaApp, self).__init__()

        self.window = None

    def build(self):
        from kivy.base import EventLoop
        EventLoop.ensure_window()

        self.window = EventLoop.window
        self.title = __appname__

        return Agenda()


if __name__ == '__main__':
    AgendaApp().run()