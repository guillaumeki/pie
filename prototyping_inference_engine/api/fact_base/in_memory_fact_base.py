from abc import ABC
from typing import Tuple, Type, Iterator, Set

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.set.atom_set import AtomSet
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.fact_base.fact_base import FactBase
from prototyping_inference_engine.api.fact_base.query_executor import QueryExecutorRegistry
from prototyping_inference_engine.api.query.query import Query
from prototyping_inference_engine.api.query.unsupported_query import UnsupportedQuery
from prototyping_inference_engine.api.substitution.substitution import Substitution


class InMemoryFactBase(FactBase, ABC):
    def __init__(self, storage: AtomSet):
        self._storage = storage

    # QuerySupport
    @classmethod
    def get_supported_query_types(cls) -> Tuple[Type[Query], ...]:
        return QueryExecutorRegistry.instance().supported_query_types()

    # Query execution via Strategy
    def execute_query(self, query: Query, sub: Substitution) -> Iterator[Tuple[Term, ...]]:
        executor = QueryExecutorRegistry.instance().get_executor(query)
        if executor is None:
            raise UnsupportedQuery()
        return executor.execute(query, self._storage, sub)

    # TermInspectable (properties)
    @property
    def variables(self) -> Set[Variable]:
        return self._storage.variables

    @property
    def constants(self) -> Set[Constant]:
        return self._storage.constants

    @property
    def terms(self) -> Set[Term]:
        return self._storage.terms

    # Enumerable
    def __len__(self) -> int:
        return len(self._storage)

    def __iter__(self) -> Iterator[Atom]:
        return iter(self._storage)

    def __contains__(self, atom: Atom) -> bool:
        return atom in self._storage
