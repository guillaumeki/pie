"""
Stratification strategies for GRD.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass
from typing import Iterable, Optional, Protocol

from prototyping_inference_engine.api.kb.rule_base import RuleBase
from prototyping_inference_engine.api.ontology.rule.rule import Rule


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
        sccs = _strongly_connected_components(grd.rules, grd.iter_edges())
        dag = _condensation_graph(sccs, grd.iter_edges())
        order = _topological_order_sccs(sccs, dag)
        return [RuleBase(set(scc)) for scc in order]


class MinimalStratification(StratificationStrategy):
    def compute(self, grd: "GRDProtocol") -> Optional[list[RuleBase]]:
        edges = list(grd.iter_edges())
        weights = {True: 0, False: -1}
        return _bellman_ford_strata(grd.rules, edges, weights, source_weight=0)


class SingleEvaluationStratification(StratificationStrategy):
    def compute(self, grd: "GRDProtocol") -> Optional[list[RuleBase]]:
        edges = list(grd.iter_edges())
        weights = {True: -1, False: -1}
        return _bellman_ford_strata(grd.rules, edges, weights, source_weight=-1)


def is_stratifiable(grd: "GRDProtocol") -> bool:
    sccs = _strongly_connected_components(grd.rules, grd.iter_edges())
    scc_index = _scc_index(sccs)
    for edge in grd.iter_edges():
        if not edge.is_positive and scc_index[edge.src] == scc_index[edge.target]:
            return False
    return True


class GRDProtocol(Protocol):
    @property
    def rules(self) -> tuple[Rule, ...]: ...

    def iter_edges(self) -> Iterable[Edge]: ...


def _strongly_connected_components(
    rules: Iterable[Rule], edges: Iterable[Edge]
) -> list[list[Rule]]:
    adjacency: dict[Rule, list[Rule]] = {rule: [] for rule in rules}
    for edge in edges:
        adjacency[edge.src].append(edge.target)

    index = 0
    stack: list[Rule] = []
    on_stack: set[Rule] = set()
    indices: dict[Rule, int] = {}
    lowlinks: dict[Rule, int] = {}
    result: list[list[Rule]] = []

    def strongconnect(node: Rule) -> None:
        nonlocal index
        indices[node] = index
        lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)

        for neighbor in sorted(adjacency[node], key=_rule_sort_key):
            if neighbor not in indices:
                strongconnect(neighbor)
                lowlinks[node] = min(lowlinks[node], lowlinks[neighbor])
            elif neighbor in on_stack:
                lowlinks[node] = min(lowlinks[node], indices[neighbor])

        if lowlinks[node] == indices[node]:
            scc: list[Rule] = []
            while True:
                w = stack.pop()
                on_stack.remove(w)
                scc.append(w)
                if w == node:
                    break
            result.append(sorted(scc, key=_rule_sort_key))

    for rule in sorted(adjacency.keys(), key=_rule_sort_key):
        if rule not in indices:
            strongconnect(rule)

    return result


def _scc_index(sccs: list[list[Rule]]) -> dict[Rule, int]:
    index: dict[Rule, int] = {}
    for i, scc in enumerate(sccs):
        for rule in scc:
            index[rule] = i
    return index


def _condensation_graph(
    sccs: list[list[Rule]], edges: Iterable[Edge]
) -> dict[int, set[int]]:
    scc_index = _scc_index(sccs)
    dag: dict[int, set[int]] = {i: set() for i in range(len(sccs))}
    for edge in edges:
        src_i = scc_index[edge.src]
        tgt_i = scc_index[edge.target]
        if src_i != tgt_i:
            dag[src_i].add(tgt_i)
    return dag


def _topological_order_sccs(
    sccs: list[list[Rule]], dag: dict[int, set[int]]
) -> list[list[Rule]]:
    indegree = {i: 0 for i in dag}
    for src, targets in dag.items():
        for tgt in targets:
            indegree[tgt] += 1

    queue = deque(
        sorted(
            [i for i, deg in indegree.items() if deg == 0],
            key=lambda i: _scc_sort_key(sccs[i]),
        )
    )
    order: list[list[Rule]] = []

    while queue:
        current = queue.popleft()
        order.append(sccs[current])
        for neighbor in sorted(dag[current], key=lambda i: _scc_sort_key(sccs[i])):
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)

    if len(order) != len(sccs):
        return sccs
    return order


def _bellman_ford_strata(
    rules: Iterable[Rule],
    edges: Iterable[Edge],
    weights: dict[bool, int],
    *,
    source_weight: int,
) -> Optional[list[RuleBase]]:
    rules_list = list(rules)
    if not rules_list:
        return []

    dist: dict[Rule, int] = {rule: 10**9 for rule in rules_list}
    for rule in rules_list:
        dist[rule] = source_weight

    all_edges = list(edges)

    for _ in range(len(rules_list) - 1):
        updated = False
        for edge in all_edges:
            weight = weights[edge.is_positive]
            if dist[edge.src] + weight < dist[edge.target]:
                dist[edge.target] = dist[edge.src] + weight
                updated = True
        if not updated:
            break

    for edge in all_edges:
        weight = weights[edge.is_positive]
        if dist[edge.src] + weight < dist[edge.target]:
            return None

    rules_by_cost: dict[int, set[Rule]] = {}
    for rule, cost in dist.items():
        rules_by_cost.setdefault(cost, set()).add(rule)

    strata: list[RuleBase] = []
    for cost in sorted(rules_by_cost.keys()):
        strata.append(RuleBase(rules_by_cost[cost]))

    strata.reverse()
    return strata


def _rule_sort_key(rule: Rule) -> tuple[str, int]:
    return (rule.label or "", hash(rule))


def _scc_sort_key(scc: list[Rule]) -> tuple[str, int]:
    if not scc:
        return ("", 0)
    first = sorted(scc, key=_rule_sort_key)[0]
    return (first.label or "", hash(first))
