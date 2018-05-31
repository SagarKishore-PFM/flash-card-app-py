# -*- coding: utf-8 -*-
"""
Created on Saturday, April 9th 2018

@author: sagar
"""
from functools import partial

from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import ObjectProperty
from kivy.properties import ListProperty
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.properties import BooleanProperty
from kivy.properties import NumericProperty
from kivy.uix.listview import ListItemButton, ListView
from kivy.adapters.listadapter import ListAdapter
from compound_selection import SelectableLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.selectableview import SelectableView
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.lang import Builder

from functools import partial
import re

from testdatabase import generate_test_stack_database
from testdatabase import generate_test_word_database
from stack import Stack


# from wordlistscreen import WordRelativeLayout


# ChangeLog:

# Version 0.2.0:

# The new UI design allows for ease of data manipulation and access.
# This includes 4 buttons surrounding the List of stacks.
# The Stacks are now selectable thanks to the compound_selection.py module.
# The buttons surrounding the SelectableGridLayout will be disabled until a
#   selection is made.
# Every button takes in the selected_stack_object as an argument.

# TODO:

# >> Align everything properly in the main screen
# >> Increase padding between the stack relative layouts
# >> The relative layout must now show a progress bar that depicts number of
#      words mastered
# >> Add buttons to navigate to Word List screen and DataBaseScreen(?)
# >> Add Delete Stack Popup
# >> Add logic that saves the changes often and/or upon exiting the application
# >> Rearrange and cleaup the .kv file
# >> Cleanup the code

# >> View Stack:
#     Fix the positions of the widgets and make it pretty
#     Maybe show the progress bars from the game screen(?) **
#     Implementation of flash card via Practice Button in the popup

# >> Edit Stack:
#     Fix the positions of the widgets and make it pretty
#     Input Validation with an error message using label **
#     Make sure that the stack name is unique **

# >> Create Stack:
#     Fix the positions of the widgets and make it pretty
#     Make sure that the stack name is unique **
#     Input Validation with an error message using label **

# >> Delete Stack:
#     Everything

# >> Edit Words Popup:
#     See if you want to merge the thesaurus and the search list into one
#     Give a list of old words?


# STACK_DATABASE = generate_test_stack_database()
# WORD_DATABASE = generate_test_word_database()
# STACK_NAMES = [stack.name for stack in STACK_DATABASE]
# WORD_SEARCH_DICT = {word.name: word for word in WORD_DATABASE}

STACK_DATABASE = generate_test_stack_database()
WORD_DATABASE = generate_test_word_database()
STACK_NAMES = ''
WORD_SEARCH_DICT = ''


def db_init():
    global STACK_DATABASE
    global WORD_DATABASE
    global STACK_NAMES
    global WORD_SEARCH_DICT
    STACK_NAMES = [stack.name for stack in STACK_DATABASE]
    WORD_SEARCH_DICT = {word.name: word for word in WORD_DATABASE}


class SelectableGridLayout(SelectableLayout, GridLayout):

    selected_nodes_list = ListProperty(None)
    button_disabled = BooleanProperty(True)

    # For Debugging
    def print_selected_nodes(self):
        self.selected_nodes_list = self.selected_nodes
        print(self.selected_nodes_list[0].stack_object)

    # For Debugging
    def return_selected_stack(self):
        self.selected_nodes_list = self.selected_nodes
        selected_stack_object = self.selected_nodes_list[0].stack_object
        return selected_stack_object

    def return_selected_stack_layout(self):
        self.selected_nodes_list = self.selected_nodes
        return self.selected_nodes_list[0]

    def on_selected_nodes(self, gird, nodes):
        self.button_disabled = not self.selected_nodes


