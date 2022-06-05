from ast import keyword
from cgitb import reset
from dataclasses import dataclass
from multiprocessing.sharedctypes import Value
from random import choice
from typing import List, Literal
from xml.dom import NotFoundErr
from xmlrpc.client import Boolean
from kivy.uix.screenmanager import Screen
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.label import Label
import re
from typing import Tuple, Dict


import rdflib.plugin

from kivy.properties import ObjectProperty, ListProperty, BooleanProperty,NumericProperty, DictProperty, StringProperty
from kivy.uix.behaviors import FocusBehavior, ButtonBehavior
from kivy.clock import Clock
from kivy.app import App
from kivy.core.window import Window
import rdflib
import re
from templates.queryScene import NormalLabel
from behaviors import HoverBehavior
#from rdflib.query import Result

if not __name__ == '__main__':
    from kivy.lang import Builder
    Builder.load_file('templates/talk.kv')


#UP       = 273
#DOWN     = 274
#LEFT     = 276
#RIGHT    = 275
#SPACE    = 32

@dataclass(frozen=True)
class Speaker:
    name: str
    depiction: str


@dataclass(frozen=True)
class TalkItem:
    speaker: Speaker
    text: str
    triples: Dict[str, List[str]]


@dataclass(frozen=True)
class TalkInfo:
    dialogue: List[TalkItem]
    background: str
    

class TalkScene(Screen):
    graph = ObjectProperty()            # rdflib.Graph that returns RDF data to current episode graph / triggers assignment on value change.
    index: int = NumericProperty(0)      # update.talk() executes when index changes

    ################################################################################
    # Widget variables
    view_talk = ObjectProperty()        # widget with textual dialogue and hidden tripples
    rdf_displayer = ObjectProperty()    # widget that shows RDF data in Turtle, XML and JSON-LD format
    btn_continue: ObjectProperty()      # Next button 

    ################################################################################
    # Dataclass Variables
    dialogue: List[TalkItem] = ListProperty()   # stores Talkinfo.dialogue
    background = StringProperty()               # stores current Talkinfo.background (file path)
    
    speaker_name = StringProperty()             # stores current Speaker.name
    depiction =  StringProperty()               # stores current Speaker.depiction
    
    talk = StringProperty()                     # stores current Talkitem.text
    triples = ListProperty()                    # stores current Talkitem.triples
      
    def __init__(self, talk_info: TalkInfo, **kwargs):
        super().__init__(**kwargs)
        # Initalize variables static for all Talkitems
        self.g = rdflib.Graph()
        self.dialogue = talk_info.dialogue
        self.background = talk_info.background
        self.finished = False
     
        # Bind functions
        self.bind(index=lambda self, value:self.next_talk_item(value))     # execute update.talk() when index changes
        self.view_talk.bind(found_triples=self.update_displayer)        # add triple to RDF displayer
        self.btn_continue.bind(on_release=self.update_index)            # next scene

        # Initalize Talkitem specific variables 
        self.next_talk_item(self.index)
        self.view_talk.triples_labels = self.triples
        #self.view_talk.bind(triples=self.triple_was_found)     # TODO delete after test / obsolete
        
    def update_index(self, *args):
        self.index += 1

    def next_talk_item(self, idx: int):
        # load next talk item, if not end of scene  
        if self.end_talk_scene(idx): return
        self.speaker_name = self.dialogue[idx].speaker.name
        self.depiction = self.dialogue[idx].speaker.depiction
        self.triples = self.dialogue[idx].triples
        self.talk = self.dialogue[idx].text
        # enable next button, if no hidden triples
        self.btn_continue.disabled = (len(self.triples) != 0)

    def end_talk_scene(self, idx) -> bool:
        # closes Talkscene by assigning valuie to self.graph
        is_end = len(self.dialogue) <= idx
        if is_end: self.graph = self.g
        return is_end

    def update_displayer(self, instance, triple):
        if not triple: return
        temp = []
        for t in triple:
            if re.search('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', t):
                temp.append(rdflib.URIRef(t))
            else:
                temp.append(rdflib.Literal(t))
        self.g.add((temp[0], temp[1], temp[2]))

        if len(self.g) > 0:
            for tab in self.rdf_displayer.tab_list:
                tab.content.text = self.g.serialize(format=tab.text.lower())
        if len(self.view_talk.triples) == 0: self.btn_continue.disabled = False


    #def triple_was_found(self, instance, remaining_triples):
    #    if len(remaining_triples) < 1: self.index += 1


    ######################################################################################################
    # Enable space bar press for talk continuation
    def on_enter(self, *args):
        # allow use of space bar to continue
        Window.bind(on_key_down=self.check_for_space)

    def on_leave(self, *args):
        # decouple use of space bar with Talkscene
        Window.unbind(on_key_down=self.check_for_space)

    def check_for_space(self, *args): #keyboard_on_key_down(self, window, keycode , text, modifiers):
        #TODO replace with window keydown event and remove focusbehavior
        keycode = args[1]
        if keycode == 32 and len(self.view_talk.triples) == 0 : self.update_index() #'spacebar'
        #return super().keyboard_on_key_down(window, keycode,text, modifiers)


