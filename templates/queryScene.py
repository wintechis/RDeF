
from typing import Tuple, List, Union, Dict
from dataclasses import dataclass
from unittest import result
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader, TabbedPanelItem
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

from rdf_utils import remove_all_namespaces, get_ns_from_string
from rdflib.namespace import NamespaceManager, Namespace

kv_file = f'{__file__[: __file__.rfind(".")]}.kv'
if not kv_file in Builder.files: Builder.load_file(kv_file) # load kv file with same name of py file in same dir

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

    def activate_tab(self, header: Union[str, TabbedPanelHeader, TabbedPanelItem]) -> None:
        if isinstance(header, str):
            self.__activate_tab_by_str(header)
        if isinstance(header, (TabbedPanelHeader, TabbedPanelItem)):
            self.__activate_tab_by_obj(header)

    def __activate_tab_by_str(self, header: str) -> None:         
        for tab in self.viewer.tab_list: 
            if tab.text == header: self.viewer.switch_to(tab)

    def __activate_tab_by_obj(self, header: Union[TabbedPanelHeader, TabbedPanelItem]) -> None:
        for tab in self.viewer.tab_list: 
            if tab == header: self.viewer.switch_to(tab)


class QueryPanel(TabbedPanel):
    query_tab= ObjectProperty()
    free_view= ObjectProperty()
    markup_query= StringProperty()


    def on_markup_query(self, instance, value):
        for tab in self.tab_list:
            if tab.text == 'Free': continue
            tab.content.query_space.markup_query = self.markup_query

class QueryLine(StackLayout):
    pass