class StackRelativeLayout(SelectableLayout, RelativeLayout):
    Builder.load_string("""
<StackRelativeLayout>:

    canvas.before:
        Color:
            rgba: 1, 1, 1, 0.5
        Rectangle:
            pos: 0, 0
            size: self.size
    multiselect: False
    touch_multiselect: False

    Button:
        id: StackBtn
        canvas.before:
            Color:
                rgba: .3, .3, .3, 1
            Rectangle:
                pos: 0, 0
                size: self.size
        size_hint: 1, 1

    Label:
        id: StackNameLabel
        pos: 100, 80
        font_size: 30

    Label:
        id: StackSizeLabel
        pos: 160, 40
        font_size: 20

    Label:
        id: MasteredLabel
        pos_hint: {'center_x': 0.5, 'y': -0.1}

    ProgressBar:
        id: MasteredProgressBar
        max: root.stack_object.size
        pos_hint: {'center_x': 0.5, 'y': 0.25}
        size_hint: 0.6, 0.05
""")

    def __init__(self, stack_object, *args, **kwargs):
        self.stack_object = stack_object
        self.stack_object.refresh_rank_dict()
        super(StackRelativeLayout, self).__init__(*args, **kwargs)
        # Clock.schedule_once(self.redraw, 0)
        self.redraw()

    def redraw(self, dt=0):
        # self.stack_object = new_stack_object
        self.ids.StackNameLabel.text = self.stack_object.name
        self.ids.StackSizeLabel.text = str(self.stack_object.size)
        self.ids.MasteredLabel.text = 'Mastered {0} / {1} words'.format(
            len(self.stack_object.rank_dict['6']), self.stack_object.size)
        self.ids.MasteredProgressBar.value = len(self.stack_object.rank_dict['6'])


class WordListAdapter(ListAdapter):

    word_object_list = ObjectProperty(None)


class ViewStackWordViewList(ListView):
    pass


class WordGridLayout(SelectableLayout, GridLayout):
    pass


class ViewStackButton(Button):

    Builder.load_string("""
<ViewStackButton>:
    pos_hint: {'x': 0.1, 'y': 0.5}
    size_hint: 0.15, 0.15
    """)

    def open_popup(self, selected_stack_relative_layout):
        selected_stack_object = selected_stack_relative_layout.stack_object
        popup = ViewStackPopup(selected_stack_object)
        popup.ids.PlayBtn.bind(on_release=partial(self.practice_stack,
                                                  popup,
                                                  selected_stack_object))
        popup.open()

    def practice_stack(self, popup, selected_stack, instance):
        popup.dismiss()
        manager = self.parent.parent.manager
        game_screen = manager.get_screen('game screen')
        game_screen.game_stack = selected_stack
        manager.current = 'game screen'
        print(f"Bout to send the stack {selected_stack} to gamescreen")


