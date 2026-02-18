"""Equivalent checker (restricted + local equivalence guard)."""

from __future__ import annotations

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.fact_base.fact_base import FactBase
from prototyping_inference_engine.api.formula.conjunction_formula import (
    ConjunctionFormula,
)
from prototyping_inference_engine.api.formula.formula import Formula
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_checker.restricted_checker import (
    RestrictedChecker,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_checker.trigger_checker import (
    TriggerChecker,
)
from prototyping_inference_engine.query_evaluation.evaluator.fo_query.fo_query_evaluators import (
    GenericFOQueryEvaluator,
)


class EquivalentChecker(TriggerChecker):
    def __init__(self, evaluator: GenericFOQueryEvaluator | None = None):
        self._evaluator = evaluator or GenericFOQueryEvaluator()
        self._restricted = RestrictedChecker()

    def check(
        self,
        rule: Rule,
        substitution: Substitution,
        read_write_data: FactBase,
    ) -> bool:
        if not self._restricted.check(rule, substitution, read_write_data):
            return False

        piece = _get_piece_in_fact_base(rule, substitution, read_write_data)
        if not piece:
            return True

        image_atoms = {substitution.apply(atom) for atom in rule.head.atoms}
        all_atoms = list(piece | image_atoms)
        formula: Formula = all_atoms[0]
        for atom in all_atoms[1:]:
            formula = ConjunctionFormula(formula, atom)
        query = FOQuery(formula, [])
        return not any(self._evaluator.evaluate(query, read_write_data))


def _get_piece_in_fact_base(
    rule: Rule,
    substitution: Substitution,
    read_write_data: FactBase,
) -> set[Atom]:
    pending: list[Variable] = []
    visited_vars: set[Variable] = set()
    result: set[Atom] = set()

    for variable in rule.frontier:
        image = substitution.apply(variable)
        if isinstance(image, Variable):
            pending.append(image)

    while pending:
        current = pending.pop()
        if current in visited_vars:
            continue
        visited_vars.add(current)

        for atom in read_write_data:
            if current not in atom.variables:
                continue
            if atom in result:
                continue
            result.add(atom)
            for atom_var in atom.variables:
                if atom_var not in visited_vars:
                    pending.append(atom_var)

    return result
