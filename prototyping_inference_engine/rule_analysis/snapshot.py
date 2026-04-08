"""Immutable snapshot facade over rule-analysis derived data."""

from __future__ import annotations

from functools import cached_property
from typing import Iterable

import igraph as ig  # type: ignore[import-untyped]

from prototyping_inference_engine.api.kb.rule_base import RuleBase
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.grd.grd import GRD
from prototyping_inference_engine.rule_analysis.affected_positions import (
    AffectedPositionSet,
    compute_affected_positions,
)
from prototyping_inference_engine.rule_analysis.fragments import (
    RuleFragments,
    ensure_safe_negation,
    extract_rule_fragments,
)
from prototyping_inference_engine.rule_analysis.marked_variables import (
    MarkedVariableSet,
    compute_marked_variables,
)
from prototyping_inference_engine.rule_analysis.position_graph import (
    PositionDependencyGraph,
)


class AnalysisSnapshot:
    """Canonical, lazily-derived analysis data for a fixed rule set."""

    def __init__(self, rules: RuleBase | Iterable[Rule]):
        source_rules: Iterable[Rule]
        if isinstance(rules, RuleBase):
            source_rules = rules.rules
        else:
            source_rules = tuple(rules)
        self._rules = tuple(sorted(source_rules, key=_rule_sort_key))

    @property
    def rules(self) -> tuple[Rule, ...]:
        return self._rules

    @cached_property
    def fragments_by_rule(self) -> dict[Rule, RuleFragments]:
        return {rule: extract_rule_fragments(rule) for rule in self._rules}

    @cached_property
    def has_negation(self) -> bool:
        return len(self.rules_with_negation) > 0

    @cached_property
    def rules_with_negation(self) -> tuple[Rule, ...]:
        rules_with_negation: list[Rule] = []
        for rule in self._rules:
            ensure_safe_negation(rule)
            if len(self.fragments_by_rule[rule].negative_body) > 0:
                rules_with_negation.append(rule)
        return tuple(rules_with_negation)

    @cached_property
    def has_disjunctive_head(self) -> bool:
        return len(self.rules_with_disjunctive_head) > 0

    @cached_property
    def rules_with_disjunctive_head(self) -> tuple[Rule, ...]:
        return tuple(
            rule
            for rule, fragments in self.fragments_by_rule.items()
            if fragments.has_disjunctive_head
        )

    @cached_property
    def affected_positions(self) -> AffectedPositionSet:
        return compute_affected_positions(self._rules, self.fragments_by_rule)

    @cached_property
    def position_dependency_graph(self) -> PositionDependencyGraph:
        return PositionDependencyGraph.from_fragments(
            self._rules, self.fragments_by_rule
        )

    @cached_property
    def marked_variables(self) -> MarkedVariableSet:
        return compute_marked_variables(self._rules, self.fragments_by_rule)

    @cached_property
    def grd(self) -> GRD:
        return GRD(self._rules)

    @cached_property
    def sccs(self) -> tuple[tuple[Rule, ...], ...]:
        rule_index = {rule: index for index, rule in enumerate(self._rules)}
        graph = ig.Graph(directed=True)
        graph.add_vertices(len(self._rules))
        edges = [
            (rule_index[edge.src], rule_index[edge.target])
            for edge in self.grd.iter_edges()
        ]
        if edges:
            graph.add_edges(edges)
        membership = graph.connected_components(mode="STRONG").membership
        by_component: dict[int, list[Rule]] = {}
        for rule, component_index in zip(self._rules, membership):
            by_component.setdefault(component_index, []).append(rule)
        return tuple(
            tuple(sorted(component_rules, key=_rule_sort_key))
            for _, component_rules in sorted(by_component.items())
        )


def _rule_sort_key(rule: Rule) -> tuple[str, str, str]:
    return (
        rule.label or "",
        str(rule.body),
        str(rule.head),
    )
