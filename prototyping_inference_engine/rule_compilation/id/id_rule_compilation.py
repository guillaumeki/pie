"""
ID rule compilation (Integraal/Graal style).
"""

# References:
# - "Query Rewriting for Existential Rules with Compiled Preorder." —
#   Mélanie König, Michel Leclère, Marie-Laure Mugnier.
#   Link: https://www.ijcai.org/Proceedings/15/Papers/195.pdf
#
# Summary:
# The compiled preorder encodes when an atom predicate can be replaced by
# another through a compilation of simple rules. ID compilation stores
# conditions between predicates and saturates them by composition, enabling
# unfolding and compatibility checks during rewriting and query evaluation.
#
# Properties used here:
# - Conditions capture admissible substitutions between body/head atoms.
# - Saturation by composition yields a transitive closure of compatible
#   predicates and conditions.

from __future__ import annotations

from typing import Iterable

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.kb.rule_base import RuleBase
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.rule_compilation.api.rule_compilation import (
    RuleCompilation,
)
from prototyping_inference_engine.rule_compilation.api.rule_compilation_condition import (
    RuleCompilationCondition,
)
from prototyping_inference_engine.rule_compilation.api.rule_compilation_result import (
    RuleCompilationResult,
)
from prototyping_inference_engine.rule_compilation.id.id_rule_compilation_condition import (
    IDRuleCompilationCondition,
)
from prototyping_inference_engine.rule_compilation.validators import (
    extract_atomic_rule,
    rule_has_constants,
    rule_has_existentials,
)


class IDRuleCompilation(RuleCompilation):
    """
    Compilation for atomic rules (body and head) without existentials or constants.
    """

    def __init__(self) -> None:
        self._conditions: dict[
            Predicate, dict[Predicate, list[RuleCompilationCondition]]
        ] = {}

    def compile(self, rule_base: RuleBase) -> None:
        compilable = self._extract_compilable(rule_base)
        self._create_id_conditions(compilable)
        self._compute_saturation()

    def compile_and_get(self, rule_base: RuleBase) -> RuleCompilationResult:
        original = list(rule_base.rules)
        compilable = self._extract_compilable(rule_base)
        non_compilable = [rule for rule in original if rule not in compilable]
        self._create_id_conditions(compilable)
        self._compute_saturation()
        return RuleCompilationResult(self, compilable, compilable, non_compilable)

    def is_more_specific_than(self, atom_a: Atom, atom_b: Atom) -> bool:
        for condition in self._get_conditions(atom_a.predicate, atom_b.predicate):
            if condition.check(atom_a, atom_b):
                return True
        return False

    def unfold(self, atom: Atom) -> list[tuple[Atom, Substitution]]:
        result: list[tuple[Atom, Substitution]] = [(atom, Substitution())]
        cond_head = self._conditions.get(atom.predicate)
        if cond_head is None:
            return result
        for pred_body, conditions in cond_head.items():
            for cond in conditions:
                instantiated = cond.instantiate(atom.terms)
                if instantiated is None:
                    continue
                body_terms, substitution = instantiated
                result.append((Atom(pred_body, *body_terms), substitution))
        return result

    def is_compatible(self, pred_p: Predicate, pred_q: Predicate) -> bool:
        if pred_p == pred_q:
            return True
        return bool(self._get_conditions(pred_p, pred_q))

    def get_compatible_predicates(self, pred: Predicate) -> set[Predicate]:
        predicates = {pred}
        cond_head = self._conditions.get(pred)
        if cond_head:
            predicates.update(cond_head.keys())
        return predicates

    def get_homomorphisms_with_substitution(
        self, atom_a: Atom, atom_b: Atom, substitution: Substitution
    ) -> list[Substitution]:
        result: list[Substitution] = []
        for condition in self._get_conditions(atom_b.predicate, atom_a.predicate):
            homomorphism = condition.homomorphism(
                atom_a.terms, atom_b.terms, substitution
            )
            if homomorphism is not None:
                if homomorphism not in result:
                    result.append(homomorphism)
        return result

    def get_unifications(self, atom_a: Atom, atom_b: Atom):
        result = set()
        for condition in self._get_conditions(atom_a.predicate, atom_b.predicate):
            unifier = condition.unifier(atom_a, atom_b)
            if unifier is not None:
                result.add(unifier)
        return result

    def _add_condition(
        self, pred_body: Predicate, pred_head: Predicate, cond: RuleCompilationCondition
    ) -> bool:
        cond_head = self._conditions.setdefault(pred_head, {})
        conditions = cond_head.setdefault(pred_body, [])
        if cond in conditions:
            return False
        conditions.append(cond)
        return True

    def _get_conditions(
        self, pred_body: Predicate, pred_head: Predicate
    ) -> list[RuleCompilationCondition]:
        result: list[RuleCompilationCondition] = []
        if pred_body == pred_head:
            variables = [Variable.fresh_variable() for _ in range(pred_body.arity)]
            result.append(IDRuleCompilationCondition.from_terms(variables, variables))
        cond_head = self._conditions.get(pred_head)
        if cond_head:
            cond_body = cond_head.get(pred_body)
            if cond_body:
                result.extend(cond_body)
        return result

    def _create_id_conditions(self, rules: Iterable[Rule]) -> None:
        for rule in rules:
            atoms = extract_atomic_rule(rule)
            if atoms is None:
                continue
            body, head = atoms
            condition = IDRuleCompilationCondition.from_terms(body.terms, head.terms)
            self._add_condition(body.predicate, head.predicate, condition)

    def _compute_saturation(self) -> None:
        conditions_tmp: dict[
            Predicate, dict[Predicate, list[RuleCompilationCondition]]
        ] = {
            pred_head: {
                pred_body: list(conds) for pred_body, conds in cond_head.items()
            }
            for pred_head, cond_head in self._conditions.items()
        }

        for pred_q, cond_head in conditions_tmp.items():
            for pred_p, conditions in cond_head.items():
                for condition_pq in conditions:
                    self._compute_saturation_step(
                        conditions_tmp, pred_p, pred_q, condition_pq
                    )

    def _compute_saturation_step(
        self,
        conditions_tmp: dict[
            Predicate, dict[Predicate, list[RuleCompilationCondition]]
        ],
        pred_p: Predicate,
        pred_q: Predicate,
        condition_pq: RuleCompilationCondition,
    ) -> None:
        cond_head = conditions_tmp.get(pred_p)
        if not cond_head:
            return
        for pred_r, conditions in cond_head.items():
            for condition_rp in conditions:
                condition_rq = condition_rp.compose_with(condition_pq)
                if condition_rq is None:
                    continue
                if pred_r == pred_q and condition_rq.is_identity():
                    continue
                if self._add_condition(pred_r, pred_q, condition_rq):
                    self._compute_saturation_step(
                        conditions_tmp, pred_r, pred_q, condition_rq
                    )

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
        if rule_has_existentials(rule):
            return False
        if rule_has_constants(rule):
            return False
        return True
