"""
Created on 23 déc. 2021

@author: guillaume
"""
from abc import ABC


class Term(ABC):
    def __init__(self, identifier: object):
        self._identifier = identifier

    @property
    def identifier(self) -> object:
        return self._identifier

    def __str__(self):
        return str(self.identifier)
