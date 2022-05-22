
from operator import index
from typing import Tuple, List, Literal, Dict
from dataclasses import dataclass
from xmlrpc.client import Boolean
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.textinput import TextInput
from kivy.uix.codeinput import CodeInput
from kivy.properties import ObjectProperty, ListProperty, BooleanProperty,NumericProperty, DictProperty, StringProperty
#from behaviors import DragBehavior
from kivy.uix.behaviors import DragBehavior, FocusBehavior
from prettytable import PrettyTable
import pygments
from kivy.clock import Clock
from rdflib import ConjunctiveGraph, URIRef
import rdflib
from behaviors import HoverBehavior
from pyparsing.exceptions import ParseException
import json
import pygments.styles as styles
import os
from kivy.app import App
#from rdflib.query import Result

from rdf_utils import remove_all_namespaces

if not __name__ == '__main__':
    from kivy.lang import Builder
    Builder.load_file('templates/query.kv')


#UP       = 273
#DOWN     = 274
#LEFT     = 276
#RIGHT    = 275
#SPACE    = 32
TAB       = 9
SHIFT     = 304


@dataclass(frozen=True)
class QueryItem:
    question: str
    markup_query: str


class FileViewerView(BoxLayout):
    btn_select = ObjectProperty()
    viewer = ObjectProperty()
    contents = DictProperty()

    graph: rdflib.Graph = ObjectProperty(None)

    def on_graph(self, instance, graph):
        for tab in self.viewer.tab_list:
            if not tab.text.lower() in ['target result', 'query result']:
                tab.content.text = graph.serialize(format=tab.text.lower())


class RectangledButton(HoverBehavior, Button):
  
    ##  Reuse Functions for functionality
    def on_enter(self, *args):
        self.background_color = App.get_running_app().hl
        return super().on_enter(*args)

    def on_leave(self, *args):
        self.background_color = App.get_running_app().bg
        return super().on_leave(*args)

class SelectButton(RectangledButton):
    pass


class FileDropDown(DropDown):

    def __init__(self, chapter_path: str, **kwargs):
        #add parameter for chapter_path: str
        super().__init__(**kwargs)
        self.bind(on_select=self.update_mainbutton)
        self.files = FileDropDown.get_chapter_dbs(chapter_path)
        self.add_buttons()

    def add_buttons(self):
        btn = SelectButton(text=f'current', size_hint_y=None, height=44)
        btn.bind(on_release=lambda btn: self.select(btn.text))
        btn.width = btn.font_size/1.5 *len(btn.text)
        self.add_widget(btn)
        for key in self.files.keys():
            btn = SelectButton(text=f'{key}', size_hint_y=None, height=44)
            btn.width = btn.font_size/1.5 *len(btn.text)
            btn.bind(on_release=lambda btn: self.select(btn.text))
            self.add_widget(btn)

    @staticmethod
    def get_chapter_dbs(chapter_path):
        base, folder_name = os.path.split(chapter_path)
        index = int(folder_name.split('_')[0])
        db_path = os.path.join(base, 'db')
        d = dict()
        for file in next(os.walk(db_path))[2]:
            try:
                if int(file.split('_')[0]) < index:
                    no_suffix = file.split('.')[0]
                    d[no_suffix] = os.path.join(db_path, file)
            except ValueError:
                no_suffix = file.split('.')[0]
                d[no_suffix] = os.path.join(db_path, file)
        return d


    def update_mainbutton(self, instance, val):
        if not self.attach_to: return
        self.attach_to.text = val     

class CustomDropDown(DropDown):


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_select=self.update_mainbutton)        

        for index in range(5):
            btn = SelectButton(text='Value %d' % index, size_hint_y=None, height=44)
            #add label for non_selectable
            btn.bind(on_release=lambda btn: self.select(btn.text))
            self.add_widget(btn)
        
        btn = SelectButton(text='Chapter 1', size_hint_y=None, height=44)
        btn.bind(on_release=lambda btn: self.select(btn.text))
        self.add_widget(btn)

        btn = SelectButton(text='Current', size_hint_y=None, height=44)
        btn.bind(on_release=lambda btn: self.select(btn.text))
        self.add_widget(btn)
       
    def update_mainbutton(self, instance, val):
        if not self.attach_to: return
        self.attach_to.text = val