class ViewStackPopup(Popup):
    Builder.load_string("""
<ViewStackPopup>:
    id: VSP
    title: "Displaying Stack Information"
    size_hint: 0.8,0.8
    pos: 0,0
    separator_color: [1, 1, 1, 1]

    FloatLayout:
        pos: VSP.pos

        Label:
            canvas:
                Color:
                    rgba: 1, 1, 1, 1.0
                Rectangle:
                    pos: self.pos
                    size: self.texture_size
            id: StackNameLbl
            halign: 'right'
            valign: 'middle'
            pos_hint: {'x': -0.4,'y': 0.4}
            text: "Stack Name"
            size: self.texture_size
            color: 1,0,0,1
            font_size: 30

        Label:
            id: StackSizeLbl
            halign: 'right'
            valign: 'middle'
            pos_hint: {'x': -0.2,'y': 0.3}

        Button:
            id: ExitBtn
            pos_hint: {'x': 0.7, 'y': 0.1}
            size_hint: 0.1, 0.1
            text: "Exit"
            on_release: root.dismiss()

        Button:
            id: PlayBtn
            pos_hint: {'x': 0.7, 'y': 0.3}
            size_hint: 0.1, 0.1
            text: "Practice"
            # on_release: print(root.manager)
            disabled: root.button_disabled

        WordGridLayout:
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1.0
                Rectangle:
                    pos: self.pos
                    size: self.size
            id: GL
            pos_hint: {'x':0.1,'y':0.1}
            size_hint: 0.5,0.4
            spacing: 10
            padding: 10
            cols: 1
            ViewStackWordViewList:
                pos_hint: {'x':0.3,'y':0.1}
                size_hint: 0.2,0.4
                id: WordViewList
                pos: GL.pos
                size: GL.size

        BoxLayout:
            orientation: 'vertical'
            pos_hint: {'center_x': 0.6, 'y': 0.6}
            size_hint: 0.5,0.3
            padding: 10,10
            spacing: 5

            canvas.before:
                Color:
                    rgba: 1, 1, 1, 0.5
                Rectangle:
                    pos: self.pos
                    size: self.size

            StackPFL:
                id: NewPFL
                max_value: root.max_value

            StackPFL:
                id: MasteredPFL
                max_value: root.max_value

            StackPFL:
                id: LearningPFL
                max_value: root.max_value

            StackPFL:
                id: ReviewingPFL
                max_value: root.max_value

<StackPFL@ProgressFloatLayout>:
    canvas.before:
        Color:
            rgba: 1, 0, 1, 0.2
        Rectangle:
            pos: self.pos
            size: self.size
    ProgressBar:
        id: PB
        pos_hint: {'center_x': 0.5, 'y': 0.3}
        size_hint: 0.8, 0.05
        max: root.max_value

    Label:
        id: Lbl
        pos_hint: {'center_x': 0.5, 'y': 0.15}
        font_size: 18

# <WordSelectableGridLayout@SelectableGridLayout>:
#     canvas:
#         Color:
#             rgba: 1, 1, 1, 1.0
#         Rectangle:
#             pos: self.pos
#             size: self.size
#     multiselect: False
#     touch_multiselect: False
#     row_force_default: False
#     cols: 1
#     padding: 10, 10
#     spacing: 10, 10
#     row_default_height: 100
#     col_force_default: False
#     col_default_width: 200
#     on_minimum_height: self.height = self.minimum_height
""")

    max_value = NumericProperty(-1)
    button_disabled = BooleanProperty(False)

    def __init__(self, stack_object, *args, **kwargs):
        self.stack_object = stack_object
        super(ViewStackPopup, self).__init__(*args, **kwargs)
        self.ids.StackNameLbl.text = self.stack_object.name
        self.ids.StackSizeLbl.text = str(self.stack_object.size)

        self.rank_dict = self.stack_object.rank_dict
        self.max_value = self.stack_object.size

        # self.load_word_widgets()

        self.word_list_view = self.ids.WordViewList
        self.word_object_list = self.stack_object.words
        self.generate_word_listview()
        self.update_progressbars()
        self.button_disabled = self.stack_object.size == 0

    # def load_word_widgets(self):
    #     SGL = self.ids.ViewWordSGL
    #     for word in self.stack_object.words:
    #         SGL.add_widget(WordRelativeLayout(word))

    def args_converter(self, row_indext, rec):
        return {'text': rec.name,
                'size_hint_y': None,
                'height': 45,
                'font_size': 18}

    def generate_word_listview(self):
        list_adapter = WordListAdapter(data=self.word_object_list,
                                       args_converter=self.args_converter,
                                       selection_mode="single",
                                       allow_empty_selection=False,
                                       cls=ListItemButton,
                                       word_object_list=self.word_object_list)
        self.word_list_view.adapter = list_adapter
        self.word_list_view.container.spacing = 8

    def update_progressbars(self):
        reviewing_set = self.rank_dict['1'].union(self.rank_dict['2'],
                                                self.rank_dict['3'],
                                                self.rank_dict['4'],
                                                self.rank_dict['5'])

        self.ids.NewPFL.ids.PB.value = len(self.rank_dict['-1'])
        self.ids.MasteredPFL.ids.PB.value = len(self.rank_dict['6'])
        self.ids.ReviewingPFL.ids.PB.value = len(reviewing_set)
        self.ids.LearningPFL.ids.PB.value = len(self.rank_dict['0'])

        self.ids.NewPFL.ids.Lbl.text = \
            f"New words left {len(self.rank_dict['-1'])} / {self.max_value}"
        self.ids.MasteredPFL.ids.Lbl.text = \
            f"Mastered {len(self.rank_dict['6'])} / {self.max_value} words"
        self.ids.ReviewingPFL.ids.Lbl.text = \
            f"Reviewing {len(reviewing_set)} / {self.max_value} words"
        self.ids.LearningPFL.ids.Lbl.text = \
            f"Learning {len(self.rank_dict['0'])} / {self.max_value} words"


class CreateStackButton(Button):
    Builder.load_string("""
<CreateStackButton>:
    pos_hint: {'x': 0.1, 'y': 0.2}
    size_hint: 0.15, 0.15
""")

    def open_popup(self, SelectableGridLayout):
        popup = CreateStackPopup()
        popup.ids.SaveChangesBtn.bind(on_release=partial(self.create_new_stack,
                                                         popup,
                                                         SelectableGridLayout))
        popup.open()

    def create_new_stack(self, popup, SelectableGridLayout, instance):
        new_stack = Stack(popup.ids.StackName.text)
        new_stack.words = popup.word_list_view.adapter.data
        new_stack.refresh_rank_dict()
        SelectableGridLayout.add_widget(StackRelativeLayout(new_stack))
        popup.dismiss()

# CreateStackPopup TODO:

