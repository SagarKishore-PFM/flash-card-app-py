# -*- coding: utf-8 -*-
"""
Created on Saturday, April 9th 2018

@author: Sagar Kishore

Kivy screen that allows for adding new Stacks as well as editing, deleting
and viewing existing Stacks in the selected Stack Database.
"""

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
from kivy.lang import Builder

from functools import partial
import re

from stack import Stack


STACK_DATABASE = []
WORD_DATABASE = []
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
        pos_hint: {'center_x': 0.5, 'y': 0.35}
        font_size: 40

    Label:
        id: MasteredLabel
        pos_hint: {'center_x': 0.5, 'y': -0.1}
        font_size: 22

    ProgressBar:
        id: MasteredPB
        max: root.stack_object.size
        pos_hint: {'center_x': 0.5, 'y': 0.2}
        size_hint: 0.8, 0.1
""")

    def __init__(self, stack_object, *args, **kwargs):
        self.stack_object = stack_object
        super(StackRelativeLayout, self).__init__(*args, **kwargs)
        self.redraw()

    def redraw(self, dt=0):
        self.ids.StackNameLabel.text = self.stack_object.name

        self.ids.MasteredLabel.text = 'Mastered {0} / {1} words'.format(
            len(self.stack_object.rank_dict['6']), self.stack_object.size)

        self.ids.MasteredPB.value = len(self.stack_object.rank_dict['6'])


class WordListAdapter(ListAdapter):

    word_list = ObjectProperty(None)


class ViewStackWordListView(ListView):
    pass


class WordListItemButton(ListItemButton):

    word_object = ObjectProperty(None)


class WordGridLayout(SelectableLayout, GridLayout):
    pass


class ViewStackButton(Button):

    Builder.load_string("""
<ViewStackButton>:
    pos_hint: {'x': 0.05, 'y': 0.5}
    size_hint: 0.15, 0.15
    """)

    def open_popup(self, selected_stack_relative_layout):
        selected_stack_object = selected_stack_relative_layout.stack_object
        popup = ViewStackPopup(selected_stack_object)
        popup.ids.PlayBtn.bind(on_release=partial(
            self.practice_stack,
            popup,
            selected_stack_object,
        ))
        popup.ids.ResetBtn.bind(on_release=partial(
            popup.reset_stack,
            selected_stack_relative_layout,
        ))
        popup.open()

    def practice_stack(self, popup, selected_stack, instance):
        popup.dismiss()
        manager = self.parent.parent.manager
        game_screen = manager.get_screen('game screen')
        game_screen.game_stack = selected_stack
        manager.current = 'game screen'


class ViewStackPopup(Popup):
    Builder.load_string("""
<ViewStackPopup>:
    id: VSP
    title: "Displaying Stack Information"
    title_size: '22sp'
    size_hint: 0.7, 0.7
    pos: 0, 0
    separator_color: [1, 1, 1, 1]

    FloatLayout:
        pos: VSP.pos

        Label:
            id: StackNameLbl
            pos_hint: {'center_x': 0.2, 'y': 0.8}
            canvas.before:
                Color:
                    rgba: 0.1, 0.1, 1, 0.0
                Rectangle:
                    pos: self.pos
                    size: self.size
            size_hint: None, None
            size: self.texture_size
            halign: 'right'
            valign: 'middle'
            text: "Stack Name"
            color: 0.1, 0.4, 0.81, 1
            font_size: 40

        Button:
            id: ExitBtn
            pos_hint: {'x': 0.8, 'y': 0.05}
            size_hint: 0.15, 0.15
            text: "Go Back"
            on_release: root.dismiss()

        Button:
            id: PlayBtn
            pos_hint: {'x': 0.55, 'y': 0.75}
            size_hint: 0.15, 0.15
            text: "Practice"
            disabled: root.button_disabled

        Button:
            id: ResetBtn
            pos_hint: {'x': 0.8, 'y': 0.75}
            size_hint: 0.15, 0.15
            text: "Reset Stack Progress"

        WordGridLayout:
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1.0
                Rectangle:
                    pos: self.pos
                    size: self.size
            id: GL
            pos_hint: {'x': 0.025, 'y': 0.15}
            size_hint: 0.35, 0.5
            padding: 10, 10
            cols: 1
            ViewStackWordListView:
                id: WordLV
                canvas.before:
                    Color:
                        rgba: 1, 0, 0, 0.0
                    Rectangle:
                        pos: self.pos
                        size: self.size
                pos: GL.pos
                size: GL.size

        BoxLayout:
            orientation: 'vertical'
            pos_hint: {'x': 0.5, 'center_y': 0.4}
            size_hint: 0.5, 0.3
            padding: 5, 5
            spacing: 5

            canvas.before:
                Color:
                    rgba: 1, 1, 1, 0.0
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
            rgba: 1, 0.4, 1, 0.0
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
        pos_hint: {'center_x': 0.5, 'y': 0.2}
        font_size: 18