class StyleDropDown(DropDown):
    def __init__(self, chapter_path:str, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_select=self.update_mainbutton)        

        for name in styles.get_all_styles():
            btn = SelectButton(text=name, size_hint_y=None, height=44)
            #add label for non_selectable
            btn.bind(on_release=lambda btn: self.select(btn.text))
            self.add_widget(btn)

       
    def update_mainbutton(self, instance, val):
        if not self.attach_to: return
        self.attach_to.text = val



class PlaceholderLabel(Label):
    highlight = BooleanProperty(False)


class DragLabel(DragBehavior, PlaceholderLabel):

    def __init__(self, drag_area: Widget = None,start_area:Widget = None, query_area:Widget = None, **kwargs):
        super().__init__(**kwargs)
        self.drag_area = drag_area
        self.query_area = query_area
        self.start_area = start_area
        self.cur_placeholder = None
        self.again = False

    
    def on_touch_down(self, touch):
        if not self.collide_point(*self.to_parent(*touch.pos)): return
        if not self.drag_area: self.drag_area = self.parent
        self.last_pos = self.pos[:]
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        placeholder = self.get_first_colliding_placeholder()
        if not placeholder == self.cur_placeholder:
            if not self.cur_placeholder == None: self.cur_placeholder.highlight = False
            self.cur_placeholder = placeholder
            if not self.cur_placeholder == None: self.cur_placeholder.highlight = True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if not self.collide_point(*self.to_parent(*touch.pos)): return
        #if not self.is_within(self.drag_area): self.x, self.y = self.last_pos
        self.switch_with_placeholder() 
        return super().on_touch_up(touch)


    def is_within(self, widget: Widget):
        x, y, w, h  = *self.to_widget(*widget.to_window(*widget.pos)), *widget.size
        return (self.x > x and self.x + self.width < x + w) and (self.y > y and self.y + self.height < y + h)


    def switch_with_placeholder(self):
        if self.parent == self.query_area:
           self.replace_with_placeholder()
        # Otherwise draglabel cannot directly move from query space to placeholder because second add_widget is not considered for next frame 
        Clock.schedule_once(self.replace_placeholder)
    
    def replace_with_placeholder(self):
        i = self.query_area.children.index(self)
        self.switch_area(self.query_area, self.start_area, i)
        self.query_area.add_widget(PlaceholderLabel(text='  '*self.query_area.max_len), index=i)

        #sort alphabetically
        self.start_area.children.sort(key=lambda c: c.text.lower(), reverse=True)

    def replace_placeholder(self, dt):
        ph = self.cur_placeholder
        if not ph: return
        self.switch_area(self.start_area,self.query_area, self.query_area.children.index(ph))
        self.query_area.remove_widget(ph)
        self.cur_placeholder = None

    def switch_area(self, origin: Widget, target: Widget, idx: int):
        origin.remove_widget(self)
        target.add_widget(self, index=idx)


    def get_first_colliding_placeholder(self):
        for c in self.query_area.children: 
            if type(c) == PlaceholderLabel and self.collide_with(c): return c #self.collide_widget
        return None

    def collide_with(self, wd:Widget):
        x, y, w, h  = *self.to_widget(*wd.to_window(*wd.pos)), *wd.size
        if self.right < x:
            return False
        if self.x > x + w:
            return False
        if self.top < y:
            return False
        if self.y > y + h:
            return False
        return True

    
class QueryPanel(TabbedPanel):
    query_tab= ObjectProperty()
    free_view= ObjectProperty()
    markup_query= StringProperty()


    def on_markup_query(self, instance, value):
        for tab in self.tab_list:
            if tab.text == 'Free': continue
            tab.content.query_space.markup_query = self.markup_query



class QuerySpace(StackLayout):
    start_area = ObjectProperty()
    mode = StringProperty()
    markup_query = StringProperty()
    draggables = ListProperty()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #test_string = 'Hallo, das $ist ein langer Test, $um zu schauen, $ob das $ganze auch funktioniert'*2
      #len(max(self.lst_str, key=len))
        self.max_len = 0 
        #self.fragmented_query = query.query
        #self.solution = query.solution
        #self.lst_query = query.split()
      
        #TODO add comma handling


    def on_markup_query(self, instance, value):
        self.reset()

    def create_drag_drop(self, lst: List):
         for word in lst:
                if word[0] == '$':
                    self.add_widget(PlaceholderLabel(text='  '*self.max_len))
                else:
                    self.add_widget(NormalLabel(text=word))

    def create_blank(self, lst):
        for word in lst:
            if word[0] == '$':
                self.add_widget(QueryBlank(char_limit=self.max_len))
            else:
                self.add_widget(NormalLabel(text=word))

    def replace_placeholder(self, dl: DragLabel, ph: PlaceholderLabel):
        if not ph: return
        i = self.children.index(ph)
        self.remove_widget(ph)
        dl.cur_placeholder = None
        dl.parent.remove_widget(dl)
        self.add_widget(dl, index=i)

    
    def reset(self):
        self.lst_query = self.markup_query.split()
        x = []
        for word in self.lst_query:
            if word.startswith('$'):
                #remove $ from variable 
                x.append(word[1:])
                #adjust max blank width
                self.max_len = max(self.max_len, len(x[-1]))
        self.draggables = x

        self.clear_widgets()
        if self.mode == 'drag':
            self.create_drag_drop(self.lst_query)
        else:
            self.create_blank(self.lst_query)
        if self.start_area: self.start_area.reset()