# Write logic to redraw or re-generate the word list view with the modified
#     word_object_list
# Write logic to bind on_press function of the save button to create a new
#     stack object with the properties
# Make the text input to have a validator for stack name so that it doesn't
#     accept number in the first letter


class CreateStackPopup(Popup):
    Builder.load_string("""
<CreateStackPopup>:
    id: CreateStackPopup
    stack_name_lbl: StackNameLbl
    stack_size_lbl: StackSizeLbl
    title: "Add a new Stack"
    size_hint: 0.7,0.7
    separator_color: [1, 1, 1, 1]

    FloatLayout:
        pos: CreateStackPopup.pos
        Label:
            id: StackNameLbl
            halign: 'right'
            valign: 'middle'
            pos_hint: {'x': -0.3,'y': 0.4}
            text: "Stack Name"

        Label:
            id: StackSizeLbl
            halign: 'right'
            valign: 'middle'
            pos_hint: {'x': -0.3,'y': -0.1}
            # text: "Stack Size"

        RETextInput:
            id: StackName
            multiline: False
            pos_hint: {'x': 0.4,'y':0.85}
            size_hint: 0.4,0.1
            hint_text: "Enter Stack Name...."
            on_text: root.validate_text_input()
            on_text_validatate: root.open_edit_words_popup()

        Label:
            id: ErrorMessage
            pos_hint: {'x': 0.3,'y': 0.8}
            canvas.before:
                Color:
                    rgba: 0.4, 0.4, 0.4, 0.2
                Rectangle:
                    pos: self.pos
                    size: self.size
            text: "POSITTION"
            size_hint: None, None
            font_size: 24
            size: self.texture_size
            halign: 'right'
            valign: 'middle'
            disabled: not root.button_disabled

        Button:
            id: EditWordsBtn
            pos_hint: {'x': 0.65, 'y': 0.1}
            size_hint: 0.1, 0.1
            text: "Add Word"
            on_release: root.open_edit_words_popup()

        Button:
            id: SaveChangesBtn
            pos_hint: {'x': 0.85, 'y': 0.1}
            size_hint: 0.1, 0.1
            text: "Save Changes"
            # on_release: root.create_new_stack()
            disabled: root.button_disabled


        WordGridLayout:
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1.0
                Rectangle:
                    pos: self.pos
                    size: self.size
            id: GL
            pos_hint: {'x':0.1,'y':0.1}
            size_hint: 0.5,0.6
            spacing: 10
            padding: 10
            cols: 2

            ViewStackWordViewList:
                id: WordViewList
                pos: GL.pos
                size: GL.size
""")
    stack_name_lbl = ObjectProperty(None)
    stack_size_lbl = ObjectProperty(None)
    button_disabled = BooleanProperty(True)

    def __init__(self, *args, **kwargs):
        super(CreateStackPopup, self).__init__(*args, **kwargs)
        self.word_list_view = self.ids.WordViewList
        self.word_object_list = []
        self.list_adapter = None
        self.generate_word_listview()

    def args_converter(self, row_indext, rec):

        return {'text': rec.name,
                'size_hint_y': None,
                'height': 45,
                'font_size': 18}

    def generate_word_listview(self):

        self.list_adapter = WordListAdapter(data=self.word_object_list,
                                            args_converter=self.args_converter,
                                            selection_mode="single",
                                            allow_empty_selection=False,
                                            cls=ListItemButton,
                                            word_object_list=self.word_object_list)
        self.word_list_view.adapter = self.list_adapter
        self.word_list_view.container.spacing = 8

    def open_edit_words_popup(self):

        popup = EditWordsPopup(self.word_object_list)
        popup.ids.SaveChangesBtn.bind(on_release=partial(
                            self.update_changes_to_word_list,
                            popup))
        popup.open()

    def update_changes_to_word_list(self,
                                    popup,
                                    instance):
        self.word_object_list = popup.selected_list_adapter.data
        popup.dismiss()
        # self.generate_word_listview()
        self.word_list_view.adapter.data = self.word_object_list

    def validate_text_input(self):
        min_len = 3
        text = self.ids.StackName.text
        cond1 = len(text) < min_len
        cond2 = text in STACK_NAMES and text != self.stack_name_lbl.text
        self.button_disabled = cond1 or cond2
        if(self.button_disabled):
            self.ids.ErrorMessage.text = \
                f'Stack Name must be unique and contain more than {min_len} letters'
        else:
            self.ids.ErrorMessage.text = ""


# EditWordsPopup TODO:

