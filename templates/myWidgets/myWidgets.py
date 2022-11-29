import kivy

kivy.require("2.0.0")

from kivy.lang import Builder
from kivy.properties import DictProperty, ListProperty
from kivy.uix.codeinput import CodeInput
from kivy.uix.tabbedpanel import TabbedPanel

kv_file = f'{__file__[: __file__.rfind(".")]}.kv'
if not kv_file in Builder.files:
    Builder.load_file(kv_file)  # load kv file with same name of py file in same dir


class RdfDisplayer(TabbedPanel):
    triples = ListProperty(None)
    boxes = DictProperty(None)


class RdfDisplay(CodeInput):
    pass


from kivy.factory import Factory

Factory.register("RdfDisplayer", RdfDisplayer)
Factory.register("Rdf", RdfDisplay)
