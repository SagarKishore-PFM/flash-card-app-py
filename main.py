from databasescreen import DataBaseApp
from kivy.config import Config
import os

Config.set("kivy", "desktop", 1)
Config.set("kivy", "exit_on_escape", 1)
Config.set("graphics", "resizable", 1)
Config.set("graphics", "window_state", "maximized")
Config.set("graphics", "borderless", 0)
Config.set("graphics", "fullscreen", 0)
Config.write()


def folder_init():
    cwd = os.getcwd()
    if not (os.path.exists(os.path.join(cwd, "temp"))):
        temp_path = os.path.join(cwd, "temp")
        os.mkdir(temp_path)


if __name__ == "__main__":
    folder_init()
    DataBaseApp().run()
