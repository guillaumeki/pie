from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type, Iterator, Tuple, Optional

from prototyping_inference_engine.api.atom.set.atom_set import AtomSet
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.query.atomic_query import AtomicQuery
from prototyping_inference_engine.api.query.query import Query
from prototyping_inference_engine.api.substitution.substitution import Substitution

Q = TypeVar('Q', bound=Query)


class QueryExecutor(ABC, Generic[Q]):
    """Strategy for executing a specific type of query."""

    @classmethod
    @abstractmethod
    def supported_query_type(cls) -> Type[Q]:
        ...

    @abstractmethod
    def execute(self, query: Q, storage: AtomSet, sub: Substitution) -> Iterator[Tuple[Term, ...]]:
        ...


class AtomicQueryExecutor(QueryExecutor[AtomicQuery]):
    """Executor for AtomicQuery."""

    @classmethod
    def supported_query_type(cls) -> Type[AtomicQuery]:
        return AtomicQuery

    def execute(self, query: AtomicQuery, storage: AtomSet, sub: Substitution) -> Iterator[Tuple[Term, ...]]:
        for atom in storage.match(query.atom, sub):
            yield atom.terms


class QueryExecutorRegistry:
    """Singleton registry - allows adding new executors (OCP)."""

    _instance: Optional["QueryExecutorRegistry"] = None

    def __init__(self):
        self._executors: dict[Type[Query], QueryExecutor] = {}

    @classmethod
    def instance(cls) -> "QueryExecutorRegistry":
        if cls._instance is None:
            cls._instance = QueryExecutorRegistry()
            # Register default executors
            cls._instance.register(AtomicQueryExecutor())
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance (useful for testing)."""
        cls._instance = None

    def register(self, executor: QueryExecutor) -> None:
        self._executors[executor.supported_query_type()] = executor

    def get_executor(self, query: Query) -> Optional[QueryExecutor]:
        # Try exact match first
        query_type = type(query)
        if query_type in self._executors:
            return self._executors[query_type]
        # Try subclass match
        for registered_type, executor in self._executors.items():
            if isinstance(query, registered_type):
                return executor
        return None

    def supported_query_types(self) -> Tuple[Type[Query], ...]:
        return tuple(self._executors.keys())
