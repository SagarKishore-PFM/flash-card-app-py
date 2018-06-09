from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.core.audio import SoundLoader
from kivy.clock import Clock

import string
import requests
import os
import jsonpickle
from functools import partial


def load_db():
    dir_path = os.getcwd() + '\\db\\'
    dir_, subdirs_, files_ = next(os.walk(dir_path))
    fpaths = [dir_ + file_ for file_ in files_]
    database_list = []
    for path in fpaths:
        with open(path, 'r') as fp:
            db_ret = jsonpickle.decode(fp.read(), keys=True)
        database_list.append(db_ret)
    return database_list


def save_db(database_list):
    dir_path = os.getcwd() + '\\db\\'
    for fcdb in database_list:
        file_path = dir_path + fcdb.name + '.json'
        fcdb_json = jsonpickle.encode(fcdb, keys=True)
        with open(file_path, 'w') as fp:
            fp.write(fcdb_json)


def play(word):
    if(word.audio == ''):
        return -1
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
    return 1


def unload_sound(instance):
    instance.unload()


def delete_temp():
        cwd = os.getcwd()
        temp_dir = cwd + '\\temp\\'
        dir_, subdirs_, files_ = next(os.walk(temp_dir))
        fpaths = [temp_dir + file_ for file_ in files_]
        for path in fpaths:
            os.remove(path)


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
            examples_core = examples_core + f"({azlower[j]})  "\
                + ex + '\n' + '            '
        examples_string = f"""[size=20][b]Examples: [/b][/size]

            [size=18][i]{examples_core}[/size][/i]
    """
        defex_string = defex_string + definition_string + examples_string

    synant_string = ""

    for i, x in enumerate(word.synant):
        # try:
        syns = ', '.join(word.synant[x]['synonyms'])
        syn_string = f"""[size=26][b]({'i'*(i+1)}) {x}:[/b][/size]

        [b][size=20]Synonyms:[/b][/size]  [i][size=22]{syns}[/size][/i]

    """
        ants = ', '.join(word.synant[x]['antonyms'])
        ant_string = f"""\
    [size=20][b]Antonyms: [/b][i][size=22]{ants}[/size][/i][/size]

    """
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
