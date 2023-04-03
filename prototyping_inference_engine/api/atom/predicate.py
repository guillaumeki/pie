"""
Created on 23 déc. 2021

@author: guillaume
"""
from builtins import property
from enum import Enum
from functools import cache


class Predicate:
    @cache
    def __new__(cls, name: str, arity: int):
        return super(Predicate, cls).__new__(cls)

    def __init__(self, name: str, arity: int):
        self._name = name
        self._arity = arity

    @property
    def arity(self):
        return self._arity

    @property
    def name(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return str(self)+"/"+str(self.arity)

    def __str__(self) -> str:
        return self.name


class SpecialPredicate(Enum):
    EQUALITY = Predicate("=", 2)
