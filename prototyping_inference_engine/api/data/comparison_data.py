"""
Readable data source for comparison operators.
"""
from __future__ import annotations

from typing import Iterator, Tuple, Optional, Iterable

from prototyping_inference_engine.api.atom.predicate import (
    Predicate,
    COMPARISON_OPERATORS,
    comparison_predicate,
)
from prototyping_inference_engine.api.atom.term.literal import Literal
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.data.atomic_pattern import SimpleAtomicPattern
from prototyping_inference_engine.api.data.constraint.position_constraint import GROUND
from prototyping_inference_engine.api.data.readable_data import ReadableData
from prototyping_inference_engine.api.data.basic_query import BasicQuery
from prototyping_inference_engine.api.atom.term.literal_config import LiteralComparison


class ComparisonDataSource(ReadableData):
    """
    ReadableData implementation for built-in comparison predicates.

    The data source requires both arguments to be ground. If the comparison
    holds, it yields a single empty tuple (no answers). Otherwise yields nothing.
    """

    def __init__(
        self,
        comparison_mode: LiteralComparison = LiteralComparison.BY_NORMALIZED_VALUE,
    ) -> None:
        if comparison_mode not in {
            LiteralComparison.BY_NORMALIZED_VALUE,
            LiteralComparison.BY_LEXICAL,
        }:
            raise ValueError(f"Unsupported comparison mode: {comparison_mode}")
        self._comparison_mode = comparison_mode
        self._predicates = tuple(comparison_predicate(op) for op in COMPARISON_OPERATORS)
        self._patterns = {
            predicate: SimpleAtomicPattern(predicate, {0: GROUND, 1: GROUND})
            for predicate in self._predicates
        }

    @property
    def comparison_mode(self) -> LiteralComparison:
        return self._comparison_mode

    def get_predicates(self) -> Iterator[Predicate]:
        return iter(self._predicates)

    def has_predicate(self, predicate: Predicate) -> bool:
        return predicate in self._patterns

    def get_atomic_pattern(self, predicate: Predicate) -> SimpleAtomicPattern:
        if predicate not in self._patterns:
            raise KeyError(f"No comparison predicate: {predicate}")
        return self._patterns[predicate]

    def evaluate(self, query: BasicQuery) -> Iterator[Tuple[Term, ...]]:
        left = query.get_bound_term(0)
        right = query.get_bound_term(1)
        if left is None or right is None:
            return iter(())
        if self._compare(query.predicate, left, right):
            return iter([tuple()])
        return iter(())

    def _compare(self, predicate: Predicate, left: Term, right: Term) -> bool:
        op = predicate.name
        left_value = self._extract_value(left)
        right_value = self._extract_value(right)

        try:
            if op == "<":
                return left_value < right_value
            if op == "<=":
                return left_value <= right_value
            if op == ">":
                return left_value > right_value
            if op == ">=":
                return left_value >= right_value
            if op == "!=":
                return left_value != right_value
        except TypeError:
            return False
        return False

    def _extract_value(self, term: Term) -> object:
        if isinstance(term, Literal):
            if self._comparison_mode == LiteralComparison.BY_LEXICAL:
                return term.lexical if term.lexical is not None else str(term.value)
            return term.value
        if isinstance(term, Constant):
            return term.identifier
        return term


def comparison_predicates() -> Iterable[Predicate]:
    return tuple(comparison_predicate(op) for op in COMPARISON_OPERATORS)
