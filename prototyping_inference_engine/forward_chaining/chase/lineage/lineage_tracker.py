"""Lineage tracking abstractions for forward chaining."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Collection, Mapping, Set

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.substitution.substitution import Substitution


class LineageTracker(ABC):
    @abstractmethod
    def get_ancestors_of(self, atom: Atom) -> Collection[Atom]: ...

    @abstractmethod
    def get_prime_ancestors_of(self, atom: Atom) -> Collection[Atom]: ...

    @abstractmethod
    def track(
        self,
        body_facts: Set[Atom],
        head_facts_possibly_new: Set[Atom],
        rule: Rule,
        substitution: Substitution,
    ) -> bool: ...

    @abstractmethod
    def get_rule_instances_yielding(
        self,
        atom: Atom,
    ) -> Mapping[Rule, Mapping[Substitution, Set[Atom]]]: ...

    @abstractmethod
    def is_prime(self, atom: Atom) -> bool: ...

    @abstractmethod
    def is_non_prime(self, atom: Atom) -> bool: ...
