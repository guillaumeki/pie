"""Parallel-trigger rule applier (collect inferred facts for end-of-step merge)."""

from __future__ import annotations

from collections.abc import Collection

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.forward_chaining.chase.data.chasable_data import (
    ChasableData,
)
from prototyping_inference_engine.forward_chaining.chase.rule_application_step_result import (
    RuleApplicationStepResult,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.abstract_rule_applier import (
    AbstractRuleApplier,
)


class ParallelTriggerRuleApplier(AbstractRuleApplier):
    def apply(
        self,
        rules: Collection[Rule],
        chasable_data: ChasableData,
    ) -> RuleApplicationStepResult:
        rules_by_body = self.group_rules_by_body_query(rules)
        applied_rules: set[Rule] = set()
        created_facts: set[Atom] = set()

        for body, grouped_rules in rules_by_body.items():
            substitutions = self.computer.compute(body, grouped_rules, chasable_data)
            for substitution in substitutions:
                for rule in grouped_rules:
                    if not self.checker.check(
                        rule,
                        substitution,
                        chasable_data.get_writing_target(),
                    ):
                        continue
                    application = self.applier.apply(
                        rule,
                        substitution,
                        chasable_data.get_writing_target(),
                    )
                    if application is None:
                        continue
                    applied_rules.add(rule)
                    created_facts.update(application.atoms)

        return RuleApplicationStepResult.from_created(applied_rules, created_facts)
