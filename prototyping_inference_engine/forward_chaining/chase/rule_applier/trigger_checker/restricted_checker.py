"""Restricted checker."""

from __future__ import annotations

from prototyping_inference_engine.api.fact_base.fact_base import FactBase
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_checker.semi_oblivious_checker import (
    SemiObliviousChecker,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_checker.trigger_checker import (
    TriggerChecker,
)


class RestrictedChecker(TriggerChecker):
    def __init__(self) -> None:
        self._semi = SemiObliviousChecker()

    def check(
        self,
        rule: Rule,
        substitution: Substitution,
        read_write_data: FactBase,
    ) -> bool:
        if not self._semi.check(rule, substitution, read_write_data):
            return False

        if not rule.existential_variables:
            return True

        for atom in rule.head.atoms:
            image_atom = substitution.apply(atom)
            if image_atom not in read_write_data:
                return True
        return False
