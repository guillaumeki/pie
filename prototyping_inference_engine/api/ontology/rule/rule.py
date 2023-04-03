"""
Created on 23 déc. 2021

@author: guillaume
"""
from functools import cached_property
from typing import Optional, Iterable, TypeVar, Generic

from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.query.query import Query
from prototyping_inference_engine.api.atom.term.variable import Variable

BodyQueryType = TypeVar("BodyQueryType", bound=Query)
HeadQueryType = TypeVar("HeadQueryType", bound=Query)


class Rule(Generic[BodyQueryType, HeadQueryType]):
    def __init__(self, body: BodyQueryType, head: Iterable[HeadQueryType], label: Optional[str] = None):
        self._frontier = body.variables & frozenset(v for h in head for v in h.variables)
        self._body = body.query_with_other_answer_variables(tuple(self._frontier))
        self._head = tuple(h.query_with_other_answer_variables(tuple(self._frontier & h.variables)) for h in head)
        self._label = label

    @property
    def frontier(self) -> set[Variable]:
        return self._frontier

    def head_frontier(self, num_head: int) -> set[Variable]:
        return self.head[num_head].answer_variables

    @cached_property
    def existential_variables(self) -> set[Variable]:
        return {v for h in self.head for v in h.existential_variables}

    @cached_property
    def variables(self) -> set[Variable]:
        return {v for h in self.head for v in h.variables} | self.body.variables

    @property
    def body(self) -> BodyQueryType:
        return self._body

    @property
    def head(self) -> tuple[HeadQueryType, ...]:
        return self._head

    @property
    def label(self) -> Optional[str]:
        return self._label

    @property
    def is_conjunctive(self) -> bool:
        return len(self.head) == 1

    @staticmethod
    def aggregate_conjunctive_rules(
            rule1: "Rule[ConjunctiveQuery, ConjunctiveQuery]",
            rule2: "Rule[ConjunctiveQuery, ConjunctiveQuery]") -> "Rule[ConjunctiveQuery, ConjunctiveQuery]":
        return Rule(rule1.body.aggregate(rule2.body), [rule1.head[0].aggregate(rule2.head[0])])

    @staticmethod
    def extract_conjunctive_rule(rule: "Rule[ConjunctiveQuery, ConjunctiveQuery]",
                                 head_number: int) -> "Rule[ConjunctiveQuery, ConjunctiveQuery]":
        return Rule(rule.body, [rule.head[head_number]], rule.label)

    def __eq__(self, other):
        return self.body == other.body and self.head == other.head and self.label == other.label

    def __hash__(self):
        return hash((self.body, self.head, self.label))

    def __str__(self):
        heads = [
            ("\u2203" + ",".join(str(v) for v in h.existential_variables) + " " if h.existential_variables else "")
            + str(h.str_without_answer_variables)
            for h in self.head]
        return "{}{} \u2192 {}".format(
            "" if not self.label else "["+str(self.label)+"] ",
            str(self.body.str_without_answer_variables),
            " \u2228 ".join("("+h+")" for h in heads) if not self.is_conjunctive
            else " \u2228 ".join(h for h in heads))

    def __repr__(self):
        return "<Rule: "+str(self)+">"
