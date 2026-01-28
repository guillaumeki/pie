from abc import ABC, abstractmethod
from typing import Tuple, Iterable

from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.query.query import Query
from prototyping_inference_engine.api.query.query_support import QuerySupport
from prototyping_inference_engine.api.substitution.substitution import Substitution


class UnsupportedFactBaseOperation(Exception):
    def __init__(self, operation, msg=None, *args):
        if not msg:
            msg = "The operation " + operation.__name__ + " is unsupported on this fact base"
        super().__init__(msg, *args)


class FactBase(QuerySupport, ABC):
    @abstractmethod
    def execute_query(self, query: Query, sub: Substitution) -> Iterable[Tuple[Term, ...]]:
        pass
