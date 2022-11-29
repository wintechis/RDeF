from kivy.core.window import Window
from kivy.properties import BooleanProperty, ObjectProperty


class HoverBehavior(object):
    # Optimized from https://programmer.help/blogs/implementation-of-hover-event-in-kivy-control.html
    # and https://stackoverflow.com/questions/61055633/how-to-create-a-custom-title-bar-in-kivy

    is_hovering = BooleanProperty(False)
    border_point = ObjectProperty(None)
    hover_enabled = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type("on_enter")
        self.register_event_type("on_leave")
        Window.bind(mouse_pos=self.on_mouse_pos)
        # self.pos = 0,0

    def on_mouse_pos(self, *args):
        if not self.get_root_window() or not self.hover_enabled:
            return
        pos = args[1]
        # self.pos = pos
        is_colliding = self.collide_point(*self.to_widget(*pos))
        if self.is_hovering == is_colliding:
            return
        self.is_hovering = is_colliding
        self.border_point = pos
        self.dispatch("on_enter") if is_colliding else self.dispatch("on_leave")

    ##  Reuse Functions for functionality
    def on_enter(self, *args):
        Window.set_system_cursor("hand")

    def on_leave(self, *args):
        Window.set_system_cursor("arrow")


from kivy.factory import Factory

Factory.register("HoverBehavior", HoverBehavior)
