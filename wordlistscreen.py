# -*- coding: utf-8 -*-
"""
Created on Saturday, April 24th 2018

@author: sagar

Kivy screen that allows for adding new words as well as editting, deleting
and viewing existing words in the selected Word Databse.
"""

from kivy.app import App
from word import Word
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.properties import BooleanProperty

from functools import partial

from oxfordapi import addword
from compound_selection import SelectableLayout
from testdatabase import generate_test_stack_database
from testdatabase import generate_test_word_database
from helperfuncs import word_description, short_meaning

# TODO:

#     >> Database is not affected at the moment.
#     >> Minor clean up in the popup UIs
#     >> Add navigation to the StackList Screen and DataBaseScreen(?)
#     >> Cleanup the kv file
#     >> Add audio button in description?
#     >> Add audio in main screen WordRelativeLayouts

WORD_DATABASE = generate_test_word_database()

WORD_LIST = {word.name for word in WORD_DATABASE}
WORD_SEARCH_DICT = {word.name: word for word in WORD_DATABASE}


class WordRelativeLayout(SelectableLayout, RelativeLayout):

    def __init__(self, word_object, *args, **kwargs):
        self.word_object = word_object
        super(WordRelativeLayout, self).__init__(*args, **kwargs)
        self.draw()

    def draw(self):
        self.ids.WordNameLbl.text = self.word_object.name
        self.ids.WordMeaningLbl.text = short_meaning(self.word_object)


class WordGridLayout(SelectableLayout, GridLayout):
    pass


class ViewWordButton(Button):

    def open_popup(self, selected_word_relative_layout):
        selected_word_object = selected_word_relative_layout.word_object
        popup = ViewWordPopup(selected_word_object)
        popup.open()


class ViewWordPopup(Popup):

    def __init__(self, selected_word_object, *args, **kwargs):
        self.word_object = selected_word_object
        super(ViewWordPopup, self).__init__(*args, **kwargs)
        self.draw()

    def draw(self):
        self.ids.WordDescription.text = word_description(self.word_object)


class EditWordButton(Button):

    def open_popup(self, selected_word_relative_layout):
        selected_word_object = selected_word_relative_layout.word_object
        popup = EditWordPopup(selected_word_object)
        popup.open()


class EditWordPopup(Popup):

    def __init__(self, selected_word_object, *args, **kwargs):
        self.word_object = selected_word_object
        super(ViewWordPopup, self).__init__(*args, **kwargs)
        self.draw()


class AddWordButton(Button):

    def open_popup(self, selectable_grid_layout):
        popup = AddWordPopup()
        popup.ids.SaveChangesBtn.bind(on_release=partial(self.add_new_word,
                                                         popup,
                                                         selectable_grid_layout
                                                         ))
        popup.open()

    def add_new_word(self, popup, selectable_grid_layout, instance):
        # print("adding new word -->", popup.ids.TextIP.text)
        # print("adding new word -->", popup.word_object)
        new_word_RL = WordRelativeLayout(popup.word_object)
        selectable_grid_layout.add_widget(new_word_RL)
        WORD_DATABASE.append(popup.word_object)
        popup.dismiss()


class AddWordPopup(Popup):

    error_disabled = BooleanProperty(True)
    button_disabled = BooleanProperty(True)
    exists_flag = BooleanProperty(False)

    def __init__(self, *args, **kwargs):
        super(AddWordPopup, self).__init__(*args, **kwargs)

    def check_input(self, text):
        # self.ids.WordDescription.text = ''
        if text in WORD_LIST:
            self.error_disabled = False
            self.ids.ErrorMessage.text = 'Word Already Exists'
            self.exists_flag = True
        else:
            self.error_disabled = True
            self.ids.ErrorMessage.text = ''
            self.exists_flag = False

    def call_api(self, text):

        if(self.exists_flag):
            return

        word_object, status1, status2 = addword(Word(text))
        # print("trying to add word --> ", text)

        http_error_flag = status1[0]
        if(status1[1] >= 400):
            self.ids.ErrorMessage.text = """\
Please check the word you have entered or your internet connection."""
        self.error_disabled = http_error_flag
        self.button_disabled = not http_error_flag
        self.ids.WordDescription.text = word_description(word_object)
        if(not self.button_disabled):
            self.word_object = word_object


class DeleteWordButton(Button):

    def open_popup(self, selectable_grid_layout):
        popup = DeleteWordPopup()
        popup.ids.DeleteBtn.bind(on_release=partial(self.delete_word,
                                                    popup,
                                                    selectable_grid_layout
                                                    ))
        popup.open()

    def delete_word(self, popup, selectable_grid_layout, instance):
        selected_word = selectable_grid_layout.return_selected_stack_layout()
        selectable_grid_layout.remove_widget(selected_word)
        popup.dismiss()


class DeleteWordPopup(Popup):
    pass


class RootFloatLayout(RelativeLayout):

    def __init__(self, WORD_DATABASE, *args, **kwargs):
        super(RootFloatLayout, self).__init__(*args, **kwargs)

    def load_word_widgets(self, search_result):
        for word_object in search_result:
            self.add_word_widget(word_object)

    def add_word_widget(self, word_object):
        WordRL = WordRelativeLayout(word_object)
        self.ids.SelectableGL.add_widget(WordRL)

    def search_words(self, input):
        search_result = []
        if(len(input) != 0):
            for key in WORD_SEARCH_DICT:
                if(input in key[0:len(input)]):
                    search_result.append(WORD_SEARCH_DICT[key])
                else:
                    try:
                        self.ids.SelectableGL.clear_widgets()
                    except AttributeError:
                        pass
            self.load_word_widgets(search_result)
        else:
            try:
                self.ids.SelectableGL.clear_widgets()
            except AttributeError:
                pass


class WordListScreen(Screen):

    def __init__(self, *args, **kwargs):
        super(WordListScreen, self).__init__(*args, **kwargs)
        self.add_widget(RootFloatLayout(WORD_DATABASE))


class WordListApp(App):

    def build(self):
        return WordListScreen()


def main():
    WordListApp().run()


if __name__ == '__main__':
    main()
