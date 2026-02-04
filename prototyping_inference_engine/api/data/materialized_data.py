"""
MaterializedData interface for fully materialized data sources.
"""

from abc import abstractmethod
from typing import Iterator, Optional, Set, TYPE_CHECKING

from prototyping_inference_engine.api.data.readable_data import ReadableData

if TYPE_CHECKING:
    from prototyping_inference_engine.api.atom.atom import Atom
    from prototyping_inference_engine.api.atom.predicate import Predicate
    from prototyping_inference_engine.api.atom.term.constant import Constant
    from prototyping_inference_engine.api.atom.term.term import Term
    from prototyping_inference_engine.api.atom.term.variable import Variable
    from prototyping_inference_engine.api.data.atomic_pattern import AtomicPattern
    from prototyping_inference_engine.api.substitution.substitution import Substitution


class MaterializedData(ReadableData):
    """
    Data source where all atoms are materialized (available in memory).

    This interface extends ReadableData with full iteration capabilities.
    Since all data is available, there are no position constraints -
    any atom pattern can be evaluated.
    """

    @abstractmethod
    def __iter__(self) -> Iterator["Atom"]:
        """Iterate over all atoms in this data source."""
        ...

    @abstractmethod
    def __len__(self) -> int:
        """Return the number of atoms in this data source."""
        ...

    @abstractmethod
    def __contains__(self, atom: "Atom") -> bool:
        """Check if an atom is in this data source."""
        ...

    @property
    @abstractmethod
    def variables(self) -> Set["Variable"]:
        """All variables appearing in the atoms."""
        ...

    @property
    @abstractmethod
    def constants(self) -> Set["Constant"]:
        """All constants appearing in the atoms."""
        ...

    @property
    @abstractmethod
    def terms(self) -> Set["Term"]:
        """All terms appearing in the atoms."""
        ...

    def get_atoms_by_predicate(self, predicate: "Predicate") -> Iterator["Atom"]:
        """Get all atoms with the given predicate."""
        for atom in self:
            if atom.predicate == predicate:
                yield atom

    def get_atomic_pattern(self, predicate: "Predicate") -> "AtomicPattern":
        """
        Materialized data has no constraints - any pattern can be evaluated.

        Returns an unconstrained pattern for any predicate.
        """
        from prototyping_inference_engine.api.data.atomic_pattern import (
            UnconstrainedPattern,
        )

        return UnconstrainedPattern(predicate)

    def can_evaluate_atom(
        self, atom: "Atom", substitution: Optional["Substitution"] = None
    ) -> bool:
        """Materialized data can always evaluate any atom."""
        return True
