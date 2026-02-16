"""
Utilities for extracting GRD-specific rule fragments.
"""

from prototyping_inference_engine.api.atom.atom import Atom
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
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery


def split_head_disjuncts(rule: Rule) -> tuple[Formula, ...]:
    return tuple(_split_disjunction(rule.head))


def extract_positive_body(rule: Rule) -> ConjunctiveQuery:
    atoms = _extract_positive_atoms(rule.body)
    return ConjunctiveQuery(atoms, sorted(rule.frontier, key=str))


def extract_negative_body(rule: Rule) -> ConjunctiveQuery:
    atoms = _extract_negative_atoms(rule.body)
    if not atoms:
        return ConjunctiveQuery()
    return ConjunctiveQuery(atoms, sorted(rule.frontier, key=str))


def ensure_safe_negation(rule: Rule) -> None:
    positive_atoms = _extract_positive_atoms(rule.body)
    negative_atoms = _extract_negative_atoms(rule.body)
    positive_vars = {v for atom in positive_atoms for v in atom.variables}
    negative_vars = {v for atom in negative_atoms for v in atom.variables}
    if not negative_vars.issubset(positive_vars):
        raise ValueError("Negation is not safe: negative vars not in positive body.")


def extract_head_conjunction(formula: Formula) -> ConjunctiveQuery:
    atoms = _extract_conjunctive_atoms(formula, allow_negation=False)
    variables = {v for atom in atoms for v in atom.variables}
    return ConjunctiveQuery(atoms, sorted(variables, key=str))


def extract_head_disjunct_conjunctions(rule: Rule) -> tuple[ConjunctiveQuery, ...]:
    return tuple(
        extract_head_conjunction(disjunct) for disjunct in split_head_disjuncts(rule)
    )


def _split_disjunction(formula: Formula) -> list[Formula]:
    if isinstance(formula, DisjunctionFormula):
        return _split_disjunction(formula.left) + _split_disjunction(formula.right)
    return [formula]


def _extract_positive_atoms(formula: Formula) -> frozenset[Atom]:
    if isinstance(formula, Atom):
        return frozenset({formula})
    if isinstance(formula, DisjunctionFormula):
        raise ValueError("Disjunction is not allowed in GRD bodies.")
    if isinstance(formula, ConjunctionFormula):
        return _extract_positive_atoms(formula.left) | _extract_positive_atoms(
            formula.right
        )
    if isinstance(formula, NegationFormula):
        return frozenset()
    if isinstance(formula, (ExistentialFormula, UniversalFormula)):
        return _extract_positive_atoms(formula.inner)
    if isinstance(formula, BinaryFormula):
        return _extract_positive_atoms(formula.left) | _extract_positive_atoms(
            formula.right
        )
    raise ValueError(f"Unsupported formula type for positive body: {type(formula)}")


def _extract_negative_atoms(formula: Formula) -> frozenset[Atom]:
    if isinstance(formula, NegationFormula):
        return _extract_conjunctive_atoms(formula.inner, allow_negation=False)
    if isinstance(formula, DisjunctionFormula):
        raise ValueError("Disjunction is not allowed in GRD bodies.")
    if isinstance(formula, ConjunctionFormula):
        return _extract_negative_atoms(formula.left) | _extract_negative_atoms(
            formula.right
        )
    if isinstance(formula, (ExistentialFormula, UniversalFormula)):
        return _extract_negative_atoms(formula.inner)
    if isinstance(formula, Atom):
        return frozenset()
    if isinstance(formula, BinaryFormula):
        return _extract_negative_atoms(formula.left) | _extract_negative_atoms(
            formula.right
        )
    raise ValueError(f"Unsupported formula type for negative body: {type(formula)}")


def _extract_conjunctive_atoms(
    formula: Formula,
    *,
    allow_negation: bool,
) -> frozenset[Atom]:
    if isinstance(formula, Atom):
        return frozenset({formula})
    if isinstance(formula, ConjunctionFormula):
        return _extract_conjunctive_atoms(
            formula.left, allow_negation=allow_negation
        ) | _extract_conjunctive_atoms(formula.right, allow_negation=allow_negation)
    if isinstance(formula, NegationFormula):
        if not allow_negation:
            raise ValueError("Negation is not allowed in this fragment.")
        return _extract_conjunctive_atoms(formula.inner, allow_negation=allow_negation)
    if isinstance(formula, (ExistentialFormula, UniversalFormula)):
        return _extract_conjunctive_atoms(formula.inner, allow_negation=allow_negation)
    if isinstance(formula, DisjunctionFormula):
        raise ValueError("Disjunction is not allowed in a conjunction.")
    if isinstance(formula, BinaryFormula):
        return _extract_conjunctive_atoms(
            formula.left, allow_negation=allow_negation
        ) | _extract_conjunctive_atoms(formula.right, allow_negation=allow_negation)
    raise ValueError(f"Unsupported formula type: {type(formula)}")
