"""
Universal quantification formula: ∀x.φ
"""
from prototyping_inference_engine.api.formula.quantified_formula import QuantifiedFormula


class UniversalFormula(QuantifiedFormula):
    """Universal quantification: ∀x.φ"""

    @property
    def quantifier_symbol(self) -> str:
        return "∀"
