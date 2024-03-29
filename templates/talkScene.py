import re
from dataclasses import dataclass
from typing import Dict, List, Tuple, Union

import rdflib
import rdflib.plugin
from kivy.app import App
from kivy.core.window import Window

# from rdflib.query import Result
from kivy.lang import Builder
from kivy.properties import (
    ListProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.screenmanager import Screen
from kivy.uix.stacklayout import StackLayout

from templates.myWidgets.myLabels import NormalLabel, TripleLabel

kv_file = f'{__file__[: __file__.rfind(".")]}.kv'
if not kv_file in Builder.files:
    Builder.load_file(kv_file)  # load kv file with same name of py file in same dir


from templates.myDataclasses import Speaker, TalkInfo, TalkItem
from templates.rdf_utils import initalize_graph


class TalkScene(Screen):
    graph = (
        ObjectProperty()
    )  # rdflib.Graph that returns RDF data to current episode graph / triggers assignment on value change.
    index: int = NumericProperty(0)  # update.talk() executes when index changes

    ################################################################################
    # Widget variables
    view_talk = ObjectProperty()  # widget with textual dialogue and hidden tripples
    rdf_displayer = (
        ObjectProperty()
    )  # widget that shows RDF data in Turtle, XML and JSON-LD format
    btn_continue: ObjectProperty()  # Next button

    ################################################################################
    # Dataclass Variables
    dialogue: List[TalkItem] = ListProperty()  # stores Talkinfo.dialogue
    background = StringProperty()  # stores current Talkinfo.background (file path)

    speaker_name = StringProperty()  # stores current Speaker.name
    depiction = StringProperty()  # stores current Speaker.depiction

    talk = StringProperty()  # stores current Talkitem.text
    triples = ListProperty()  # stores current Talkitem.triples

    def __init__(self, talk_info: TalkInfo, **kwargs):
        super().__init__(**kwargs)
        # Initalize variables static for all Talkitems
        self.g = initalize_graph(keep_prefixes=False)
        # rdflib.Graph()
        # remove_all_namespaces(self.g)

        self.dialogue = talk_info.dialogue
        self.background = talk_info.background
        self.finished = False
        self.ns = []

        # Bind functions
        self.bind(
            index=lambda self, value: self.next_talk_item(value)
        )  # execute update.talk() when index changes
        self.view_talk.bind(
            found_triples=self.update_displayer
        )  # add triple to RDF displayer
        self.btn_continue.bind(on_release=self.update_index)  # next scene

        # Initalize Talkitem specific variables
        self.view_talk.triples_labels = self.triples
        self.next_talk_item(self.index)
        # self.view_talk.triples_labels = self.triples

    def update_index(self, *args):
        self.index += 1

    def next_talk_item(self, idx: int):
        # load next talk item, if not end of scene
        if self.end_talk_scene(idx):
            return
        self.speaker_name = self.dialogue[idx].speaker.name
        self.depiction = self.dialogue[idx].speaker.depiction
        self.triples = self.dialogue[idx].triples
        self.talk = self.dialogue[idx].text
        # enable next button, if no hidden triples
        self.btn_continue.disabled = len(self.triples) != 0

    def end_talk_scene(self, idx) -> bool:
        # closes Talkscene by assigning valuie to self.graph
        is_end = len(self.dialogue) <= idx
        if is_end:
            self.graph = self.g
        return is_end

    def update_displayer(
        self, instance, lst: List[Union[rdflib.Graph, List[Tuple[str]]]]
    ):
        if not lst:
            return
        self.workaround_namespace_bindings(lst)

        if len(self.g) > 0:
            for tab in self.rdf_displayer.tab_list:
                tab.content.text = self.g.serialize(format=tab.text.lower(), base="")
        if len(self.view_talk.triples) == 0:
            self.btn_continue.disabled = False

    def workaround_namespace_bindings(
        self, lst: List[Union[rdflib.Graph, List[Tuple[str]]]]
    ):
        # bind replace/override does not work
        # as soon as an automatically namespaces is created when adding a triple, the namespace cannot be replaced or overridden
        self.g = self.update_graph(lst[0])
        self.bind_namespaces_to_g(lst[1])

    def update_graph(self, new_graph: rdflib.Graph) -> None:
        # create temporary graph with all old and new triples
        temp = rdflib.Graph()
        temp += new_graph
        temp += self.g

        new_g = initalize_graph(keep_prefixes=False)
        # rdflib.Graph()
        # remove_all_namespaces(new_g)
        for triple in temp:
            new_g.add(triple)
        return new_g

    def bind_namespaces_to_g(self, ns) -> None:
        self.ns.extend(ns)
        for prefix, namespace in self.ns:
            self.g.namespace_manager.bind(
                prefix, namespace, replace=True, override=True
            )

    ######################################################################################################
    # Enable space bar press for talk continuation
    def on_enter(self, *args):
        # allow use of space bar to continue
        Window.bind(on_key_down=self.check_for_space)
        self.view_talk.update_labels()  # test / stay

    def on_leave(self, *args):
        # decouple use of space bar with Talkscene
        Window.unbind(on_key_down=self.check_for_space)

    def check_for_space(
        self, *args
    ):  # keyboard_on_key_down(self, window, keycode , text, modifiers):
        # TODO replace with window keydown event and remove focusbehavior
        keycode = args[1]
        if keycode == 32 and len(self.view_talk.triples) == 0:
            self.update_index()  #'spacebar'
        # return super().keyboard_on_key_down(window, keycode,text, modifiers)


# class RdfDisplayer(TabbedPanel):
#     triples = ListProperty()
#     boxes = DictProperty(None)

# class DialogueBox(BoxLayout):
#     pass


class TalkView(StackLayout):
    text = StringProperty()
    triples = ListProperty()
    found_triples = ListProperty()  # prior ListProperty

    colors = [
        [1, 0, 0, 0.5],
        [0, 0, 1, 0.5],
        [0, 1, 0, 0.5],
    ]  # highlighting triplelabel background: Red, Blue, Green

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.triples_labels = []
        self.cur_triple = {}
        self.allowed_triples = []
        self.lst_triple_labels = []
        self.lbls = {}

    def on_text(self, *args):
        self.update_labels()

    def replace_blank_spaces(self, txt: str, spaceholder: str) -> str:
        pattern = "(\[[^\]]+\]){1}(\([^\)]+\))?"  # [...] or [...](...)
        matches = re.findall(pattern, txt)  # [0]: keyword, [1]: alias
        for match in matches:
            m = "".join(match)
            txt = txt.replace(m, m.replace(" ", spaceholder))
        return txt

    def split_alias_punctuation_marks(self, word: str) -> Tuple[str, str, str]:
        mark = ""
        if word[-1] in ".,:;!?":
            word, mark = word[:-1], word[-1]
        try:
            word, alias = word.split("](")
            word = word[1:]
            alias = alias[:-1]
        except ValueError:
            word = alias = word[1:-1]
        return word, alias, mark

    def is_keyword(self, word: str) -> bool:
        return bool(re.search("(\[[^\]]+\]){1}(\([^\)]+\))?", word))

    def update_labels(self):
        self.clear_widgets()
        txt = self.text  # needed to avoid that on_text is called again
        spaceholder = "\u2334"  #'\u2334' arch as spaceholder
        txt = self.replace_blank_spaces(txt, spaceholder)
        self.add_labels(txt.split())

    def add_labels(self, words: List[str]) -> None:
        self.lst_triple_labels = []
        for word in words:
            word = word.replace("\u2334", " ")
            if self.is_keyword(word):
                word, alias, mark = self.split_alias_punctuation_marks(word)
                self.lst_triple_labels.append(
                    TripleLabel(text=word + mark, keyword=alias)
                )
                self.add_widget(self.lst_triple_labels[-1])
                continue
            self.add_widget(NormalLabel(text=word))

    def detect_triple(self, lbl: TripleLabel):
        # [0] keywords, [1] URIs, [2] query
        for triple in self.triples:
            keywords = triple[0]
            for k in keywords.keys():
                if lbl.keyword == keywords[k]:
                    self.update_current_triple(lbl, k)

    def colorize_lbls(self, colorize: bool = True):
        for i, k in enumerate(("subject", "predicate", "object")):
            if k in self.lbls.keys():
                self.lbls[k].background_color = (
                    self.colors[i] if colorize else App.get_running_app().bg
                )

    def get_current_uris(self):
        return list(map(lambda x: x.keyword if x else None, self.lst_triple))

    def update_current_triple(self, lbl: TripleLabel, term: str):
        self.colorize_lbls(False)

        self.cur_triple[term] = lbl.keyword
        self.add_triple_label_or_reset(lbl, term)

        if len(self.cur_triple) == 3:
            idx = self.get_found_triple_index()
            self.found_triples = self.create_new_graph(*self.triples.pop(idx))
            self.deactivate_obsolete_labels()
            self.lbls = {}
            self.cur_triple = {}
        else:
            self.colorize_lbls()

    def deactivate_obsolete_labels(self) -> None:
        for lbl in self.lst_triple_labels:
            if any([lbl.keyword in triple[0].values() for triple in self.triples]):
                continue
            lbl.activate(False)

    def add_triple_label_or_reset(self, lbl: TripleLabel, term: str) -> None:
        if any(
            [self.cur_triple.items() <= triple[0].items() for triple in self.triples]
        ):
            self.lbls[term] = lbl
            return
        self.cur_triple = {term: lbl.keyword}
        self.lbls = {term: lbl}

    def get_found_triple_index(self) -> int:
        # returns index of current (potential) triple
        for i, triple in enumerate(self.triples):
            if self.cur_triple.items() <= triple[0].items():
                return i
        raise Exception(
            "The selected keywords are not part of a hidden triple! Please check your story files."
        )

    def create_new_graph(
        self,
        keywords: List[str],
        update: List[Union[str, rdflib.URIRef, rdflib.Literal]],
        namespaces: List[Tuple[str]],
    ):
        # update: [uriref, uriref, literal/uriref] OR SPARQL update string
        g = initalize_graph(keep_prefixes=False)
        # g = rdflib.Graph()
        # remove_all_namespaces(g)
        if isinstance(update, str):
            g.update(update)
        else:
            g.add(update)
        return [g, namespaces]


if __name__ == "__main__":
    print('Run "python main.py" to start RDeF!')
