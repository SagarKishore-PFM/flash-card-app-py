# -*- coding: utf-8 -*-
"""
Created on Saturday, April 1st 2018

@author: sagar
"""

import json
from word import Word
from stack import Stack


def stackobjectfromjson(json_data: list) -> list:
    """Converts a list of stack objects represented in json to python object"""
    # assert(type(json_list) is list), 'Function requires a list'
    object_list = []
    for entry in json_data:
        stack_object = Stack(entry['name'])
        words_list = entry['words']
        for word in words_list:
            word_object = Word(word['name'])
            word_object.definitions = word['definitions']
            word_object.audio = word['audio']
            word_object.synant = word['synant']
            stack_object.words.append(word_object)
        object_list.append(stack_object)
    return object_list


def wordobjectfromjson(json_data: list) -> list:
    """Converts a list of word objects represented in json to python object"""

    object_list = []
    for entry in json_data:
        word_object = Word(entry['name'])
        word_object.definitions = entry['definitions']
        word_object.audio = entry['audio']
        word_object.synant = entry['synant']
        object_list.append(word_object)
    return object_list


def generate_test_word_database(file: str=None) -> list:
    """
    Function to generate or fetch database from a file. If no file is given,
    it will automatically use the test database.
    """
    if(file is None):
        file = r'E:\Projects\Flash Card App\test_word_db.json'
    with open(file, 'r') as f:
        json_data = json.load(f)
    database = wordobjectfromjson(json_data)
    return database


def generate_test_stack_database(file: str=None) -> list:
    """
    Function to generate or fetch database from a file. If no file is given,
    it will automatically use the test database.
    """
    if(file is None):
        file = r'E:\Projects\Flash Card App\test_stack_db.json'
    with open(file, 'r') as f:
        json_data = json.load(f)
    database = stackobjectfromjson(json_data)
    return database


def main():
    word_database = generate_test_word_database()
    stack_database = generate_test_stack_database()
    print(len(word_database))
    print(len(stack_database))


if __name__ == '__main__':
    main()
