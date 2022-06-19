from dataclasses import dataclass
import re
from kivy.uix.screenmanager import ScreenManager, Screen
from templates.sparqlManager import SparqlManager
from templates.mapScene import Location, Detail
from templates.talkScene import TalkScene, TalkInfo, TalkItem, Speaker
from templates.queryScene import QueryScene, QueryItem
from templates.resourceManager import ResourceManager
from rdf_utils import remove_all_namespaces, workaround_namespace_bindings, get_ns_from_string
from typing import List, Tuple, Union

import rdflib
from kivy.properties import ObjectProperty


class Episode(Screen):
    graph = ObjectProperty()

    def __init__(self, uri: str, location: Location, detail: Detail, chapter_path:str, **kw):
        self.name = uri
        self.uri = uri
        self.location = location
        self.detail = detail
        self.chapter_path = chapter_path
        super().__init__(**kw)

        self.sm = ScreenManager()
        self.add_widget(self.sm)
        self.scenes = []
        self.sparql = SparqlManager()
        self.g = None


    def on_pre_enter(self, *args):
        #insert loading screen
        pass
      
    def on_enter(self, *args):
        self.next_scene()


    def update_episode_graph(self, scene, scene_graph: rdflib.Graph):
        workaround_namespace_bindings(self.g, scene_graph)
        self.next_scene()
    
    def next_scene(self):
        if len(self.scenes) > 0:
            scene = self.scenes.pop()
            scene.bind(graph=self.update_episode_graph)
            self.sm.switch_to(scene)
        else:
            self.graph = self.g


    def load(self, g: rdflib.Graph):
        self.g = rdflib.Graph()
        remove_all_namespaces(self.g)

        scenes_as_uri = self.sparql.execute('get_scenes', g, {'_:placeholder' :f"<{self.name}>"})
        scenes = list(map(lambda x: [x['type'].toPython(), f"<{x['scene'].toPython()}>"], scenes_as_uri))
        for scene in scenes:
            if scene[0].endswith('TalkScene'):
                s = TalkScene(talk_info=self.get_talk(g, scene[1]))
            elif scene[0].endswith('QueryScene'):
                q = self.sparql.execute('get_query', g, {'_:placeholder': scene[1]})[0]  
                s = QueryScene(query_item=QueryItem(question=q['question'].toPython(), markup_query=q['query'].toPython()), episode_graph=self.g, chapter_path=self.chapter_path)
            self.scenes.append(s)
        self.scenes.reverse()
       


    def get_talk(self, g, uri):
        dialogue = self.sparql.execute('get_talk', g, {'_:placeholder': uri} ) #self.get_talk_data(g, uri) 
        l = []
        for talk in dialogue:
            triples = self.sparql.execute('get_statements_in_talk_item', g,  {'_:placeholder': uri, ':_placeholder': '<'+ talk['idx'].toPython() +'>'})
            tri = []
            for triple in triples:
                # only process hidden triples with spo or sparql update object
                if any(('update' in triple.keys(), all([k in triple.keys() for k in ['subject', 'predicate', 'object']]))):
                    lbls = [lbl.toPython() for lbl in self.sparql.get_list_items(g, triple['labels'], l=[])] # keywords
                    tri.append([{term: lbls[i] for i, term in enumerate(['subject', 'predicate', 'object'])},  triple['update'].toPython() if 'update' in triple.keys() else [triple[term] for i, term in enumerate(['subject', 'predicate', 'object'])]])   # [0] keywords, [1] triple
                    tri[-1].append(self.get_namespaces(triple))
            s = Speaker(name=talk['name'].toPython(), depiction=ResourceManager.get_resource_path( self.chapter_path, talk['img'].toPython()))
            t = TalkItem(speaker=s, text=talk['text'].toPython(), triples=tri)
            l.append(t)
        return TalkInfo(dialogue=l, background=ResourceManager.get_resource_path( self.chapter_path, talk['background']))


    def get_namespaces(self, triple:dict) -> List[Tuple[str]]:
        if 'update' in triple.keys(): update = triple['update'].toPython()
        elif'namespaces' in triple.keys(): update = triple['namespaces'].toPython()
        else: return []
        return get_ns_from_string(update)