""")

    max_value = NumericProperty(-1)
    button_disabled = BooleanProperty(False)

    def __init__(self, stack_object, *args, **kwargs):
        self.stack_object = stack_object
        super(ViewStackPopup, self).__init__(*args, **kwargs)
        self.ids.StackNameLbl.text = self.stack_object.name

        self.rank_dict = self.stack_object.rank_dict
        self.max_value = self.stack_object.size

        self.word_list_view = self.ids.WordLV
        self.word_list = self.stack_object.words
        self.generate_word_listview()
        self.update_progressbars()
        self.button_disabled = self.stack_object.size < 3

    def reset_stack(self, selected_stack_relative_layout, instance):
        self.stack_object.refresh_rank_dict()
        selected_stack_relative_layout.redraw()
        self.update_progressbars()

    def args_converter(self, row_index, rec):
        return {'text': rec.name,
                'word_object': rec,
                'size_hint_y': None,
                'height': 35,
                'font_size': 20, }

    def generate_word_listview(self):
        list_adapter = WordListAdapter(
            data=self.word_list,
            args_converter=self.args_converter,
            selection_mode="single",
            allow_empty_selection=False,
            cls=WordListItemButton,
            word_list=self.word_list
        )
        self.word_list_view.adapter = list_adapter
        self.word_list_view.container.spacing = 0.2

    def update_progressbars(self):
        reviewing_set = self.rank_dict['1'].union(
            self.rank_dict['2'],
            self.rank_dict['3'],
            self.rank_dict['4'],
            self.rank_dict['5']
        )

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
        popup.ids.SaveChangesBtn.bind(
            on_release=partial(
                self.create_new_stack,
                popup,
                SelectableGridLayout,
            )
        )
        popup.open()

    def create_new_stack(self, popup, SelectableGridLayout, instance):
        new_stack = Stack(popup.ids.StackName.text)
        new_stack.words = popup.word_list_view.adapter.data
        new_stack.refresh_rank_dict()
        STACK_DATABASE.append(new_stack)
        db_init()
        SelectableGridLayout.add_widget(StackRelativeLayout(new_stack))
        popup.dismiss()


class CreateStackPopup(Popup):
    Builder.load_string("""
<CreateStackPopup>:
    id: CreateStackPopup
    stack_name_lbl: StackNameLbl
    title: "Add a new Stack"
    title_size: '22sp'
    size_hint: 0.7, 0.7
    separator_color: [1, 1, 1, 1]

    FloatLayout:
        pos: CreateStackPopup.pos
        Label:
            id: StackNameLbl
            halign: 'left'
            valign: 'middle'
            size_hint: None, None
            pos_hint: {'x': 0.1,'center_y': 0.9}
            text: "Stack Name"
            font_size: 30

        RETextInput:
            id: StackName
            multiline: False
            pos_hint: {'x': 0.25,'y':0.85}
            size_hint: 0.45, 0.08
            hint_text: "Enter Stack Name...."
            on_text: root.validate_text_input()
            on_text_validate: root.open_edit_words_popup()

        Label:
            id: ErrorMessage
            pos_hint: {'x': 0.25,'y': 0.77}
            canvas.before:
                Color:
                    rgba: 0.4, 0.4, 0.4, 0.2
                Rectangle:
                    pos: self.pos
                    size: self.size
            bold: True
            size_hint: None, None
            font_size: 24
            size: self.texture_size
            halign: 'right'
            valign: 'middle'
            disabled: not root.button_disabled

        Button:
            id: EditWordsBtn
            pos_hint: {'x': 0.6, 'y': 0.1}
            size_hint: 0.15, 0.15
            text: "Edit Words"
            on_release: root.open_edit_words_popup()

        Button:
            id: SaveChangesBtn
            pos_hint: {'x': 0.825, 'y': 0.1}
            size_hint: 0.15, 0.15
            text: "Save Changes"
            disabled: root.button_disabled

        WordGridLayout:
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1.0
                Rectangle:
                    pos: self.pos
                    size: self.size
            id: GL
            pos_hint: {'x': 0.05, 'y': 0.1}
            size_hint: 0.5, 0.6
            padding: 10, 10
            cols: 1

            ViewStackWordListView:
                id: WordLV
                pos: GL.pos
                size: GL.size
