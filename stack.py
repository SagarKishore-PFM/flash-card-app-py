# -*- coding: utf-8 -*-
"""
Created on Saturday, April 1st 2018

@author: sagar
"""


class Stack:
    """
    Stack Class that takes in the stack name as mandatory parameter.
    """

    def __init__(self, name, **kwargs):
        self.name = name
        self.words = []
        self._rank_dict = {'-1': set(self.words),
                           '0': set(),
                           '1': set(),
                           '2': set(),
                           '3': set(),
                           '4': set(),
                           '5': set(),
                           '6': set(), }

    @property
    def rank_dict(self):
        return self._rank_dict

    @rank_dict.setter
    def rank_dict(self, value):
        self._rank_dict = value

    def refresh_rank_dict(self):
        self.rank_dict['-1'] = set(self.words)
        self.rank_dict['0'] = set()
        self.rank_dict['1'] = set()
        self.rank_dict['2'] = set()
        self.rank_dict['3'] = set()
        self.rank_dict['4'] = set()
        self.rank_dict['5'] = set()
        self.rank_dict['6'] = set()

    @property
    def size(self):
        return len(self.words)

    def __repr__(self):
        return "Stack({!r})".format((self.name))

    def __str__(self):
        return f"""\
        Stack - {self.name}
        Words - {self.words}
        Size - {self.size}
        """

    def __len__(self):
        return len(self.words)