# Create a space that shows definitions, sentences, etc for the selected word
#     object(s). If multiple word objects then view meanings for all
# Allow for multiple select
# Write the logic to add selected words from search to the word_object_list of
#     the previous screen
# Upon pressing the save button return the modified word_object_list
# Maybe have only two list views. Merge the thesaurus and search list view into
    # one
class WordListItemButton(ListItemButton):

    word_object = ObjectProperty(None)


class WordDescriptionLayout(SelectableView, FloatLayout):
    Builder.load_string("""
<WordDescriptionLayout>:
    id: WRL
    canvas.before:
        Color:
            rgba: 1, 1, 1, 0.5
        Rectangle:
            pos: 0, 0
            size: self.size
    multiselect: False
    touch_multiselect: False
    Button:
        size: root.size
        pos: root.pos
        id: WordBtn
        canvas.before:
            Color:
                rgba: .3, .3, .3, 1
            Rectangle:
                pos: 0, 0
                size: self.size

    Label:
        id: WordNameLbl
        pos_hint: {'x': 0.02, 'y': 0.3}
        font_size: 24
        bold: True
        halign: 'left'
        valign: 'middle'
        size: WRL.size
        texture_size: self.size
        text_size: self.width, None
        text: root.word_object.name

    Label:

        id: WordMeaningLbl
        pos_hint: {'x': 0.05, 'y': -0.18}
        markup: True
        size: WRL.size #[0] * 0.8, WRL.size[1] * 0.8
        texture_size: self.size
        text_size: self.width * 0.8, self.height * 0.8
        halign: 'left'
        valign: 'middle'
        text: short_meaning(root.word_object)
""")
    word_object = ObjectProperty(None)


class ProgressFloatLayout(FloatLayout):
    max_value = NumericProperty(-1)