""")
    stack_name_lbl = ObjectProperty(None)
    button_disabled = BooleanProperty(True)

    def __init__(self, *args, **kwargs):
        super(CreateStackPopup, self).__init__(*args, **kwargs)
        self.word_list_view = self.ids.WordLV
        self.word_list = []
        self.list_adapter = None
        self.generate_word_listview()

    def args_converter(self, row_index, rec):

        return {'text': rec.name,
                'size_hint_y': None,
                'height': 35,
                'font_size': 20}

    def generate_word_listview(self):

        self.list_adapter = WordListAdapter(
            data=self.word_list,
            args_converter=self.args_converter,
            selection_mode="single",
            allow_empty_selection=False,
            cls=ListItemButton,
            word_list=self.word_list
        )
        self.word_list_view.adapter = self.list_adapter
        self.word_list_view.container.spacing = 0.2

    def open_edit_words_popup(self):

        popup = EditWordsPopup(self.word_list)
        popup.ids.SaveChangesBtn.bind(on_release=partial(
            self.update_changes_to_word_list,
            popup
        ))
        popup.open()

    def update_changes_to_word_list(self,
                                    popup,
                                    instance):
        self.word_list = popup.selected_list_adapter.data
        popup.dismiss()
        self.word_list_view.adapter.data = self.word_list

    def validate_text_input(self):
        min_len = 3
        text = self.ids.StackName.text
        cond1 = len(text) < min_len
        cond2 = text in STACK_NAMES and text != self.stack_name_lbl.text
        self.button_disabled = cond1 or cond2
        if(self.button_disabled):
            self.ids.ErrorMessage.text = \
                '* Stack Name must be unique and contain more than ' + \
                f'{min_len} letters'
        else:
            self.ids.ErrorMessage.text = ""


class WordDescriptionLayout(SelectableView, FloatLayout):
    Builder.load_string("""
#:import short_meaning helperfuncs.short_meaning
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
        pos_hint: {'x': 0.025, 'y': 0.3}
        font_size: 28
        bold: True
        halign: 'left'
        valign: 'middle'
        size: WRL.size
        texture_size: self.size
        text_size: self.width, None
        text: root.word_object.name

    Label:

        id: WordMeaningLbl
        pos_hint: {'x': 0.025, 'y': -0.1}
        markup: True
        size: WRL.size #[0] * 0.8, WRL.size[1] * 0.8
        texture_size: self.size
        text_size: self.width * 0.8, self.height * 0.8
        halign: 'left'
        valign: 'middle'
        text: short_meaning(root.word_object)
        shorten: True
        shorten_from: 'right'
""")
    word_object = ObjectProperty(None)


class ProgressFloatLayout(FloatLayout):
    max_value = NumericProperty(-1)


class EditWordsPopup(Popup):

    Builder.load_string("""
