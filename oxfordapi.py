# -*- coding: utf-8 -*-
"""
Created on Saturday, March 31st 2018

@author: sagar
"""

import requests
from urllib3.exceptions import HTTPError
from word import Word
from pprint import PrettyPrinter


def getdefinitions(word_object, word_id):

    """
    Adds definitions to the word_object. Returns an error status indicating
    if the GET failed.
    """

    # Maybe encrypt these information?
    APP_ID = '5c0f7093'
    APP_KEY = 'd10576f4a34a64e8236472e947af906f'
    LANGUAGE = 'en'

    url_head = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/'
    url = url_head + LANGUAGE + '/' + word_id.lower()
    r = requests.get(url, headers={'app_id': APP_ID, 'app_key': APP_KEY})
    try:
        r.raise_for_status()
        status = True
    except HTTPError:
        status = False

    response_dict = r.json()
    header = response_dict['results'][0]
    name = header['word']
    lex_entries = {}
    lex_list = header['lexicalEntries']
    for lex in lex_list:
        lexentry = {}
        category = lex['lexicalCategory']
        AudioLink = lex['pronunciations'][0]['audioFile']
        sense = lex['entries'][0]['senses'][0]
        lexentry['definition'] = sense['definitions']
        lexentry['examples'] = []
        for examples in sense['examples']:
            lexentry['examples'].append(examples['text'])

        lex_entries[category] = lexentry

    word_object.name = name
    word_object.definitions = lex_entries
    word_object.audio = AudioLink
    return status


def getsynant(word_object, word_id):

    """
    Adds Synonyms and Antonyms to the word_object. Returns an error status
    indicating if the GET failed.
    """

    app_id = '5c0f7093'
    app_key = 'd10576f4a34a64e8236472e947af906f'
    language = 'en'

    url_head = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/'
    url = url_head + language + '/' + word_id.lower() + '/synonyms;antonyms'

    r = requests.get(url, headers={'app_id': app_id, 'app_key': app_key})
    try:
        r.raise_for_status()
        status = True
    except HTTPError:
        status = False
    response_dict = r.json()

    header = response_dict['results'][0]

    lex_entries = {}
    lex_list = header['lexicalEntries']
    for lex in lex_list:
        lexentry = {}
        category = lex['lexicalCategory']
        sense = lex['entries'][0]['senses'][0]
        try:
            lex_ant_list = sense['antonyms']
        except KeyError:
            lex_ant_list = []
        try:
            lex_syn_list = sense['synonyms']
        except KeyError:
            lex_syn_list = []

        antonyms_list = []
        for antonyms in lex_ant_list:
            antonyms_list.append(antonyms['text'])

        synonyms_list = []
        for synonyms in lex_syn_list:
            synonyms_list.append(synonyms['text'])

        lexentry['synonyms'] = synonyms_list
        lexentry['antonyms'] = antonyms_list

        lex_entries[category] = lexentry

    word_object.synant = lex_entries
    return status


def addword(word_object):

    word_id = word_object.name
    status1 = getdefinitions(word_object, word_id)
    status2 = getsynant(word_object, word_id)
    return (word_object, status1 and status2)


""" DEBUGGING """


def main(name=None):
    pp = PrettyPrinter(indent=4)
    if name is None:
        name = 'set'
    a = Word(name)
    a, status = addword(a, a.name)
    repr(a)
    pp.pprint(a)


if __name__ == '__main__':
    main()
