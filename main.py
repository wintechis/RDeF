#####################################
## Set Variable for Logger Path #####
import argparse
import json
import os
from typing import Dict, Iterator, List

main_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(main_dir)

###################################
## Kivy Import
os.environ["KIVY_HOME"] = os.path.join(os.getcwd(), "kivy")
os.environ["KIVY_NO_ARGS"] = "1"
import kivy

kivy.require("2.0.0")

###################################
## Scene Import
import sys

import kivy.logger

#### Update standard font, if defined
# from kivy.config import Config
# Config.set('kivy', 'default_font', ['Roboto', 'data/fonts/Roboto-Regular.ttf', 'data/fonts/Roboto-Italic.ttf', 'data/fonts/Roboto-Bold.ttf', 'data/fonts/Roboto-BoldItalic.ttf'])
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import DictProperty, ListProperty
from kivy.resources import resource_add_path, resource_find
from kivy.uix.screenmanager import ScreenManager

####################################
####################################


resource_add_path(os.path.join(os.getcwd(), "templates"))
import sys

sys.path.append(os.path.join(os.getcwd(), "templates"))

####################################
####################################


from templates.sparqlManager import SparqlManager
from templates.startScene import StartScene

# from chapter import Chapter
from templates.story import Story

from templates.myDataclasses import StoryInfo, DesignInfo
################################################################
# Main Loop





class RDeFManager(ScreenManager):
    def __init__(self, story_path: str, story_names: Dict[str, str], story=None, **kw):
        super().__init__(**kw)
        self.story_path = story_path
        self.start_screen = StartScene(story_names=story_names, idx=[])
        self.switch_to(self.start_screen)
        if story:
            self.start_story(story)

    def start_story(self, story_name):
        story_path = os.path.join(self.story_path, story_name)
        self.switch_to(Story(story_path))

    def close_story(self):
        current = self.current_screen
        self.switch_to(self.start_screen)
        self.remove_widget(current)


class MainApp(App):
    fg = ListProperty()
    bg = ListProperty()
    hl = ListProperty()
    story_info = DictProperty()

    def build(self):
        ## Load Design / Stories
        self.sparql = SparqlManager()
        self.title = "RDeF - RDF Training and Demonstration Framework"
        self.icon = "resources/rdef_16x16.ico"

        story_dir = os.path.join(os.getcwd(), "stories")
        story_names = self.get_stories(story_dir)

        args = parser.parse_args()
        args_story = args.story if args.story in story_names else None
        try:
            story = args_story if args_story else list(story_names.keys())[0]
            self.load_story_info(story=story, path=os.path.join(os.getcwd(), "stories" ))
        except AttributeError:
            # if no story folder is empty
            raise AttributeError
        except FileNotFoundError:
            di = DesignInfo()
            self.fg = di.fg
            self.bg = di.bg
            self.hl = di.hl
        self.font_size = 20

        return RDeFManager(story_dir, story_names, story=args_story)

    def get_stories(self, story_dir: str) -> list:
        return {
            story: os.path.join(story_dir, story)
            for story in next(os.walk(story_dir))[1]
        }

    def load_story_info(self, story, path):
        self.story_info = self.sparql.load_story_info(story, path)
        self.fg, self.bg, self.hl = self.story_info["colors"]


###########################################################
######## Main
##########################################################
if __name__ == "__main__":
    if hasattr(sys, "_MEIPASS"):
        resource_add_path(os.path.join(sys._MEIPASS))
    Clock.max_iteration = 50

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--play", "-p", dest="story", required=False, help="name of story to play"
    )
    MainApp().run()
