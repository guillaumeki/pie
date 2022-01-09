from abc import ABC
from typing import Tuple, Type, List, Iterator

from api.atom.atom_set import AtomSet
from api.atom.term.term import Term
from api.fact_base.fact_base import FactBase
from api.query.atomic_query import AtomicQuery
from api.query.query import Query
from api.query.substitution import Substitution
from api.query.unsupported_query import UnsupportedQuery


class InMemoryFactBase(FactBase, ABC):
    def __init__(self, atom_set):
        self._atom_set = atom_set

    @classmethod
    def get_supported_query_types(cls) -> Tuple[Type[Query]]:
        return AtomicQuery,

    @property
    def atom_set(self) -> AtomSet:
        return self._atom_set

    def execute_query(self, query: Query, sub: Substitution) -> Iterator[Tuple[Term]]:
        match query:
            case AtomicQuery() as aq:
                for t in self.atom_set.match(aq.atom):
                    yield t.terms
            case _:
                raise UnsupportedQuery()
