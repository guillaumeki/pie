"""
First-order logic formulas.

This module provides classes for representing and constructing first-order
logic formulas including:
- Atomic formulas (Atom)
- Negation (¬)
- Conjunction (∧)
- Disjunction (∨)
- Universal quantification (∀)
- Existential quantification (∃)
"""

from prototyping_inference_engine.api.formula.formula import Formula
from prototyping_inference_engine.api.formula.negation_formula import NegationFormula
from prototyping_inference_engine.api.formula.binary_formula import BinaryFormula
from prototyping_inference_engine.api.formula.conjunction_formula import (
    ConjunctionFormula,
)
from prototyping_inference_engine.api.formula.disjunction_formula import (
    DisjunctionFormula,
)
from prototyping_inference_engine.api.formula.quantified_formula import (
    QuantifiedFormula,
)
from prototyping_inference_engine.api.formula.universal_formula import UniversalFormula
from prototyping_inference_engine.api.formula.existential_formula import (
    ExistentialFormula,
)
from prototyping_inference_engine.api.formula.formula_builder import FormulaBuilder

__all__ = [
    "Formula",
    "NegationFormula",
    "BinaryFormula",
    "ConjunctionFormula",
    "DisjunctionFormula",
    "QuantifiedFormula",
    "UniversalFormula",
    "ExistentialFormula",
    "FormulaBuilder",
]
