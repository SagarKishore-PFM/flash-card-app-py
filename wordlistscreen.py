# -*- coding: utf-8 -*-
"""
Created on Saturday, April 24th 2018

@author: sagar

Kivy screen that allows for adding new words as well as editting, deleting
and viewing existing words in the selected Word Database.
"""

from word import Word
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.popup import Popup
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.lang import Builder
from kivy.uix.textinput import TextInput
from functools import partial
import re

from oxfordapi import addword
from compound_selection import SelectableLayout
from helperfuncs import word_description, short_meaning

# TODO:

#     >> Database is not affected at the moment.
#     >> Minor clean up in the popup UIs
#     >> Add navigation to the StackList Screen and DataBaseScreen(?)
#     >> Cleanup the kv file
#     >> Add audio button in description?
#     >> Add audio in main screen WordRelativeLayouts

WORD_DATABASE = []
STACK_DATABASE = []
WORD_LIST = ''
WORD_SEARCH_DICT = ''


def db_init():
    global WORD_DATABASE
    global WORD_LIST
    global WORD_SEARCH_DICT
    WORD_LIST = {word.name for word in WORD_DATABASE}
    WORD_SEARCH_DICT = {word.name: word for word in WORD_DATABASE}


class WordRelativeLayout(SelectableLayout, RelativeLayout):

    Builder.load_string("""
<WordRelativeLayout>:
    id: WRL
    canvas.before:
        Color:
            rgba: 1, 0, 1, 0.5
        Rectangle:
            pos: 0, 0
            size: self.size
    multiselect: False
    touch_multiselect: False

    Button:
        id: WordBtn
        canvas.before:
            Color:
                rgba: .3, .3, .3, 1
            Rectangle:
                pos: 0, 0
                size: self.size

    Label:
        id: WordNameLbl
        pos_hint: {'x': 0.05, 'y': 0.3}
        font_size: 24
        bold: True
        halign: 'left'
        valign: 'middle'
        size: WRL.size
        texture_size: self.size
        text_size: self.width, None

    Label:

        id: WordMeaningLbl
        pos_hint: {'x': 0.08, 'y': -0.18}
        markup: True
        size: WRL.size #[0] * 0.8, WRL.size[1] * 0.8
        texture_size: self.size
        # height: self.texture_size[1]
        text_size: self.width, None
        halign: 'left'
        valign: 'middle'
""")

    def __init__(self, word_object, *args, **kwargs):
        self.word_object = word_object
        super(WordRelativeLayout, self).__init__(*args, **kwargs)
        self.draw()

    def draw(self):
        self.ids.WordNameLbl.text = self.word_object.name
        self.ids.WordMeaningLbl.text = short_meaning(self.word_object)


class ViewWordButton(Button):

    Builder.load_string("""
<ViewWordButton>:
    pos_hint: {'x': 0.05, 'y': 0.5}
    size_hint: 0.15, 0.15
""")

    def open_popup(self, selected_word_relative_layout):
        selected_word_object = selected_word_relative_layout.word_object
        popup = ViewWordPopup(selected_word_object)
        popup.open()


class ViewWordPopup(Popup):

    Builder.load_string("""
<ViewWordPopup>:
    id: ViewWordPopup
    title: "Word Description"
    size_hint: 0.7,0.7
    separator_color: [1, 1, 1, 1]

    FloatLayout:
        id: FL
        canvas.before:
            Color:
                rgba: 1, 0, 0, 0.0
            Rectangle:
                pos: 0, 0
                size: self.size
        ScrollView:
            top: FL.height* 1.2
            width: FL.width
            pos: FL.pos[0],FL.pos[1]
            # height: FL.height
            size_hint_y: None
            height: FL.height * 0.8

            canvas.before:
                Color:
                    rgba: 1, 1, 0, 1.0
                Rectangle:
                    pos: self.pos
                    size: self.size

            Label:
                id: WordDescription
                canvas.before:
                    Color:
                        rgba: 0.1, 0.4, 0.4, 0.4
                    Rectangle:
                        pos: self.pos
                        size: self.size
                pos_hint_x: 0.1
                height: self.texture_size[1]
                size_hint_y: None
                size: FL.size[0] * 0.85, FL.size[1] * 0.85
                text_size: self.width, None
                halign: 'left'
                valign: 'middle'
                markup: True
                # disabled: True
                padding: 100, 100
        Button:
            id: ExitBtn
            pos_hint: {'x':0.7, 'y': 0.05}
            size_hint: 0.2, 0.1
            text: "Go Back"
            on_release: root.dismiss()
""")

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

    Builder.load_string("""
<AddWordButton>:
    pos_hint: {'x': 0.05, 'y': 0.2}
    size_hint: 0.15, 0.15
""")

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
        selectable_grid_layout.clear_selection()
        selectable_grid_layout.add_widget(new_word_RL)
        global WORD_DATABASE
        WORD_DATABASE.append(popup.word_object)
        db_init()
        popup.dismiss()


