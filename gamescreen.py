"""
Created on Saturday, May 7th, 2018
@author: sagar


The game screen which implements the flash card algorithm and provides the
feature to continue where you left off.
"""

from kivy.app import App
from kivy.uix.screenmanager import Screen


class GameScreen(Screen):
    pass


class GameScreenApp(App):

    def build(self):
        return GameScreen()


def main():
    GameScreenApp().run()


if __name__ == '__main__':
    main()
