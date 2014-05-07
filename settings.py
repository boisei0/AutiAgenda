import kivy
kivy.require('1.8.0')

from kivy.app import App
from kivy.compat import string_types
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import ListProperty, ObjectProperty, NumericProperty, DictProperty, StringProperty

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.popup import Popup
from kivy.uix.settings import SettingItem, SettingSpacer, SettingString, SettingBoolean, SettingNumeric, \
    SettingOptions, SettingTitle, SettingPath, SettingsPanel
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

import json

from dbhandler import DBHandler
from strings import TextData, cap_first_letter

__author__ = 'Rob Derksen (boisei0)'

dbh = DBHandler()
strings = TextData()

Builder.load_file('customwidgets.kv')
Builder.sync()


class CustomSettings(BoxLayout):
    """Settings UI. Check module documentation for more information on how
    to use this class.

    :Events:
        `on_config_change`: ConfigParser instance, section, key, value
            Fired when section/key/value of a ConfigParser changes.
        `on_close`
            Fired by the default panel when the Close button is pressed.
        `on_add_course`
            Fired by the default panel when the Add Course button is pressed.
        """

    interface = ObjectProperty(None)
    '''(internal) Reference to the widget that will contain, organise and
    display the panel configuration panel widgets.

    :attr:`interface` is an :class:`~kivy.properties.ObjectProperty` and
    defaults to None.

    '''

    interface_cls = ObjectProperty('CustomInterfaceWithSpinner')
    '''The widget class that will be used to display the graphical
    interface for the settings panel. By default, it displays one Settings
    panel at a time with a sidebar to switch between them.

    :attr:`interface_cls` is an
    :class:`~kivy.properties.ObjectProperty` and defaults to
    :class`CustomInterfaceWithSidebar`.

    .. versionchanged:: 1.8.0 / AutiAgenda 0.2

        If you set a string, the :class:`~kivy.factory.Factory` will be used to
        resolve the class.

    '''

    __events__ = ('on_close', 'on_config_change', 'on_add_course', )

    def __init__(self, *args, **kwargs):
        self._types = {}
        super(CustomSettings, self).__init__(**kwargs)
        self.add_interface()
        self.register_type('string', SettingString)
        self.register_type('bool', SettingBoolean)
        self.register_type('numeric', SettingNumeric)
        self.register_type('options', SettingOptions)
        self.register_type('title', SettingTitle)
        self.register_type('path', SettingPath)
        self.register_type('color', SettingColor)
        self.register_type('dynstring', DynamicStringSetting)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            super(CustomSettings, self).on_touch_down(touch)
            return True

    def register_type(self, tp, cls):
        """Register a new type that can be used in the JSON definition.
        """
        self._types[tp] = cls

    def on_close(self):
        dbh.courses_ini_to_db()
        self.parent.parent.parent.attach_to.ids['agenda_layout'].__self__.on_update()
        self.parent.parent.parent.dismiss()

    def add_interface(self):
        """(Internal) creates an instance of :attr:`Settings.interface_cls`,
        and sets it to :attr:`~Settings.interface`. When json panels are
        created, they will be added to this interface which will display them
        to the user.
        """
        cls = self.interface_cls
        if isinstance(cls, string_types):
            cls = Factory.get(cls)
        interface = cls()
        self.interface = interface
        self.add_widget(interface)
        self.interface.bind(on_close=lambda j: self.dispatch('on_close'))
        if isinstance(self.interface, CustomInterfaceWithSpinner):
            self.interface.bind(on_add_course=lambda j: self.dispatch('on_add_course'))

    def on_config_change(self, config, section, key, value):
        pass

    def add_json_panel(self, title, config, filename=None, data=None):
        """Create and add a new :class:`SettingsPanel` using the configuration
        `config` with the JSON definition `filename`.

        Check the :ref:`settings_json` section in the documentation for more
        information about JSON format and the usage of this function.
        """
        panel = self.create_json_panel(title, config, filename, data)
        uid = panel.uid
        if self.interface is not None:
            self.interface.add_panel(panel, title, uid)

    def create_json_panel(self, title, config, filename=None, data=None):
        """Create new :class:`SettingsPanel`.

        .. versionadded:: 1.5.0

        Check the documentation of :meth:`add_json_panel` for more information.
        """
        if filename is None and data is None:
            raise Exception('You must specify either the filename or data')
        if filename is not None:
            with open(filename, 'r') as fd:
                data = json.loads(fd.read())
        else:
            data = json.loads(data)
        if type(data) != list:
            raise ValueError('The first element must be a list')
        panel = SettingsPanel(title=title, settings=self, config=config)

        for setting in data:
            # determine the type and the class to use
            if not 'type' in setting:
                raise ValueError('One setting are missing the "type" element')
            ttype = setting['type']
            cls = self._types.get(ttype)
            if cls is None:
                raise ValueError(
                    'No class registered to handle the <%s> type' %
                    setting['type'])

            # create a instance of the class, without the type attribute
            del setting['type']
            str_settings = {}
            for key, item in setting.items():
                str_settings[str(key)] = item

            instance = cls(panel=panel, **str_settings)

            # instance created, add to the panel
            panel.add_widget(instance)

        return panel

    def set_interface_text(self):
        self.interface.menu.close_button.text = cap_first_letter(_(strings.text['close']))

    def add_kivy_panel(self):
        """Add a panel for configuring Kivy. This panel acts directly on the
        kivy configuration. Feel free to include or exclude it in your
        configuration.

        See :meth:`~kivy.app.App.use_kivy_settings` for information on
        enabling/disabling the automatic kivy panel.

        """
        from kivy import kivy_data_dir
        from kivy.config import Config
        from os.path import join
        self.add_json_panel('Kivy', Config,
                            join(kivy_data_dir, 'settings_kivy.json'))

    def on_add_course(self):
        print('hi')


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
        pass

    def get_full_courses_json(self):
        no_courses = dbh.get_no_courses()
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


