import kivy
kivy.require('1.8.0')

from kivy.app import App
from kivy.config import ConfigParser
from kivy.properties import ObjectProperty

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.popup import Popup
from kivy.uix.settings import Settings
from kivy.uix.widget import Widget

__author__ = 'Rob Derksen (boisei0)'
__appname__ = 'AutiAgenda'

config = ConfigParser()
config.read('config/autiagenda.ini')

settings = Settings()
# TODO: Add settings / config later


class Agenda(Widget):
    selected_date = 'Today'
    about_popup = Popup(title='About...', size_hint=(0.3, 0.5), auto_dismiss=False)

    def __init__(self, **kwargs):
        super(Agenda, self).__init__(**kwargs)

        self.top_menu_more = AgendaTopMenuDropDown(self)
        self.selected_date_dropdown = SelectedDateDropDown(self)

        self.about_popup.attach_to = self
        self.about_popup.content = AboutDialog(root=self)

        self.settings = settings

    def open_settings_dialog(self):
        print('settings')
        settings.to_window(0, 0)
        self.top_menu_more.dismiss()

    def sync_all(self):
        print('sync')
        self.top_menu_more.dismiss()

    def display_courses(self):
        print('courses')
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