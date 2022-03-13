from kivy.event import EventDispatcher
from kivy.uix.screenmanager import ScreenManager
import rdflib
import os

from sparqlManager import SparqlManager
from templates.mapScene import MapScene
from templates.mapScene import MapScene, Location, Event
from templates.talkScene import TalkScene, TalkItem, TalkInfo, Speaker
from templates.queryScene import QueryScene, QueryItem

from rdflib.term import Literal, URIRef
from rdflib.namespace import XSD 

class Chapter(EventDispatcher):
   
    def __init__(self, path: str, g: rdflib.ConjunctiveGraph, sm: ScreenManager, **kw) -> None:
        super().__init__(**kw)
        self.sparql = SparqlManager()
        self.sm = sm
        self.idx = self.sm.cur_episode
        self.path = path
        self.g = rdflib.ConjunctiveGraph()
        self.prepare_graph(g)
        self.episodes = self.get_episodes(self.g)
        self.sm.episodes = []
        self.sm.episodes.append(MapScene(events=self.episodes, idx=self.sm.cur_episode))
        


    def prepare_graph(self, g: rdflib.ConjunctiveGraph):
        self.g += g
        for name in os.listdir(self.path):
            try:
                file = self.path + f'/{name}'
                if os.path.isfile(file): self.g.parse(file)
            except Exception as e:
                print(e, file)

    def get_episodes(self, g):
        episodes = self.sparql.execute('get_episodes', g, dict())
        l = []
        for e in episodes:
            scenes_as_uri = self.sparql.execute('get_scenes', g, {'_:placeholder' :f"<{e['episode'].__str__()}>"})
            scenes = list(map(lambda x: [x['type'].__str__(), f"<{x['scene'].__str__()}>"], scenes_as_uri))
            ti = []
            for scene in scenes:
                if scene[0].endswith('TalkScene'):
                    ti.append(TalkScene(talk_info=self.get_talk(g, scene[1]), idx=self.idx)) 
                elif scene[0].endswith('QueryScene'):
                    q = self.sparql.execute('get_query', g, {'_:placeholder': scene[1]})[0]  
                    ti.append(QueryScene(query_item=QueryItem(question=q['question'].__str__(), markup_query=q['query'].__str__()), idx=self.idx))
            lo = Location(location_name=e['location_name'].__str__(), uri=e['link'].__str__(), lat=float(e['lat'].__str__()), lon=float(e['long'].__str__()))
            l.append(Event(location=lo, img_path=e['img'], title=e['title'], desc=e['desc'], scenes=ti))
        return l
      

    def get_talk(self, g, uri):
        dialogue = self.sparql.execute('get_talk', g, {'_:placeholder': uri} ) #self.get_talk_data(g, uri) 
        l = []
        for talk in dialogue:
            triples = self.sparql.execute('get_statements_in_talk_item', g,  {'_:placeholder': uri, ':_placeholder': '<'+ talk['idx'].__str__() +'>'}) 
            tri = []
            for triple in triples:
            #    spo = []
            #    for term in ['subject', 'predicate', 'object']:
            #        if term == 'object' and type(triple[term]) == Literal:
            #            x = triple[term].__str__()
            #            if not x.isnumeric(): x = f'"{x}"'
            #            spo.append(f"{x}")
            #        else:
            #            spo.append(f"<{triple[term].__str__()}>")
            # 
            #    tri.append(spo)   
                tri.append([triple['subject'].__str__(), triple['predicate'].__str__(), triple['object'].__str__()])
            s = Speaker(name=talk['name'].__str__(), depiction=talk['img'].__str__())
            t = TalkItem(speaker=s, text=talk['text'].__str__(), triples=tri)
            l.append(t)
        return TalkInfo(dialogue=l, background=talk['background'])

    