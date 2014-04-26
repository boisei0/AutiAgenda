import kivy
kivy.require('1.8.0')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.dropdown import DropDown

__author__ = 'boisei0'


class Agenda(Widget):
    def __init__(self, **kwargs):
        super(Agenda, self).__init__(**kwargs)

        self.top_menu_more = AgendaTopMenuDropDown(self)

    def open_settings_dialog(self):
        print('settings')
        self.top_menu_more.dismiss()

    def sync_all(self):
        print('sync')
        self.top_menu_more.dismiss()


class AgendaTopMenuDropDown(DropDown):
    def __init__(self, app):
        super(AgendaTopMenuDropDown, self).__init__()

        self.auto_width = False

        self.app = app


class AgendaApp(App):
    def __init__(self):
        super(AgendaApp, self).__init__()

        self.window = None

    def build(self):
        from kivy.base import EventLoop
        EventLoop.ensure_window()

        self.window = EventLoop.window

        return Agenda()


if __name__ == '__main__':
    AgendaApp().run()