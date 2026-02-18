"""Multi-threaded rule applier with workers per grouped body."""

from __future__ import annotations

from collections.abc import Collection
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

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


class MultiThreadRuleApplier(AbstractRuleApplier):
    def apply(
        self,
        rules: Collection[Rule],
        chasable_data: ChasableData,
    ) -> RuleApplicationStepResult:
        rules_by_body = self.group_rules_by_body_query(rules)
        applied_rules: set[Rule] = set()
        created_facts: set[Atom] = set()
        lock = Lock()

        def process_one_body(body, grouped_rules: list[Rule]) -> None:
            local_applied: set[Rule] = set()
            local_created: set[Atom] = set()
            for substitution in self.computer.compute(
                body, grouped_rules, chasable_data
            ):
                for rule in grouped_rules:
                    if not self.checker.check(
                        rule,
                        substitution,
                        chasable_data.get_writing_target(),
                    ):
                        continue
                    with lock:
                        application = self.applier.apply(
                            rule,
                            substitution,
                            chasable_data.get_writing_target(),
                        )
                    if application is None:
                        continue
                    local_applied.add(rule)
                    local_created.update(application.atoms)
            with lock:
                applied_rules.update(local_applied)
                created_facts.update(local_created)

        max_workers = min(32, max(1, len(rules_by_body)))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(process_one_body, body, grouped_rules)
                for body, grouped_rules in rules_by_body.items()
            ]
            for future in futures:
                future.result()

        return RuleApplicationStepResult.from_created(applied_rules, created_facts)
