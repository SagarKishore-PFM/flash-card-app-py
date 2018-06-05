# -*- coding: utf-8 -*-
"""
Created on Saturday, May 26th 2018

@author: sagar

Kivy screen that displays the options for databases to select for the app.
"""

from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.popup import Popup
from kivy.uix.button import Button

from functools import partial

from fcdb import FCDataBase
from stacklistscreen import StackListScreen
from wordlistscreen import WordListScreen
from gamescreen import GameScreen
from helperfuncs import load_db, save_db, delete_temp

# TODO:

# Maybe make the stack and word databases object property inside the
#   screen manager. This way you can access it everywhere with
#   screen.manager.DB. Check if changing on other screens reflects it
#   here and if you can have a on_db function.
# Check what happens when you send empty stack and word databases to stack and
#   word screens
# Test more for empty databases... seems good so far
# Save db changes at appropriate places and on exit of app
# Clean up UI
# In word list screen show a label with number of words in database

DATABASE_LIST = []
DB_SEARCH_LIST = []


def db_init():
    global DATABASE_LIST
    global DB_SEARCH_LIST
    DB_SEARCH_LIST = [fcdb.name for fcdb in DATABASE_LIST]


class MainScreenManager(ScreenManager):

    database_list = ObjectProperty(None)


class DBRelativeLayout(RelativeLayout):

    # fc_database = ObjectProperty(None)

    def __init__(self, fc_database, *args, **kwargs):
        super(DBRelativeLayout, self).__init__(*args, **kwargs)
        self.fcdb = fc_database
        self.ids.DBNameLbl.text = self.fcdb.name

    def link_screens(self):
        self.manager_ = self.parent.parent.parent.parent.manager
        self.stack_screen = self.manager_.get_screen('stack screen')
        self.word_screen = self.manager_.get_screen('word screen')
        self.stack_screen.fcdb = self.fcdb
        self.word_screen.fcdb = self.fcdb

    def select_stack_database(self, instance):
        self.link_screens()
        self.manager_.current = 'stack screen'

    def select_word_database(self, instance):
        self.link_screens()
        self.manager_.current = 'word screen'


class DataBaseScreen(Screen):

    database_list = ObjectProperty(None)

    def __init__(self, database_list, *args, **kwargs):
        super(DataBaseScreen, self).__init__(*args, **kwargs)
        self.database_list = database_list
        self.load_db_widgets()

    def on_leave(self):
        pass

    def on_enter(self):
        pass

    def load_db_widgets(self):
        for fc_database in self.database_list:
            self.add_db_widget(fc_database)

    def add_db_widget(self, fc_database):
        DBRL = DBRelativeLayout(fc_database)
        self.ids.DBSelGL.add_widget(DBRL)


class CreateDBButton(Button):

    def open_popup(self, SelectableGridLayout):
        popup = CreateDBPopup()
        popup.ids.CreateNewDBBtn.bind(on_release=partial(self.create_new_fcdb,
                                                         popup,
                                                         SelectableGridLayout))
        popup.open()

    def create_new_fcdb(self, popup, SelectableGridLayout, instance):
        new_fcdb = FCDataBase(popup.ids.DBName.text)
        # TODO:
        # Add an option to choose words from an existing db in the below line
        # new_fcdb.word_db = popup.ids.XXXXX.
        global DATABASE_LIST
        SelectableGridLayout.add_widget(DBRelativeLayout(new_fcdb))
        DATABASE_LIST.append(new_fcdb)
        db_init()
        popup.dismiss()


class CreateDBPopup(Popup):

    button_disabled = BooleanProperty(True)

    def validate_text_input(self):
        global DB_SEARCH_LIST
        text = self.ids.DBName.text
        min_len = 3
        cond1 = len(text) < min_len
        cond2 = text in DB_SEARCH_LIST
        self.button_disabled = cond1 or cond2
        if(self.button_disabled):
            self.ids.ErrorMessage.text = \
                '* Database name must be Unique and contain more than ' + \
                f'{min_len} letters'
        else:
            self.ids.ErrorMessage.text = ""


class DataBaseApp(App):

    sm = ObjectProperty(None)

    def build(self):
        global DATABASE_LIST
        DATABASE_LIST = load_db()
        db_init()
        self.sm = ScreenManager()
        self.sm.current_screen
        d = DataBaseScreen(DATABASE_LIST)
        self.sm.add_widget(d)
        self.sm.current = 'db screen'
        a = StackListScreen()
        b = WordListScreen()
        c = GameScreen()
        self.sm.add_widget(a)
        self.sm.add_widget(b)
        self.sm.add_widget(c)
        return self.sm

    def on_stop(self):
        if(self.sm.current == 'game screen'):
            screen_ = self.sm.get_screen('game screen')
            screen_.save_changes()
        global DATABASE_LIST
        save_db(DATABASE_LIST)
        delete_temp()

    def on_start(self):
        pass


def main():
    DataBaseApp().run()


if __name__ == '__main__':
    main()
