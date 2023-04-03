"""
Created on 26 déc. 2021

@author: guillaume
"""
import typing

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.query.query import Query
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.variable import Variable


class AtomicQuery(Query):
    def __init__(self,
                 atom: Atom,
                 answer_variables: typing.Iterable[Variable] = None,
                 label: typing.Optional[str] = None):
        Query.__init__(answer_variables, label)
        self._atom = atom

    @property
    def atom(self) -> Atom:
        return self._atom

    @property
    def variables(self) -> set[Variable]:
        return self.atom.variables

    @property
    def constants(self) -> set[Constant]:
        return self.atom.constants

    @property
    def terms(self) -> set[Term]:
        return set(self.atom.terms)

    def query_with_other_answer_variables(self, answers_variables: tuple[Variable]) -> "AtomicQuery":
        return AtomicQuery(self._atom, answers_variables)

    @property
    def str_without_answer_variables(self) -> str:
        return ", ".join(str(self.atom))

    def __repr__(self):
        return "ConjunctiveQuery: "+str(self)

    def __str__(self):
        return "({}) :- {}".format(
            ", ".join(map(str, self.answer_variables)),
            ", ".join(str(self.atom)))

