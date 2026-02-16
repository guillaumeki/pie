"""
Hierarchical rule compilation.
"""

# References:
# - "Query Rewriting for Existential Rules with Compiled Preorder." —
#   Mélanie König, Michel Leclère, Marie-Laure Mugnier.
#   Link: https://www.ijcai.org/Proceedings/15/Papers/195.pdf
#
# Summary:
# Hierarchical compilation is the restricted compiled preorder where body and
# head atoms are aligned position-wise by the same variables. This produces a
# simple predicate hierarchy that can be used to unfold and match atoms during
# rewriting and query evaluation.
#
# Properties used here:
# - Compatibility is defined by the transitive closure of the predicate order.
# - Unfolding substitutes a predicate by any compatible predicate.

from __future__ import annotations

from typing import Iterable

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.atom.term.term_partition import TermPartition
from prototyping_inference_engine.api.kb.rule_base import RuleBase
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.rule_compilation.api.rule_compilation import (
    RuleCompilation,
)
from prototyping_inference_engine.rule_compilation.api.rule_compilation_result import (
    RuleCompilationResult,
)
from prototyping_inference_engine.rule_compilation.validators import (
    extract_atomic_rule,
    rule_has_constants,
    rule_has_existentials,
)


def _merge_homomorphism_term(
    term_from: Term,
    term_to: Term,
    pre_sub: Substitution,
    homomorphism: Substitution,
) -> Substitution | None:
    from prototyping_inference_engine.api.atom.term.logical_function_term import (
        LogicalFunctionalTerm,
    )
    from prototyping_inference_engine.api.atom.term.evaluable_function_term import (
        EvaluableFunctionTerm,
    )

    if term_from.is_ground:
        return homomorphism if term_from == term_to else None

    if isinstance(term_from, Variable):
        if term_from in pre_sub:
            return homomorphism if pre_sub[term_from] == term_to else None
        if term_from in homomorphism:
            return homomorphism if homomorphism[term_from] == term_to else None
        homomorphism[term_from] = term_to
        return homomorphism

    if isinstance(term_from, LogicalFunctionalTerm):
        if not isinstance(term_to, LogicalFunctionalTerm):
            return None
        if term_from.name != term_to.name or len(term_from.args) != len(term_to.args):
            return None
        for arg_from, arg_to in zip(term_from.args, term_to.args):
            next_hom = _merge_homomorphism_term(arg_from, arg_to, pre_sub, homomorphism)
            if next_hom is None:
                return None
            homomorphism = next_hom
        return homomorphism

    if isinstance(term_from, EvaluableFunctionTerm):
        if not isinstance(term_to, EvaluableFunctionTerm):
            return None
        if term_from.name != term_to.name or len(term_from.args) != len(term_to.args):
            return None
        for arg_from, arg_to in zip(term_from.args, term_to.args):
            next_hom = _merge_homomorphism_term(arg_from, arg_to, pre_sub, homomorphism)
            if next_hom is None:
                return None
            homomorphism = next_hom
        return homomorphism

    return None


class HierarchicalRuleCompilation(RuleCompilation):
    """
    Compilation for rules of the form p(X, Y, ...) -> q(X, Y, ...), with
    no constants or existential variables and identical variables by position.
    """

    def __init__(self) -> None:
        self._order: dict[Predicate, set[Predicate]] = {}

    def compile(self, rule_base: RuleBase) -> None:
        compilable = self._extract_compilable(rule_base)
        self._compute_order(compilable)

    def compile_and_get(self, rule_base: RuleBase) -> RuleCompilationResult:
        original = list(rule_base.rules)
        compilable = self._extract_compilable(rule_base)
        non_compilable = [rule for rule in original if rule not in compilable]
        self._compute_order(compilable)
        return RuleCompilationResult(self, compilable, compilable, non_compilable)

    def is_more_specific_than(self, atom_a: Atom, atom_b: Atom) -> bool:
        if not self.is_compatible(atom_a.predicate, atom_b.predicate):
            return False
        return all(t1 == t2 for t1, t2 in zip(atom_a.terms, atom_b.terms))

    def unfold(self, atom: Atom) -> list[tuple[Atom, Substitution]]:
        result = [(atom, Substitution())]
        for pred in self.get_compatible_predicates(atom.predicate):
            if pred == atom.predicate:
                continue
            result.append((Atom(pred, *atom.terms), Substitution()))
        return result

    def is_compatible(self, pred_p: Predicate, pred_q: Predicate) -> bool:
        return pred_p == pred_q or pred_q in self._order.get(pred_p, set())

    def get_compatible_predicates(self, pred: Predicate) -> set[Predicate]:
        predicates = {pred}
        predicates.update(self._order.get(pred, set()))
        return predicates

    def get_homomorphisms_with_substitution(
        self, atom_a: Atom, atom_b: Atom, substitution: Substitution
    ) -> list[Substitution]:
        if not self.is_compatible(atom_a.predicate, atom_b.predicate):
            return []

        homomorphism = Substitution()
        for term_from, term_to in zip(atom_a.terms, atom_b.terms):
            next_hom = _merge_homomorphism_term(
                term_from, term_to, substitution, homomorphism
            )
            if next_hom is None:
                return []
            homomorphism = next_hom
        return [homomorphism]

    def get_unifications(self, atom_a: Atom, atom_b: Atom) -> set[TermPartition]:
        if not self.is_compatible(atom_b.predicate, atom_a.predicate):
            return set()
        partition = TermPartition()
        for term_a, term_b in zip(atom_a.terms, atom_b.terms):
            partition.union(term_a, term_b)
        return {partition}

    def _extract_compilable(self, rule_base: RuleBase) -> list[Rule]:
        compilable: list[Rule] = []
        to_remove: list[Rule] = []
        for rule in list(rule_base.rules):
            if self._is_compilable(rule):
                compilable.append(rule)
                to_remove.append(rule)
        for rule in to_remove:
            rule_base.remove_rule(rule)
        return compilable

    @staticmethod
    def _is_compilable(rule: Rule) -> bool:
        atoms = extract_atomic_rule(rule)
        if atoms is None:
            return False
        body, head = atoms
        if rule_has_existentials(rule):
            return False
        if rule_has_constants(rule):
            return False
        if len(body.terms) != len(head.terms):
            return False
        body_terms = list(body.terms)
        head_terms = list(head.terms)
        if len(set(body_terms)) != len(body_terms):
            return False
        for term_body, term_head in zip(body_terms, head_terms):
            if not isinstance(term_body, Variable):
                return False
            if term_body != term_head:
                return False
        return True

    def _compute_order(self, rules: Iterable[Rule]) -> None:
        for rule in rules:
            atoms = extract_atomic_rule(rule)
            if atoms is None:
                continue
            body, head = atoms
            body_pred = body.predicate
            head_pred = head.predicate
            self._order.setdefault(head_pred, set()).add(body_pred)
            self._update_transitive_closure(body_pred, head_pred)

    def _update_transitive_closure(
        self, body_pred: Predicate, head_pred: Predicate
    ) -> None:
        hierarchy_body = self._order.get(body_pred, set())
        hierarchy_head = self._order.get(head_pred, set())
        hierarchy_head.update(hierarchy_body)
        self._order[head_pred] = hierarchy_head

        for pred, hierarchy in list(self._order.items()):
            if head_pred in hierarchy:
                hierarchy.update(hierarchy_head)
                self._order[pred] = hierarchy
