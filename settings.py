import kivy
kivy.require('1.8.0')

from kivy.app import App
from kivy.properties import ListProperty, ObjectProperty

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.popup import Popup
from kivy.uix.settings import Settings, SettingItem, SettingSpacer, SettingString
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from dbhandler import DBHandler
from strings import TextData

__author__ = 'Rob Derksen (boisei0)'

strings = TextData()


class CustomSettings(Settings):
    self_awareness = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(CustomSettings, self).__init__(*args, **kwargs)
        self.register_type('color', SettingColor)
        self.register_type('dynstring', DynamicStringSetting)

    def on_close(self):
        self.self_awareness.dismiss()

    def set_self_awareness(self, self_awareness_object):
        self.self_awareness = self_awareness_object


class SettingColor(SettingItem):
    popup = ObjectProperty(None, allownone=True)
    color_store = ListProperty(None)
    color_picker = ObjectProperty(None)

    def on_panel(self, instance, value):
        if value is None:
            return
        self.bind(on_release=self._create_popup)

    def _dismiss(self, *largs):
        if self.color_picker:
            self.color_picker.focus = False
        if self.popup:
            self.popup.dismiss()
        self.popup = None

    def _on_color(self, instance, value):
        self.color_store = instance.color

    def _validate(self, instance):
        self._dismiss()
        self.value = self.color_store

    def _create_popup(self, instance):
        app = App.get_running_app()
        # create popup layout
        content = BoxLayout(orientation='vertical', spacing='5dp')
        self.popup = popup = Popup(title=self.title, content=content, size_hint=(None, None),
                                   size=(app.window.width * .9, app.window.height * .9))

        # create the colorpicker used for color input
        self.color_picker = color_picker = ColorPicker(text=self.value, font_size='24sp', multiline=False)
        color_picker.bind(color=self._on_color)
        self.color_picker = color_picker

        # construct the content
        content.add_widget(color_picker)
        content.add_widget(SettingSpacer())

        # 2 buttons are created for accept or cancel the current value
        button_layout = BoxLayout(size_hint_y=None, height=app.window.height * .075, spacing=app.window.height * .025)
        btn = Button(text='Ok')
        btn.bind(on_release=self._validate)
        button_layout.add_widget(btn)
        btn = Button(text='Cancel')
        btn.bind(on_release=self._dismiss)
        button_layout.add_widget(btn)
        content.add_widget(button_layout)

        # all done, open the popup !
        popup.open()


class DynamicStringSetting(SettingString):
    def _create_popup(self, instance):
        app = App.get_running_app()
        # create popup layout
        content = BoxLayout(orientation='vertical', spacing='5dp')
        self.popup = popup = Popup(title=self.title, content=content, size_hint=(None, None),
                                   size=(app.window.width * .6, app.window.height * .3))

        # create the textinput used for numeric input
        self.textinput = textinput = TextInput(text=self.value, font_size='24sp', multiline=False, size_hint_y=None,
                                               height='42sp')
        textinput.bind(on_text_validate=self._validate)
        self.textinput = textinput

        # construct the content, widget are used as a spacer
        content.add_widget(Widget())
        content.add_widget(textinput)
        content.add_widget(Widget())
        content.add_widget(SettingSpacer())

        # 2 buttons are created for accept or cancel the current value
        button_layout = BoxLayout(size_hint_y=None, height=app.window.height * .075, spacing=app.window.height * .025)
        btn = Button(text='Ok')
        btn.bind(on_release=self._validate)
        button_layout.add_widget(btn)
        btn = Button(text='Cancel')
        btn.bind(on_release=self._dismiss)
        button_layout.add_widget(btn)
        content.add_widget(button_layout)

        # all done, open the popup !
        popup.open()


class JSONData:
    def __init__(self):
        self.dbh = DBHandler()

    def get_full_courses_json(self):
        no_courses = self.dbh.get_no_courses()
        if no_courses == 0:
            return '[]'
        json = '['
        for i in range(no_courses):
            json += self.get_courses_json_by_course_id(i)
            if i != (no_courses - 1):
                json += ','
        json += ']'
        return json

    @staticmethod
    def get_courses_json_by_course_id(course_id):
        json = '{{"type": "dynstring", ' \
               u'"title": "{}", ' \
               u'"desc": "{}", ' \
               '"section": "course{}", ' \
               '"key": "name" ' \
               '}},'.format(_(strings.courses_dialog['name_title']), _(strings.courses_dialog['name_descr']), course_id)
        json += '{{"type": "dynstring", ' \
                u'"title": "{}", ' \
                u'"desc": "{}", ' \
                '"section": "course{}", ' \
                '"key": "abbr"' \
                '}},'.format(_(strings.courses_dialog['abbr_title']), _(strings.courses_dialog['abbr_descr']), course_id)
        json += '{{"type": "color", ' \
                u'"title": "{}", ' \
                u'"desc": "{}", ' \
                '"section": "course{}", ' \
                '"key": "color"' \
                '}},'.format(_(strings.courses_dialog['col_title']), _(strings.courses_dialog['col_descr']), course_id)
        json += '{{"type": "bool", ' \
                u'"title": "{}", ' \
                u'"desc": "{}?", ' \
                '"section": "course{}", ' \
                '"key": "active"' \
                '}}'.format(_(strings.courses_dialog['active_title']), _(strings.courses_dialog['active_descr']), course_id)
        return json