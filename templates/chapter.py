from turtle import Screen
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import BooleanProperty
import rdflib
from templates.mapScene import MapScene, Location, Detail
from templates.episode import Episode

from sparqlManager import SparqlManager
import os



class Chapter(Screen):
    is_finished = BooleanProperty(False)
    

    def __init__(self, path: str, data: rdflib.ConjunctiveGraph, **kw) -> None:
        self.path = path
        super().__init__(**kw)
         
        self.sparql = SparqlManager()
        self.sm = ScreenManager()
        self.add_widget(self.sm)
        self.episodes = set()
        self.g = rdflib.ConjunctiveGraph() + data

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

    def update_knowledge_base(self, *args):
        x = self.sm.current_screen
        x.unbind(graph=self.update_knowledge_base)
        self.sm.remove_widget(x)
        self.sm.current = 'landing'
        if len(self.sm.current_screen.lst_episodes) == 0: self.is_finished = True
       

  
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
            lo = Location(location_name=e['location_name'].__str__(), uri=e['link'].__str__(), lat=float(e['lat'].__str__()), lon=float(e['long'].__str__()))
            detail = Detail( img_path=e['img'].__str__(), title=e['title'].__str__(), desc=e['desc'].__str__())
            l.append(Episode(uri=e['episode'].__str__(), location=lo, detail=detail))
        return l

    def close_chapter(self, *args):
        self.is_finished = True
