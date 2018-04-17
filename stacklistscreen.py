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
from testdatabase import generate_test_database
from compound_selection import SelectableLayout
from kivy.uix.listview import ListItemButton, ListView
from kivy.adapters.listadapter import ListAdapter

# ChangeLog:

# Version 0.2.0:

# The new UI design allows for ease of data manipulation and access.
# This includes 4 buttons surrounding the List of stacks.
# The Stacks are now selectable thanks to the compound_selection.py module.
# The buttons surrounding the SelectableGridLayout will be disabled until a
#   selection is made.
# Every button takes in the selected_stack_object as an argument.

# TODO:

# Add popups for all the functionalities required.
# Fix the existing popups or create new ones.
# Text inputs need to have their rules changed
# Consider reomving max size for stack object ELSE implement the logic for it
# Create a word database

# TODO:
# >> View Stack:
#     Fix the positions of the widgets and make it pretty
#     Implementation of flash card via Practice Button in the popup

# >> Edit Stack:
#     Fix the positions of the widgets and make it pretty
#     Create the word list view and add a button that take you to a different\
#         screen or popup that allows you to edit the words of the stack
#     Logic for the edit word UI and backend

# >> Create Stack:
#     Fix the positions of the widgets and make it pretty
#     Make the text input mandatory
#     Create a button that takes you to a different screen or popup that allows\
#         you to add words to the stack
#     Make sure that the stack name is unique

# >> Delete Stack:
#     Everything

STACK_DATABASE = generate_test_database()

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
        self.button_disabled = bool(not self.selected_nodes)


class StackRelativeLayout(SelectableLayout, RelativeLayout):

    def __init__(self, stack_object, *args, **kwargs):
        self.stack_object = stack_object
        super(StackRelativeLayout, self).__init__(*args, **kwargs)
        # self.ids.StackNameLabel.text = self.stack_object.name
        # self.ids.StackSizeLabel.text = str(self.stack_object.size)
        self.redraw(self.stack_object)

    def redraw(self, new_stack_object):

        self.stack_object = new_stack_object
        self.ids.StackNameLabel.text = self.stack_object.name
        self.ids.StackSizeLabel.text = str(self.stack_object.size)


class WordListAdapter(ListAdapter):

    word_object_list = ObjectProperty(None)


class ViewStackWordViewList(ListView):
    pass


class WordGridLayout(GridLayout):
    pass


class ViewStackPopup(Popup):

    stack_name_lbl = ObjectProperty(None)
    stack_size_lbl = ObjectProperty(None)
    stack_words_lbl = ObjectProperty(None)
    stack_maxsize_lbl = ObjectProperty(None)

    def __init__(self, stack_object, *args, **kwargs):
        self.stack_object = stack_object
        super(ViewStackPopup, self).__init__(*args, **kwargs)
        self.ids.StackNameLbl.text = self.stack_object.name
        self.ids.StackSizeLbl.text = str(self.stack_object.size)
        # self.ids.StackMaxSizeLbl.text = str(self.stack_object.maxsize)
        self.word_list_view = self.ids.WordViewList
        self.generate_word_listview(self.stack_object.words,
                                    self.word_list_view)

    def generate_word_listview(self, word_object_list, word_list_view):

        list_adapter = WordListAdapter(data=word_object_list,
                                       args_converter=lambda row_index, rec: {'text': rec.name,
                                                                              'size_hint_y': None,
                                                                              'height': 25},
                                       selection_mode="single",
                                       allow_empty_selection=False,
                                       cls=ListItemButton,
                                       word_object_list=word_object_list)
        word_list_view.adapter = list_adapter


class ViewStackPopupButton(Button):

    selected_stack_relative_layout = ObjectProperty(None)
    selected_stack_object = ObjectProperty(None)

    def open_popup(self, selected_stack_relative_layout):
        selected_stack_object = selected_stack_relative_layout.stack_object
        popup = ViewStackPopup(selected_stack_object)
        popup.open()


class CreateStackPopup(Popup):
    pass


class CreataStackPopupButton(Button):

    def open_popup(self):
        popup = CreateStackPopup()
        popup.open()


class EditStackPopup(Popup):

    stack_name_lbl = ObjectProperty(None)
    stack_size_lbl = ObjectProperty(None)
    stack_name_txt = ObjectProperty(None)
    save_changes_btn = ObjectProperty(None)
    # object_info_lbl = ObjectProperty(None)

    def __init__(self, stack_object, *args, **kwargs):
        self.stack_object = stack_object
        super(EditStackPopup, self).__init__(*args, **kwargs)
        self.stack_name_lbl.text = self.stack_object.name
        self.stack_size_lbl.text = str(self.stack_object.size)
        # self.object_info_lbl.text = str(stack_object)

    def save_changes_to_stack_object(self):
        self.stack_object.name = self.stack_name_txt.text
        self.stack_object.size = int(self.stack_size_lbl.text)

        return self.stack_object


class EditStackPopupButton(Button):

    def open_popup(self, selected_stack_relative_layout):
        selected_stack_object = selected_stack_relative_layout.stack_object
        popup = EditStackPopup(selected_stack_object)
        popup.ids.SaveChangesBtn.bind(
            on_release=partial(self.update_changes_to_stack,
                               popup,
                               selected_stack_relative_layout))
        popup.open()

    def update_changes_to_stack(self,
                                popup,
                                selected_stack_relative_layout,
                                instance):
        changed_stack_object = popup.save_changes_to_stack_object()
        selected_stack_relative_layout.redraw(changed_stack_object)


class StackListScreen(Screen):
    # pass
    def __init__(self, *args, **kwargs):
        super(StackListScreen, self).__init__(*args, **kwargs)
        self.load_stack_widgets_from_database(STACK_DATABASE)

    def load_stack_widgets_from_database(self, STACK_DATABASE):
        for stack_object in STACK_DATABASE:
            self.add_stack_widget(stack_object)

    def add_stack_widget(self, stack_object):
        SRL = StackRelativeLayout(stack_object)
        self.ids.SelectableGridLayout.add_widget(SRL)


class StackListApp(App):

    def build(self):
        return StackListScreen()


if __name__ == '__main__':
    StackListApp().run()
