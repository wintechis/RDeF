if __name__ == '__main__':
    import os
    os.environ['KIVY_HOME'] = os.getcwd()

from dataclasses import dataclass

import kivy
kivy.require('2.0.0')



from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.image import Image
from kivy.properties import ObjectProperty, ListProperty, ColorProperty, DictProperty
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


@dataclass(frozen=True)
class Event:
    location: Location
    #later person instead of filepath
    img_path: str
    title: str
    desc: str
    scenes: List

class Pin(ToggleButtonBehavior, HoverBehavior, Image):
    my_color = ListProperty()

    def __init__(self,event: Event, **kwargs):
        super().__init__(**kwargs)
        self.event = event

    def on_state(self, widget, value):
        self.parent.show_detail(self)

           

class MapScene(Screen):
    wd_detail = ObjectProperty()
    lst_episodes = ListProperty()
    #scenes = DictProperty()

    def __init__(self, events: List[Event], idx: ListProperty, **kw):
        super().__init__(**kw)

        self.idx = idx
        #[0] normal color , [1] down color
        #self.colors = (app.get, (255/255, 200/255, 100/255, 1)) 
        pins = []
        #for event in self.load_events():
        for event in events:
            pins.append(Pin(event))

        self.lst_episodes = pins     
        self.wd_detail = DetailWidget()
        self.wd_detail.btn_start.bind(on_press=self.start_scenes)


    def start_scenes(self, *args):
        self.parent.episodes.extend(self.wd_detail.pin.event.scenes)
        self.parent.episodes.append(self)
        self.close_episode()
        self.idx[0] += 1

    def close_episode(self):
        p = self.wd_detail.pin
        p.state = 'normal'
        self.lst_episodes.remove(p)
      
    def on_lst_episodes(self, instance, lst):
        self.remove_pins(lst)
        self.add_pins(lst)

        #next map
        #if len(lst) < 1: self.idx[0] += 1    
    

    def on_enter(self, *args):
        if len(self.lst_episodes) < 1: self.idx[0] += 1
      
    def remove_pins(self, pins: List):
        for c in self.children:
            if c not in pins and isinstance(c, Pin): self.remove_widget(c)

    def add_pins(self, pins: List):
        for pin in pins:
            if pin in self.children: self.remove_widget(pin)
            self.add_widget(pin)
            #pin.color = self.colors[0]
            x, y = self.convert_geo_to_point(pin.event.location.lat, pin.event.location.lon)
            pin.pos_hint = {'x': x, 'center_y': y} 
            #print(pin.pos, self.size, x,y)


    def load_events(self) -> list:
        #TODO Replace example with sparql query

        #latlon: https://www.latlong.net/
        #uri: https://www.wikidata.org
        berlin = Location('Berlin', 'https://www.wikidata.org/wiki/Q64', 52.5170365,13.3888599)
        rome = Location('Rome', 'https://www.wikidata.org/wiki/Q220',41.8933203,12.4829321)
        sydney = Location('Sydney', 'https://www.wikidata.org/wiki/Q220',-33.8548157,151.2164539)
        zero = Location('Zero', 'https://www.wikidata.org/wiki/Q220',0,0)

        d = '''Lorem ipsum dolor sit amet'''

        t = 'ssssssssssssssssss asdsadasd     dasdasdsad        dasdasdsa               asdaad       asds'

        events = []
        events.append(Event(berlin, '../resources/julian.png', t, d))
        events.append(Event(rome, '../resources/julian.png', 'Second Encounter', 'Second description'))
        events.append(Event(sydney, '../resources/julian.png', '3rdd Encounter', '3rd description'))
        events.append(Event(zero, '../resources/julian.png', '3rdd Encounter', '3rd description'))
        return events

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
        self.img.source = pin.event.img_path
        self.lbl_title.text = pin.event.title
        self.lbl_desc.text = pin.event.desc

        #add hyperlink
        self.lbl_city.text = pin.event.location.location_name
        self.lbl_city.url = pin.event.location.uri



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
       