class CustomInterfaceWithSpinner(BoxLayout):
    __events__ = ('on_close', 'on_add_course', )

    menu = ObjectProperty()
    '''(internal) A reference to the sidebar menu widget.

    :attr:`menu` is an :class:`~kivy.properties.ObjectProperty` and
    defauls to None.
    '''

    content = ObjectProperty()
    '''(internal) A reference to the panel display widget (a
    :class:`ContentPanel`).

    :attr:`menu` is an :class:`~kivy.properties.ObjectProperty` and
    defaults to None.

    '''

    def __init__(self, *args, **kwargs):
        super(CustomInterfaceWithSpinner, self).__init__(**kwargs)
        self.menu.close_button.bind(on_release=lambda j: self.dispatch('on_close'))
        self.menu.add_course_button.bind(on_release=lambda j: self.dispatch('on_add_course'))

    def add_panel(self, panel, name, uid):
        """This method is used by Settings to add new panels for possible
        display. Any replacement for ContentPanel *must* implement
        this method.

        :param panel: A :class:`SettingsPanel`. It should be stored
                      and the interface should provide a way to switch
                      between panels.

        :param name: The name of the panel as a string. It
                     may be used to represent the panel but may not
                     be unique.

        :param uid: A unique int identifying the panel. It should be
                    used to identify and switch between panels.

        """
        self.content.add_panel(panel, name, uid)
        self.menu.add_item(name, uid)

    def on_close(self, *args):
        pass

    def on_add_course(self, *args):
        pass


class CustomMenuSpinner(BoxLayout):
    """The menu class used by :class:`SettingsWithSpinner`. It provides a
    sidebar with an entry for each settings panel.

    This widget is considered internal and is not documented. See
    :class:`MenuSidebar` for information on menus and creating your own menu
    class.

    """
    selected_uid = NumericProperty(0)
    spinner = ObjectProperty()
    panel_names = DictProperty({})
    spinner_text = StringProperty()
    close_button = ObjectProperty()
    close_button_text = StringProperty()
    add_course_button = ObjectProperty()

    def add_item(self, name, uid):
        values = self.spinner.values
        if name in values:
            i = 2
            while name + ' {}'.format(i) in values:
                i += 1
            name = name + ' {}'.format(i)
        self.panel_names[name] = uid
        self.spinner.values.append(name)
        if not self.spinner.text:
            self.spinner.text = name

    def on_spinner_text(self, *args):
        text = self.spinner_text
        self.selected_uid = self.panel_names[text]