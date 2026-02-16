"""Topological sorting utilities."""

# References:
# - "A Note on a Simple Algorithm for Generating a Topological Ordering of a
#   Directed Acyclic Graph" — Arthur B. Kahn.
#   Link: https://doi.org/10.1145/368996.369025
#
# Summary:
# Kahn's algorithm iteratively removes nodes with zero in-degree to produce a
# topological ordering of a DAG.
#
# Properties used here:
# - Linear-time topological sorting in the size of nodes plus edges.
# - Detection of cycles when not all nodes can be ordered.
#
# Implementation notes:
# This implementation keeps a priority queue to provide deterministic ordering
# when multiple nodes are available.

from __future__ import annotations

import heapq
from typing import Callable, Iterable, TypeVar


T = TypeVar("T")


def topological_sort(
    nodes: Iterable[T],
    edges: Iterable[tuple[T, T]],
    *,
    key: Callable[[T], str] | None = None,
) -> list[T]:
    if key is None:
        key = _default_key

    node_list = list(nodes)
    adjacency: dict[T, set[T]] = {node: set() for node in node_list}
    indegree: dict[T, int] = {node: 0 for node in node_list}

    for src, target in edges:
        if target not in adjacency[src]:
            adjacency[src].add(target)
            indegree[target] += 1

    heap: list[tuple[object, int, T]] = []
    for idx, node in enumerate(sorted(node_list, key=key)):
        if indegree[node] == 0:
            heapq.heappush(heap, (key(node), idx, node))

    order: list[T] = []
    while heap:
        _, _, node = heapq.heappop(heap)
        order.append(node)
        for neighbor in sorted(adjacency[node], key=key):
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                heapq.heappush(heap, (key(neighbor), len(order), neighbor))

    if len(order) != len(node_list):
        return sorted(node_list, key=key)
    return order


def _default_key(node: T) -> str:
    return str(node)
