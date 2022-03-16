from kivy.uix.screenmanager import ScreenManager, Screen
from templates.chapter import Chapter
from kivy.app import App
import os
from kivy.core.window import Window
import rdflib




class Story(Screen):
    def __init__(self, path: str, **kw):
        self.path = path
        super().__init__(**kw)

        self.sm = ScreenManager()
        self.add_widget(self.sm)
        self.g = rdflib.ConjunctiveGraph()
        self.load_data(self.path, self.g)
        self.chapters = self.get_chapters_reversed()
        self.next_chapter()

    
    def load_data(self, path: str,  g: rdflib.ConjunctiveGraph):
        for file in ['people.ttl', 'locations.ttl']:
            self.g.parse(os.path.join(path, file))

    def get_chapters_reversed(self) -> list:
        chapters = filter(lambda x: x.split('_')[0].isnumeric() , next(os.walk(self.path))[1])
        full_chapters = [os.path.join(self.path,chapter).replace('\\', '/') for chapter in chapters]
        return sorted(full_chapters,reverse=True)

    def next_chapter(self, *args):
        if len(self.chapters) > 0:
            chapter = Chapter(self.chapters.pop(), self.g)
            chapter.bind(is_finished=self.next_chapter)
            self.sm.switch_to(chapter)
        else:
            App.get_running_app().stop()
        
