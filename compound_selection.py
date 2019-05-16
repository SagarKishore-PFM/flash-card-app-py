# -*- coding: utf-8 -*-
"""
Kivy mixer class for implementing compound selection behavior with any Kivy layouts.
"""
from kivy.uix.behaviors.compoundselection import CompoundSelectionBehavior
from kivy.uix.button import Button
from kivy.uix.behaviors import FocusBehavior
from kivy.app import App


class SelectableLayout(FocusBehavior, CompoundSelectionBehavior):

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        """Based on FocusBehavior that provides automatic keyboard
        access, key presses will be used to select children.
        """
        if super(SelectableLayout, self).keyboard_on_key_down(
            window,
            keycode,
            text,
            modifiers,
        ):
            return True
        if self.select_with_key_down(window, keycode, text, modifiers):
            return True
        return False

    def keyboard_on_key_up(self, window, keycode):
        """Based on FocusBehavior that provides automatic keyboard
        access, key release will be used to select children.
        """
        if super(SelectableLayout, self).keyboard_on_key_up(window, keycode):
            return True
        if self.select_with_key_up(window, keycode):
            return True
        return False

    def add_widget(self, widget):
        """ Override the adding of widgets so we can bind and catch their
        *on_touch_down* events. """
        widget.bind(on_touch_down=self.button_touch_down,
                    on_touch_up=self.button_touch_up)
        return super(SelectableLayout, self).add_widget(widget)

    def button_touch_down(self, button, touch):
        """ Use collision detection to select buttons when the touch occurs
        within their area. """
        if button.collide_point(*touch.pos):
            self.select_with_touch(button, touch)

    def button_touch_up(self, button, touch):
        """ Use collision detection to de-select buttons when the touch
        occurs outside their area and *touch_multiselect* is not True. """
        if not button.collide_point(*touch.pos) or self.touch_multiselect:
            self.deselect_node(button)

    def select_node(self, node):
        node.background_color = (0.5, 0.2, 0.1, 0.9)
        return super(SelectableLayout, self).select_node(node)

    def deselect_node(self, node):
        node.background_color = (0.3, 0.3, 0.3, 0.81)
        super(SelectableLayout, self).deselect_node(node)

    def on_selected_nodes(self, gird, nodes):
        # print("Selected nodes = {0}".format(nodes))
        pass


class TestApp(App):
    def build(self):
        grid = SelectableLayout(cols=2, rows=2, touch_multiselect=True,
                                multiselect=True)
        for i in range(0, 6):
            grid.add_widget(Button(text="Button {0}".format(i)))
        return grid


if(__name__ == '__main__'):
    TestApp().run()