class AddWordPopup(Popup):

    Builder.load_string("""
#:import RETextInput stacklistscreen.RETextInput
<AddWordPopup>:
    id: AddWordPopup
    title: "Add a new Word"
    size_hint: 0.7,0.7
    separator_color: [1, 1, 1, 1]

    FloatLayout:
        id: FL
        canvas.before:
            Color:
                rgba: 1, 0, 0, 0.0
            Rectangle:
                pos: 0, 0
                size: self.size

        RETextInput:
            id: TextIP
            size_hint: 0.85, 0.1
            pos_hint: {'center_x': 0.5, 'y':0.85}
            hint_text: "Enter the word here..."
            multiline: False
            on_text_validate: root.call_api(self.text)
            on_text: root.check_input(self.text)

        Label:
            id: ErrorMessage
            pos_hint: {'x': 0.3,'y': 0.8}
            canvas.before:
                Color:
                    rgba: 0.4, 0.4, 0.4, 0.2
                Rectangle:
                    pos: self.pos
                    size: self.size
            text: "POSITION"
            size_hint: None, None
            font_size: 24
            size: self.texture_size
            halign: 'right'
            valign: 'middle'
            disabled: AddWordPopup.error_disabled

        ScrollView:
            top: FL.height
            width: FL.width
            pos: FL.pos[0],FL.pos[1]*0.7
            # pos_hint: {'x':0, 'y': 0.8}
            size_hint_y: None
            height: FL.height * 0.6

            canvas.before:
                Color:
                    rgba: 1, 1, 0, 1.0
                Rectangle:
                    pos: self.pos
                    size: self.size
            Label:
                id: WordDescription
                canvas.before:
                    Color:
                        rgba: 0.1, 0.4, 0.4, 0.4
                    Rectangle:
                        pos: self.pos
                        size: self.size
                pos_hint_x: 0.1
                height: self.texture_size[1]
                size_hint_y: None
                size: FL.size[0] * 0.85, FL.size[1] * 0.85
                text_size: self.width, None
                halign: 'left'
                valign: 'middle'
                disabled: AddWordPopup.button_disabled
                markup: True
                padding: 100, 100

        Button:
            id: SaveChangesBtn
            pos_hint: {'x':0.7, 'y': 0.1}
            size_hint: 0.2, 0.1
            text: "Add Word"
            disabled: root.button_disabled
""")

    error_disabled = BooleanProperty(True)
    button_disabled = BooleanProperty(True)
    exists_flag = BooleanProperty(False)

    def __init__(self, *args, **kwargs):
        super(AddWordPopup, self).__init__(*args, **kwargs)

    def check_input(self, text):
        # self.ids.WordDescription.text = ''
        global WORD_LIST
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
        try:
            if(status1[2]):
                self.ids.ErrorMessage.text = f"""\
Please try {status1[2]} instead."""
        except IndexError:
            pass
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

    Builder.load_string("""
<DeleteWordButton>:
    pos_hint: {'x': 0.8, 'y': 0.5}
    size_hint: 0.15, 0.15
""")

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
        global WORD_DATABASE
        WORD_DATABASE.remove(selected_word.word_object)
        db_init()
        popup.dismiss()


class DeleteWordPopup(Popup):

    Builder.load_string("""
<DeleteWordPopup>:
    id: DeleteWordPopup
    title: ""
    size_hint: 0.4,0.3
    separator_color: [1, 1, 1, 1]

    FloatLayout:
        id: FL

        Label:
            font_size: 30
            size_hint: None, None
            size: self.texture_size
            text: 'Are you sure you want to delete?'
            halign: 'center'
            valign: 'middle'
            pos_hint: {'center_x': 0.5, 'y':0.65}

        Button:
            id: DeleteBtn
            text:"YES"
            size_hint: 0.3,0.2
            pos_hint: {'x':0.1, 'y':0.1}
            # disabled: True

        Button:
            text:"NEIN!"
            size_hint: 0.3,0.2
            pos_hint: {'x':0.6, 'y':0.1}
            on_release: root.dismiss()
""")


