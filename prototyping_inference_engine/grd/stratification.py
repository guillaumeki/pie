"""
Stratification strategies for GRD.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, Optional, Protocol

import igraph as ig  # type: ignore[import-untyped]

from prototyping_inference_engine.api.kb.rule_base import RuleBase
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.utils.graph.topological_sort import (
    topological_sort,
)


@dataclass(frozen=True)
class Edge:
    src: Rule
    target: Rule
    is_positive: bool


class StratificationStrategy(ABC):
    """Strategy interface for GRD stratification."""

    @abstractmethod
    def compute(self, grd: "GRDProtocol") -> Optional[list[RuleBase]]:
        raise NotImplementedError


class BySccStratification(StratificationStrategy):
    def compute(self, grd: "GRDProtocol") -> Optional[list[RuleBase]]:
        graph, rules, rule_index, edge_list = _build_graph(grd)
        components = graph.connected_components(mode="STRONG")
        membership = components.membership

        comp_rules: dict[int, list[Rule]] = {}
        for rule, comp_idx in zip(rules, membership):
            comp_rules.setdefault(comp_idx, []).append(rule)

        dag_edges: set[tuple[int, int]] = set()
        for edge in edge_list:
            src_comp = membership[rule_index[edge.src]]
            tgt_comp = membership[rule_index[edge.target]]
            if src_comp != tgt_comp:
                dag_edges.add((src_comp, tgt_comp))

        order = topological_sort(
            sorted(comp_rules.keys()),
            dag_edges,
            key=lambda idx: _scc_sort_key(comp_rules[idx]),
        )
        return [RuleBase(set(comp_rules[idx])) for idx in order]


class MinimalStratification(StratificationStrategy):
    def compute(self, grd: "GRDProtocol") -> Optional[list[RuleBase]]:
        return _bellman_ford_strata(grd, {True: 0, False: -1}, source_weight=0)


class SingleEvaluationStratification(StratificationStrategy):
    def compute(self, grd: "GRDProtocol") -> Optional[list[RuleBase]]:
        return _bellman_ford_strata(grd, {True: -1, False: -1}, source_weight=-1)


class MinimalEvaluationStratification(StratificationStrategy):
    def compute(self, grd: "GRDProtocol") -> Optional[list[RuleBase]]:
        if not is_stratifiable(grd):
            return None

        graph, rules, rule_index, edge_list = _build_graph(grd)
        components = graph.connected_components(mode="STRONG")
        membership = components.membership

        comp_rules: dict[int, list[Rule]] = {}
        for rule, comp_idx in zip(rules, membership):
            comp_rules.setdefault(comp_idx, []).append(rule)

        comp_edges: set[tuple[int, int]] = set()
        for edge in edge_list:
            src_comp = membership[rule_index[edge.src]]
            tgt_comp = membership[rule_index[edge.target]]
            if src_comp != tgt_comp:
                comp_edges.add((src_comp, tgt_comp))

        comp_order = topological_sort(
            sorted(comp_rules.keys()),
            comp_edges,
            key=lambda idx: _scc_sort_key(comp_rules[idx]),
        )

        predecessors: dict[int, set[int]] = {idx: set() for idx in comp_rules}
        for src, tgt in comp_edges:
            predecessors[tgt].add(src)

        levels: dict[int, int] = {}
        for comp_idx in comp_order:
            if not predecessors[comp_idx]:
                levels[comp_idx] = 0
            else:
                levels[comp_idx] = (
                    max(levels[pred] for pred in predecessors[comp_idx]) + 1
                )

        rules_by_level: dict[int, set[Rule]] = {}
        for comp_idx, level in levels.items():
            rules_by_level.setdefault(level, set()).update(comp_rules[comp_idx])

        return [RuleBase(rules_by_level[level]) for level in sorted(rules_by_level)]


def is_stratifiable(grd: "GRDProtocol") -> bool:
    graph, _, rule_index, edge_list = _build_graph(grd)
    components = graph.connected_components(mode="STRONG")
    membership = components.membership
    for edge in edge_list:
        if not edge.is_positive:
            src_comp = membership[rule_index[edge.src]]
            tgt_comp = membership[rule_index[edge.target]]
            if src_comp == tgt_comp:
                return False
    return True


class GRDProtocol(Protocol):
    @property
    def rules(self) -> tuple[Rule, ...]: ...

    def iter_edges(self) -> Iterable[Edge]: ...


def _build_graph(
    grd: "GRDProtocol",
) -> tuple[ig.Graph, list[Rule], dict[Rule, int], list[Edge]]:
    rules = list(grd.rules)
    rule_index = {rule: idx for idx, rule in enumerate(rules)}
    edge_list = list(grd.iter_edges())
    edges = [(rule_index[e.src], rule_index[e.target]) for e in edge_list]

    graph = ig.Graph(directed=True)
    graph.add_vertices(len(rules))
    if edges:
        graph.add_edges(edges)
    return graph, rules, rule_index, edge_list


def _bellman_ford_strata(
    grd: "GRDProtocol",
    weights: dict[bool, int],
    *,
    source_weight: int,
) -> Optional[list[RuleBase]]:
    _, rules, rule_index, edge_list = _build_graph(grd)
    source_index = len(rules)
    weighted_edges = [
        (rule_index[edge.src], rule_index[edge.target]) for edge in edge_list
    ]
    edge_weights = [weights[edge.is_positive] for edge in edge_list]

    source_edges = [(source_index, rule_idx) for rule_idx in range(len(rules))]
    weighted_edges.extend(source_edges)
    edge_weights.extend([source_weight for _ in source_edges])

    graph = ig.Graph(
        n=len(rules) + 1,
        edges=weighted_edges,
        directed=True,
    )
    graph.es["weight"] = edge_weights

    try:
        distances = graph.distances(
            source=source_index,
            weights="weight",
            algorithm="bellman-ford",
        )[0]
    except ig.InternalError:
        return None

    rules_by_cost: dict[int, set[Rule]] = {}
    for rule, cost in zip(rules, distances[: len(rules)]):
        rules_by_cost.setdefault(int(cost), set()).add(rule)

    strata = [RuleBase(rules_by_cost[cost]) for cost in sorted(rules_by_cost.keys())]
    strata.reverse()
    return strata


def _rule_sort_key(rule: Rule) -> tuple[str, int]:
    return (rule.label or "", hash(rule))


def _scc_sort_key(rules: list[Rule]) -> str:
    if not rules:
        return ""
    first = sorted(rules, key=_rule_sort_key)[0]
    return f"{first.label or ''}:{hash(first)}"
