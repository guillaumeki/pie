"""
Created on 23 déc. 2021

@author: guillaume
"""
from typing import Optional

from api.query.query import Query
from api.atom.term.variable import Variable


class Rule(object):
    def __init__(self, head: Query, body: Query = None, label: Optional[str] = None):
        if not body:
            body = ()
        self._frontier = body.get_variables & head.get_variables
        self._body = body.query_with_other_answer_variables(tuple(self._frontier))
        self._head = head.query_with_other_answer_variables(tuple(self._frontier))
        self._label = label

    @property
    def frontier(self) -> set[Variable]:
        return self._frontier

    @property
    def body(self) -> Query:
        return self._body

    @property
    def head(self) -> Query:
        return self._head

    @property
    def label(self) -> Optional[str]:
        return self._label

    def __str__(self):
        return "{}{} -> {}".format(
            "" if not self.label else "["+str(self.label)+"] ",
            str(self.body.str_without_answer_variables()),
            str(self.head.str_without_answer_variables()))

    def __repr__(self):
        return "Rule: "+str(self)