# class RdfDisplayer(TabbedPanel):
#     triples = ListProperty()
#     boxes = DictProperty(None)
 
# class DialogueBox(BoxLayout):
#     pass


class TripleLabel(HoverBehavior, ButtonBehavior, NormalLabel):
    background_color = ListProperty()
    keyword = StringProperty()
    activated = True
    
    def on_press(self):
        if self.activated: self.parent.detect_triple(self)

    def activate(self, activate: bool):
        self.hover_enabled = self.activated = activate
        self.background_color = [0.5,0.5,0.5,0.5]
        self.dispatch('on_leave')
        
       
       
class TalkView(StackLayout):
    text = StringProperty()
    triples = ListProperty()
    found_triples = ListProperty()
    triples_labels = []
    cur_triple = {}
    allowed_triples = []
    lbls = {}

    colors = [[1,0,0,0.5],[0,0,1,0.5], [0,1,0,0.5]]    #highlighting triplelabel background: Red, Blue, Green

    def on_text(self, *args):
        self.update_labels()


    def replace_blank_spaces(self, txt:str, spaceholder: str) -> str:
        pattern = '(\[[^\]]+\]){1}(\([^\)]+\))?' # [...] or [...](...)
        matches = re.findall(pattern, txt) # [0]: keyword, [1]: alias
        for match in matches:
            m = ''.join(match)
            txt = txt.replace(m, m.replace(' ', spaceholder))
        return txt

    def split_alias_punctuation_marks(self, word: str) -> Tuple[str, str, str]:
        mark = ''
        if word[-1] in '.,:;!?':
            word, mark = word[:-1], word[-1]
        try:
            word, alias = word.split('](')
            word = word[1:]
            alias = alias[:-1]
        except ValueError:
            word = alias = word[1:-1]
        return word, alias, mark

    def is_keyword(self, word:str) -> bool:
        return bool(re.search('(\[[^\]]+\]){1}(\([^\)]+\))?', word))

    def update_labels(self):
        self.clear_widgets()
        txt = self.text     # needed to avoid that on_text is called again
        spaceholder = '\u2334' #'\u2334' arch as spaceholder
        txt = self.replace_blank_spaces(txt, spaceholder)
        self.add_labels(txt.split())
    
    def add_labels(self, words: List[str]) -> None:
        for word in words:
            word = word.replace('\u2334', ' ')
            if self.is_keyword(word):
                word, alias, mark = self.split_alias_punctuation_marks(word)
                self.add_widget(TripleLabel(text=word + mark, keyword=alias))
                continue
            self.add_widget(NormalLabel(text=word))

          
    def detect_triple(self, lbl: TripleLabel):
        # [0] keywords, [1] URIs, [2] query
        for triple in self.triples:
            keywords = triple[0]
            for k in keywords.keys():
                if lbl.keyword == keywords[k]:
                    self.update_current_triple(lbl, k)

    def colorize_lbls(self, colorize: Boolean = True):
        for i, k in enumerate(('subject', 'predicate', 'object')):
            if k in self.lbls.keys():
                self.lbls[k].background_color = self.colors[i] if colorize else App.get_running_app().bg

    def get_current_uris(self):
        return list(map(lambda x: x.keyword if x else None, self.lst_triple))

    def update_current_triple(self, lbl: TripleLabel, term: str):
        self.colorize_lbls(False)
        
        self.cur_triple[term] = lbl.keyword
        self.add_triple_label_or_reset(lbl, term)

        if len(self.cur_triple) == 3:
            idx = self.get_found_triple_index()
            self.found_triples = self.triples.pop(idx)[1]
            self.deactivate_obsolete_labels()
            self.lbls = {}
        else:   
            self.colorize_lbls()

    def deactivate_obsolete_labels(self) -> None:
        for lbl in self.lbls.values():
            if any([lbl.keyword in triple[0].values() for triple in self.triples]):
                continue
            lbl.activate(False)

    def add_triple_label_or_reset(self, lbl: TripleLabel, term: str) -> None:
        if any([self.cur_triple.items() <= triple[0].items() for triple in self.triples]):
            self.lbls[term] = lbl
            return
        self.cur_triple = {term: lbl.keyword}
        self.lbls= {term: lbl}
        
           

    def get_found_triple_index(self) -> int:
        for i, triple in enumerate(self.triples):
            if self.cur_triple.items() <= triple[0].items():
                return i
        raise NotFoundErr

            
    def remove_completed_triple(self, triple: List[str]):
        for k, tri in enumerate(self.allowed_triples):
            i = 0
            for j in range(len(triple)):
                if tri[j] == triple[j] and triple[j] != None: i+=1
                if i == 3:
                    x = self.allowed_triples.pop(k)
                    self.triples.remove(x) 
                    self.found_triples = x
                    self.colorize_triple()
                    self.lst_triple = [None, None, None]

    
       