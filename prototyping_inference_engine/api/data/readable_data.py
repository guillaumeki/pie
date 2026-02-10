"""
ReadableData interface for queryable data sources.
"""

from abc import ABC, abstractmethod
from typing import Iterator, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from prototyping_inference_engine.api.atom.predicate import Predicate
    from prototyping_inference_engine.api.atom.term.term import Term
    from prototyping_inference_engine.api.data.atomic_pattern import AtomicPattern
    from prototyping_inference_engine.api.data.basic_query import BasicQuery


class ReadableData(ABC):
    """
    Abstract interface for readable data sources.

    This interface abstracts data access, allowing evaluators to work with
    different backends: in-memory fact bases, SQL databases, REST APIs, etc.

    Each data source declares its capabilities through AtomicPatterns, which
    specify what constraints must be satisfied to query each predicate.
    """

    @abstractmethod
    def get_predicates(self) -> Iterator["Predicate"]:
        """Return all predicates available in this data source."""
        ...

    @abstractmethod
    def has_predicate(self, predicate: "Predicate") -> bool:
        """Check if this data source contains the given predicate."""
        ...

    @abstractmethod
    def get_atomic_pattern(self, predicate: "Predicate") -> "AtomicPattern":
        """
        Get the atomic pattern for a predicate.

        The pattern describes what constraints must be satisfied to query
        this predicate from the data source.

        Args:
            predicate: The predicate to get the pattern for

        Returns:
            The atomic pattern describing query constraints
        """
        ...

    @abstractmethod
    def evaluate(self, query: "BasicQuery") -> Iterator[Tuple["Term", ...]]:
        """
        Evaluate a basic query against this data source.

        Returns tuples of terms for the answer positions (sorted by position).
        The data source only filters by bound positions - no post-processing.

        Args:
            query: The basic query specifying predicate and bound positions

        Returns:
            Iterator of term tuples for the answer positions
        """
        ...

    def can_evaluate(self, query: "BasicQuery") -> bool:
        """
        Check if a basic query can be evaluated.

        Args:
            query: The basic query to check

        Returns:
            True if the query satisfies the data source's constraints
        """
        pattern = self.get_atomic_pattern(query.predicate)

        # Check that all constrained positions are bound in the query
        for pos in range(query.predicate.arity):
            constraint = pattern.get_constraint(pos)
            if constraint is not None:
                term = query.get_bound_term(pos)
                if term is None or not constraint.is_satisfied_by(term):
                    return False

        return True

    def estimate_bound(self, query: "BasicQuery") -> int | None:
        """
        Return a lightweight upper bound on the number of results.

        Implementations should keep this computation cheap and may return
        None when no reliable bound is available.
        """
        return None
