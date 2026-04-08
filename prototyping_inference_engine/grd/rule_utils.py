"""
Utilities for extracting GRD-specific rule fragments.
"""

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.formula.formula import Formula
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.rule_analysis.fragments import (
    ensure_safe_negation as _ensure_safe_negation,
    extract_conjunctive_atoms,
    extract_negative_atoms,
    extract_positive_atoms,
    split_disjunction,
)


def split_head_disjuncts(rule: Rule) -> tuple[Formula, ...]:
    return split_disjunction(rule.head)


def extract_positive_body(rule: Rule) -> ConjunctiveQuery:
    atoms = _extract_positive_atoms(rule.body)
    return ConjunctiveQuery(atoms, sorted(rule.frontier, key=str))


def extract_negative_body(rule: Rule) -> ConjunctiveQuery:
    atoms = _extract_negative_atoms(rule.body)
    if not atoms:
        return ConjunctiveQuery()
    return ConjunctiveQuery(atoms, sorted(rule.frontier, key=str))


def ensure_safe_negation(rule: Rule) -> None:
    _ensure_safe_negation(rule)


def extract_head_conjunction(formula: Formula) -> ConjunctiveQuery:
    atoms = _extract_conjunctive_atoms(formula, allow_negation=False)
    variables = {v for atom in atoms for v in atom.variables}
    return ConjunctiveQuery(atoms, sorted(variables, key=str))


def extract_head_disjunct_conjunctions(rule: Rule) -> tuple[ConjunctiveQuery, ...]:
    return tuple(
        extract_head_conjunction(disjunct) for disjunct in split_head_disjuncts(rule)
    )


def _extract_positive_atoms(formula: Formula) -> frozenset[Atom]:
    try:
        return extract_positive_atoms(formula)
    except TypeError as exc:
        raise ValueError(str(exc)) from exc


def _extract_negative_atoms(formula: Formula) -> frozenset[Atom]:
    try:
        return extract_negative_atoms(formula)
    except TypeError as exc:
        raise ValueError(str(exc)) from exc


def _extract_conjunctive_atoms(
    formula: Formula,
    *,
    allow_negation: bool,
) -> frozenset[Atom]:
    try:
        return extract_conjunctive_atoms(formula, allow_negation=allow_negation)
    except TypeError as exc:
        raise ValueError(str(exc)) from exc
