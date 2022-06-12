
from turtle import width
from typing import Tuple, List
from dataclasses import dataclass
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.textinput import TextInput
from kivy.uix.codeinput import CodeInput
from kivy.properties import ObjectProperty, ListProperty, BooleanProperty, DictProperty, StringProperty
from prettytable import PrettyTable
from kivy.clock import Clock
from rdflib import Graph
import rdflib
from pyparsing.exceptions import ParseException
import os
#from rdflib.query import Result

from myWidgets.myDropDowns import FileDropDown, StyleDropDown
from myWidgets.myLabels import PlaceholderLabel, DragLabel, NormalLabel

from rdf_utils import remove_all_namespaces

Builder.load_file(f'{__file__[:-2]}kv') # load kv file with same name of py file in same dir

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
        self.max_len = 0 
      
        #TODO add comma handling

    def on_markup_query(self, instance, value):
        self.reset()

    def create_drag_drop(self, lst: List):
          
        indices = sorted([i for i, x in enumerate(lst) if x == "{"], reverse=True)
        for idx in indices:
            lst.insert(idx+1, '\n')

        for word in lst:
            if word[0] == '$':
                self.add_widget(PlaceholderLabel(text='  '*self.max_len))
            else:
                self.add_widget(NormalLabel(text=word))

    def create_blank(self, lst):
        pass
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
      
  
# class NormalLabel(Label):
#     pass

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

    def __init__(self, query_item: QueryItem, episode_graph: Graph, chapter_path: str, **kwargs):
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


    def on_enter(self, **kw):
        ## Display solution result
        self.chapters_graph = rdflib.Graph()
        remove_all_namespaces(self.chapters_graph)
        files = FileDropDown.get_chapter_dbs(self.chapter_path)
        for file_name in files:
            self.chapters_graph.parse(os.path.split(self.chapter_path)[0] + f'/db/{file_name}.ttl')
        
        # see end result of given solution
        self.chapters_graph += self.g
        query =  ' '.join(self.markup_query.replace('$', '').split())
        self.rst_solution = self.chapters_graph.query(query)
        #print(query)
        self.display_result(input=self.rst_solution, output=self.upper_view.contents['target'], nm=self.chapters_graph.namespace_manager)

        return super().on_enter(**kw)



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
            g = Graph()
            remove_all_namespaces(g)
            self.graph = g


    def display_result(self, input: rdflib.query.Result, output: TextInput, nm: rdflib.Graph.namespace_manager):
        s = 'No valid SPARQL query. Use "ASK", "CONSTRUCT". "DESCRIBE", or "SELECT" at the start of a SPARQL query!'
        if input.type == 'ASK':  
            s = "Result: True" if input.askAnswer else "Result: False"
        elif input.type in ("CONSTRUCT", "DESCRIBE"):
            s = input.serialize(format='txt')
        elif input.type == 'SELECT':
            #create prefix table
            tbl_p = PrettyTable()
            tbl_p.field_names = ["PREFIX", "NAMESPACE"]
            for p, n in sorted(nm.namespaces(), key=lambda nm: nm[0]):
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

# class RdfDisplayer(TabbedPanel):
#     triples = ListProperty(None)
#     boxes = DictProperty(None)
    
        
class DialogueBox(BoxLayout):
    info_label = ObjectProperty(None)
    speaker_label = ObjectProperty(None)
    speaker_img   = ObjectProperty(None)
    cleared       = BooleanProperty(False)
    completed     = BooleanProperty(False)
    file_name     = StringProperty('')
   

              
if __name__ == '__main__':
    print('Run "python main.py" to start RDeF!')


