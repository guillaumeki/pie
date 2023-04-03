from functools import cached_property
from typing import Iterable, Iterator

from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.query.query import Query
from prototyping_inference_engine.api.substitution.substitutable import Substitutable
from prototyping_inference_engine.api.substitution.substitution import Substitution


class UnionConjunctiveQueries(Query, Substitutable["UnionConjunctiveQueries"]):
    def __init__(self, cqs: Iterable[ConjunctiveQuery] = None, answer_variables: Iterable[Variable] = None,
                 label: str = None):
        if answer_variables is None:
            answer_variables = ()
        if cqs is None:
            cqs = []

        Query.__init__(self, answer_variables, label)

        ncqs = []
        for cq in cqs:
            if len(answer_variables) != len(cq.answer_variables):
                raise ValueError("This CQ has an unappropriated number of answer variables: " + repr(cq) +
                                 " - expected: " + str(len(answer_variables)))
            ncqs.append(Substitution({v: t for v, t in zip(cq.answer_variables, self.answer_variables)})(cq))

        self._cqs = frozenset(ncqs)

    @property
    def conjunctive_queries(self) -> frozenset[ConjunctiveQuery]:
        return self._cqs

    @cached_property
    def terms(self) -> set[Term]:
        return set().union(*[cq.terms for cq in self.conjunctive_queries])

    @cached_property
    def constants(self) -> set[Constant]:
        return set().union(*[cq.constants for cq in self.conjunctive_queries])

    @cached_property
    def variables(self) -> set[Variable]:
        return set().union(*[cq.variables for cq in self.conjunctive_queries])

    def apply_substitution(self, substitution: Substitution) -> "UnionConjunctiveQueries":
        return UnionConjunctiveQueries((substitution(cq) for cq in self.conjunctive_queries),
                                       [substitution(v) for v in self.answer_variables],
                                       self.label)

    @property
    def str_without_answer_variables(self) -> str:
        return " \u2228 ".join("(" + cq.str_without_answer_variables + ")"
                               if len(cq.atoms) != 1 or len(cq.pre_substitution) != 0
                               else cq.str_without_answer_variables
                               for cq in self.conjunctive_queries)

    def __or__(self, other: "UnionConjunctiveQueries") -> "UnionConjunctiveQueries":
        if self.answer_variables != other.answer_variables:
            raise ValueError(f"You can't do the union of two ucqs with distinct answer variables: {self} and {other}")
        return UnionConjunctiveQueries(self.conjunctive_queries | other.conjunctive_queries, self.answer_variables)

    def __eq__(self, other):
        if not isinstance(other, UnionConjunctiveQueries):
            return False
        return (self.conjunctive_queries == other.conjunctive_queries
                and self.answer_variables == other.answer_variables
                and self.label == other.label)

    def __hash__(self):
        return hash((self.conjunctive_queries, self.answer_variables, self.label))

    def __repr__(self):
        return "UCQ: " + str(self)

    def __str__(self):
        return "({}) :- {}".format(
            ", ".join(map(str, self.answer_variables)),
            self.str_without_answer_variables)

    def __iter__(self) -> Iterator[ConjunctiveQuery]:
        return iter(self.conjunctive_queries)

    def __len__(self):
        return len(self.conjunctive_queries)
