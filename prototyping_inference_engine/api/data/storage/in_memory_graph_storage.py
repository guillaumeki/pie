"""In-memory graph storage inspired by Integraal LightInMemoryGraphStore."""

from __future__ import annotations

from typing import Dict, Iterable, Iterator, Set

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.data.atomic_pattern import UnconstrainedPattern
from prototyping_inference_engine.api.data.basic_query import BasicQuery
from prototyping_inference_engine.api.data.schema import (
    LogicalType,
    PositionSpec,
    RelationSchema,
    SchemaAware,
)
from prototyping_inference_engine.api.fact_base.fact_base import FactBase
from prototyping_inference_engine.api.fact_base.protocols import Writable


class InMemoryGraphStorage(FactBase, Writable, SchemaAware):
    """Graph-like in-memory storage with predicate and term indexes."""

    def __init__(self, atoms: Iterable[Atom] | None = None) -> None:
        self._atoms: Set[Atom] = set()
        self._by_predicate: Dict[Predicate, Set[Atom]] = {}
        self._by_term: Dict[Term, Set[Atom]] = {}
        if atoms is not None:
            self.update(atoms)

    def get_predicates(self) -> Iterator[Predicate]:
        return iter(self._by_predicate.keys())

    def has_predicate(self, predicate: Predicate) -> bool:
        return predicate in self._by_predicate

    def get_atomic_pattern(self, predicate: Predicate) -> UnconstrainedPattern:
        return UnconstrainedPattern(predicate)

    def get_schema(self, predicate: Predicate) -> RelationSchema | None:
        if predicate not in self._by_predicate:
            return None
        positions = tuple(
            PositionSpec(name=f"c{idx}", logical_type=LogicalType.UNKNOWN)
            for idx in range(predicate.arity)
        )
        return RelationSchema(predicate, positions)

    def get_schemas(self) -> Iterable[RelationSchema]:
        for predicate in self._by_predicate:
            schema = self.get_schema(predicate)
            if schema is not None:
                yield schema

    def evaluate(self, query: BasicQuery) -> Iterator[tuple[Term, ...]]:
        answer_positions = sorted(query.answer_variables.keys())
        candidates = self._candidates(query)

        for atom in candidates:
            if atom.predicate != query.predicate:
                continue
            if any(
                atom.terms[pos] != term for pos, term in query.bound_positions.items()
            ):
                continue
            yield tuple(atom.terms[pos] for pos in answer_positions)

    def _candidates(self, query: BasicQuery) -> Set[Atom]:
        by_predicate = self._by_predicate.get(query.predicate, set())
        if not query.bound_positions:
            return by_predicate

        best: Set[Atom] | None = None
        for term in query.bound_positions.values():
            bucket = self._by_term.get(term, set())
            if best is None or len(bucket) < len(best):
                best = bucket

        if best is None:
            return by_predicate
        if best is by_predicate:
            return best
        return best.intersection(by_predicate)

    @property
    def variables(self) -> Set[Variable]:
        variables: Set[Variable] = set()
        for atom in self._atoms:
            variables.update(atom.variables)
        return variables

    @property
    def constants(self) -> Set[Constant]:
        constants: Set[Constant] = set()
        for atom in self._atoms:
            constants.update(atom.constants)
        return constants

    @property
    def terms(self) -> Set[Term]:
        terms: Set[Term] = set()
        for atom in self._atoms:
            terms.update(atom.terms)
        return terms

    def add(self, atom: Atom) -> None:
        if atom in self._atoms:
            return
        self._atoms.add(atom)
        self._by_predicate.setdefault(atom.predicate, set()).add(atom)
        for term in atom.terms:
            self._by_term.setdefault(term, set()).add(atom)

    def update(self, atoms: Iterable[Atom]) -> None:
        for atom in atoms:
            self.add(atom)

    def remove(self, atom: Atom) -> None:
        if atom not in self._atoms:
            return
        self._atoms.remove(atom)

        predicate_bucket = self._by_predicate.get(atom.predicate)
        if predicate_bucket is not None:
            predicate_bucket.discard(atom)
            if not predicate_bucket:
                del self._by_predicate[atom.predicate]

        for term in atom.terms:
            term_bucket = self._by_term.get(term)
            if term_bucket is None:
                continue
            term_bucket.discard(atom)
            if not term_bucket:
                del self._by_term[term]

    def remove_all(self, atoms: Iterable[Atom]) -> None:
        for atom in atoms:
            self.remove(atom)

    def __iter__(self) -> Iterator[Atom]:
        return iter(self._atoms)

    def __len__(self) -> int:
        return len(self._atoms)

    def __contains__(self, atom: Atom) -> bool:
        return atom in self._atoms
