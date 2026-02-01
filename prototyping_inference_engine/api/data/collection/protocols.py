"""
Protocols for data source capabilities.

These protocols define structural contracts that data sources may satisfy,
enabling the collection system to work with heterogeneous backends.
"""
from typing import Protocol, Iterator, Tuple, Set, runtime_checkable, TYPE_CHECKING

if TYPE_CHECKING:
    from prototyping_inference_engine.api.atom.atom import Atom
    from prototyping_inference_engine.api.atom.predicate import Predicate
    from prototyping_inference_engine.api.atom.term.constant import Constant
    from prototyping_inference_engine.api.atom.term.term import Term
    from prototyping_inference_engine.api.atom.term.variable import Variable
    from prototyping_inference_engine.api.data.atomic_pattern import AtomicPattern
    from prototyping_inference_engine.api.data.basic_query import BasicQuery


@runtime_checkable
class Queryable(Protocol):
    """
    Protocol for data sources that support basic query evaluation.

    A Queryable source can enumerate its predicates, describe query constraints
    via AtomicPattern, and evaluate BasicQuery instances.

    This protocol is satisfied by ReadableData and its subclasses.
    """

    def get_predicates(self) -> Iterator["Predicate"]:
        """Return all predicates available in this data source."""
        ...

    def has_predicate(self, predicate: "Predicate") -> bool:
        """Check if this data source contains the given predicate."""
        ...

    def get_atomic_pattern(self, predicate: "Predicate") -> "AtomicPattern":
        """Get the atomic pattern describing query constraints for a predicate."""
        ...

    def evaluate(self, query: "BasicQuery") -> Iterator[Tuple["Term", ...]]:
        """Evaluate a basic query, returning tuples of terms for answer positions."""
        ...

    def can_evaluate(self, query: "BasicQuery") -> bool:
        """Check if a basic query can be evaluated against this source."""
        ...


@runtime_checkable
class Materializable(Protocol):
    """
    Protocol for data sources with fully materialized (in-memory) atoms.

    A Materializable source supports iteration, containment checks, and
    term inspection. This enables full enumeration of the data.

    This protocol is satisfied by MaterializedData and its subclasses.
    """

    def __iter__(self) -> Iterator["Atom"]:
        """Iterate over all atoms in this data source."""
        ...

    def __len__(self) -> int:
        """Return the number of atoms in this data source."""
        ...

    def __contains__(self, atom: "Atom") -> bool:
        """Check if an atom is in this data source."""
        ...

    @property
    def variables(self) -> Set["Variable"]:
        """All variables appearing in the atoms."""
        ...

    @property
    def constants(self) -> Set["Constant"]:
        """All constants appearing in the atoms."""
        ...

    @property
    def terms(self) -> Set["Term"]:
        """All terms appearing in the atoms."""
        ...


@runtime_checkable
class DynamicPredicates(Protocol):
    """
    Marker protocol for sources that may add predicates dynamically.

    Sources implementing this protocol signal that their predicate set
    may grow over time. Collections use this to know when to refresh
    their predicate routing tables.

    Note: This assumes single-threaded access. No synchronization is provided.
    """

    def get_predicates(self) -> Iterator["Predicate"]:
        """Return all predicates currently available."""
        ...
