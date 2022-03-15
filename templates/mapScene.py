if __name__ == '__main__':
    import os
    os.environ['KIVY_HOME'] = os.getcwd()

from dataclasses import dataclass
from xmlrpc.client import Boolean

import kivy
kivy.require('2.0.0')

from typing import Optional, Dict
#from story import Episode
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.image import Image
from kivy.properties import ObjectProperty, ListProperty, ColorProperty, DictProperty, BooleanProperty
from myLabels import *
from behaviors import HoverBehavior
from typing import List
from kivy.clock import Clock
#from talkScene import TalkScene
### Import .kv ##############

if not __name__ == '__main__':
    from kivy.lang import Builder
    Builder.load_file('templates/map.kv')



### End Import ###############################
##############################################

@dataclass(frozen=True)
class Location:
    # must be referenced via uri later
    location_name: str
    uri: str
    lat: float
    lon: float

@dataclass
class Detail:
    img_path: str
    title: str
    desc: str



class Pin(ToggleButtonBehavior, HoverBehavior, Image):
    my_color = ListProperty()

    def __init__(self, episode, **kwargs):
        super().__init__(**kwargs)
        self.episode = episode
        self.location = episode.location
        self.detail = episode.detail


    def on_state(self, widget, value):
        self.parent.show_detail(self)

           

class MapScene(Screen):
    wd_detail = ObjectProperty()
    lst_episodes = ListProperty()
    episode = ObjectProperty()
    

    def __init__(self, episodes: Dict[str, Location], **kw):
        super().__init__(**kw)

        #[0] normal color , [1] down color
        #self.colors = (app.get, (255/255, 200/255, 100/255, 1)) 
        pins = []

        for episode in episodes:
            pins.append(Pin(episode))

        self.lst_episodes = pins     
        self.wd_detail = DetailWidget()
        self.wd_detail.btn_start.bind(on_press=self.start_scenes)


    def start_scenes(self, *args):
        self.episode = self.wd_detail.pin.episode
        self.close_episode()

    def close_episode(self):
        p = self.wd_detail.pin
        p.state = 'normal'
        self.lst_episodes.remove(p)
      
    def on_lst_episodes(self, instance, lst):
        self.remove_pins(lst)
        self.add_pins(lst)

       
    #def on_enter(self, *args):
    #    self.fin
      
    def remove_pins(self, pins: List):
        for c in self.children:
            if c not in pins and isinstance(c, Pin): self.remove_widget(c)

    def add_pins(self, pins: List):
        for pin in pins:
            if pin in self.children: self.remove_widget(pin)
            self.add_widget(pin)
            #pin.color = self.colors[0]
            x, y = self.convert_geo_to_point(pin.location.lat, pin.location.lon)
            pin.pos_hint = {'x': x, 'center_y': y} 
            #print(pin.pos, self.size, x,y)

    def show_detail(self, pin: Pin):
        if pin.state == 'normal':
            pin.color = pin.my_color #self.colors[0]
            if pin is self.wd_detail.pin: self.remove_widget(self.wd_detail)
        else:
            new_color = [1-x for x in pin.my_color]
            new_color[3] = 1 #alpha value
            pin.color = new_color
            self.wd_detail.update(pin)
            if self.wd_detail not in self.children: self.add_widget(self.wd_detail)


    
    def convert_geo_to_point(self, lat: float, lon:float) -> tuple[float, float]:
        #approximately maps only to this specific world map 1830
        return  (1720 + lon*13.17)/4500, (985 + lat*15.4)/2234




class Map(Image):
    def __init__(self, **kwargs):
        self.ix, iy = 0,0
        return super().__init__(**kwargs)

class DetailWidget(RelativeLayout):
    btn_close: ObjectProperty()
    btn_start: ObjectProperty()
    img: ObjectProperty()
    lbl_title: ObjectProperty()
    lbl_desc: ObjectProperty()
    lbl_city: ObjectProperty()
    pin = None

    def update(self, pin: Pin):
        if self.pin not in [None, pin]: self.pin.state = 'normal'

        self.pin = pin
        self.img.source = pin.detail.img_path
        self.lbl_title.text = pin.detail.title
        self.lbl_desc.text = pin.detail.desc

        #add hyperlink
        self.lbl_city.text = pin.location.location_name
        self.lbl_city.url = pin.location.uri



################################################################
# Main Loop

class DummyManager(ScreenManager):
    
    def __init__(self, **kw):
        super().__init__(**kw)
        self.add_widget(MapScene(name='map'))
        self.current = 'map'

      
class MapApp(App):
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
    MapApp().run()
       