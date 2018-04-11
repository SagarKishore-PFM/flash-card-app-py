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
        self.maxsize = 50
        self.size = 0

    def __repr__(self):
        return "Stack({!r})".format((self.name))

    def __str__(self):
        return f"""\
        Stack - {self.name}
        Words - {self.words}
        Size - {self.size}
        Max Size - {self.maxsize}"""

    def __len__(self):
        return len(self.words)
