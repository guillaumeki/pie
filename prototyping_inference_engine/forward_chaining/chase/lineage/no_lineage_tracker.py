"""No-op lineage tracker."""

from __future__ import annotations

from collections.abc import Set as AbstractSet

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.forward_chaining.chase.lineage.lineage_tracker import (
    LineageTracker,
)


class NoLineageTracker(LineageTracker):
    def get_ancestors_of(self, atom: Atom):
        return set()

    def get_prime_ancestors_of(self, atom: Atom):
        return set()

    def track(
        self,
        body_facts: AbstractSet[Atom],
        head_facts_possibly_new: AbstractSet[Atom],
        rule: Rule,
        substitution: Substitution,
    ) -> bool:
        return False

    def get_rule_instances_yielding(self, atom: Atom):
        return {}

    def is_prime(self, atom: Atom) -> bool:
        return False

    def is_non_prime(self, atom: Atom) -> bool:
        return False
