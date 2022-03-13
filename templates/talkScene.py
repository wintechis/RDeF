from dataclasses import dataclass
from multiprocessing.sharedctypes import Value
from random import choice
from typing import List, Literal
from xmlrpc.client import Boolean
from kivy.uix.screenmanager import Screen
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.label import Label
import re

import rdflib.plugin

from kivy.properties import ObjectProperty, ListProperty, BooleanProperty,NumericProperty, DictProperty, StringProperty
from kivy.uix.behaviors import FocusBehavior, ButtonBehavior
from kivy.clock import Clock
from kivy.app import App
from kivy.core.window import Window
import rdflib
import re
from templates.queryScene import NormalLabel
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
    triples: List[str]

@dataclass(frozen=True)
class TalkInfo:
    dialogue: List[TalkItem]
    background: str
    

class TalkScene(Screen):
    lst_episodes = ListProperty()
    dialogue: List[TalkItem] = ListProperty()
    index: int = NumericProperty()

    speaker_name = StringProperty()
    background = StringProperty()
    depiction =  StringProperty()
    talk = StringProperty()
    triples = ListProperty()

    view_talk = ObjectProperty()
    rdf_displayer = ObjectProperty()

    def __init__(self, talk_info: TalkInfo, idx: ListProperty, **kwargs):
        super().__init__(**kwargs)
        self.g = rdflib.Graph()
        self.idx = idx
        self.dialogue = talk_info.dialogue
        self.background = talk_info.background
        self.index = 0
        self.focus = True
        self.bind(index=lambda self, value:self.update_talk(value))
        self.update_talk(self.index)
        self.view_talk.bind(triples=self.triple_was_found)
        self.view_talk.bind(found_triples=self.update_displayer)
        self.finished = False
        
        #just for image
        self.update_displayer(self, '')
       
    def on_enter(self, *args):
        Window.bind(on_key_down=self.update_index)



    def on_leave(self, *args):
        Window.unbind(on_key_down=self.update_index)



    def update_displayer(self, instance, triple):
        if not triple: return
        print('triple', triple)
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

    def update_talk(self, idx: int):
        if len(self.dialogue) <= idx:
            if not self.finished:
                self.finished = True
                self.idx[0] += 1
            return
        self.speaker_name = self.dialogue[idx].speaker.name
        self.depiction = self.dialogue[idx].speaker.depiction
        self.talk = self.dialogue[idx].text
        self.triples = self.dialogue[idx].triples

    def triple_was_found(self, instance, remaining_triples):
        if len(remaining_triples) < 1: self.index += 1

    def update_index(self, *args): #keyboard_on_key_down(self, window, keycode , text, modifiers):
        #TODO replace with window keydown event and remove focusbehavior
        keycode = args[1]
        if keycode == 32: self.index += 1 #'spacebar'
        #return super().keyboard_on_key_down(window, keycode,text, modifiers)



class RdfDisplayer(TabbedPanel):
    triples = ListProperty()
    boxes = DictProperty(None)

        
class DialogueBox(BoxLayout):
    pass
   

class TripleLabel(ButtonBehavior, NormalLabel):
    background_color = ListProperty()
    uri = StringProperty()
    
    def on_press(self):
        self.parent.detect_triple(self)
       
       

class TalkView(StackLayout):
    text = StringProperty()
    triples = ListProperty()
    found_triples = ListProperty()

    lst_triple: List[TripleLabel] = ListProperty([None, None, None])
    allowed_triples = []


    #highlighting triplelabel background
    colors = [[1,0,0,1],[0,0,1,1], [0,1,0,1]]

    def on_text(self, *args):
        #'\u2334' arch as spaceholder
        self.clear_widgets()

        txt = self.text
        pattern = '\[[^\]]+\]\([^\)]+\)'
        matches = re.findall(pattern, txt)
        for match in matches:
            txt = txt.replace(match, match.replace(' ', '\u2334'))
        
       
        lst = txt.split()
        for word in lst:
            dot = None
            if word[-1] in '.,:;!?':
                dot = word[-1]
                word = word[:-1]
            word = word.replace('\u2334', ' ')
            if word in matches:
                txt, uri = word.split('](')
                self.add_widget(TripleLabel(text=txt[1:], uri=uri[:-1]))
            else:
                self.add_widget(NormalLabel(text=word))
            if dot: self.add_widget(NormalLabel(text=dot))

    #def on_triples(self, instance, triples):
    #    pass

    
    def set_allowed_triples(self):
        self.allowed_triples = []
        for triple in self.triples:
            self.allowed_triples.append([*triple])


    def detect_triple(self, lbl: TripleLabel):
        for triple in self.triples:
            for i in range(len(triple)):
                if lbl.uri == triple[i]:
                    self.update_current_triple(lbl, i)
                    return


    def colorize_triple(self, colorize: Boolean = True):
        for i, lbl in enumerate(self.lst_triple):
            if isinstance(lbl, TripleLabel):
                lbl.background_color = self.colors[i] if colorize else App.get_running_app().bg

    def get_current_uris(self):
        return list(map(lambda x: x.uri if x else None, self.lst_triple))

    def update_current_triple(self, lbl: TripleLabel, index: int):
        self.colorize_triple(False)
        self.lst_triple[index] = lbl
        #get current triple
        cur = self.get_current_uris()
        #retrieve all remaining triples
        self.set_allowed_triples()
        for_removal = []
        for triple in self.allowed_triples:
            for i in range(len(cur)):
                if cur[i] == None: triple[i] = None
                elif cur[i] != triple[i] and triple not in for_removal:
                    for_removal.append(triple) 
        for triple in for_removal:
            self.allowed_triples.remove(triple)

        #triple combination does not exist
        if len(self.allowed_triples) < 1:
            self.lst_triple = [None, None, None]
            self.lst_triple[index] = lbl
            self.colorize_triple()
        else:
            self.remove_completed_triple(cur)
        self.colorize_triple()
            
    def remove_completed_triple(self, triple: List[str]) -> List[str]:
        for k, triple in enumerate(self.allowed_triples):
            i = 0
            for j in range(len(triple)):
                if triple[j] == triple[j] and triple[j] != None: i+=1
                if i == 3:
                    self.found_triples = self.triples.pop(k)
                    self.colorize_triple()
                    self.lst_triple = [None, None, None]

    
       