from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, Optional

from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.term_partition import TermPartition
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.query.union_conjunctive_queries import UnionConjunctiveQueries
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.backward_chaining.unifier.disjunctive_piece_unifier import DisjunctivePieceUnifier
from prototyping_inference_engine.backward_chaining.unifier.piece_unifier import PieceUnifier
from prototyping_inference_engine.backward_chaining.unifier.piece_unifier_algorithm import PieceUnifierAlgorithm


@dataclass
class _PartialDisjunctivePieceUnifier:
    rule: Rule[ConjunctiveQuery, ConjunctiveQuery]
    piece_unifiers: list[Optional[PieceUnifier]]
    cqs: list[Optional[ConjunctiveQuery]]
    answer_variables: tuple[Variable]

    def to_disjunctive_piece_unifier(self):
        return DisjunctivePieceUnifier(self.rule,
                                       tuple(self.piece_unifiers),
                                       UnionConjunctiveQueries(self.cqs, self.answer_variables))

    @property
    def partial_associated_partition(self):
        it = iter(self.piece_unifiers)
        first = next(it)
        while not first:
            first = next(it)
        part = TermPartition(first.partition)

        for p in it:
            if p:
                part.join(p.partition)

        return part

    def partial_frontier_instantiation(self, head_number: int) -> tuple[Optional[Constant], ...]:
        instantiation = []
        for v in self.rule.head_frontier(head_number):
            representative = self.partial_associated_partition.get_representative(v)
            if isinstance(representative, Constant):
                instantiation.append(representative)
            else:
                instantiation.append(None)
        return tuple(instantiation)


class DisjunctivePieceUnifierAlgorithm:
    def __init__(self):
        # The previous piece unifiers are a dict from a rule, to a list in which indices are the number of the heads
        # and contains dictionaries from a CQ unified with the head to another dictionary where the keys are
        # instantiation of the frontier with constants and the values are the corresponding piece unifiers
        self._previous_piece_unifiers: \
            defaultdict[ConjunctiveQuery, defaultdict[Rule[ConjunctiveQuery, ConjunctiveQuery],
                defaultdict[defaultdict[tuple[Optional[Constant], ...], list[PieceUnifier]]]]] \
            = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))
        self._has_unifiers: dict[Rule, list[bool]] = {}

    def compute_disjunctive_unifiers(self,
                                     all_cqs: UnionConjunctiveQueries,
                                     new_cqs: UnionConjunctiveQueries,
                                     rule: Rule[ConjunctiveQuery, ConjunctiveQuery]) -> set[DisjunctivePieceUnifier]:
        for cq in (self._previous_piece_unifiers.keys() - all_cqs):
            del self._previous_piece_unifiers[cq]
        result = set()
        if rule not in self._has_unifiers:
            self._has_unifiers[rule] = [False] * len(rule.head)
        for i, h in enumerate(rule.head):
            fpus = DisjunctivePieceUnifierAlgorithm._compute_full_unifiers_of_a_ucq(rule, i, new_cqs)
            if fpus and not self._has_unifiers[rule][i]:
                self._has_unifiers[rule][i] = True
            if all(self._has_unifiers[rule]):
                pieces_unifiers = [None] * len(rule.head)
                cqs = [None] * len(rule.head)
                for fpu, cq in fpus:
                    pieces_unifiers[i] = fpu
                    cqs[i] = fpu.query
                    pdpu = _PartialDisjunctivePieceUnifier(rule, pieces_unifiers[:], cqs[:], new_cqs.answer_variables)
                    self._extend(rule, i, pdpu, result)
            for fpu, cq in fpus:
                self._previous_piece_unifiers[cq][rule][i][fpu.frontier_instantiation].append(fpu)
        return result

    def _extend(self,
                rule: Rule[ConjunctiveQuery, ConjunctiveQuery],
                head_number: int,
                pdpu: _PartialDisjunctivePieceUnifier,
                result: set[DisjunctivePieceUnifier],
                i: int = 0):
        if i == len(rule.head):
            result.add(pdpu.to_disjunctive_piece_unifier())
        elif i != head_number:
            for q in self._previous_piece_unifiers:
                for instantiation, unifiers in self._previous_piece_unifiers[q][rule][i].items():
                    if DisjunctivePieceUnifierAlgorithm._is_instantiation_compatible_with(
                            pdpu.partial_frontier_instantiation(i), instantiation):
                        for unifier in unifiers:
                            pdpu.piece_unifiers[i] = unifier
                            pdpu.cqs[i] = unifier.query
                            self._extend(rule, head_number, pdpu, result, i + 1)
        else:
            self._extend(rule, head_number, pdpu, result, i + 1)

    @staticmethod
    def _is_instantiation_more_general_than(i1: tuple[Optional[Constant], ...],
                                            i2: tuple[Optional[Constant], ...]) -> bool:
        return all(c1 is None or c1 == c2 for c1, c2 in zip(i1, i2))

    @staticmethod
    def _is_instantiation_compatible_with(i1: tuple[Optional[Constant], ...],
                                          i2: tuple[Optional[Constant], ...]) -> bool:
        return all(c1 is None or c2 is None or c1 == c2 for c1, c2 in zip(i1, i2))

    def _get_compatible_unifiers(self, head_number: int, pu: PieceUnifier) -> Iterable[PieceUnifier]:
        for q in self._previous_piece_unifiers:
            for k, v in self._previous_piece_unifiers[q][pu.rule][head_number].items():
                if self._is_instantiation_more_general_than(pu.frontier_instantiation, k):
                    for compatible_pu in v:
                        yield compatible_pu

    @staticmethod
    def _compute_full_unifiers_of_a_cq(rule: Rule[ConjunctiveQuery, ConjunctiveQuery],
                                       head_number: int,
                                       cq: ConjunctiveQuery) -> list[PieceUnifier]:
        return PieceUnifierAlgorithm. \
            compute_most_general_full_piece_unifiers(
            Substitution.safe_renaming(cq.existential_variables)(cq),
            Rule.extract_conjunctive_rule(rule, head_number))

    @staticmethod
    def _compute_full_unifiers_of_a_ucq(rule: Rule[ConjunctiveQuery, ConjunctiveQuery],
                                        head_number: int,
                                        ucq: UnionConjunctiveQueries) -> list[tuple[PieceUnifier, ConjunctiveQuery]]:
        return [(fpu, cq) for cq in ucq
                for fpu in DisjunctivePieceUnifierAlgorithm._compute_full_unifiers_of_a_cq(rule, head_number, cq)]
