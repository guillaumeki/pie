"""
Disjunction formula: φ ∨ ψ
"""

from typing import TYPE_CHECKING

from prototyping_inference_engine.api.formula.binary_formula import BinaryFormula

if TYPE_CHECKING:
    from prototyping_inference_engine.api.substitution.substitution import Substitution


class DisjunctionFormula(BinaryFormula):
    """Disjunction: φ ∨ ψ"""

    @property
    def symbol(self) -> str:
        return "∨"

    def apply_substitution(self, substitution: "Substitution") -> "DisjunctionFormula":
        return DisjunctionFormula(
            self._left.apply_substitution(substitution),
            self._right.apply_substitution(substitution),
        )
