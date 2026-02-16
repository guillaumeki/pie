"""
Validation helpers for rule compilation.
"""

from __future__ import annotations

from typing import Optional

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.formula.formula import Formula
from prototyping_inference_engine.api.ontology.rule.rule import Rule


def extract_single_atom(formula: Formula) -> Optional[Atom]:
    if isinstance(formula, Atom):
        return formula
    atoms = list(formula.atoms)
    if len(atoms) == 1:
        return atoms[0]
    return None


def is_atomic_rule(rule: Rule) -> bool:
    return (
        extract_single_atom(rule.body) is not None
        and extract_single_atom(rule.head) is not None
    )


def rule_has_constants(rule: Rule) -> bool:
    for atom in rule.body.atoms | rule.head.atoms:
        if any(isinstance(term, Constant) for term in atom.terms):
            return True
    return False


def rule_has_existentials(rule: Rule) -> bool:
    return bool(rule.existential_variables)


def extract_atomic_rule(rule: Rule) -> Optional[tuple[Atom, Atom]]:
    body_atom = extract_single_atom(rule.body)
    if body_atom is None:
        return None
    head_atom = extract_single_atom(rule.head)
    if head_atom is None:
        return None
    return body_atom, head_atom
