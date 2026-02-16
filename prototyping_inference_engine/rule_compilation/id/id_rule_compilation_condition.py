"""
ID rule compilation condition.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.atom.term.term_partition import TermPartition
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.rule_compilation.api.rule_compilation_condition import (
    RuleCompilationCondition,
)
from prototyping_inference_engine.utils.partition import Partition


def _merge_substitutions(
    left: Substitution, right: Substitution
) -> Optional[Substitution]:
    merged = Substitution(left)
    for var, term in right.items():
        if var in merged and merged[var] != term:
            return None
        merged[var] = term
    return merged


def _term_homomorphism(
    term_from: Term,
    term_to: Term,
    pre_sub: Substitution,
    homomorphism: Substitution,
) -> Optional[Substitution]:
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
            next_hom = _term_homomorphism(arg_from, arg_to, pre_sub, homomorphism)
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
            next_hom = _term_homomorphism(arg_from, arg_to, pre_sub, homomorphism)
            if next_hom is None:
                return None
            homomorphism = next_hom
        return homomorphism

    return None


@dataclass(frozen=True)
class IDRuleCompilationCondition(RuleCompilationCondition):
    cond_body: tuple[int, ...]
    cond_head: tuple[int, ...]

    @classmethod
    def from_terms(
        cls, body: Iterable[Term], head: Iterable[Term]
    ) -> "IDRuleCompilationCondition":
        body_terms = list(body)
        head_terms = list(head)

        cond_body = [-1] * len(body_terms)
        var_index = -1
        for i, term in enumerate(body_terms):
            for j in range(i):
                if term == body_terms[j]:
                    cond_body[i] = cond_body[j]
                    break
            if cond_body[i] == -1:
                var_index += 1
                cond_body[i] = var_index

        cond_head = [0] * len(head_terms)
        for j, term in enumerate(head_terms):
            found = False
            for i, body_term in enumerate(body_terms):
                if term == body_term:
                    found = True
                    cond_head[j] = cond_body[i]
                    break
            if not found:
                raise ValueError("Head term not present in body for ID condition.")

        return cls(tuple(cond_body), tuple(cond_head))

    def check(self, atom_body: Atom, atom_head: Atom) -> bool:
        body = list(atom_body.terms)
        head = list(atom_head.terms)

        if len(body) != len(self.cond_body) or len(head) != len(self.cond_head):
            return False

        check: list[Optional[Term]] = [None] * len(body)
        for index, class_id in enumerate(self.cond_body):
            if check[class_id] is None:
                check[class_id] = body[index]
            elif body[index] != check[class_id]:
                return False

        for index, class_id in enumerate(self.cond_head):
            if head[index] != check[class_id]:
                return False

        return True

    def instantiate(
        self, head_terms: Iterable[Term]
    ) -> Optional[tuple[list[Term], Substitution]]:
        terms = list(head_terms)
        if len(terms) != len(self.cond_head):
            return None

        substitution = Substitution()
        to_remove: set[Variable] = set()
        fresh_vars: dict[int, Variable] = {}

        for index, class_id in enumerate(self.cond_head):
            fresh = fresh_vars.get(class_id, Variable.fresh_variable())
            fresh_vars[class_id] = fresh
            to_remove.add(fresh)

            merged = _merge_substitutions(
                substitution, Substitution({fresh: terms[index]})
            )
            if merged is None:
                return None
            substitution = merged

        body_terms: list[Term] = []
        for class_id in self.cond_body:
            fresh = fresh_vars.get(class_id, Variable.fresh_variable())
            fresh_vars[class_id] = fresh
            to_remove.add(fresh)
            body_terms.append(substitution.apply(fresh))

        for var in to_remove:
            if var in substitution:
                del substitution[var]

        return body_terms, substitution

    def compose_with(
        self, other: RuleCompilationCondition
    ) -> Optional["IDRuleCompilationCondition"]:
        if not isinstance(other, IDRuleCompilationCondition):
            return None

        partition: Partition[int] = Partition()
        for i, class_id in enumerate(self.cond_head):
            partition.union(class_id * 2, other.cond_body[i] * 2 + 1)

        new_cond_body: list[int] = []
        for class_id in self.cond_body:
            new_cond_body.append(partition.get_representative(class_id * 2))

        new_cond_head: list[int] = []
        for class_id in other.cond_head:
            new_cond_head.append(partition.get_representative(class_id * 2 + 1))

        mapping: dict[int, int] = {}
        next_id = -1

        for i, class_id in enumerate(new_cond_body):
            if class_id not in mapping:
                next_id += 1
                mapping[class_id] = next_id
            new_cond_body[i] = mapping[class_id]

        for i, class_id in enumerate(new_cond_head):
            if class_id not in mapping:
                next_id += 1
                mapping[class_id] = next_id
            new_cond_head[i] = mapping[class_id]

        return IDRuleCompilationCondition(tuple(new_cond_body), tuple(new_cond_head))

    def is_identity(self) -> bool:
        return self.cond_body == self.cond_head

    def homomorphism(
        self,
        head_terms: Iterable[Term],
        to_terms: Iterable[Term],
        initial_substitution: Substitution,
    ) -> Optional[Substitution]:
        instantiation = self.instantiate(head_terms)
        if instantiation is None:
            return None
        generated_body, specialization = instantiation
        to_terms_list = list(to_terms)
        if len(generated_body) != len(to_terms_list):
            return None

        homomorphism = Substitution()
        for term_from, term_to in zip(generated_body, to_terms_list):
            next_hom = _term_homomorphism(
                term_from, term_to, initial_substitution, homomorphism
            )
            if next_hom is None:
                return None
            homomorphism = next_hom

        for var, term in specialization.items():
            homomorphism[var] = homomorphism.apply(term)

        return homomorphism

    def unifier(self, atom_body: Atom, atom_head: Atom) -> TermPartition:
        body = list(atom_body.terms)
        head = list(atom_head.terms)
        partition = TermPartition()
        mapping: list[Optional[Term]] = [None] * len(body)

        for index, class_id in enumerate(self.cond_body):
            term = body[index]
            if mapping[class_id] is None:
                mapping[class_id] = term
            else:
                representative = mapping[class_id]
                if representative is None:
                    continue
                partition.add_class({representative, term})

        for index, class_id in enumerate(self.cond_head):
            term = head[index]
            representative = mapping[class_id]
            if representative is None:
                continue
            partition.add_class({representative, term})

        return partition
