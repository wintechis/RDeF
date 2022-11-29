from typing import Tuple

import kivy

kivy.require("2.0.0")

import webbrowser

from behaviors import HoverBehavior
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import (
    BooleanProperty,
    ListProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.behaviors import ButtonBehavior, DragBehavior
from kivy.uix.label import Label
from kivy.uix.stacklayout import StackLayout
from kivy.uix.widget import Widget

kv_file = f'{__file__[: __file__.rfind(".")]}.kv'
if not kv_file in Builder.files:
    Builder.load_file(kv_file)  # load kv file with same name of py file in same dir


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
        self.opacity = 100 - 100 * val


class ConstraintLabel(HoverBehavior, Label):
    tooltip: ObjectProperty(Tooltip)

    def on_enter(self, *args):
        if self.is_shortened:
            self.tooltip.hidden = False

    def on_leave(self, *args):
        self.tooltip.hidden = True


class HyperLinkLabel(HoverBehavior, ButtonBehavior, Label):
    url = StringProperty("")
    tooltip = ObjectProperty(Tooltip)

    def __init__(self, url: str = "", text: str = "", **kwargs):
        super().__init__(**kwargs)
        self.url = url
        self.text = text
        self.color_visited = (102 / 255, 51 / 255, 102 / 255, 1)

    def on_press(self):
        self._open_link()

    def _open_link(self):
        try:
            webbrowser.open(self.url, 1)
        except webbrowser.Error as e:
            Logger.error(f'Failed to open url "{self.url}"')


class NormalLabel(Label):
    pass


class PlaceholderLabel(Label):
    highlight = BooleanProperty(False)


class DragLabel(DragBehavior, PlaceholderLabel):
    def __init__(
        self,
        drag_area: Widget = None,
        start_area: Widget = None,
        query_area: Widget = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.drag_area = drag_area
        self.query_area = query_area
        self.start_area = start_area
        self.cur_placeholder = None
        self.cur_line = None
        self.again = False

    def on_touch_down(self, touch):
        if not self.collide_point(*self.to_parent(*touch.pos)):
            return
        if not self.drag_area:
            self.drag_area = self.parent
        self.last_pos = self.pos[:]
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        line, placeholder = self.get_first_colliding_placeholder_pair()
        if not placeholder == self.cur_placeholder:
            if not self.cur_placeholder == None:
                self.cur_placeholder.highlight = False
            self.cur_line, self.cur_placeholder = line, placeholder
            if not self.cur_placeholder == None:
                self.cur_placeholder.highlight = True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if not self.collide_point(*self.to_parent(*touch.pos)):
            return
        if not self.is_within(self.drag_area):
            self.x, self.y = self.last_pos
        self.switch_with_placeholder()
        return super().on_touch_up(touch)

    def is_within(self, widget: Widget):
        x, y, w, h = *self.to_widget(*widget.to_window(*widget.pos)), *widget.size
        return (self.x > x and self.x + self.width < x + w) and (
            self.y > y and self.y + self.height < y + h
        )

    def switch_with_placeholder(self):
        if self.parent in self.query_area.children:
            self.replace_with_placeholder()
        # Otherwise draglabel cannot directly move from query space to placeholder because second add_widget is not considered for next frame
        Clock.schedule_once(self.replace_placeholder)

    def replace_with_placeholder(self):
        line = self.parent
        i = line.children.index(self)
        self.switch_area(line, self.start_area, i)
        line.add_widget(PlaceholderLabel(text="  " * self.query_area.max_len), index=i)
        # i = self.query_area.children.index(self)
        # self.switch_area(self.query_area, self.start_area, i)
        # self.query_area.add_widget(PlaceholderLabel(text='  '*self.query_area.max_len), index=i)

        # sort alphabetically
        self.start_area.children.sort(key=lambda c: c.text.lower(), reverse=True)

    def replace_placeholder(self, dt):
        line, ph = self.cur_line, self.cur_placeholder
        if not ph:
            return
        self.switch_area(self.start_area, line, line.children.index(ph))
        line.remove_widget(ph)
        # self.switch_area(self.start_area,self.query_area, self.query_area.children.index(ph))
        # self.query_area.remove_widget(ph)
        self.cur_placeholder = None

    def switch_area(self, origin: Widget, target: Widget, idx: int):
        origin.remove_widget(self)
        target.add_widget(self, index=idx)

    def get_first_colliding_placeholder_pair(
        self,
    ) -> Tuple[StackLayout, PlaceholderLabel]:
        for line in self.query_area.children:
            for label in line.children:
                if type(label) == PlaceholderLabel and self.collide_with(label):
                    return (line, label)
        return None, None

    def collide_with(self, wd: Widget):
        x, y, w, h = *self.to_widget(*wd.to_window(*wd.pos)), *wd.size
        if self.right < x:
            return False
        if self.x > x + w:
            return False
        if self.top < y:
            return False
        if self.y > y + h:
            return False
        return True


class InfoLabel(Label):
    rdf_box = ObjectProperty(None)
    found_triples = ListProperty([])
    cleared = ObjectProperty(False)
    count_label = ObjectProperty()
    # all_triples = ListProperty([])


class TripleLabel(HoverBehavior, ButtonBehavior, NormalLabel):
    background_color = ListProperty()
    keyword = StringProperty()
    activated = True

    def on_press(self):
        if self.activated:
            self.parent.detect_triple(self)

    def activate(self, activate: bool):
        self.hover_enabled = self.activated = activate
        self.background_color = [0.5, 0.5, 0.5, 0.5]
        self.dispatch("on_leave")


class CenteredLabel(Label):
    pass


from kivy.factory import Factory

Factory.register("HyperLinkLabel", HyperLinkLabel)
Factory.register("ConstraintLabel", ConstraintLabel)
Factory.register("PlaceholderLabel", PlaceholderLabel)
Factory.register("DragLabel", DragLabel)
Factory.register("InfoLabel", InfoLabel)
Factory.register("NormalLabel", NormalLabel)
Factory.register("TripleLabel", TripleLabel)
Factory.register("CenteredLabel", CenteredLabel)