class QuerySpace(GridLayout):

    start_area = ObjectProperty()
    mode = StringProperty()
    markup_query: str = StringProperty()
    draggables = ListProperty()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.max_len = 0 
        #TODO add comma handling

    def on_markup_query(self, instance, value):
        self.reset()

    def add_new_stackline(self) -> QueryLine:
        self.add_widget(QueryLine())
        return self.children[0]

    def fill_query_space(self, lst: List, is_drag: bool):
       turtle_indent = False
       lst_indent = []
       stack_line = self.add_new_stackline()
       for i, word in enumerate(lst):
            new_line = False
            if word == '\t': continue #ignore tabs
            if '\n' in word and i != 0:
                new_line = True 
                stack_line = self.add_new_stackline()
            lst_indent, turtle_indent = self.calculate_indents(word, lst[i-1], lst[i+1] if len(lst) > i+1 else '\n', lst_indent, turtle_indent)

            if new_line: self.add_indents(stack_line, lst_indent, turtle_indent)
            self.add_label(stack_line, word, is_drag)

    def calculate_indents(self, cur_word: str, prior_word: str, next_word:str, bracket_indent: List[str], turtle_indent:str) -> Tuple[List[str], str]:
        # [0] brackets indentation, [1] turtle indentation
        if prior_word == '{':
                bracket_indent.append(' '*6) # big tab
        elif prior_word == ';':
            turtle_indent = ' '*4 #tab
        elif prior_word == ',':
            turtle_indent = ' '*8 #double tab

        if cur_word == '.': turtle_indent = ''
        if cur_word == '}' and '\n' in next_word:
            bracket_indent.pop()  
        return bracket_indent, turtle_indent

    def add_indents(self, line: QueryLine, lst_indent: List[str], turtle_indent:str) -> None:
         #only creates NormalLabels, is_drag parameter does not affect creation
        for indent in lst_indent:
            self.add_label(line, indent, True)
        if turtle_indent: self.add_label(line, turtle_indent, True) 

    def add_label(self, line: QueryLine, word: str, is_drag: bool) -> None:
        if word[0] == '$':
            #if not is_drag, then is_blank instead
            line.add_widget(PlaceholderLabel(text='  '*self.max_len)) if is_drag else line.add_widget(QueryBlank(char_limit=self.max_len))
        else:
            line.add_widget(NormalLabel(text=word))

    def replace_placeholder(self, dl: DragLabel, ph: PlaceholderLabel):
        if not ph: return
        i = self.children.index(ph)
        self.remove_widget(ph)
        dl.cur_placeholder = None
        dl.parent.remove_widget(dl)
        self.add_widget(dl, index=i)

    def reset(self):
        new_query = self.markup_query.replace('\r\n', '\n').replace('\n', ' \n') #ensure space for new line for Win/Linux
        self.lst_query = [s for s in new_query.split(' ') if s] # remove spaces, indendation is handled by add_indents

        x = []
        for word in self.lst_query:
            if word.startswith('$'):
                #remove $ from variable 
                x.append(word[1:])
                #adjust max blank width
                self.max_len = max(self.max_len, len(x[-1]))
        self.draggables = x

        self.clear_widgets()
        self.fill_query_space(self.lst_query, is_drag=(self.mode == 'drag'))
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
        
        # # query string for blank view is not updated bc self.children is not updated... this is a temporary workaround.
        # self.parent.parent.parent.query =  ' '.join(map(lambda child: child.text, list(reversed(self.parent.children))))

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
        # self.cols=1

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

    upper_view: FileViewerView = ObjectProperty()
    lower_view: FileViewerView = ObjectProperty()

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

        # Print result from solution
        nm = {n.toPython(): p for p,n in self.chapters_graph.namespace_manager.namespaces()} | {n.toPython(): p for p,n in self.g.namespace_manager.namespaces()}
        self.display_result(input=self.rst_solution, output=self.upper_view.contents['target'], nm=nm)
        self.lower_view.contents['target'].text = self.upper_view.contents['target'].text

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
        self.upper_view.activate_tab('Query Result')
        self.lower_view.activate_tab('Target Result')
       
        content = self.query_panel.content.children[0].query_space
        query = content.text if self.query_panel.query_tab.text == 'Free'else ' '.join(reversed([word.text for line in content.children for word in line.children]))
        
        try:
            rst = self.chapters_graph.query(query)
            self.display_result(input=rst, output=self.upper_view.contents['query'], nm=self.get_my_namespaces(query))
        except ParseException as e:
            self.upper_view.contents['query'].text = f'Invalid SPARQL Query!\n\n{e.msg}'
            return


        if rst == self.rst_solution:
            self.btn_execute.unbind(on_release=self.execute_query)
            self.btn_execute.bind(on_release=lambda *args: self.close_scene())
            self.btn_execute.text = 'Continue'
            self.btn_reset.disabled = True
            
    def close_scene(self):
        g = Graph()
        remove_all_namespaces(g)
        self.graph = g

    def get_my_namespaces(self, query:str) -> Dict[str,str]:
        return {ns:p for p, ns in get_ns_from_string(query)}

    def display_result(self, input: rdflib.query.Result, output: TextInput, nm: Dict[str,str]):
        s = 'No valid SPARQL query. Use "ASK", "CONSTRUCT". "DESCRIBE", or "SELECT" at the start of a SPARQL query!'
        if input.type == 'ASK':  
            s = "Result: True" if input.askAnswer else "Result: False"
        elif input.type in ("CONSTRUCT", "DESCRIBE"):
            s = input.serialize(format='txt')
        elif input.type == 'SELECT':
            _input = list(input)
            #create prefix table
            tbl_p, nm = self.create_prefix_table(_input, nm)
            #create result table            
            tbl_rst, header = self.create_result_table(_input, nm)
            #create meta table
            tbl_meta = self.create_meta_table(_input, header)
            #combine tables into single string
            s = tbl_meta.get_string() + '\n\n' \
                        + tbl_p.get_string() + '\n\n' \
                        +(tbl_rst.get_string() if len(input) > 0 else '')
        output.text = s
        
    def create_prefix_table(self, resultSet: List[rdflib.query.ResultRow], all_nm: Dict[str,str]) -> Tuple[PrettyTable,NamespaceManager]:
        tbl_p = PrettyTable()
        tbl_p.field_names = ["PREFIX", "NAMESPACE"]
        nm = self.get_rel_namespace_manager(resultSet, all_nm) #retrieve only relevant namespaces
        for p, n in sorted(nm.namespaces(), key=lambda nm: nm[0]):
            tbl_p.add_row([p, n])
        tbl_p.align = 'l'
        return tbl_p, nm

    def create_result_table(self, resultSet: List[rdflib.query.ResultRow], nm: NamespaceManager) -> Tuple[PrettyTable, List[str]]:
        header=[]
        tbl_rst = PrettyTable()
        for i, row in enumerate(resultSet):
            if i == 0: 
                header = list(row.asdict().keys())
                tbl_rst.field_names = header
            tbl_rst.add_row(list(map(lambda term: term.n3(nm), row)))
        tbl_rst.align = 'l'
        return tbl_rst, header

    def create_meta_table(self, resultSet: List[rdflib.query.ResultRow], header: List[str]) -> PrettyTable:
        tbl_meta = PrettyTable()
        tbl_meta.header = False
        try:                
            tbl_meta.add_row(['Column Count:', len(header)])
        except UnboundLocalError:
            tbl_meta.add_row(['Column Count:', 0])
        tbl_meta.add_row(['Row Count:', len(resultSet)])
            
        tbl_meta.align = 'l'
        return tbl_meta


    def get_rel_namespace_manager(self, result: List[rdflib.query.ResultRow], nm_dict: Dict[str, str]) -> NamespaceManager:
        # get new dict with only namespaces used by results
        pn = {}
        for row in result:
            for field in row:
                x = field.toPython()
                if isinstance(x,str):
                    for k,v in nm_dict.items():
                        if x.startswith(k):
                            pn[v] = k
        # create new NamespaceManager
        g = Graph()
        nm = NamespaceManager(g)
        remove_all_namespaces(g)
        for k,v in pn.items():
            nm.bind(k, Namespace(v))
        return nm


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


