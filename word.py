# -*- coding: utf-8 -*-
"""
Created on Saturday, March 31st 2018

@author: Sagar Kishore
"""


class Word:
    """
    Word Class that takes in the word name as mandatory parameter.
    """

    def __init__(self, name, *args, **kwargs):
        self.name = name.lower()
        self.definitions = dict()
        self.audio = ''
        self.synant = dict()

    def __str__(self):
        return f"""\
Word Obeject - {self.name}
Audio URL - {self.audio}
Definitions - {self.definitions}
Synonyms and Antonyms - {self.synant}
"""

    def __repr__(self):
        return f'{self.name.title()}'
