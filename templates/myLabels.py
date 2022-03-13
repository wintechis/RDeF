import kivy
kivy.require('2.0.0')

from kivy.uix.label import Label
from kivy.uix.behaviors.button import ButtonBehavior
from behaviors import HoverBehavior
from kivy.properties import ObjectProperty, StringProperty
import webbrowser
from kivy.lang import Builder
from kivy.logger import Logger

Builder.load_file('templates/myLabels.kv')


class Tooltip(Label):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._hidden = True

    @property
    def hidden(self) -> bool:
        return self._hidden

    @hidden.setter
    def hidden(self, val: bool) -> None:
        if not self._hidden == val:
            self._hide_me(val)
            self._hidden = val

    def _hide_me(self, val: bool) -> None:
        self.disabled = val
        self.opacity = 100 - 100*val

    
class ConstraintLabel(HoverBehavior, Label):
    tooltip: ObjectProperty(Tooltip)

    def on_enter(self, *args):
        if self.is_shortened: self.tooltip.hidden = False

    def on_leave(self, *args):
        self.tooltip.hidden = True


class HyperLinkLabel(HoverBehavior, ButtonBehavior, Label):
    url = StringProperty('')
    tooltip = ObjectProperty(Tooltip)

    def __init__(self, url: str='', text: str='', **kwargs):
        super().__init__(**kwargs)
        self.url = url
        self.text = text
        self.color_visited = (102/255,51/255,102/255, 1)

    def on_press(self):
        self._open_link()


    def _open_link(self):
        try:
            webbrowser.open(self.url, 1)
        except webbrowser.Error as e:
            Logger.error(f'Failed to open url "{self.url}"')


from kivy.factory import Factory
Factory.register('HyperLinkLabel', HyperLinkLabel) 
Factory.register('ConstraintLabel', ConstraintLabel)

