"""Default in-memory lineage tracker."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Set as AbstractSet

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.forward_chaining.chase.lineage.lineage_tracker import (
    LineageTracker,
)


class LineageTrackerImpl(LineageTracker):
    def __init__(self) -> None:
        self._lineage: dict[Atom, dict[Rule, dict[Substitution, set[Atom]]]] = (
            defaultdict(lambda: defaultdict(lambda: defaultdict(set)))
        )
        self._prime_atoms: set[Atom] = set()
        self._non_prime_atoms: set[Atom] = set()

    def get_ancestors_of(self, atom: Atom):
        return self._compute_ancestors(atom, return_only_prime=False)

    def get_prime_ancestors_of(self, atom: Atom):
        return self._compute_ancestors(atom, return_only_prime=True)

    def _compute_ancestors(self, atom: Atom, return_only_prime: bool):
        ancestors: set[Atom] = set()
        queue: list[Atom] = [atom]
        seen: set[Atom] = set()

        while queue:
            current = queue.pop()
            if current in seen:
                continue
            seen.add(current)
            for by_sub in self._lineage.get(current, {}).values():
                for body_facts in by_sub.values():
                    for ancestor in body_facts:
                        if ancestor in ancestors:
                            continue
                        if return_only_prime and self._lineage.get(ancestor):
                            queue.append(ancestor)
                            continue
                        ancestors.add(ancestor)
                        queue.append(ancestor)
        return ancestors

    def track(
        self,
        body_facts: AbstractSet[Atom],
        head_facts_possibly_new: AbstractSet[Atom],
        rule: Rule,
        substitution: Substitution,
    ) -> bool:
        for atom in body_facts:
            if atom not in self._non_prime_atoms:
                self._prime_atoms.add(atom)

        for atom in head_facts_possibly_new:
            if atom not in self._prime_atoms:
                self._non_prime_atoms.add(atom)

        added = False
        for head_atom in head_facts_possibly_new:
            before = len(self._lineage[head_atom][rule][substitution])
            self._lineage[head_atom][rule][substitution].update(body_facts)
            if len(self._lineage[head_atom][rule][substitution]) > before:
                added = True
        return added

    def get_rule_instances_yielding(self, atom: Atom):
        return self._lineage.get(atom, {})

    def is_prime(self, atom: Atom) -> bool:
        return atom in self._prime_atoms

    def is_non_prime(self, atom: Atom) -> bool:
        return atom in self._non_prime_atoms