<EditWordsPopup>:
    title: "Edit Words"
    size_hint: 0.7, 0.7
    title_size: '22sp'
    separator_color: [1, 1, 1, 1]
    FloatLayout:
        id: RootFL
        RETextInput:
            id: SearchBar
            pos_hint: {'center_x': 0.4, 'center_y': 0.9}
            size_hint: 0.7, 0.075
            on_text: root.search_words(self.text)
            multiline: False
            hint_text: "Search words..."

        Button:
            id: SaveChangesBtn
            text: "Save changes"
            pos_hint: {'center_x': 0.8825, 'y': 0.85}
            size_hint: 0.2, 0.1

        Button:
            id: AddWordsBtn
            text: "Add Selected Words"
            pos_hint: {'x': 0.03,'y': 0.7}
            size_hint: 0.17, 0.1
            on_release: root.populate_selected_list()

        Button:
            id: RemoveWordsBtn
            text: "Remove Selected Words"
            pos_hint: {'x': 0.8,'y': 0.7}
            size_hint: 0.17, 0.1
            on_release: root.remove_selected_list()


        WordGridLayout:
            canvas.before:
                Color:
                    rgba: 1, 1, 0, 1.0
                Rectangle:
                    pos: self.pos
                    size: self.size
            id: SearchWordGL
            pos_hint: {'x': 0.03,'y': 0.05}
            size_hint: 0.17, 0.6
            spacing: 10
            padding: 10
            cols: 1

            ViewStackWordListView:
                id: SearchWordLV
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
            pos_hint: {'x': 0.8,'y': 0.05}
            size_hint: 0.17, 0.6
            spacing: 10
            padding: 10
            cols: 1
            ViewStackWordListView:
                id: SelectedWordLV
                pos: SelectedWordGL.pos
                size: SelectedWordGL.size
        ScrollView:
            id:SV
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 0.15
                Rectangle:
                    pos: self.pos
                    size: self.size
            height: RootFL.height * 0.6
            top: self.height
            pos_hint: {'x': 0.25, 'y': 0.05}
            size_hint: 0.5, None
            ThesaurusWordGridLayout:
                id: ThesaurusWordGL

<ThesaurusWordGridLayout@SelectableGridLayout>:
    canvas.before:
        Color:
            rgba: 1, 1, 1, 0.0
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
        self.word_list = stack_words
        self.selected_word_list_view = self.ids.SelectedWordLV
        self.search_word_list_view = self.ids.SearchWordLV
        self.search_list_adapter = None
        self.selected_list_adapter = None
        self.generate_selected_word_listview()

    def args_converter(self, row_index, rec):

        return {'text': rec.name,
                'font_size': 20,
                'size_hint_y': None,
                'height': 45,
                'word_object': rec}

    def generate_selected_word_listview(self):

        self.selected_list_adapter = WordListAdapter(
            data=self.word_list,
            args_converter=self.args_converter,
            selection_mode='single',
            allow_empty_selection=True,
            cls=WordListItemButton,
            word_list=self.word_list,
        )
        self.selected_word_list_view.adapter = self.selected_list_adapter

    def generate_search_word_listview(self, search_word_list):

        self.search_list_adapter = WordListAdapter(
            data=search_word_list,
            args_converter=self.args_converter,
            selection_mode='multiple',
            allow_empty_selection=True,
            cls=WordListItemButton
        )
        self.search_word_list_view.adapter = self.search_list_adapter
        self.search_word_list_view.adapter.bind(
            on_selection_change=self.generate_thesaurus_listview
        )

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

    def search_words(self, input):
        self.search_word_list_view.container.parent.scroll_y = 1
        search_result = []
        if(len(input) != 0):
            for key in WORD_SEARCH_DICT:
                if(input in key[0:len(input)]):
                    search_result.append(WORD_SEARCH_DICT[key])

        self.generate_search_word_listview(search_result)
        if(search_result == []):
            self.ids.ThesaurusWordGL.clear_widgets()

    def populate_selected_list(self):
        for button in self.search_list_adapter.selection:
            if(button.word_object not in self.word_list):
                self.word_list.append(button.word_object)

        self.selected_list_adapter.data = self.word_list
        self.selected_word_list_view.container.parent.scroll_y = 0

    def remove_selected_list(self):
        selected_words = []
        for button in self.selected_list_adapter.selection:
            selected_words.append(button.word_object)
        for word in selected_words:
            self.word_list.remove(word)
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
        popup.ids.SaveChangesBtn.bind(on_release=partial(
            self.update_changes_to_stack,
            popup,
        ))

        popup.bind(on_dismiss=partial(
            self.redraw_callback,
            selected_stack_relative_layout,
        ))

        popup.open()

    def update_changes_to_stack(self, popup, instance):
        popup.save_changes_to_stack_object()
        popup.dismiss()

    def redraw_callback(self, selected_stack_relative_layout, instance):
        selected_stack_relative_layout.redraw()


