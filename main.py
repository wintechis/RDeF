#####################################
## Set Variable for Logger Path #####
from dataclasses import  dataclass, field, asdict
import os
import json
from typing import Iterator, List, Dict
main_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(main_dir)
os.environ['KIVY_HOME'] = os.path.join(os.getcwd(), 'kivy')
import kivy.logger
###################################
## Kivy Import
import kivy
kivy.require('2.0.0')

#### Update standard font, if defined
#from kivy.config import Config
#Config.set('kivy', 'default_font', ['Roboto', 'data/fonts/Roboto-Regular.ttf', 'data/fonts/Roboto-Italic.ttf', 'data/fonts/Roboto-Bold.ttf', 'data/fonts/Roboto-BoldItalic.ttf'])
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.clock import Clock
from kivy.properties import ListProperty, DictProperty
####################################
####################################

###################################
## Scene Import
import sys
from kivy.resources import resource_add_path, resource_find

resource_add_path(os.path.join(os.getcwd(), 'templates'))
import sys
sys.path.append(os.path.join(os.getcwd(), 'templates'))

#from chapter import Chapter
from templates.story import Story
####################################
####################################
from string import Template
import rdflib
from templates.sparqlManager import SparqlManager
from templates.startScene import StartScene

################################################################
# Main Loop

@dataclass
class StoryInfo:
    title: str = ''
    media_source: str =''
    authors: List[str] = field(default_factory=lambda: [])
    tags: List[str] = field(default_factory=lambda: [])
    desc: str = ''


@dataclass
class DesignInfo:
    font_size: int = 20
    fg: list[float] = field(default_factory=lambda:[151/255, 27/255, 47/255, 1])
    bg: list[float] = field(default_factory=lambda:[0.9, 0.9, 0.9, 1])
    hl: list[float] = field(default_factory=lambda: [209/255, 231/255, 224/255, 1]  )  #[200/255, 15/255, 46/255, 1]


class RDeFManager(ScreenManager):
    def __init__(self, story_path: str, story_names: Dict[str,str], **kw):
        super().__init__(**kw)
        self.story_path = story_path
        self.start_screen = StartScene(story_names=story_names, idx=[])
        self.switch_to(self.start_screen)
        

    def start_story(self, story_name):
        story_path = os.path.join(self.story_path, story_name)
        self.switch_to(Story(story_path))

    def close_story(self):
        current = self.current_screen
        self.switch_to(self.start_screen)
        self.remove_widget(current)

# class RDeFManager(ScreenManager):
#     cur_chapter = ListProperty([0]) #next episode by  cur_story[0] += 1
#     cur_episode = ListProperty([0])

#     def __init__(self, story_names: Dict[str,str], **kw):
#         super().__init__(**kw)
#         self.chapters = []
#         self.episodes = []
#         self.sparql = SparqlManager()
      
#         self.switch_to(Story(story_names))

class MainApp(App):
    fg = ListProperty()
    bg = ListProperty()
    hl = ListProperty()
    story_info = DictProperty()

    def build(self):
        ## Load Design / Stories
        self.sparql = SparqlManager()
        self.title = 'RDeF - RDF Training and Demonstration Framework'
        self.icon = 'resources/rdef_16x16.ico'

        story_dir = os.path.join(os.getcwd(),'stories')
        story_names = self.get_stories(story_dir)
        try:
            self.load_story_info(story=os.path.join(os.getcwd(),'stories', list(story_names.keys())[0]))
        except FileNotFoundError:
            di = DesignInfo()
            self.fg = di.fg
            self.bg = di.bg
            self.hl = di.hl
        self.font_size = 20

        return RDeFManager(story_dir, story_names)

        # story_path = self.select_story()
        
        # if story_path == 'exit':
        #     self.stop()
        #     return

        # self.story_info = asdict(StoryInfo())
        # self.paths_resources = []
        # ###
        # try:
        #     self.load_story_info(story=story_path)
        # except FileNotFoundError:
        #     di = DesignInfo()
        #     self.fg = di.fg
        #     self.bg = di.bg
        #     self.hl = di.hl
        # self.font_size = 20
    
        # return RDeFManager(story_names=story_path)

    def select_story(self):
        story_dir = os.path.join(os.getcwd(),'stories')
        story_names = list(self.get_stories(story_dir).keys())
        if len(story_names) == 1:
            return os.path.join(story_dir, story_names[0])
        s = ''
        for i, name in enumerate(story_names):
            s += f'[{i+1}] {name} '

        s += f'[{len(story_names)+ 1}] exit'
        print(f'Select Game: {s}')
        story = input()

        if story in story_names:
            return os.path.join(story_dir, story)
        elif story.isnumeric() and 0 < int(story) <= len(story_names):
                return os.path.join(story_dir, story_names[int(story)-1])
        else:
            return 'exit'

    def get_stories(self, story_dir: str) -> list:
        return {story: os.path.join(story_dir, story)  for story in next(os.walk(story_dir))[1]}




    def load_story_info(self, story):
        self.story_info = self.sparql.load_story_info(story)
        self.fg, self.bg, self.hl = self.story_info['colors']
    #         p = os.path.join(story, 'info.ttl')
    #         g = rdflib.ConjunctiveGraph().parse(p.replace('\\','/'))
    #         g.parse(os.path.join(story,'db', 'people.ttl').replace('\\','/'))
    #         info = self.sparql.execute('get_info', g, dict())[0]
    #         authors = self.sparql.execute('get_authors', g, dict())
    #         self.story_info = {
    #             'path': story,
    #             'title': info['title'].__str__(),
    #             'media_source': info['trailer'].__str__(),
    #             'authors': [author['author'].__str__() for author in authors],
    #             'tags': info['tags'].__str__().split(','),
    #             'desc': info['desc'].__str__()
    #         }
    #         colors = [list(map(float, info['bg'].__str__().split(','))), 
    #                 list(map(float, info['fg'].__str__().split(','))),
    #                 list(map(float, info['hl'].__str__().split(',')))
    #                 ]
    #         self.fg, self.bg, self.hl = map(self.convert_color, colors)
        

    # def convert_color(self, rgb: List[int]):
    #     if len(rgb) == 3: rgb.append(255)
    #     return [val/255 for val in rgb]


    #def load_resources(self):
    #    #<-- not used -->
    #    templ_dir = os.path.join(self.base_dir, 'templates')
    #    for base, dir, files in os.walk(templ_dir):
    #        for f in files:
    #            if f.endswith('.kv'): 
    #                kivy.lang.Builder.load_file(os.path.join(base, f))
    #            if f.endswith('.py'): 
    #                x = os.path.join(base, f)
    #                #from x import *

    #def exist_base_dirs(self) -> bool:
    #    for name in ['stories', 'resources', 'templates']:
    #        if name not in next(os.walk(self.base_dir))[1]:
    #            return False
    #        return True


###########################################################
######## Main
##########################################################
if __name__ == '__main__':
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))
    Clock.max_iteration = 50
    MainApp().run()
   






