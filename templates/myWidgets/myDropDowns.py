import os
from kivy.uix.dropdown import DropDown
import pygments.styles as styles


from .myButtons import SelectButton

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


from kivy.factory import Factory
Factory.register('CustomDropDown', CustomDropDown)
Factory.register('StyleDropDown', StyleDropDown)
Factory.register('FileDropDown', FileDropDown)   