class EditStackPopup(Popup):

    Builder.load_string("""
<EditStackPopup>:
    id: EditStackPopup
    stack_name_lbl: StackNameLbl
    stack_name_txt: StackName
    title: "Edit Stack Information"
    size_hint: 0.7, 0.7
    title_size: '22sp'
    separator_color: [1, 1, 1, 1]

    FloatLayout:
        id: FL
        pos: EditStackPopup.pos
        Label:
            id: StackNameLbl
            halign: 'right'
            valign: 'middle'
            size_hint: None, None
            pos_hint: {'x': 0.1,'center_y': 0.9}
            text: "Stack Name"
            font_size: 30

        RETextInput:
            id: StackName
            multiline: False
            pos_hint: {'x': 0.25,'y':0.85}
            size_hint: 0.45, 0.08
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
            text: "WARNING! \
Changing words in the Stack will reset your progress!"
            halign: 'center'
            valign: 'middle'
            size_hint: 0.25, 0.25
            text_size: self.size
            pos_hint: {'x': 0.65,'y': 0.5}
            font_size: 18

        Label:
            id: ErrorMessage
            pos_hint: {'x': 0.25,'y': 0.77}
            canvas.before:
                Color:
                    rgba: 0.4, 0.4, 0.4, 0.2
                Rectangle:
                    pos: self.pos
                    size: self.size
            text: ""
            size_hint: None, None
            font_size: 24
            size: self.texture_size
            halign: 'right'
            valign: 'middle'
            disabled: not root.button_disabled

        Button:
            id: EditWordsBtn
            pos_hint: {'x': 0.60, 'y': 0.1}
            size_hint: 0.15, 0.15
            text: "Edit Words"
            on_release: root.open_edit_words_popup()

        Button:
            id: SaveChangesBtn
            pos_hint: {'x': 0.825, 'y': 0.1}
            size_hint: 0.15, 0.15
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
            pos_hint: {'x': 0.05, 'y': 0.1}
            size_hint: 0.5, 0.6
            padding: 10, 10
            cols: 1

            ViewStackWordListView:
                id: WordLV
                pos: GL.pos
                size: GL.size
""")

    stack_name_lbl = ObjectProperty(None)
    button_disabled = BooleanProperty(True)
    stack_name_txt = ObjectProperty(None)

    def __init__(self, stack_object, *args, **kwargs):
        self.stack_object = stack_object
        super(EditStackPopup, self).__init__(*args, **kwargs)
        self.ids.StackNameLbl.text = self.stack_object.name
        self.word_list_view = self.ids.WordLV
        self.generate_word_listview()
        self.list_adapter = WordListAdapter
        self.validate_text_input()

    def save_changes_to_stack_object(self):
        self.stack_object.name = self.stack_name_txt.text
        db_init()

    def args_converter(self, row_index, rec):

        return {'text': rec.name,
                'size_hint_y': None,
                'height': 35,
                'font_size': 20}

    def generate_word_listview(self):

        self.list_adapter = WordListAdapter(
            data=self.stack_object.words,
            args_converter=self.args_converter,
            selection_mode="single",
            allow_empty_selection=False,
            cls=ListItemButton,
            word_list=self.stack_object.words
        )
        self.word_list_view.adapter = self.list_adapter
        self.word_list_view.container.spacing = 0.2

    def open_edit_words_popup(self):

        popup = EditWordsPopup(self.stack_object.words)
        popup.ids.SaveChangesBtn.bind(on_release=partial(
            self.update_changes_to_word_list,
            popup
        ))
        popup.open()

    def update_changes_to_word_list(self, popup, instance):
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
                'Stack Name must be unique and contain more than ' + \
                f'{min_len} letters'
        else:
            self.ids.ErrorMessage.text = ""


class DeleteStackButton(Button):

    Builder.load_string("""
<DeleteStackButton>:
    pos_hint: {'x': 0.8, 'y': 0.2}
    size_hint: 0.15, 0.15
""")

    def open_popup(self, selectable_grid_layout):
        popup = DeleteStackPopup()
        popup.ids.DeleteBtn.bind(on_release=partial(
            self.delete_stack,
            popup,
            selectable_grid_layout,
        ))
        popup.open()

    def delete_stack(self, popup, selectable_grid_layout, instance):
        selected_stack = selectable_grid_layout.return_selected_stack_layout()
        selectable_grid_layout.remove_widget(selected_stack)
        global STACK_DATABASE
        STACK_DATABASE.remove(selected_stack.stack_object)
        db_init()
        popup.dismiss()


