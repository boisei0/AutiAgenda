import kivy
kivy.require('1.8.0')

from kivy.uix.label import Label
from kivy.uix.popup import Popup


class DebugTools:
    def __init__(self):
        pass

    @staticmethod
    def alert(msg, parent):
        popup = Popup(title='debug', content=Label(text=str(msg)), attach_to=parent, size_hint=(0.7, 0.8))
        popup.open()