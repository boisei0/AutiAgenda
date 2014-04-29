import kivy
kivy.require('1.8.0')

from kivy.properties import ListProperty, ObjectProperty

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.popup import Popup
from kivy.uix.settings import Settings, SettingItem, SettingSpacer

__author__ = 'Rob Derksen (boisei0)'


class CustomSettings(Settings):
    def __init__(self, *args, **kwargs):
        super(CustomSettings, self).__init__(*args, **kwargs)
        self.self_awareness = None
        self.register_type('color', SettingColor)

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
        # create popup layout
        content = BoxLayout(orientation='vertical', spacing='5dp')
        self.popup = popup = Popup(
            title=self.title, content=content, size_hint=(None, None),
            size=('500dp', '400dp')
        )

        # create the colorpicker used for color input
        self.color_picker = color_picker = ColorPicker(
            text=self.value, font_size='24sp', multiline=False,
        )
        color_picker.bind(color=self._on_color)
        self.color_picker = color_picker

        # construct the content
        content.add_widget(color_picker)
        content.add_widget(SettingSpacer())

        # 2 buttons are created for accept or cancel the current value
        button_layout = BoxLayout(size_hint_y=None, height='50dp', spacing='5dp')
        btn = Button(text='Ok')
        btn.bind(on_release=self._validate)
        button_layout.add_widget(btn)
        btn = Button(text='Cancel')
        btn.bind(on_release=self._dismiss)
        button_layout.add_widget(btn)
        content.add_widget(button_layout)

        # all done, open the popup !
        popup.open()