class DeleteStackPopup(Popup):

    Builder.load_string("""
<DeleteStackPopup>:
    title: ""
    size_hint: 0.4, 0.3
    separator_color: [1, 1, 1, 1]

    FloatLayout:
        id: FL

        Label:
            font_size: 34
            size_hint: None, None
            size: self.texture_size
            text: 'Are you sure you want to delete?'
            halign: 'center'
            valign: 'middle'
            pos_hint: {'center_x': 0.5, 'y':0.75}

        Button:
            id: DeleteBtn
            text:"YES"
            size_hint: 0.4, 0.35
            pos_hint: {'x': 0.05, 'y': 0.1}
            # disabled: True

        Button:
            text:"NO"
            size_hint: 0.4, 0.35
            pos_hint: {'x': 0.55, 'y': 0.1}
            on_release: root.dismiss()
""")


class RETextInput(TextInput):

    pat1 = re.compile(r'[^a-zA-Z0-9\-\s]')
    pat2 = re.compile(r'[^A-Za-z]')

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
                rgba: 0.1, 0.5, 1, 0.0
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            id: DBTitle
            pos_hint: {'center_x': 0.5, 'y': 0.4}
            font_size: 60
            size: self.texture_size
            halign: 'center'
            valign: 'middle'

        ViewStackButton:
            id: ViewStackBtn
            pos_hint: {'x': 0.05, 'y': 0.5}
            size_hint: 0.15, 0.15
            on_release: self.open_popup(\
                StackSGL.return_selected_stack_layout())
            disabled: StackSGL.button_disabled
            text: "Practice Selected Stack"

        EditStackButton:
            id: EditStackBtn
            pos_hint: {'x': 0.8, 'y': 0.5}
            size_hint: 0.15, 0.15
            on_release: self.open_popup(\
                StackSGL.return_selected_stack_layout())
            disabled: StackSGL.button_disabled
            text: "Edit Selected Stack"

        CreateStackButton:
            id: CreateStackBtn
            pos_hint: {'x': 0.05, 'y': 0.15}
            size_hint: 0.15, 0.15
            on_release: self.open_popup(root.ids.StackSGL)
            text: "Create a new Stack"

        DeleteStackButton:
            id: DeleteStackBtn
            pos_hint: {'x': 0.8, 'y': 0.15}
            size_hint: 0.15, 0.15
            text: 'Delete Stack'
            disabled: StackSGL.button_disabled
            on_release: self.open_popup(StackSGL)

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
            canvas.before:
                Color:
                    rgba: 0.5, 0.1, 0.1, 1.0
                Rectangle:
                    pos: self.pos
                    size: self.size
            height: root.height * 0.8
            top: self.height
            pos_hint: {'center_x': .5}
            size_hint_x: 0.5
            size_hint_y: None
            top: self.height
            bar_color: 0.1, 0.5, 1, 1
            bar_width: 5

            StackSelectableGridLayout:
                id: StackSGL
                cols: 2

<WordListButton@Button>:
    pos_hint: {'x': 0.825, 'y': 0.85}
    size_hint: 0.15, 0.1


<DBListButton@Button>:
    pos_hint: {'x': 0.025, 'y': 0.85}
    size_hint: 0.15, 0.1


<StackSelectableGridLayout@SelectableGridLayout>:
    canvas.before:
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

    stack_db = ObjectProperty(None)
    fcdb = ObjectProperty(None)

    def on_enter(self, *args, **kwargs):
        super(StackListScreen, self).__init__(*args, **kwargs)
        global STACK_DATABASE
        global WORD_DATABASE
        STACK_DATABASE = self.fcdb.stack_db
        WORD_DATABASE = self.fcdb.word_db
        self.stack_db = self.fcdb.stack_db
        db_init()
        self.load_stack_widgets_from_database()
        self.ids.DBTitle.text = self.fcdb.name

    def on_leave(self):
        self.clear_widgets()

    def load_stack_widgets_from_database(self):
        for stack_object in self.stack_db:
            self.add_stack_widget(stack_object)

    def add_stack_widget(self, stack_object):
        SRL = StackRelativeLayout(stack_object)
        self.ids.StackSGL.add_widget(SRL)
