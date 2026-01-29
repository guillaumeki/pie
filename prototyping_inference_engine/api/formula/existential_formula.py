"""
Existential quantification formula: ∃x.φ
"""
from prototyping_inference_engine.api.formula.quantified_formula import QuantifiedFormula


class ExistentialFormula(QuantifiedFormula):
    """Existential quantification: ∃x.φ"""

    @property
    def quantifier_symbol(self) -> str:
        return "∃"
