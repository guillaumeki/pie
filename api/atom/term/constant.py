'''
Created on 23 déc. 2021

@author: guillaume
'''
from api.atom.term.term import Term
from functools import cache


class Constant(Term):
    @cache
    def __new__(cls, identifier):
        return super(Constant, cls).__new__(cls)

    def __init__(self, identifier):
        super().__init__(identifier)

    def __repr__(self):
        return "Cst:" + str(self)