class WordRETextInput(TextInput):

    pat1 = re.compile('[^a-zA-Z0-9\s]')
    # pat = re.compile('^\d+|[^a-zA-Z0-9\s]')
    pat2 = re.compile('[^A-Za-z]')

    def insert_text(self, substring, from_undo=False):
        if(len(self.text) == 0):
            pat = self.pat2
        else:
            pat = self.pat1
        s = re.sub(pat, '', substring)
        return super(WordRETextInput, self).insert_text(s, from_undo=from_undo)


class WordListScreen(Screen):
    Builder.load_string("""
<WordListScreen>:
    name: 'word screen'
    canvas.before:
        Color:
            rgba: 1, 0, 0, 0.0
        Rectangle:
            pos: 0, 0
            size: self.size

    WordRETextInput:
        id: SearchBar
        pos_hint: {'center_x': 0.5, 'y': 0.8}
        size_hint: 0.7,0.1
        hint_text: "Search words..."
        on_text: root.search_words(self.text)

    ViewWordButton:
        id: ViewWordBtn
        text: 'View Word'
        disabled: SelectableGL.button_disabled
        on_release: self.open_popup(\
            SelectableGL.return_selected_stack_layout())

    AddWordButton:
        id: AddWordButton
        text: 'Add a new Word'
        on_release: self.open_popup(SelectableGL)

    DeleteWordButton:
        id: DeleteWordBtn
        text: 'Delete Word'
        disabled: SelectableGL.button_disabled
        on_release: self.open_popup(SelectableGL)

    Button:
        on_release: root.manager.current = 'db screen'
        pos_hint: {'x': 0.03, 'y': 0.8}
        size_hint: 0.1,0.1
        text: 'Go back to DB Selection'

    Button:
        on_release: root.manager.current = 'stack screen'
        pos_hint: {'x': 0.85, 'y': 0.8}
        size_hint: 0.1,0.1
        text: 'Go to Stack List Screen'

    ScrollView:
        id:SV
        height: root.height * 0.7
        top: self.height
        pos_hint: {'center_x': .5}
        size_hint_x: 0.5
        size_hint_y: None
        canvas.before:
            Color:
                rgba: 1, 1, 0, 1.0
            Rectangle:
                pos: SV.pos
                size: SV.size
        WordSelectableGridLayout:
            id: SelectableGL


<WordSelectableGridLayout@SelectableGridLayout>:
    canvas:
        Color:
            rgba: 1, 1, 1, 1.0
        Rectangle:
            pos: self.pos
            size: self.size
    multiselect: False
    touch_multiselect: False
    row_force_default: False
    cols: 1
    padding: 10, 10
    spacing: 10, 10
    row_default_height: 100
    col_force_default: False
    col_default_width: 200
    pos_hint: {'center_x': 0.5}
    size_hint: 1, None
    on_minimum_height: self.height = self.minimum_height
""")

    # word_db = ObjectProperty(None)
    fcdb = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(WordListScreen, self).__init__(*args, **kwargs)

    def on_enter(self,  *args, **kwargs):
        global STACK_DATABASE
        global WORD_DATABASE
        STACK_DATABASE = self.fcdb.stack_db
        WORD_DATABASE = self.fcdb.word_db
        db_init()

    # def on_pre_enter(self, *args, **kwargs):

    def load_word_widgets(self, search_result):
        for word_object in search_result:
            self.add_word_widget(word_object)

    def add_word_widget(self, word_object):
        WordRL = WordRelativeLayout(word_object)
        self.ids.SelectableGL.add_widget(WordRL)

    def search_words(self, ip_text):
        try:
            self.ids.SelectableGL.clear_widgets()
        except AttributeError:
            pass
        global WORD_SEARCH_DICT
        search_result = []
        if(len(ip_text) != 0):
            for key in WORD_SEARCH_DICT:
                if(ip_text in key[0:len(ip_text)]):
                    search_result.append(WORD_SEARCH_DICT[key])
                else:
                    try:
                        self.ids.SelectableGL.clear_widgets()
                    except AttributeError:
                        pass
            self.ids.SelectableGL.clear_selection()
            self.load_word_widgets(search_result)

    # def __init__(self, *args, **kwargs):
    #     super(WordListScreen, self).__init__(*args, **kwargs)
    #     self.word_db = WORD_DATABASE
    #     self.add_widget(RootRelativeLayout(self.word_db))


# class WordListApp(App):

#     def build(self):
#         return WordListScreen()


# def main():
#     WordListApp().run()


# if __name__ == '__main__':
#     main()
