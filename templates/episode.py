from kivy.uix.screenmanager import ScreenManager, Screen
from templates.sparqlManager import SparqlManager
from templates.mapScene import Location, Detail
from templates.talkScene import TalkScene, TalkInfo, TalkItem, Speaker
from templates.queryScene import QueryScene, QueryItem

import rdflib
from kivy.properties import ObjectProperty


class Episode(Screen):
    graph = ObjectProperty()

    def __init__(self, uri: str, location: Location, detail: Detail, **kw):
        self.name = uri
        self.uri = uri
        self.location = location
        self.detail = detail
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


    def update_episode_graph(self, scene, scene_graph):
        self.g += scene_graph
        self.next_scene()
    
    def next_scene(self):
        if len(self.scenes) > 0:
            scene = self.scenes.pop()
            scene.bind(graph=self.update_episode_graph)
            self.sm.switch_to(scene)
        else:
            self.graph = self.g


    def load(self, g: rdflib.ConjunctiveGraph):
        self.g = rdflib.ConjunctiveGraph()
        scenes_as_uri = self.sparql.execute('get_scenes', g, {'_:placeholder' :f"<{self.name}>"})
        scenes = list(map(lambda x: [x['type'].__str__(), f"<{x['scene'].__str__()}>"], scenes_as_uri))
        for scene in scenes:
            if scene[0].endswith('TalkScene'):
                s = TalkScene(talk_info=self.get_talk(g, scene[1]))
            elif scene[0].endswith('QueryScene'):
                q = self.sparql.execute('get_query', g, {'_:placeholder': scene[1]})[0]  
                s = QueryScene(query_item=QueryItem(question=q['question'].__str__(), markup_query=q['query'].__str__()), episode_graph=self.g)
            self.scenes.append(s)
        self.scenes.reverse()
       


    def get_talk(self, g, uri):
        dialogue = self.sparql.execute('get_talk', g, {'_:placeholder': uri} ) #self.get_talk_data(g, uri) 
        l = []
        for talk in dialogue:
            triples = self.sparql.execute('get_statements_in_talk_item', g,  {'_:placeholder': uri, ':_placeholder': '<'+ talk['idx'].__str__() +'>'}) 
            tri = []
            for triple in triples:
                tri.append([triple['subject'].__str__(), triple['predicate'].__str__(), triple['object'].__str__()])
            s = Speaker(name=talk['name'].__str__(), depiction=talk['img'].__str__())
            t = TalkItem(speaker=s, text=talk['text'].__str__(), triples=tri)
            l.append(t)
        return TalkInfo(dialogue=l, background=talk['background'])

    
