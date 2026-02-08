"""
Wrap a fact base into a conjunction formula.
"""

from typing import Iterable, TYPE_CHECKING

from prototyping_inference_engine.api.formula.conjunction_formula import (
    ConjunctionFormula,
)
from prototyping_inference_engine.api.formula.formula import Formula

if TYPE_CHECKING:
    from prototyping_inference_engine.api.atom.atom import Atom
    from prototyping_inference_engine.api.atom.term.variable import Variable
    from prototyping_inference_engine.api.fact_base.fact_base import FactBase
    from prototyping_inference_engine.api.substitution.substitution import Substitution


class FOConjunctionFactBaseWrapper(Formula):
    """Expose a fact base as a conjunction of its atoms."""

    def __init__(self, fact_base: "FactBase"):
        self._fact_base = fact_base

    @property
    def fact_base(self) -> "FactBase":
        return self._fact_base

    @property
    def free_variables(self) -> frozenset["Variable"]:
        return frozenset(self._fact_base.variables)

    @property
    def bound_variables(self) -> frozenset["Variable"]:
        return frozenset()

    @property
    def atoms(self) -> frozenset["Atom"]:
        return frozenset(self._fact_base)

    def apply_substitution(self, substitution: "Substitution") -> "Formula":
        atoms = [
            atom.apply_substitution(substitution)
            for atom in sorted(self._fact_base, key=str)
        ]
        if not atoms:
            return self
        return _conjoin_all(atoms)

    def __str__(self) -> str:
        return " \u2227 ".join(map(str, sorted(self._fact_base, key=str)))

    def __repr__(self) -> str:
        return str(self)


def _conjoin_all(atoms: Iterable["Atom"]) -> Formula:
    iterator = iter(atoms)
    try:
        current: Formula = next(iterator)
    except StopIteration:
        raise ValueError("Cannot build a conjunction from an empty iterable.")
    for atom in iterator:
        current = ConjunctionFormula(current, atom)
    return current
