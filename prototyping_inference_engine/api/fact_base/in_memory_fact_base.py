"""
In-memory fact base implementation.
"""

from abc import ABC
from typing import Iterator, Set, Tuple, TYPE_CHECKING

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.set.atom_set import AtomSet
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.fact_base.fact_base import FactBase

if TYPE_CHECKING:
    from prototyping_inference_engine.api.data.basic_query import BasicQuery


class InMemoryFactBase(FactBase, ABC):
    """Base class for in-memory fact bases backed by an AtomSet."""

    def __init__(self, storage: AtomSet):
        self._storage = storage

    # ReadableData implementation

    def get_predicates(self) -> Iterator[Predicate]:
        """Return all predicates in this fact base."""
        seen: set[Predicate] = set()
        for atom in self._storage:
            if atom.predicate not in seen:
                seen.add(atom.predicate)
                yield atom.predicate

    def has_predicate(self, predicate: Predicate) -> bool:
        """Check if this fact base contains atoms with the given predicate."""
        return any(atom.predicate == predicate for atom in self._storage)

    def evaluate(self, query: "BasicQuery") -> Iterator[Tuple[Term, ...]]:
        """
        Evaluate a basic query against this fact base.

        Filters facts by predicate and bound positions, returns tuples of
        terms for the answer positions (sorted by position index).
        """
        predicate = query.predicate
        bound_positions = query.bound_positions
        answer_positions = sorted(query.answer_variables.keys())

        for fact in self._storage:
            if fact.predicate != predicate:
                continue

            # Check bound positions match
            match = True
            for pos, bound_term in bound_positions.items():
                if fact.terms[pos] != bound_term:
                    match = False
                    break

            if not match:
                continue

            # Return tuple of terms at answer positions
            yield tuple(fact.terms[pos] for pos in answer_positions)

    # TermInspectable properties

    @property
    def variables(self) -> Set[Variable]:
        return self._storage.variables

    @property
    def constants(self) -> Set[Constant]:
        return self._storage.constants

    @property
    def terms(self) -> Set[Term]:
        return self._storage.terms

    # Enumerable / Container

    def __len__(self) -> int:
        return len(self._storage)

    def __iter__(self) -> Iterator[Atom]:
        return iter(self._storage)

    def __contains__(self, atom: Atom) -> bool:
        return atom in self._storage
