# -*- coding: utf-8 -*-
"""
Created on Saturday, May 31st 2018

@author: sagar
"""


class FCDataBase:
    """
    Stack Class that takes in the stack name as mandatory parameter.
    """

    def __init__(self, name, **kwargs):
        self.name = name
        self.stack_db = []
        self.word_db = []