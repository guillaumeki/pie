"""Position-dependency graph for weak acyclicity analysis."""

# References:
# - "Data Exchange: Semantics and Query Answering" —
#   Ronald Fagin, Phokion G. Kolaitis, Renée J. Miller, Lucian Popa.
#   Link: https://research.ibm.com/publications/data-exchange-semantics-and-query-answering
# - "Query Answering under Non-guarded Rules in Datalog+/-" —
#   Andrea Calì, Georg Gottlob, Andreas Pieris.
#   Link: https://www.research.ed.ac.uk/en/publications/query-answering-under-non-guarded-rules-in-datalog/
#
# Summary:
# Weak acyclicity is decided on a dependency graph over predicate positions.
# Ordinary edges capture value propagation through shared frontier variables,
# while special edges capture value creation by existential variables. A ruleset
# is weakly acyclic when no strongly connected component contains a special edge.
#
# Properties used here:
# - Ordinary body-to-head edges preserve variable flow.
# - Special edges connect every body position to existential head positions.
# - SCC detection identifies non-finite-rank positions.
#
# Implementation source:
# This module reconstructs the position graph from PIE-native rule fragments and
# uses igraph only for SCC computation.

from __future__ import annotations

from dataclasses import dataclass

import igraph as ig  # type: ignore[import-untyped]

from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.rule_analysis.fragments import RuleFragments
from prototyping_inference_engine.rule_analysis.model import (
    PositionDependencyEdge,
    PredicatePosition,
)


@dataclass(frozen=True)
class PositionDependencyGraph:
    """Directed graph over predicate positions with special edges."""

    positions: frozenset[PredicatePosition]
    edges: frozenset[PositionDependencyEdge]

    @classmethod
    def from_fragments(
        cls,
        rules: tuple[Rule, ...],
        fragments_by_rule: dict[Rule, RuleFragments],
    ) -> "PositionDependencyGraph":
        positions: set[PredicatePosition] = set()
        edges: set[PositionDependencyEdge] = set()

        for rule in rules:
            fragments = fragments_by_rule[rule]
            head_positions_by_var: dict[Variable, set[PredicatePosition]] = {}
            existential_positions: set[PredicatePosition] = set()

            for head_atom in fragments.all_head_atoms:
                for position, term in enumerate(head_atom.terms):
                    head_position = PredicatePosition(head_atom.predicate, position)
                    positions.add(head_position)
                    if isinstance(term, Variable):
                        head_positions_by_var.setdefault(term, set()).add(head_position)
                    if term in fragments.existential_variables:
                        existential_positions.add(head_position)

            for body_atom in fragments.positive_body:
                for position, term in enumerate(body_atom.terms):
                    body_position = PredicatePosition(body_atom.predicate, position)
                    positions.add(body_position)
                    if not isinstance(term, Variable):
                        continue
                    for head_position in head_positions_by_var.get(term, ()):
                        edges.add(PositionDependencyEdge(body_position, head_position))
                    for existential_position in existential_positions:
                        edges.add(
                            PositionDependencyEdge(
                                body_position,
                                existential_position,
                                is_special=True,
                            )
                        )

        return cls(frozenset(positions), frozenset(edges))

    def is_weakly_acyclic(self) -> bool:
        return all(
            edge.source not in self.non_finite_rank_positions
            or edge.target not in self.non_finite_rank_positions
            or not edge.is_special
            for edge in self.edges
        )

    @property
    def non_finite_rank_positions(self) -> frozenset[PredicatePosition]:
        if not self.edges:
            return frozenset()

        vertices = sorted(self.positions, key=lambda position: position.sort_key)
        vertex_index = {vertex: index for index, vertex in enumerate(vertices)}
        graph = ig.Graph(directed=True)
        graph.add_vertices(len(vertices))
        graph.add_edges(
            [
                (vertex_index[edge.source], vertex_index[edge.target])
                for edge in self.edges
            ]
        )

        membership = graph.connected_components(mode="STRONG").membership
        component_has_special_edge: dict[int, bool] = {}
        for edge in self.edges:
            src_component = membership[vertex_index[edge.source]]
            tgt_component = membership[vertex_index[edge.target]]
            if edge.is_special and src_component == tgt_component:
                component_has_special_edge[src_component] = True

        return frozenset(
            vertex
            for vertex in vertices
            if component_has_special_edge.get(membership[vertex_index[vertex]], False)
        )

    @property
    def finite_rank_positions(self) -> frozenset[PredicatePosition]:
        return self.positions - self.non_finite_rank_positions

    def is_finite_rank(self, position: PredicatePosition) -> bool:
        return position in self.finite_rank_positions
