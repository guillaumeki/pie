"""
Helpers for extracting quantified variables from formulas.
"""

from typing import TYPE_CHECKING

from prototyping_inference_engine.api.formula.binary_formula import BinaryFormula
from prototyping_inference_engine.api.formula.existential_formula import (
    ExistentialFormula,
)
from prototyping_inference_engine.api.formula.formula import Formula
from prototyping_inference_engine.api.formula.negation_formula import NegationFormula
from prototyping_inference_engine.api.formula.universal_formula import UniversalFormula

if TYPE_CHECKING:
    from prototyping_inference_engine.api.atom.term.variable import Variable


def collect_existential_variables(formula: Formula) -> frozenset["Variable"]:
    if isinstance(formula, ExistentialFormula):
        return frozenset({formula.variable}) | collect_existential_variables(
            formula.inner
        )
    if isinstance(formula, UniversalFormula):
        return collect_existential_variables(formula.inner)
    if isinstance(formula, NegationFormula):
        return collect_existential_variables(formula.inner)
    if isinstance(formula, BinaryFormula):
        return collect_existential_variables(
            formula.left
        ) | collect_existential_variables(formula.right)
    if isinstance(formula, Formula):
        return frozenset()
    raise TypeError(f"Unsupported formula type: {type(formula)}")
