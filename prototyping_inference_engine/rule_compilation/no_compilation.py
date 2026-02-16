"""
Null object for rule compilation.
"""

from __future__ import annotations

from typing import Set

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.term_partition import TermPartition
from prototyping_inference_engine.api.kb.rule_base import RuleBase
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.rule_compilation.api.rule_compilation import (
    RuleCompilation,
)
from prototyping_inference_engine.rule_compilation.api.rule_compilation_result import (
    RuleCompilationResult,
)


class NoCompilation(RuleCompilation):
    """Compilation that performs no transformation."""

    def compile(self, rule_base: RuleBase) -> None:
        return None

    def compile_and_get(self, rule_base: RuleBase) -> RuleCompilationResult:
        rules = list(rule_base.rules)
        return RuleCompilationResult(self, rules, [], rules)

    def is_more_specific_than(self, atom_a: Atom, atom_b: Atom) -> bool:
        return atom_a == atom_b

    def unfold(self, atom: Atom) -> list[tuple[Atom, Substitution]]:
        return [(atom, Substitution())]

    def is_compatible(self, pred_p: Predicate, pred_q: Predicate) -> bool:
        return pred_p == pred_q

    def get_compatible_predicates(self, pred: Predicate) -> Set[Predicate]:
        return {pred}

    def get_homomorphisms_with_substitution(
        self, atom_a: Atom, atom_b: Atom, substitution: Substitution
    ) -> list[Substitution]:
        from prototyping_inference_engine.api.atom.atom_operations import specialize

        spec = specialize(atom_a, atom_b, substitution)
        if spec is None:
            return []
        return [spec]

    def get_unifications(self, atom_a: Atom, atom_b: Atom) -> set[TermPartition]:
        if atom_a.predicate != atom_b.predicate:
            return set()
        partition = TermPartition()
        for term_a, term_b in zip(atom_a.terms, atom_b.terms):
            partition.union(term_a, term_b)
        return {partition}
