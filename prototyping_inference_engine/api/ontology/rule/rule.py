"""
Created on 23 déc. 2021

@author: guillaume
"""

from functools import cached_property
from typing import Optional

from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.formula.binary_formula import BinaryFormula
from prototyping_inference_engine.api.formula.conjunction_formula import (
    ConjunctionFormula,
)
from prototyping_inference_engine.api.formula.disjunction_formula import (
    DisjunctionFormula,
)
from prototyping_inference_engine.api.formula.formula import Formula
from prototyping_inference_engine.api.formula.universal_formula import UniversalFormula
from prototyping_inference_engine.api.formula.variable_collectors import (
    collect_existential_variables,
)


class Rule:
    def __init__(
        self,
        body: Formula,
        head: Formula,
        label: Optional[str] = None,
    ):
        body_free = body.free_variables
        head_free = head.free_variables
        if body_free != head_free:
            raise ValueError(
                "Rule body and head must have the same free variables. "
                f"Body free vars={sorted(body_free, key=str)}, "
                f"head free vars={sorted(head_free, key=str)}."
            )
        self._frontier = frozenset(body_free)
        self._body = body
        self._head = head
        self._label = label

    @property
    def frontier(self) -> set[Variable]:
        return set(self._frontier)

    def head_frontier(self, num_head: int) -> set[Variable]:
        disjuncts = self.head_disjuncts
        if num_head < 0 or num_head >= len(disjuncts):
            raise IndexError("Head disjunct index out of range.")
        return set(self._frontier & disjuncts[num_head].free_variables)

    @cached_property
    def existential_variables(self) -> set[Variable]:
        return set(collect_existential_variables(self._head))

    @cached_property
    def variables(self) -> set[Variable]:
        return set(
            self._body.free_variables
            | self._body.bound_variables
            | self._head.free_variables
            | self._head.bound_variables
        )

    @property
    def body(self) -> Formula:
        return self._body

    @property
    def head(self) -> Formula:
        return self._head

    @cached_property
    def head_disjuncts(self) -> tuple[Formula, ...]:
        return tuple(_split_disjunction(self._head))

    @property
    def label(self) -> Optional[str]:
        return self._label

    @property
    def is_conjunctive(self) -> bool:
        return len(self.head_disjuncts) == 1

    @staticmethod
    def aggregate_conjunctive_rules(
        rule1: "Rule",
        rule2: "Rule",
    ) -> "Rule":
        if rule1 == rule2:
            return rule1
        return Rule(
            ConjunctionFormula(rule1.body, rule2.body),
            ConjunctionFormula(rule1.head, rule2.head),
        )

    @staticmethod
    def extract_conjunctive_rule(rule: "Rule", head_number: int) -> "Rule":
        disjuncts = rule.head_disjuncts
        if head_number < 0 or head_number >= len(disjuncts):
            raise IndexError("Head disjunct index out of range.")
        head = disjuncts[head_number]
        body = rule.body
        missing = body.free_variables - head.free_variables
        for var in sorted(missing, key=str):
            body = UniversalFormula(var, body)
        return Rule(body, head, rule.label)

    def __eq__(self, other):
        return (
            self.body == other.body
            and self.head == other.head
            and self.label == other.label
        )

    def __hash__(self):
        return hash((self.body, self.head, self.label))

    def __str__(self):
        label = "" if not self.label else "[" + str(self.label) + "] "
        body = _format_formula_top(self.body)
        if isinstance(self.head, DisjunctionFormula):
            disjuncts = " \u2228 ".join(f"({str(h)})" for h in self.head_disjuncts)
            head = disjuncts
        else:
            head = _format_formula_top(self.head)
        return f"{label}{body} \u2192 {head}"

    def __repr__(self):
        return "<Rule: " + str(self) + ">"


def _split_disjunction(formula: Formula) -> list[Formula]:
    if isinstance(formula, DisjunctionFormula):
        return _split_disjunction(formula.left) + _split_disjunction(formula.right)
    return [formula]


def _format_formula_top(formula: Formula) -> str:
    text = str(formula)
    if (
        isinstance(formula, BinaryFormula)
        and text.startswith("(")
        and text.endswith(")")
    ):
        return text[1:-1]
    return text