class QueryBlank(TextInput):
    hold_shift=False
    
    def __init__(self, char_limit: int, **kwargs):
        super().__init__(**kwargs)
        self.bind(text=self.on_text)
        self.char_limit = char_limit
        self.width = self.char_limit*self.font_size

    
    def on_text(self, instance, val):
        if len(self.text) > self.char_limit:
            self.text = self.text[:self.char_limit]
        
        # query string for blank view is not updated bc self.children is not updated... this is a temporary workaround.
        self.parent.parent.parent.query =  ' '.join(map(lambda child: child.text, list(reversed(self.parent.children))))

    def on_enter(self, *args):
        self.focus= True

    
    def keyboard_on_key_down(self, window, keycode: Tuple[int, str], text, modifiers):
        if keycode[1] == 'shift': QueryBlank.hold_shift = True
        if keycode[1] == 'tab':
            if QueryBlank.hold_shift: self.get_focus_previous().focus = True
            else: self.get_focus_next().focus = True
        return super().keyboard_on_key_down(window, keycode,text, modifiers)

    def keyboard_on_key_up(self, window, keycode: Tuple[int, str]):
        if keycode[1] == 'shift': QueryBlank.hold_shift = False
        return super().keyboard_on_key_up(window, keycode)
      
  


class NormalLabel(Label):
    pass

class DragNDropView(GridLayout):
    
    def __init__(self, **kw):
      
        #self.orientation = 'vertical'
        super().__init__(**kw)
        self.cols=1


    #def contains(self, widget: Widget):
    #    x, y, w, h  = *self.to_widget(*widget.pos), *widget.size
    #    return (self.x < x and self.x + self.width > x + w) and (self.y < y and self.y + self.height > y + h)
           
        
      


class DragLabelStart(StackLayout):
    query_area=ObjectProperty()
    draggables: List[str] = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.drag_labels: List[DragLabel] = []


    #def on_draggables(self, instance, lst):
    #    self.reset()
       

    def init(self, dt):
        for c in self.children:
            c.query_area = self.query_area


    def update_drag_labels(self):
        self.clear_widgets()
        for lbl in self.drag_labels: self.add_widget(lbl)


    def reset(self):
        self.drag_labels = []
        for word in sorted(self.draggables):
            self.drag_labels.append(DragLabel(text=word, drag_area=self.parent.parent, start_area=self))
        Clock.schedule_once(self.init)
        self.update_drag_labels()

