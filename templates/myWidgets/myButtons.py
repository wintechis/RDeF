import kivy

kivy.require("2.0.0")


from behaviors import HoverBehavior
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.button import Button

kv_file = f'{__file__[: __file__.rfind(".")]}.kv'
if not kv_file in Builder.files:
    Builder.load_file(kv_file)  # load kv file with same name of py file in same dir


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

Factory.register("RectangledButton", RectangledButton)
Factory.register("SelectButton", SelectButton)
