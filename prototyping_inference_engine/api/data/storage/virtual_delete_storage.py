"""Virtual deletion wrapper for materialized writable storages."""

from __future__ import annotations

from typing import Iterable, Iterator, Set

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.data.atomic_pattern import AtomicPattern
from prototyping_inference_engine.api.data.basic_query import BasicQuery
from prototyping_inference_engine.api.data.delegating_atom_wrapper import DelAtomWrapper
from prototyping_inference_engine.api.data.schema import RelationSchema, SchemaAware
from prototyping_inference_engine.api.fact_base.fact_base import FactBase
from prototyping_inference_engine.api.fact_base.protocols import Writable


class VirtualDeleteStorage(FactBase, Writable, SchemaAware):
    """Materialized writable wrapper that supports virtual deletions."""

    def __init__(self, storage: FactBase, removed_atoms: Iterable[Atom] = ()):
        if not isinstance(storage, Writable):
            raise TypeError("VirtualDeleteStorage requires a writable storage")
        self._storage = storage
        self._writable = storage
        self._removed: Set[Atom] = set(removed_atoms)
        self._wrapper = DelAtomWrapper(self._removed)

    @property
    def removed_atoms(self) -> Set[Atom]:
        return set(self._removed)

    def concrete_deletions(self) -> None:
        for atom in list(self._removed):
            self._writable.remove(atom)
        self._removed.clear()

    def get_predicates(self) -> Iterator[Predicate]:
        predicates = {atom.predicate for atom in self}
        return iter(predicates)

    def has_predicate(self, predicate: Predicate) -> bool:
        return any(atom.predicate == predicate for atom in self)

    def get_atomic_pattern(self, predicate: Predicate) -> AtomicPattern:
        return self._storage.get_atomic_pattern(predicate)

    def get_schema(self, predicate: Predicate) -> RelationSchema | None:
        if isinstance(self._storage, SchemaAware):
            return self._storage.get_schema(predicate)
        return None

    def get_schemas(self) -> Iterable[RelationSchema]:
        if isinstance(self._storage, SchemaAware):
            return self._storage.get_schemas()
        return ()

    def evaluate(self, query: BasicQuery) -> Iterator[tuple[Term, ...]]:
        results = self._storage.evaluate(query)
        return self._wrapper.filter_results(query, results)

    def estimate_bound(self, query: BasicQuery) -> int | None:
        return self._storage.estimate_bound(query)

    @property
    def variables(self) -> Set[Variable]:
        variables: Set[Variable] = set()
        for atom in self:
            variables.update(atom.variables)
        return variables

    @property
    def constants(self) -> Set[Constant]:
        constants: Set[Constant] = set()
        for atom in self:
            constants.update(atom.constants)
        return constants

    @property
    def terms(self) -> Set[Term]:
        terms: Set[Term] = set()
        for atom in self:
            terms.update(atom.terms)
        return terms

    def add(self, atom: Atom) -> None:
        self._writable.add(atom)
        self._removed.discard(atom)

    def update(self, atoms: Iterable[Atom]) -> None:
        for atom in atoms:
            self.add(atom)

    def remove(self, atom: Atom) -> None:
        if atom in self._storage:
            self._removed.add(atom)

    def remove_all(self, atoms: Iterable[Atom]) -> None:
        for atom in atoms:
            self.remove(atom)

    def __iter__(self) -> Iterator[Atom]:
        for atom in self._storage:
            if atom not in self._removed:
                yield atom

    def __len__(self) -> int:
        return sum(1 for _ in self)

    def __contains__(self, atom: Atom) -> bool:
        return atom not in self._removed and atom in self._storage
