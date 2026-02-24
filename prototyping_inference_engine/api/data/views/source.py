"""Runtime ReadableData implementation for declared views."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, Protocol

from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.blank_node_term import BlankNodeTerm
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.storage.dict_storage import DictStorage
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.factory.literal_factory import (
    LiteralFactory,
)
from prototyping_inference_engine.api.data.atomic_pattern import SimpleAtomicPattern
from prototyping_inference_engine.api.data.basic_query import BasicQuery
from prototyping_inference_engine.api.data.constraint.position_constraint import GROUND
from prototyping_inference_engine.api.data.readable_data import ReadableData
from prototyping_inference_engine.api.data.schema import (
    LogicalType,
    PositionSpec,
    RelationSchema,
    SchemaAware,
)
from prototyping_inference_engine.api.data.views.missing_values import (
    apply_missing_value_policy,
)
from prototyping_inference_engine.api.data.views.model import ViewDeclaration
from prototyping_inference_engine.api.data.views.model import MissingValuePolicy
from prototyping_inference_engine.api.data.views.specialization import (
    SpecializedViewInvocation,
    specialize_view_invocation,
)


class ViewQueryBackend(Protocol):
    """Protocol for datasource-specific native query execution."""

    def fetch_rows(
        self,
        compiled_view: "CompiledView",
        invocation: SpecializedViewInvocation,
    ) -> Iterable[tuple[object | None, ...]]:
        """Return one tuple of non-mandatory values per matching native result row."""


@dataclass(frozen=True)
class CompiledView:
    """Runtime representation of one declared view."""

    declaration: ViewDeclaration
    predicate: Predicate
    query_template: str
    non_mandatory_positions: tuple[int, ...]
    schema: RelationSchema


class ViewRuntimeSource(ReadableData, SchemaAware):
    """ReadableData adapter exposing declared views as predicates."""

    def __init__(
        self,
        name: str,
        backend: ViewQueryBackend,
        views: Iterable[CompiledView] = (),
        literal_factory: LiteralFactory | None = None,
    ):
        self._name = name
        self._backend = backend
        self._views: dict[Predicate, CompiledView] = {}
        self._literal_factory = literal_factory or LiteralFactory(DictStorage())
        self._optional_counter = 0
        for view in views:
            self.add_view(view)

    @property
    def name(self) -> str:
        return self._name

    def add_view(self, compiled_view: CompiledView) -> None:
        existing = self._views.get(compiled_view.predicate)
        if existing is not None and existing != compiled_view:
            raise ValueError(
                f"Predicate {compiled_view.predicate} already mapped in source {self._name}"
            )
        self._views[compiled_view.predicate] = compiled_view

    def get_predicates(self) -> Iterator[Predicate]:
        return iter(self._views.keys())

    def has_predicate(self, predicate: Predicate) -> bool:
        return predicate in self._views

    def get_atomic_pattern(self, predicate: Predicate) -> SimpleAtomicPattern:
        compiled = self._require_view(predicate)
        constraints = {
            index: GROUND
            for index, entry in enumerate(compiled.declaration.signature)
            if entry.is_mandatory
        }
        return SimpleAtomicPattern(predicate, constraints)

    def can_evaluate(self, query: BasicQuery) -> bool:
        compiled = self._views.get(query.predicate)
        if compiled is None:
            return False

        for index, entry in enumerate(compiled.declaration.signature):
            if not entry.is_mandatory:
                continue
            bound = query.get_bound_term(index)
            if bound is None or not bound.is_ground:
                return False
        return True

    def evaluate(self, query: BasicQuery) -> Iterator[tuple[Term, ...]]:
        compiled = self._require_view(query.predicate)
        if not self.can_evaluate(query):
            raise ValueError(
                f"Query does not satisfy mandatory bindings for predicate {query.predicate}"
            )

        invocation = specialize_view_invocation(
            compiled.declaration,
            compiled.query_template,
            query,
        )

        answer_positions = tuple(sorted(query.answer_variables.keys()))
        rows = self._backend.fetch_rows(compiled, invocation)

        for row_index, row in enumerate(rows):
            tuple_terms = self._materialize_row(
                compiled=compiled,
                query=query,
                invocation=invocation,
                row=row,
                row_index=row_index,
            )
            if tuple_terms is None:
                continue
            yield tuple(tuple_terms[position] for position in answer_positions)

    def get_schema(self, predicate: Predicate) -> RelationSchema | None:
        compiled = self._views.get(predicate)
        if compiled is None:
            return None
        return compiled.schema

    def get_schemas(self) -> Iterable[RelationSchema]:
        for compiled in self._views.values():
            yield compiled.schema

    def _materialize_row(
        self,
        *,
        compiled: CompiledView,
        query: BasicQuery,
        invocation: SpecializedViewInvocation,
        row: tuple[object | None, ...],
        row_index: int,
    ) -> tuple[Term, ...] | None:
        declaration = compiled.declaration
        materialized: list[Term] = []
        non_mandatory_index = 0
        mandatory_terms = tuple(term for term in invocation.mandatory_terms if term)

        for position, signature in enumerate(declaration.signature):
            if signature.is_mandatory:
                bound = query.get_bound_term(position)
                if bound is None:
                    return None
                materialized.append(bound)
                continue

            if non_mandatory_index < len(row):
                raw_value = row[non_mandatory_index]
            else:
                raw_value = None
            non_mandatory_index += 1

            if _is_missing(raw_value):
                replacement = apply_missing_value_policy(
                    signature.if_missing,
                    view_name=declaration.id,
                    row_index=row_index,
                    position=position,
                    row_values=row,
                    mandatory_terms=mandatory_terms,
                    optional_counter=self._optional_counter,
                )
                self._optional_counter += 1
                if replacement is None:
                    return None
                materialized.append(replacement)
                continue

            materialized.append(self._convert_value_to_term(raw_value))

        return tuple(materialized)

    def _convert_value_to_term(self, value: object) -> Term:
        if isinstance(value, Term):
            return value

        if isinstance(value, bool):
            return self._literal_factory.create_from_value(value)
        if isinstance(value, int):
            return self._literal_factory.create_from_value(value)
        if isinstance(value, float):
            return self._literal_factory.create_from_value(value)

        if isinstance(value, bytes):
            value = value.decode("utf-8", errors="replace")

        if isinstance(value, str):
            if value.startswith("_:"):
                return BlankNodeTerm(value)
            lowered = value.lower()
            if lowered.startswith("http://") or lowered.startswith("https://"):
                return Constant(value)
            if lowered.startswith("urn:"):
                return Constant(value)
            return self._literal_factory.create(value)

        return self._literal_factory.create_from_value(value)

    def _require_view(self, predicate: Predicate) -> CompiledView:
        compiled = self._views.get(predicate)
        if compiled is None:
            raise KeyError(f"No view bound to predicate: {predicate}")
        return compiled


def build_relation_schema(
    predicate: Predicate,
    declaration: ViewDeclaration,
) -> RelationSchema:
    """Create a RelationSchema representation for one view predicate."""
    positions: list[PositionSpec] = []
    for index, signature in enumerate(declaration.signature):
        name = signature.mandatory if signature.mandatory else f"c{index}"
        nullable = (
            not signature.is_mandatory
            and signature.if_missing != MissingValuePolicy.IGNORE
        )
        positions.append(
            PositionSpec(
                name=name,
                logical_type=LogicalType.UNKNOWN,
                nullable=nullable,
            )
        )
    return RelationSchema(predicate=predicate, positions=tuple(positions))


def non_mandatory_positions(declaration: ViewDeclaration) -> tuple[int, ...]:
    """Return declaration positions that are produced by native query results."""
    return tuple(
        index
        for index, signature in enumerate(declaration.signature)
        if not signature.is_mandatory
    )


def _is_missing(value: object | None) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value == ""
    return False
