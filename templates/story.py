import os

import rdflib
from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from rdf_utils import remove_all_namespaces

from templates.chapter import Chapter
from rdf_utils import initalize_and_parse
from utils import join_path

class Story(Screen):
    def __init__(self, path: str, **kw):
        self.path = path
        super().__init__(**kw)

        self.sm = ScreenManager()
        self.add_widget(self.sm)
        people = join_path(self.path, 'db', 'people.ttl')
        locations = join_path(self.path, 'db', 'locations.ttl')
        self.g = initalize_and_parse(files=[people, locations], keep_prefixes=False)
        # rdflib.ConjunctiveGraph()
        # remove_all_namespaces(self.g)
        #self.load_data(self.path, self.g)
        self.chapters = self.get_chapters_reversed()
        self.next_chapter()

    # def load_data(self, path: str, g: rdflib.ConjunctiveGraph):
    #     for file in ["people.ttl", "locations.ttl"]:
    #         self.g.parse(os.path.join(path, "db", file))

    def get_chapters_reversed(self) -> list:
        chapters = filter(
            lambda x: x.split("_")[0].isnumeric(), next(os.walk(self.path))[1]
        )
        full_chapters = [
            os.path.join(self.path, chapter).replace("\\", "/") for chapter in chapters
        ]
        return sorted(full_chapters, reverse=True)

    def next_chapter(self, *args):
        if len(self.chapters) > 0:
            chapter = Chapter(self.chapters.pop(), self.g)
            chapter.bind(is_finished=self.next_chapter)
            self.sm.switch_to(chapter)
        else:
            self.parent.close_story()
            # App.get_running_app().stop()
