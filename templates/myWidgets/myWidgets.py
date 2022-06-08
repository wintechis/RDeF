import kivy
kivy.require('2.0.0')

from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.codeinput import CodeInput
from kivy.properties import ListProperty, DictProperty

from kivy.lang import Builder
kv_file = f'{__file__[:-2]}kv'
if not kv_file in Builder.files: Builder.load_file(kv_file) # load kv file with same name of py file in same dir

class RdfDisplayer(TabbedPanel):
    triples = ListProperty(None)
    boxes = DictProperty(None)

class RdfDisplay(CodeInput):
    pass

from kivy.factory import Factory
Factory.register('RdfDisplayer', RdfDisplayer)
Factory.register('Rdf', RdfDisplay) 