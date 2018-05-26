from testdatabase import generate_test_word_database
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
import string
import requests
from kivy.core.audio import SoundLoader
import os
from kivy.clock import Clock
from functools import partial


def word_description(word):

    header_string = f"""[b][size=40]{word.name}[/size][/b]

    """
    defex_string = ""
    azlower = list(string.ascii_lowercase)
    for i, x in enumerate(word.definitions):
        definitions = '.\n'.join(word.definitions[x]['definition'])
        definition_string = f"""[size=26][b]({'i'*(i+1)}) {x}: [/b][/size][size=22]{definitions}[/size]

    """
        examples_core = ""
        for j, ex in enumerate(word.definitions[x]['examples']):
            examples_core = examples_core + f"({azlower[j]})"\
                + ex + '\n' + '            '
        examples_string = f"""[size=20][b]Examples: [/b][/size]
            [size=18][i]{examples_core}[/size][/i]
    """
        defex_string = defex_string + definition_string + examples_string

    synant_string = ""

    for i, x in enumerate(word.synant):
        # try:
        syns = ', '.join(word.synant[x]['synonyms'])
        syn_string = f""" [size=26][b]({'i'*(i+1)}) {x}:[/b][/size]

        [b][size=20]Synonyms:[/b][/size]  [i][size=22]{syns}[/size][/i]

    """
        ants = ', '.join(word.synant[x]['antonyms'])
        ant_string = f"""\
    [size=20][b]Antonyms: [i][size=22]{ants}[/size][/i][/b][/size]"""
        synant_string = synant_string + syn_string + ant_string

    main_string = header_string + defex_string + synant_string
    return main_string


def short_meaning(word):
    short_meaning_string = ""
    for i, x in enumerate(word.definitions):
        definitions = '.\n'.join(word.definitions[x]['definition'])
        definition_string = f"""[size=18][b]({'i'*(i+1)}) {x}: [/size][size=16]{definitions}[/size][/b]
"""
        short_meaning_string = short_meaning_string + definition_string

    return short_meaning_string


def play(word):
    file_name = word.audio.split('/')[-1]
    temp_dir = os.getcwd() + '\\temp\\'
    fpath = temp_dir + file_name
    if file_name not in os.listdir(temp_dir):
        r = requests.get(word.audio)
        with open(fpath, 'wb') as f:
            f.write(r.content)
    sound = SoundLoader.load(fpath)
    sound.play()
    sound.bind(on_stop=unload_sound)


def unload_sound(instance):
    instance.unload()


def delete_file():
        # print(file, sound, dt)
        cwd = os.getcwd()
        file = cwd + '\\temp' + '\\audiotemp.mp3'
        os.remove(file)


class WordDescTest(FloatLayout):
    b = generate_test_word_database()
    a = b[34]
    a.definitions['Adjective']['examples'].append("MY VERY OWN")
    ms = word_description(a)
    url = 'http://audio.oxforddictionaries.com/en/mp3/xconscientious_gb_2.mp3'
    r = requests.get(url)

    def play_mp3(self, r):

        cwd = os.getcwd()
        file = cwd + '\\temp' + '\\audiotemp.mp3'
        with open(file, 'wb') as f:
            f.write(r.content)
        sound = SoundLoader.load(file)
        sound.play()

        Clock.schedule_once(partial(self.delete_file, file, sound), 4)


    def delete_file(self, file, sound, dt):
        print(file, sound, dt)
        sound.unload()
        os.remove(file)


class WordDescApp(App):
    def build(self):
        return WordDescTest()


def main():
    WordDescApp().run()
    # pass


if __name__ == '__main__':

    # play_mp3(r)
    main()

# DEBUGGING:
# for x in generate_test_word_database():
#     if(x.synant == []):
#         print(x.name)
#     b = word_description(x)
