"""Rule scheduler based on body predicates."""

from __future__ import annotations

from collections.abc import Collection

from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.kb.rule_base import RuleBase
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.grd.rule_utils import (
    extract_negative_body,
    extract_positive_body,
)
from prototyping_inference_engine.forward_chaining.chase.rule_scheduler.rule_scheduler import (
    RuleScheduler,
)


class ByPredicateScheduler(RuleScheduler):
    def __init__(self, rule_base: RuleBase | None = None) -> None:
        self._rule_base: RuleBase | None = None
        self._by_body_predicate: dict[Predicate, set[Rule]] = {}
        if rule_base is not None:
            self.init(rule_base)

    def init(self, rule_base: RuleBase) -> None:
        self._rule_base = rule_base
        self._by_body_predicate = {}
        for rule in rule_base.rules:
            body_preds = (
                extract_positive_body(rule).atoms.predicates
                | extract_negative_body(rule).atoms.predicates
            )
            for predicate in body_preds:
                self._by_body_predicate.setdefault(predicate, set()).add(rule)

    def get_rules_to_apply(
        self,
        last_applied_rules: Collection[Rule] | None,
    ) -> Collection[Rule]:
        if self._rule_base is None:
            return []
        if last_applied_rules is None:
            return set(self._rule_base.rules)

        to_apply: set[Rule] = set()
        for rule in last_applied_rules:
            for head_disjunct in rule.head_disjuncts:
                for atom in head_disjunct.atoms:
                    to_apply.update(self._by_body_predicate.get(atom.predicate, set()))
        return to_apply
