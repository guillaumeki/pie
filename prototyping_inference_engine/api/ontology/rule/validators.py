"""
Validators and converters for rule fragments.
"""

from dataclasses import dataclass
from typing import Iterable

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.term.variable import Variable
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


@dataclass(frozen=True)
class ValidatedConjunctiveRule:
    rule: Rule
    body: ConjunctiveQuery
    head: ConjunctiveQuery


@dataclass(frozen=True)
class ValidatedDisjunctiveRule:
    rule: Rule
    body: ConjunctiveQuery
    head_disjuncts: tuple[ConjunctiveQuery, ...]


def ensure_conjunctive_rule(rule: Rule) -> ValidatedConjunctiveRule:
    disjuncts = _split_disjunction(rule.head)
    if len(disjuncts) != 1:
        raise ValueError("Rule head must be a single conjunctive formula.")
    body_cq = _formula_to_conjunctive_query(
        rule.body, rule.frontier, allow_universal=True, allow_existential=False
    )
    head_cq = _formula_to_conjunctive_query(
        disjuncts[0], rule.frontier, allow_universal=False, allow_existential=True
    )
    return ValidatedConjunctiveRule(rule=rule, body=body_cq, head=head_cq)


def ensure_ed_rule(rule: Rule) -> ValidatedDisjunctiveRule:
    body_cq = _formula_to_conjunctive_query(
        rule.body, rule.frontier, allow_universal=True, allow_existential=False
    )
    head_disjuncts = tuple(
        _formula_to_conjunctive_query(
            disjunct, rule.frontier, allow_universal=False, allow_existential=True
        )
        for disjunct in _split_disjunction(rule.head)
    )
    return ValidatedDisjunctiveRule(
        rule=rule, body=body_cq, head_disjuncts=head_disjuncts
    )


def _formula_to_conjunctive_query(
    formula: Formula,
    frontier: Iterable[Variable],
    *,
    allow_universal: bool,
    allow_existential: bool,
) -> ConjunctiveQuery:
    atoms = _extract_conjunctive_atoms(
        formula,
        allow_universal=allow_universal,
        allow_existential=allow_existential,
    )
    frontier_set = set(frontier)
    atom_vars = _collect_atom_variables(atoms)
    answer_variables = tuple(sorted(frontier_set & atom_vars, key=str))
    return ConjunctiveQuery(atoms, answer_variables)


def _extract_conjunctive_atoms(
    formula: Formula,
    *,
    allow_universal: bool,
    allow_existential: bool,
) -> frozenset[Atom]:
    if isinstance(formula, Atom):
        return frozenset({formula})
    if isinstance(formula, ConjunctionFormula):
        return _extract_conjunctive_atoms(
            formula.left,
            allow_universal=allow_universal,
            allow_existential=allow_existential,
        ) | _extract_conjunctive_atoms(
            formula.right,
            allow_universal=allow_universal,
            allow_existential=allow_existential,
        )
    if isinstance(formula, UniversalFormula):
        if not allow_universal:
            raise ValueError("Universal quantifier not allowed in this rule fragment.")
        return _extract_conjunctive_atoms(
            formula.inner,
            allow_universal=allow_universal,
            allow_existential=allow_existential,
        )
    if isinstance(formula, ExistentialFormula):
        if not allow_existential:
            raise ValueError(
                "Existential quantifier not allowed in this rule fragment."
            )
        return _extract_conjunctive_atoms(
            formula.inner,
            allow_universal=allow_universal,
            allow_existential=allow_existential,
        )
    if isinstance(formula, (DisjunctionFormula, NegationFormula)):
        raise ValueError("Disjunction/negation not allowed in this rule fragment.")
    raise ValueError(f"Unsupported formula type: {type(formula)}")


def _split_disjunction(formula: Formula) -> list[Formula]:
    if isinstance(formula, DisjunctionFormula):
        return _split_disjunction(formula.left) + _split_disjunction(formula.right)
    return [formula]


def _collect_atom_variables(atoms: Iterable[Atom]) -> set[Variable]:
    variables: set[Variable] = set()
    for atom in atoms:
        variables.update(atom.variables)
    return variables
