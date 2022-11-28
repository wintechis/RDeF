import os
if __name__ == '__main__':
    os.environ['KIVY_HOME'] = os.getcwd()

import webbrowser
from dataclasses import dataclass,field
import json
from typing import Dict, Iterable, Iterator, List, Any

import kivy

kivy.require('2.0.0')

from kivy.app import App
from kivy.clock import Clock

from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.logger import Logger
from kivy.properties import (BooleanProperty, 
                            ObjectProperty,
                            StringProperty,
                            DictProperty,
                            ListProperty,
                            NumericProperty)
from behaviors import HoverBehavior
import rdflib
from sparqlManager import SparqlManager
### Import .kv ##############

from kivy.lang import Builder
kv_file = f'{__file__[: __file__.rfind(".")]}.kv'
if not kv_file in Builder.files: Builder.load_file(kv_file) # load kv file with same name of py file in same dir



# test
# from story import StoryManager

### End Import ###############################
##############################################

@dataclass
class StoryInfo:
    title: str = ''
    media_source: str =''
    authors: List[str] = field(default_factory=lambda: [])
    tags: List[str] = field(default_factory=lambda: [])
    desc: str = ''

@dataclass
class DataManager:
    filename: str
    
    def load(self) -> dict[str]:
        with open(self.filename, "r") as file:
            return json.load(file)

    def save(self, data: dict):
        with open(self.filename, "w") as file:
            json.dump(data, file)


@dataclass
class Games:
    #only for consistency
    names: List[str]

class CenteredLabel(Label):
    pass

class SelectableRecycleBoxLayout(LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''    

class ListItem(RecycleDataViewBehavior, GridLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    lbl_text = ObjectProperty(None)
    text = StringProperty('')
    func = StringProperty('')
    root = ObjectProperty(None)
    params = DictProperty()

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        self.height = self.lbl_text.height if self.lbl_text.height < 100 else self.lbl_text.font_size
        return super().refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super().on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            if self.func and self.root: self.root.execute_func(self.func, self.params)
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected

class GameView(Screen):
    btn_start: ObjectProperty(Button)

    player: ObjectProperty(None)
    lbl_title: ObjectProperty(None)
    lbl_authors: ObjectProperty(None)
    lbl_tags: ObjectProperty(None)
    lbl_desc: ObjectProperty(None)

    def __init__(self, **kw):
        super().__init__(**kw)
        #self.info = game_info


    #def on_width(self, *args):
    #    if self.info.title:
    #        self.lbl_title.text = self.info.title
    #        self.lbl_authors.text = 'Authors: ' + ', '.join(self.info.authors)
    #        self.lbl_tags.text = 'Tags: ' + ', '.join(self.info.tags)
    #        self.lbl_desc.text = self.info.desc
    #        self.player.source = self.info.media_source



class MyListView(RecycleView):
    colors: DictProperty()
    mydata: ListProperty()
    sm: ObjectProperty(ScreenManager)

    def __init__(self, data: List[Dict[str, Any]] = [], **kwargs):
        super().__init__(**kwargs)
        #hl - highligt color, bg - background-color, fc - font color
        if data: self.data = data
        self.is_initalized = False

    def on_width(self, *args):
        if self.is_initalized: return

        if not self.data: self.data = self.mydata 
        for d in self.data: d.update(self.colors)
        self.is_initalized = not self.is_initalized


class RectangledButton(HoverBehavior, Button):
  
    ##  Reuse Functions for functionality
    def on_enter(self, *args):
        self.background_color = App.get_running_app().hl
        return super().on_enter(*args)

    def on_leave(self, *args):
        self.background_color = App.get_running_app().bg
        return super().on_leave(*args)

class SideMenu(BoxLayout):
    sm: ObjectProperty(ScreenManager)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.post_init, 0)

    def post_init(self, dt):
        for c in self.children:
            if isinstance(c, Button):
                c.bind(on_press=self.press)

    def press(self, instance):
        name = instance.key.lower()
        if name == 'exit':
            App.get_running_app().stop()
        else:
            self.prepare_link(name)

    def prepare_link(self, name):
        if name == 'github':
            self.open_link('https://github.com/wintechis/RDeF')
        elif name == 'website':
            self.open_link('https://wintechis.github.io/RDeF')
        elif name == 'discover':
            self.open_link('https://itch.io/games/tag-rdef')
        else:
            Logger.error(f'"{name}" has no url mapping. Check URL mapping for button names.')

    def open_link(self, url):
        try:
            webbrowser.open(url, 1)
        except webbrowser.Error as e:
            Logger.error(f'Failed to open url "{self.url}"')



class StartScene(Screen):
    story_list = ObjectProperty(None)
    sm = ObjectProperty(ScreenManager)
    game_view = ObjectProperty(None)


    def __init__(self, story_names: Dict[str, str], idx: ListProperty, **kw):
        super().__init__(**kw)
        self.idx = idx
        self.x = 0 
        self.app = App.get_running_app()
        self.sparql = SparqlManager()
        self.story_names = story_names
        self.story_list.mydata = [{'text': name, 'root': self, 'func': 'create_game_view', 'params': {'name': name}} for name in story_names.keys()]
        self.game_view = GameView(name='game_view') 
        self.game_view.btn_start.bind(on_press=self.start_story)
        self.sm.add_widget(self.game_view)

    def execute_func(self, func: str, params: Dict) -> None:
        if hasattr(self.__class__, func) and callable(getattr(self.__class__, func)): 
            getattr(self.__class__, func)(self, **params)


    # def create_game_view_json(self, **kw):
    #     ### rdflib entrt
    #     name = kw['name']
    #     p = os.path.join(self.story_names[name], 'info.json')
    #     dm = DataManager(filename=p)
    #     # app = App.get_running_app()
    #     app.story_info = dm.load()
    #     app.fg, app.bg, app.hl = map(self.convert_color, [app.story_info['colors']['foreground_color'], app.story_info['colors']['background_color'], app.story_info['colors']['highlight_color']])
    #     self.sm.current = 'game_view'

    def create_game_view(self, **kw):
        story_name = kw['name']
        a = self.app
        a.story_info = self.sparql.load_story_info(story_name, path=os.path.join(os.getcwd(), 'stories'))
        a.fg, a.bg, a.hl = a.story_info['colors']
        self.sm.current = 'game_view'

    def convert_color(self, rgb: List[int]):
        if len(rgb) == 3: rgb.append(255)
        return [val/255 for val in rgb]


    def start_story(self, instance):
        self.parent.start_story(self.app.story_info['path'])



class DummyManager(ScreenManager):
    
    def __init__(self, **kw):
        super().__init__(**kw)
        self.add_widget(StartScene(name='start'))
        self.current = 'start'

      
class StartApp(App):
    def build(self):
        self.title = 'WireGraph'
        return DummyManager()
    
    def on_start(self):
        '''Executes first after start'''
        pass

    def on_stop(self):
        '''Executes before stopping'''
        pass


if __name__ == '__main__':    
    Clock.max_iteration = 50
   
    StartApp().run()
       









