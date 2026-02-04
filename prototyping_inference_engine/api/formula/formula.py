"""
Abstract base class for first-order logic formulas.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from prototyping_inference_engine.api.substitution.substitutable import Substitutable

if TYPE_CHECKING:
    from prototyping_inference_engine.api.atom.atom import Atom
    from prototyping_inference_engine.api.atom.term.variable import Variable
    from prototyping_inference_engine.api.substitution.substitution import Substitution


class Formula(Substitutable["Formula"], ABC):
    """Abstract base for all first-order formulas."""

    @property
    @abstractmethod
    def free_variables(self) -> frozenset["Variable"]:
        """Variables not bound by any quantifier in this formula."""
        pass

    @property
    @abstractmethod
    def bound_variables(self) -> frozenset["Variable"]:
        """Variables bound by a quantifier in this formula."""
        pass

    @property
    @abstractmethod
    def atoms(self) -> frozenset["Atom"]:
        """All atoms appearing in this formula."""
        pass

    @abstractmethod
    def apply_substitution(self, substitution: "Substitution") -> "Formula":
        """Apply a substitution to this formula (only affects free variables)."""
        pass

    @property
    def is_ground(self) -> bool:
        """True if the formula has no free variables."""
        return len(self.free_variables) == 0

    @property
    def is_closed(self) -> bool:
        """Alias for is_ground (a closed formula has no free variables)."""
        return self.is_ground
