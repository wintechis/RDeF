from turtle import Screen
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import BooleanProperty
import rdflib
from templates.mapScene import MapScene, Location, Detail
from templates.episode import Episode

from sparqlManager import SparqlManager
from rdf_utils import remove_all_namespaces, workaround_namespace_bindings
import os
from templates.resourceManager import ResourceManager



class Chapter(Screen):
    is_finished = BooleanProperty(False)
    

    def __init__(self, path: str, data: rdflib.Graph, **kw) -> None:
        self.path = path
        super().__init__(**kw)
         
        self.sparql = SparqlManager()
        self.sm = ScreenManager()
        self.add_widget(self.sm)
        self.episodes = set()
        g = rdflib.Graph()
        remove_all_namespaces(g)
        self.g = g + data
        self.chapter_graph = rdflib.Graph()
        remove_all_namespaces(self.chapter_graph)
        self.prepare_graph(self.g, self.path)
        self.episodes = self.get_episodes(self.g)
        landing = MapScene(name='landing', episodes=self.episodes)
        landing.bind(episode=self.start_episode)
        self.sm.switch_to(landing)

    def start_episode(self, instance, episode):
        if episode:
            episode.bind(graph=self.update_knowledge_base)
            episode.load(self.g)
            self.sm.add_widget(episode)
            self.sm.current = episode.name

    def update_knowledge_base(self, instance, episode_graph):
        workaround_namespace_bindings(self.chapter_graph, episode_graph)
        #self.chapter_graph += episode_graph
        x = self.sm.current_screen
        x.unbind(graph=self.update_knowledge_base)
        self.sm.remove_widget(x)
        self.sm.current = 'landing'
        if len(self.sm.current_screen.lst_episodes) == 0:
           base, name = os.path.split(self.path)
           self.chapter_graph.serialize(destination=os.path.join(base, 'db', f'{name}.ttl'), format='turtle')
           self.is_finished = True
       

  
    def prepare_graph(self, g: rdflib.ConjunctiveGraph, path: str):
        # add all files
        for name in os.listdir(path):
            try:
                file = path + f'/{name}'
                if os.path.isfile(file): 
                    g.parse(file)
            except Exception as e:
                print(e, file)

    def get_episodes(self, g):
        episodes = self.sparql.execute('get_episodes', g, dict())
        l = []
        for e in episodes:
            lo = Location(location_name=e['location_name'].toPython(), uri=e['link'].toPython(), lat=float(e['lat'].toPython()), lon=float(e['long'].toPython()))
            detail = Detail(img_path=ResourceManager.get_resource_path(self.path, e['img'].toPython()), title=e['title'].toPython(), desc=e['desc'].toPython())
            l.append(Episode(uri=e['episode'].toPython(), location=lo, detail=detail, chapter_path=self.path))
        return l

    def close_chapter(self, *args):
        self.is_finished = True