class EditWordsPopup(Popup):

    Builder.load_string("""
#:import short_meaning helperfuncs.short_meaning
<EditWordsPopup>:
    id: CreateStackPopup
    title: "Edit Words"
    size_hint: 0.7,0.7
    separator_color: [1, 1, 1, 1]
    FloatLayout:
        id: RootFL
        RETextInput:
            id: SearchBar
            pos_hint: {'center_x':0.4,'y':0.85}
            size_hint: 0.7,0.1
            on_text: root.search_words(self.text)
            multiline: False

        Button:
            id: SaveChangesBtn
            text: "Save changes"
            pos_hint: {'x':0.8,'y':0.85}
            size_hint: 0.2,0.1

        Button:
            id: AddWordsBtn
            text: "Add Selected Words"
            pos_hint: {'x':0.03,'y':0.7}
            size_hint: 0.17,0.1
            on_release: root.populate_selected_list()

        Button:
            id: RemoveWordsBtn
            text: "Remove Selected Words"
            pos_hint: {'x':0.7,'y':0.7}
            size_hint: 0.17,0.1
            on_release: root.remove_selected_list()


        WordGridLayout:
            canvas.before:
                Color:
                    rgba: 1, 1, 0, 1.0
                Rectangle:
                    pos: self.pos
                    size: self.size
            id: SearchWordGL
            pos_hint: {'x':0.03,'y':0.05}
            size_hint: 0.17,0.6
            spacing: 10
            padding: 10
            cols: 1

            ViewStackWordViewList:
                id: SearchWordViewList
                pos: SearchWordGL.pos
                size: SearchWordGL.size

        WordGridLayout:
            canvas.before:
                Color:
                    rgba: 0, 1, 1, 1.0
                Rectangle:
                    pos: self.pos
                    size: self.size
            id: SelectedWordGL
            pos_hint: {'x':0.7,'y':0.05}
            size_hint: 0.17,0.6
            spacing: 10
            padding: 10
            cols: 1
            ViewStackWordViewList:
                id: SelectedWordViewList
                pos: SelectedWordGL.pos
                size: SelectedWordGL.size
        ScrollView:
            id:SV
            height: RootFL.height * 0.6
            top: self.height
            pos_hint: {'x': 0.25, 'y': 0.05}
            size_hint: 0.4, None
            ThesaurusWordGridLayout:
                id: ThesaurusWordGL

<ThesaurusWordGridLayout@SelectableGridLayout>:
    canvas:
        Color:
            rgba: 1, 1, 1, 0.2
        Rectangle:
            pos: self.pos
            size: self.size
    multiselect: False
    touch_multiselect: False
    row_force_default: False
    cols: 1
    padding: 10, 10
    spacing: 20, 20
    row_default_height: 100
    size_hint: 1, None
    on_minimum_height: self.height = self.minimum_height

""")

    def __init__(self, stack_words, *args, **kwargs):
        super(EditWordsPopup, self).__init__(*args, **kwargs)
        self.word_object_list = stack_words
        self.selected_word_list_view = self.ids.SelectedWordViewList
        self.search_word_list_view = self.ids.SearchWordViewList
        # self.thesaurus_word_list_view = self.ids.ThesaurusWordListView
        self.search_list_adapter = None
        self.selected_list_adapter = None
        self.generate_selected_word_listview()
        # self.populate_selected_list()

        # self.search_word_list_view.adapter.bind(on_selection_change=self.generate_thesaurus_listview())

    def args_converter(self, row_index, rec):

        return {'text': rec.name,
                'size_hint_y': None,
                'height': 45,
                'word_object': rec}

    def generate_selected_word_listview(self):

        self.selected_list_adapter = WordListAdapter(data=self.word_object_list,
                                                     args_converter=self.args_converter,
                                                     selection_mode='single',
                                                     allow_empty_selection=True,
                                                     cls=WordListItemButton,
                                                     word_object_list=self.word_object_list)
        self.selected_word_list_view.adapter = self.selected_list_adapter

    def generate_search_word_listview(self,
                                      search_word_list):

        self.search_list_adapter = WordListAdapter(data=search_word_list,
                                                   args_converter=self.args_converter,
                                                   selection_mode='multiple',
                                                   allow_empty_selection=True,
                                                   cls=WordListItemButton)
        self.search_word_list_view.adapter = self.search_list_adapter
        self.search_word_list_view.adapter.bind(on_selection_change=self.generate_thesaurus_listview)

    # TODO:
    # >> Need to create a floatlayout that shows info for the word

    # def thesaurus_args_converter(self, row_index, rec):

    #     return {'word_object': rec, }

    def generate_thesaurus_listview(self,
                                    word_list_adapter, *args):
        self.ids.ThesaurusWordGL.clear_widgets()
        search_word_list = []
        for button in word_list_adapter.selection:
            search_word_list.append(button.word_object)

        for word in search_word_list:
            WDL = WordDescriptionLayout
            WDL.word_object = word
            self.ids.ThesaurusWordGL.add_widget(WDL())

    #     thesaurus_list_adapter = WordListAdapter(data=search_word_list,
    #                                              args_converter=self.thesaurus_args_converter,
    #                                              selection_mode='none',
    #                                              allow_empty_selection=True,
    #                                              cls=WordDescriptionLayout)
    #     self.thesaurus_word_list_view.adapter = thesaurus_list_adapter
    #     self.thesaurus_word_list_view.container.spacing = 20

    def search_words(self, input):
        self.search_word_list_view.container.parent.scroll_y = 1
        search_result = []
        if(len(input) != 0):
            for key in WORD_SEARCH_DICT:
                if(input in key[0:len(input)]):
                    search_result.append(WORD_SEARCH_DICT[key])

        self.generate_search_word_listview(search_result)
        if(search_result == []):
            # self.generate_thesaurus_listview(self.search_word_list_view.adapter)
            self.ids.ThesaurusWordGL.clear_widgets()

    def populate_selected_list(self):
        for button in self.search_list_adapter.selection:
            if(button.word_object not in self.word_object_list):
                self.word_object_list.append(button.word_object)

        self.selected_list_adapter.data = self.word_object_list
        self.selected_word_list_view.container.parent.scroll_y = 0

    def remove_selected_list(self):
        selected_words = []
        for button in self.selected_list_adapter.selection:
            selected_words.append(button.word_object)
        for word in selected_words:
            self.word_object_list.remove(word)
        self.generate_selected_word_listview()


class EditStackButton(Button):
    Builder.load_string("""
<EditStackButton>:
    pos_hint: {'x': 0.8, 'y': 0.5}
    size_hint: 0.15, 0.15
""")

    def open_popup(self, selected_stack_relative_layout):
        selected_stack_object = selected_stack_relative_layout.stack_object
        popup = EditStackPopup(selected_stack_object)
        popup.ids.SaveChangesBtn.bind(
            on_release=partial(self.update_changes_to_stack,
                               popup,))
        popup.bind(on_dismiss=partial(self.redraw_callback,
                                      selected_stack_relative_layout))
        popup.open()

    def update_changes_to_stack(self,
                                popup,
                                instance):
        popup.save_changes_to_stack_object()
        popup.dismiss()

    def redraw_callback(self, selected_stack_relative_layout, instance):
        selected_stack_relative_layout.redraw()


