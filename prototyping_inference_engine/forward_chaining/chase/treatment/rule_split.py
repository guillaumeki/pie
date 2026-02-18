"""Pretreatment splitting rules into single-piece head rules."""

from __future__ import annotations

from prototyping_inference_engine.api.kb.rule_base import RuleBase
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.formula.universal_formula import UniversalFormula
from prototyping_inference_engine.forward_chaining.chase.chase import Chase
from prototyping_inference_engine.forward_chaining.chase.formula_utils import (
    split_disjunction_formulas,
    split_into_single_piece_heads,
)
from prototyping_inference_engine.forward_chaining.chase.treatment.pretreatment import (
    Pretreatment,
)


class RuleSplit(Pretreatment):
    def __init__(self) -> None:
        self._chase: Chase | None = None

    def init(self, chase: Chase) -> None:
        self._chase = chase

    def apply(self) -> None:
        if self._chase is None:
            return

        new_rules: set[Rule] = set()
        for rule in self._chase.get_rule_base().rules:
            for disjunct in split_disjunction_formulas(rule.head):
                for piece in split_into_single_piece_heads(disjunct):
                    body = rule.body
                    missing = body.free_variables - piece.free_variables
                    for var in sorted(missing, key=str):
                        body = UniversalFormula(var, body)
                    new_rules.add(Rule(body, piece, rule.label))

        self._chase.set_rule_base(
            RuleBase(new_rules, self._chase.get_rule_base().negative_constraints)
        )
