from abc import ABC
from typing import Tuple, Type, Iterator

from prototyping_inference_engine.api.atom.set.atom_set import AtomSet
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.fact_base.fact_base import FactBase
from prototyping_inference_engine.api.query.atomic_query import AtomicQuery
from prototyping_inference_engine.api.query.query import Query
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.api.query.unsupported_query import UnsupportedQuery


class InMemoryFactBase(FactBase, ABC):
    def __init__(self, atom_set):
        self._atom_set = atom_set

    @classmethod
    def get_supported_query_types(cls) -> Tuple[Type[Query]]:
        return AtomicQuery,

    @property
    def atom_set(self) -> AtomSet:
        return self._atom_set

    def execute_query(self, query: Query, sub: Substitution, filter_out_nulls: bool = True) -> Iterator[Tuple[Term]]:
        match query:
            case AtomicQuery() as aq:
                for t in self.atom_set.match(aq.atom):
                    yield t.terms
            case _:
                raise UnsupportedQuery()