class EditStackPopup(Popup):

    Builder.load_string("""
<EditStackPopup>:
    id: EditStackPopup
    stack_name_lbl: StackNameLbl
    stack_size_lbl: StackSizeLbl
    stack_name_txt: StackName
    title: "Edit Stack Information"
    size_hint: 0.7,0.7
    separator_color: [1, 1, 1, 1]


    FloatLayout:
        id: FL
        pos: EditStackPopup.pos
        Label:
            id: StackNameLbl
            halign: 'right'
            valign: 'middle'
            pos_hint: {'x': -0.3,'y': 0.4}
            text: "Stack Name"

        Label:
            id: StackSizeLbl
            halign: 'right'
            valign: 'middle'
            pos_hint: {'x': -0.3,'y': -0.1}
            # text: "Stack Size"

        RETextInput:
            id: StackName
            multiline: False
            pos_hint: {'x': 0.4,'y':0.85}
            size_hint: 0.4,0.1
            hint_text: "Enter Stack Name...."
            text: root.stack_object.name
            on_text: root.validate_text_input()

        Label:
            id: WarningMessage
            canvas.before:
                Color:
                    rgba: 0.4, 0.4, 0.4, 0.8
                Rectangle:
                    pos: WarningMessage.pos
                    size: WarningMessage.size
            text: "WARNING:\
Changing the Words in the Stack will reset the progress"
            halign: 'center'
            valign: 'middle'
            size_hint: 0.15,0.15
            text_size: self.size
            pos_hint: {'x': 0.8,'y': 0.6}

        Label:
            id: ErrorMessage
            pos_hint: {'x': 0.3,'y': 0.8}
            canvas.before:
                Color:
                    rgba: 0.4, 0.4, 0.4, 0.2
                Rectangle:
                    pos: self.pos
                    size: self.size
            text: "POSITTION"
            size_hint: None, None
            font_size: 24
            size: self.texture_size
            halign: 'right'
            valign: 'middle'
            disabled: not root.button_disabled

        Button:
            id: EditWordsBtn
            pos_hint: {'x': 0.65, 'y': 0.1}
            size_hint: 0.1, 0.1
            text: "Edit Word"
            on_release: root.open_edit_words_popup()

        Button:
            id: SaveChangesBtn
            pos_hint: {'x': 0.85, 'y': 0.1}
            size_hint: 0.1, 0.1
            text: "Save Changes"
            # on_release: root.create_new_stack()
            disabled: root.button_disabled

        WordGridLayout:
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1.0
                Rectangle:
                    pos: self.pos
                    size: self.size
            id: GL
            pos_hint: {'x':0.1,'y':0.1}
            size_hint: 0.5,0.6
            spacing: 10
            padding: 10
            cols: 2

            ViewStackWordViewList:
                id: WordViewList
                pos: GL.pos
                size: GL.size
""")
    stack_name_lbl = ObjectProperty(None)
    stack_size_lbl = ObjectProperty(None)
    button_disabled = BooleanProperty(True)
    stack_name_txt = ObjectProperty(None)
    # save_changes_btn = ObjectProperty(None)
    # object_info_lbl = ObjectProperty(None)

    def __init__(self, stack_object, *args, **kwargs):
        self.stack_object = stack_object
        super(EditStackPopup, self).__init__(*args, **kwargs)
        self.ids.StackNameLbl.text = self.stack_object.name
        self.ids.StackSizeLbl.text = str(self.stack_object.size)
        self.word_list_view = self.ids.WordViewList
        # self.word_object_list = stack_object.words
        self.generate_word_listview()
        self.list_adapter = WordListAdapter
        self.validate_text_input()

    def save_changes_to_stack_object(self):
        self.stack_object.name = self.stack_name_txt.text
        # self.stack_object.refresh_rank_dict()
        # return self.stack_object

    def args_converter(self, row_indext, rec):

        return {'text': rec.name,
                'size_hint_y': None,
                'height': 30,
                'font_size': 18}

    def generate_word_listview(self):

        self.list_adapter = WordListAdapter(data=self.stack_object.words,
                                            args_converter=self.args_converter,
                                            selection_mode="single",
                                            allow_empty_selection=False,
                                            cls=ListItemButton,
                                            word_object_list=self.stack_object.words)
        self.word_list_view.adapter = self.list_adapter

    def open_edit_words_popup(self):

        popup = EditWordsPopup(self.stack_object.words)
        popup.ids.SaveChangesBtn.bind(on_release=partial(
                            self.update_changes_to_word_list,
                            popup))
        popup.open()

    def update_changes_to_word_list(self,
                                    popup,
                                    instance):
        self.stack_object.words = popup.selected_list_adapter.data
        self.stack_object.refresh_rank_dict()
        popup.dismiss()
        self.word_list_view.adapter.data = self.stack_object.words

    def validate_text_input(self):
        min_len = 3
        text = self.ids.StackName.text
        cond1 = len(text) < min_len
        cond2 = text in STACK_NAMES and text != self.stack_name_lbl.text
        self.button_disabled = cond1 or cond2
        if(self.button_disabled):
            self.ids.ErrorMessage.text = \
                f'Stack Name must be unique and contain more than {min_len} letters'    
        else:
            self.ids.ErrorMessage.text = ""


