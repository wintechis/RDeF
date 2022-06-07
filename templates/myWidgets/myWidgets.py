import kivy
kivy.require('2.0.0')

from kivy.uix.tabbedpanel import TabbedPanel
from kivy.properties import ListProperty, DictProperty

from kivy.lang import Builder
Builder.load_file(f'{__file__[:-2]}kv') # load kv file with same name of py file in same dir

class RdfDisplayer(TabbedPanel):
    triples = ListProperty(None)
    boxes = DictProperty(None)


from kivy.factory import Factory
Factory.register('RdfDisplayer', RdfDisplayer) 