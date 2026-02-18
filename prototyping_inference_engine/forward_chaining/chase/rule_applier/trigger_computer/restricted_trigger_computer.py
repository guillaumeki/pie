"""Restricted trigger computer: evaluate body + not(head) style equivalent by rule."""

from __future__ import annotations

from collections.abc import Collection, Iterable

from prototyping_inference_engine.api.formula.conjunction_formula import (
    ConjunctionFormula,
)
from prototyping_inference_engine.api.formula.negation_formula import NegationFormula
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.forward_chaining.chase.chase import Chase
from prototyping_inference_engine.forward_chaining.chase.data.chasable_data import (
    ChasableData,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_computer.trigger_computer import (
    TriggerComputer,
)
from prototyping_inference_engine.query_evaluation.evaluator.fo_query.fo_query_evaluators import (
    GenericFOQueryEvaluator,
)


class RestrictedTriggerComputer(TriggerComputer):
    def __init__(self, evaluator: GenericFOQueryEvaluator | None = None):
        self._evaluator = evaluator or GenericFOQueryEvaluator()

    def init(self, chase: Chase) -> None:
        return None

    def compute(
        self,
        body: FOQuery,
        rules: Collection[Rule],
        chasable_data: ChasableData,
    ) -> Iterable[Substitution]:
        data = chasable_data.get_all_readable_data()
        for rule in rules:
            query_formula = ConjunctionFormula(rule.body, NegationFormula(rule.head))
            query = FOQuery(query_formula, sorted(rule.body.free_variables, key=str))
            yield from self._evaluator.evaluate(query, data)
