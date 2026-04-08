"""Shared rule-fragment extraction for GRD and rule analysis."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.set.frozen_atom_set import FrozenAtomSet
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.formula.binary_formula import BinaryFormula
from prototyping_inference_engine.api.formula.conjunction_formula import (
    ConjunctionFormula,
)
from prototyping_inference_engine.api.formula.disjunction_formula import (
    DisjunctionFormula,
)
from prototyping_inference_engine.api.formula.existential_formula import (
    ExistentialFormula,
)
from prototyping_inference_engine.api.formula.formula import Formula
from prototyping_inference_engine.api.formula.negation_formula import NegationFormula
from prototyping_inference_engine.api.formula.universal_formula import UniversalFormula
from prototyping_inference_engine.api.ontology.rule.rule import Rule


@dataclass(frozen=True)
class RuleFragments:
    """Normalized fragments extracted from one PIE rule."""

    positive_body: FrozenAtomSet
    negative_body: FrozenAtomSet
    head_disjuncts: tuple[FrozenAtomSet, ...]
    all_head_atoms: FrozenAtomSet
    frontier: tuple[Variable, ...]
    existential_variables: frozenset[Variable]

    @property
    def is_positive(self) -> bool:
        return len(self.negative_body) == 0

    @property
    def has_disjunctive_head(self) -> bool:
        return len(self.head_disjuncts) > 1


def sort_variables(variables: Iterable[Variable]) -> tuple[Variable, ...]:
    return tuple(sorted(variables, key=str))


def extract_rule_fragments(rule: Rule) -> RuleFragments:
    positive_body = FrozenAtomSet(extract_positive_atoms(rule.body))
    negative_body = FrozenAtomSet(extract_negative_atoms(rule.body))
    head_disjuncts = tuple(
        FrozenAtomSet(extract_conjunctive_atoms(disjunct, allow_negation=False))
        for disjunct in split_disjunction(rule.head)
    )
    all_head_atoms = FrozenAtomSet(
        atom for disjunct in head_disjuncts for atom in disjunct
    )
    return RuleFragments(
        positive_body=positive_body,
        negative_body=negative_body,
        head_disjuncts=head_disjuncts,
        all_head_atoms=all_head_atoms,
        frontier=sort_variables(rule.frontier),
        existential_variables=frozenset(rule.existential_variables),
    )


def split_disjunction(formula: Formula) -> tuple[Formula, ...]:
    if isinstance(formula, (ExistentialFormula, UniversalFormula)):
        return split_disjunction(formula.inner)
    if isinstance(formula, DisjunctionFormula):
        return split_disjunction(formula.left) + split_disjunction(formula.right)
    return (formula,)


def extract_positive_atoms(formula: Formula) -> frozenset[Atom]:
    if isinstance(formula, Atom):
        return frozenset({formula})
    if isinstance(formula, DisjunctionFormula):
        raise ValueError("Disjunction is not allowed in rule bodies for analysis.")
    if isinstance(formula, ConjunctionFormula):
        return extract_positive_atoms(formula.left) | extract_positive_atoms(
            formula.right
        )
    if isinstance(formula, NegationFormula):
        return frozenset()
    if isinstance(formula, (ExistentialFormula, UniversalFormula)):
        return extract_positive_atoms(formula.inner)
    if isinstance(formula, BinaryFormula):
        return extract_positive_atoms(formula.left) | extract_positive_atoms(
            formula.right
        )
    raise TypeError(f"Unsupported formula type for positive atoms: {type(formula)}")


def extract_negative_atoms(formula: Formula) -> frozenset[Atom]:
    if isinstance(formula, NegationFormula):
        return extract_conjunctive_atoms(formula.inner, allow_negation=False)
    if isinstance(formula, DisjunctionFormula):
        raise ValueError("Disjunction is not allowed in rule bodies for analysis.")
    if isinstance(formula, ConjunctionFormula):
        return extract_negative_atoms(formula.left) | extract_negative_atoms(
            formula.right
        )
    if isinstance(formula, (ExistentialFormula, UniversalFormula)):
        return extract_negative_atoms(formula.inner)
    if isinstance(formula, Atom):
        return frozenset()
    if isinstance(formula, BinaryFormula):
        return extract_negative_atoms(formula.left) | extract_negative_atoms(
            formula.right
        )
    raise TypeError(f"Unsupported formula type for negative atoms: {type(formula)}")


def extract_conjunctive_atoms(
    formula: Formula,
    *,
    allow_negation: bool,
) -> frozenset[Atom]:
    if isinstance(formula, Atom):
        return frozenset({formula})
    if isinstance(formula, ConjunctionFormula):
        return extract_conjunctive_atoms(
            formula.left, allow_negation=allow_negation
        ) | extract_conjunctive_atoms(formula.right, allow_negation=allow_negation)
    if isinstance(formula, NegationFormula):
        if not allow_negation:
            raise ValueError("Negation is not allowed in this analysis fragment.")
        return extract_conjunctive_atoms(formula.inner, allow_negation=allow_negation)
    if isinstance(formula, (ExistentialFormula, UniversalFormula)):
        return extract_conjunctive_atoms(formula.inner, allow_negation=allow_negation)
    if isinstance(formula, DisjunctionFormula):
        raise ValueError("Disjunction is not allowed in a conjunctive fragment.")
    if isinstance(formula, BinaryFormula):
        return extract_conjunctive_atoms(
            formula.left, allow_negation=allow_negation
        ) | extract_conjunctive_atoms(formula.right, allow_negation=allow_negation)
    raise TypeError(f"Unsupported formula type: {type(formula)}")


def ensure_safe_negation(rule: Rule) -> None:
    positive_vars = {
        var for atom in extract_positive_atoms(rule.body) for var in atom.variables
    }
    negative_vars = {
        var for atom in extract_negative_atoms(rule.body) for var in atom.variables
    }
    if not negative_vars.issubset(positive_vars):
        raise ValueError("Negation is not safe: negative vars not in positive body.")