class QueryScene(Screen):
    query = StringProperty()
    solution = StringProperty()

    #lst_episodes = ListProperty()

    upper_view = ObjectProperty()
    lower_view = ObjectProperty()

    btn_style = ObjectProperty()
    btn_reset = ObjectProperty()
    btn_execute = ObjectProperty()

    query_panel = ObjectProperty()
    markup_query = StringProperty()

    graph = ObjectProperty()

    def __init__(self, query_item: QueryItem, episode_graph: ConjunctiveGraph, chapter_path: str, **kwargs):
        super().__init__(**kwargs)
        self.markup_query = query_item.markup_query
        self.query_panel.lbl_question.text = query_item.question
        for view in (self.upper_view, self.lower_view):
            view.btn_select.bind(on_release=self.show_files)
        self.btn_style.bind(on_release=self.show_styles)
        self.btn_reset.bind(on_release=self.reset_tab)
        self.btn_execute.bind(on_release=self.execute_query)
        self.g = episode_graph
        self.chapter_path = chapter_path
        self.upper_view.btn_select.bind(text=self.load_file)
        self.lower_view.btn_select.bind(text=self.load_file)


        ## Display solution result
        self.chapters_graph = rdflib.Graph()
        remove_all_namespaces(self.chapters_graph)
        files = FileDropDown.get_chapter_dbs(self.chapter_path)
        for file_name in files:
            self.chapters_graph.parse(os.path.split(self.chapter_path)[0] + f'/db/{file_name}.ttl')
        self.chapters_graph += self.g
        query =  ' '.join(self.markup_query.replace('$', '').split())
        self.rst_solution = self.chapters_graph.query(query)
        self.display_result(input=self.rst_solution, output=self.upper_view.contents['target'], nm=self.chapters_graph.namespace_manager)
        
    def load_file(self, instance, file_name):
        if file_name == 'current':
            instance.parent.parent.graph = self.g
        else:
            g = rdflib.Graph()
            remove_all_namespaces(g)
            instance.parent.parent.graph = g.parse(os.path.split(self.chapter_path)[0] + f'/db/{file_name}.ttl')
            

    def show_files(self, instance):
        self.open_dropdown(instance, 0)

    def show_styles(self, instance):
        self.open_dropdown(instance, 1)

    def open_dropdown(self, instance: Button, idx: int):
        dropdowns = [FileDropDown, StyleDropDown] #CustomDropDown
        dd = dropdowns[idx](chapter_path=self.chapter_path)
        dd.auto_width = False
        dd.width = instance.parent.parent.width
        dd.max_height = self.height#instance.parent.parent.height - instance.parent.height
        dd.open(instance)


    def reset_tab(self, instance):
        self.query_panel.content.children[0].query_space.reset()

    def execute_query(self,instance):
        content = self.query_panel.content.children[0].query_space
        query = content.text if self.query_panel.query_tab.text == 'Free'else ' '.join(map(lambda child: child.text, list(reversed(content.children))))
        
        try:
            rst = self.chapters_graph.query(query)
            self.display_result(input=rst, output=self.upper_view.contents['query'], nm=self.chapters_graph.namespace_manager)
        except ParseException as e:
            self.upper_view.contents['query'].text = f'Invalid SPARQL Query!\n\n{e.msg}'
            return


        if rst == self.rst_solution:
            g = ConjunctiveGraph()
            remove_all_namespaces(g)
            self.graph = g



    
    def display_result(self, input: rdflib.query.Result, output: TextInput, nm: rdflib.ConjunctiveGraph.namespace_manager):
        s = 'No valid SPARQL query. Use "ASK", "CONSTRUCT". "DESCRIBE", or "SELECT" at the start of a SPARQL query!'

        if input.type == 'ASK':  
            s = "Result: True" if input.askAnswer else "Result: False"
        elif input.type in ("CONSTRUCT", "DESCRIBE"):
            s = input.serialize(format='txt')
        elif input.type == 'SELECT':
            #create prefix table
            
            tbl_p = PrettyTable()
            tbl_p.field_names = ["PREFIX", "NAMESPACE"]
            for p, n in nm.namespaces():
                tbl_p.add_row([p, n])
            tbl_p.align = 'l'


            #create result table
            
            tbl_rst = PrettyTable()
            for i, row in enumerate(input):
                if i == 0: 
                    header = list(row.asdict().keys())
                    tbl_rst.field_names = header
                tbl_rst.add_row(list(map(lambda term: term.n3(nm), row)))
            tbl_rst.align = 'l'

            #create meta table
            tbl_meta = PrettyTable()
            tbl_meta.header = False
            try:                
                tbl_meta.add_row(['Column Count:', len(header)])
            except UnboundLocalError:
                tbl_meta.add_row(['Column Count:', 0])
            tbl_meta.add_row(['Row Count:', len(input)])
              
            tbl_meta.align = 'l'

            s = tbl_meta.get_string() + '\n\n' \
                +tbl_p.get_string() + '\n\n' \
                + (tbl_rst.get_string() if len(input) > 0 else '')
        output.text = s


class  SparqlDisplay(CodeInput):
    def reset(self):
        self.text = ''

class RdfDisplayer(TabbedPanel):
    triples = ListProperty(None)
    boxes = DictProperty(None)
    
        
class DialogueBox(BoxLayout):
    info_label = ObjectProperty(None)
    speaker_label = ObjectProperty(None)
    speaker_img   = ObjectProperty(None)
    cleared       = BooleanProperty(False)
    completed     = BooleanProperty(False)
    file_name     = StringProperty('')
   

              
class InfoLabel(Label):
    rdf_box = ObjectProperty(None)
    found_triples = ListProperty([])
    cleared       = ObjectProperty(False)
    count_label   = ObjectProperty()
    #all_triples = ListProperty([])



