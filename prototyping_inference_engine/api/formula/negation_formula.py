"""
Negation formula: ¬φ
"""
from typing import TYPE_CHECKING

from prototyping_inference_engine.api.formula.formula import Formula

if TYPE_CHECKING:
    from prototyping_inference_engine.api.atom.atom import Atom
    from prototyping_inference_engine.api.atom.term.variable import Variable
    from prototyping_inference_engine.api.substitution.substitution import Substitution


class NegationFormula(Formula):
    """Negation: ¬φ"""

    def __init__(self, formula: Formula):
        self._formula = formula

    @property
    def inner(self) -> Formula:
        """The negated formula."""
        return self._formula

    @property
    def free_variables(self) -> frozenset["Variable"]:
        return self._formula.free_variables

    @property
    def bound_variables(self) -> frozenset["Variable"]:
        return self._formula.bound_variables

    @property
    def atoms(self) -> frozenset["Atom"]:
        return self._formula.atoms

    def apply_substitution(self, substitution: "Substitution") -> "NegationFormula":
        return NegationFormula(self._formula.apply_substitution(substitution))

    def __str__(self) -> str:
        return f"¬({self._formula})"

    def __repr__(self) -> str:
        return f"NegationFormula({self._formula!r})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, NegationFormula):
            return False
        return self._formula == other._formula

    def __hash__(self) -> int:
        return hash(("NOT", self._formula))
