from testdatabase import generate_test_word_database
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
import string


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


class WordDescTest(FloatLayout):
    b = generate_test_word_database()
    a = b[34]
    a.definitions['Adjective']['examples'].append("MY VERY OWN")
    ms = word_description(a)


class WordDescApp(App):
    def build(self):
        return WordDescTest()


def main():
    WordDescApp().run()
    # pass


if __name__ == '__main__':
    main()

# DEBUGGING:
# for x in generate_test_word_database():
#     if(x.synant == []):
#         print(x.name)
#     b = word_description(x)
