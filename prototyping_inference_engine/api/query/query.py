"""
Created on 26 déc. 2021

@author: guillaume
"""
import typing
from abc import ABC, abstractmethod
from functools import cached_property

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.variable import Variable


class Query(ABC):
    def __init__(self,
                 answer_variables: typing.Iterable[Variable] = None,
                 label: typing.Optional[str] = None):
        if not answer_variables:
            answer_variables = ()
        self._answer_variables = tuple(answer_variables)
        self._label = label

    @property
    @abstractmethod
    def terms(self) -> set[Term]:
        pass

    @cached_property
    def answer_atom(self) -> Atom:
        return Atom(Predicate("ans", len(self.answer_variables)), *self._answer_variables)

    @property
    @abstractmethod
    def constants(self) -> set[Constant]:
        pass

    @property
    @abstractmethod
    def variables(self) -> set[Variable]:
        pass

    @cached_property
    def existential_variables(self) -> set[Variable]:
        return self.variables - set(self.answer_variables)

    @property
    def answer_variables(self) -> tuple[Variable]:
        return self._answer_variables

    @property
    def label(self) -> typing.Optional[str]:
        return self._label

    @property
    @abstractmethod
    def str_without_answer_variables(self) -> str:
        pass
