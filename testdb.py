# -*- coding: utf-8 -*-
"""
Created on Saturday, April 1st 2018

@author: sagar
"""
import json
from oxfordapi import addword
from word import Word
from stack import Stack

wordlist = ["stooge", "pupil", "create", "mass"]
wordlist2 = ["apply", "pull", "trigger"]

stack1 = Stack('Stack 1')
stack2 = Stack('Stack 2')

wordobject_list1 = []
for word in wordlist:
    word_object = Word(word)
    word_object, status = addword(word_object)
    if(status is False):
        raise RuntimeError
    wordobject_list1.append(word_object)

wordobject_list2 = []
for word in wordlist2:
    word_object = Word(word)
    word_object, status = addword(word_object)
    if(status is False):
        raise RuntimeError
    wordobject_list2.append(word_object)

stack1.words = wordobject_list1
stack2.words = wordobject_list2


def tojson(object):
    """ Converts python objects to json string"""
    return object.__dict__


file = r'E:\Projects\Flash Card App\testdb.json'
with open(file, 'w') as f:
    f.write(json.dumps([stack1, stack2], default=tojson, indent=4))
