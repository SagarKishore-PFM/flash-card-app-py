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

STACK_DATABASE = generate_test_stack_database()
WORD_DATABASE = generate_test_word_database()
STACK_NAMES = [stack.name for stack in STACK_DATABASE]
WORD_SEARCH_DICT = {word.name: word for word in WORD_DATABASE}
# class AddTestButton(Button):

#     def openpop(self):
#         popup = EditStackPopup2()
#         popup.open()


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

    def __init__(self, stack_object, *args, **kwargs):
        self.stack_object = stack_object
        self.stack_object.refresh_rank_dict()
        super(StackRelativeLayout, self).__init__(*args, **kwargs)
        self.redraw()

    def redraw(self):
        # self.stack_object = new_stack_object
        self.ids.StackNameLabel.text = self.stack_object.name
        self.ids.StackSizeLabel.text = str(self.stack_object.size)
        self.ids.MasteredLabel.text = 'Mastered {0} / {1} words'.format(
            len(self.stack_object.rank_dict[6]), self.stack_object.size)
        self.ids.MasteredProgressBar.value = len(self.stack_object.rank_dict[6])


class WordListAdapter(ListAdapter):

    word_object_list = ObjectProperty(None)


class ViewStackWordViewList(ListView):
    pass


class WordGridLayout(SelectableLayout, GridLayout):
    pass


class ViewStackButton(Button):

    # selected_stack_relative_layout = ObjectProperty(None)
    # selected_stack_object = ObjectProperty(None)

    def open_popup(self, selected_stack_relative_layout):
        selected_stack_object = selected_stack_relative_layout.stack_object
        popup = ViewStackPopup(selected_stack_object)
        popup.open()


class ViewStackPopup(Popup):

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
                'height': 45}

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
        reviewing_set = self.rank_dict[1].union(self.rank_dict[2],
                                                self.rank_dict[3],
                                                self.rank_dict[4],
                                                self.rank_dict[5])

        self.ids.NewPFL.ids.PB.value = len(self.rank_dict[-1])
        self.ids.MasteredPFL.ids.PB.value = len(self.rank_dict[6])
        self.ids.ReviewingPFL.ids.PB.value = len(reviewing_set)
        self.ids.LearningPFL.ids.PB.value = len(self.rank_dict[0])

        self.ids.NewPFL.ids.Lbl.text = \
            f'New words left {len(self.rank_dict[-1])} / {self.max_value}'
        self.ids.MasteredPFL.ids.Lbl.text = \
            f'Mastered {len(self.rank_dict[6])} / {self.max_value} words'
        self.ids.ReviewingPFL.ids.Lbl.text = \
            f'Reviewing {len(reviewing_set)} / {self.max_value} words'
        self.ids.LearningPFL.ids.Lbl.text = \
            f'Learning {len(self.rank_dict[0])} / {self.max_value} words'


class CreateStackButton(Button):

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
                'height': 45}

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
        self.generate_word_listview()

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


# class WordDescriptionLayout(SelectableView, FloatLayout):

#     word_object = ObjectProperty(None)
#     lblid = ObjectProperty(None)

class WordDescriptionLayout(SelectableView, FloatLayout):

    word_object = ObjectProperty(None)


class ProgressFloatLayout(FloatLayout):
    max_value = NumericProperty(-1)


class EditWordsPopup(Popup):

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
        search_result = []
        if(len(input) != 0):
            for key in WORD_SEARCH_DICT:
                if(input in key[0:len(input)]):
                    search_result.append(WORD_SEARCH_DICT[key])

        self.generate_search_word_listview(search_result)
        if(search_result == []):
            # self.generate_thesaurus_listview(self.search_word_list_view.adapter)
            self.ids.ThesaurusWordGL.clear_widgets()
            pass

    def populate_selected_list(self):
        for button in self.search_list_adapter.selection:
            if(button.word_object not in self.word_object_list):
                self.word_object_list.append(button.word_object)

        self.generate_selected_word_listview()

    def remove_selected_list(self):
        selected_words = []
        for button in self.selected_list_adapter.selection:
            selected_words.append(button.word_object)
        for word in selected_words:
            self.word_object_list.remove(word)
        self.generate_selected_word_listview()


class EditStackButton(Button):

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
                'height': 30, }

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
        self.generate_word_listview()

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


class RootFloatLayout(FloatLayout):

    def __init__(self, STACK_DATABASE, *args, **kwargs):
        super(RootFloatLayout, self).__init__(*args, **kwargs)
        self.load_stack_widgets_from_database(STACK_DATABASE)

    def load_stack_widgets_from_database(self, STACK_DATABASE):
        for stack_object in STACK_DATABASE:
            self.add_stack_widget(stack_object)

    def add_stack_widget(self, stack_object):
        SRL = StackRelativeLayout(stack_object)
        self.ids.StackSGL.add_widget(SRL)


class StackListScreen(Screen):
    # pass
    def __init__(self, *args, **kwargs):
        super(StackListScreen, self).__init__(*args, **kwargs)
        self.rootFL = RootFloatLayout(STACK_DATABASE)
        self.add_widget(self.rootFL)


class StackListApp(App):

    def build(self):
        return StackListScreen()


if __name__ == '__main__':
    StackListApp().run()
