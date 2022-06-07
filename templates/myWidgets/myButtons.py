import kivy
kivy.require('2.0.0')


from kivy.uix.button import Button
from kivy.app import App
from kivy.lang import Builder

from behaviors import HoverBehavior

Builder.load_file(f'{__file__[:-2]}kv') # load kv file with same name of py file in same dir


class RectangledButton(HoverBehavior, Button):
  
    ##  Reuse Functions for functionality
    def on_enter(self, *args):
        self.background_color = App.get_running_app().hl
        return super().on_enter(*args)

    def on_leave(self, *args):
        self.background_color = App.get_running_app().bg
        return super().on_leave(*args)

class SelectButton(RectangledButton):
    pass


from kivy.factory import Factory
Factory.register('RectangledButton', RectangledButton) 
Factory.register('SelectButton', SelectButton)
