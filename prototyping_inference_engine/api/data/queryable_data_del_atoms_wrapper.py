"""
Wrapper for ReadableData that hides a set of removed atoms.
"""

from typing import Iterable, Iterator

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.data.atomic_pattern import AtomicPattern
from prototyping_inference_engine.api.data.basic_query import BasicQuery
from prototyping_inference_engine.api.data.delegating_atom_wrapper import (
    DelAtomWrapper,
)
from prototyping_inference_engine.api.data.readable_data import ReadableData


class QueryableDataDelAtomsWrapper(ReadableData):
    """
    Wrapper around a ReadableData that virtually removes specific atoms.
    """

    def __init__(self, data: ReadableData, removed_atoms: Iterable[Atom]):
        self._data = data
        self._wrapper = DelAtomWrapper(removed_atoms)

    @property
    def removed_atoms(self) -> set[Atom]:
        return self._wrapper.removed_atoms

    def get_predicates(self) -> Iterator[Predicate]:
        return self._data.get_predicates()

    def has_predicate(self, predicate: Predicate) -> bool:
        return self._data.has_predicate(predicate)

    def get_atomic_pattern(self, predicate: Predicate) -> AtomicPattern:
        return self._data.get_atomic_pattern(predicate)

    def evaluate(self, query: BasicQuery) -> Iterator[tuple[Term, ...]]:
        results = self._data.evaluate(query)
        return self._wrapper.filter_results(query, results)