class RETextInput(TextInput):

    pat1 = re.compile('[^a-zA-Z0-9\s]')
    # pat = re.compile('^\d+|[^a-zA-Z0-9\s]')
    pat2 = re.compile('[^A-Za-z]')

    def insert_text(self, substring, from_undo=False):
        if(len(self.text) == 0):
            pat = self.pat2
        else:
            pat = self.pat1
        s = re.sub(pat, '', substring)
        return super(RETextInput, self).insert_text(s, from_undo=from_undo)


class StackListScreen(Screen):

    Builder.load_string("""
<StackListScreen>:
    name: 'stack screen'
    FloatLayout:
        id: FL
        canvas.before:
            Color:
                rgba: 1, 0, 0, 0.0
            Rectangle:
                pos: 0, 0
                size: self.size

        ViewStackButton:
            id: ViewStackBtn
            on_release: self.open_popup(StackSGL.return_selected_stack_layout())
            disabled: StackSGL.button_disabled
            text: "Practice Selected Stack"

        EditStackButton:
            id: EditStackBtn
            on_release: self.open_popup(StackSGL.return_selected_stack_layout())
            disabled: StackSGL.button_disabled
            text: "Edit Selected Stack"

        CreateStackButton:
            id: CreateStackBtn
            on_release: self.open_popup(root.ids.StackSGL)
            text: "Create a new Stack"

        WordListButton:
            id: WordListBtn
            on_release: root.manager.current = 'word screen'
            text: "Go to Word List"

        DBListButton:
            id: DBListBtn
            on_release: root.manager.current = 'db screen'
            text: "Go back to DB Selection"

        ScrollView:
            id:SV
            height: root.height * 0.7
            top: self.height
            pos_hint: {'center_x': .5}
            size_hint_x: 0.5
            size_hint_y: None
            top: self.height

            StackSelectableGridLayout:
                id: StackSGL
                cols: 2

<WordListButton@Button>:
    pos_hint: {'x': 0.8, 'y': 0.8}
    size_hint: 0.15,0.15


<DBListButton@Button>:
    pos_hint: {'x': 0.1, 'y': 0.8}
    size_hint: 0.15,0.15


<StackSelectableGridLayout@SelectableGridLayout>:
    canvas:
        Color:
            rgba: 1, 1, 1, 0.0
        Rectangle:
            pos: self.pos
            size: self.size
    multiselect: False
    touch_multiselect: False
    padding: 10, 10
    spacing: 10, 10
    row_default_height: 200
    row_force_default: True
    col_force_default: False
    col_default_width: 200
    pos_hint: {'center_x': 0.5}
    size_hint: 1, None
    on_minimum_height: self.height = self.minimum_height
""")

    def __init__(self, chosen_stack_db, *args, **kwargs):
        super(StackListScreen, self).__init__(*args, **kwargs)
        print(chosen_stack_db)
        self.stack_db = chosen_stack_db
        global STACK_DATABASE
        STACK_DATABASE = self.stack_db
        db_init()
        self.load_stack_widgets_from_database()

    def load_stack_widgets_from_database(self,):
        for stack_object in self.stack_db:
            self.add_stack_widget(stack_object)

    def add_stack_widget(self, stack_object):
        SRL = StackRelativeLayout(stack_object)
        self.ids.StackSGL.add_widget(SRL)

# class StackListApp(App):

#     def build(self):
#         return StackListScreen(STACK_DATABASE)


# if __name__ == '__main__':
#     StackListApp().run()
