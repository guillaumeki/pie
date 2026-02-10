"""
Readable data source for Python-backed functional predicates.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal
import inspect
from typing import (
    Any,
    Callable,
    Iterable,
    Iterator,
    Mapping,
    Optional,
    Tuple,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.literal import Literal
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.factory.literal_factory import (
    LiteralFactory,
)
from prototyping_inference_engine.api.atom.term.literal_xsd import XSD_PREFIX
from prototyping_inference_engine.api.data.atomic_pattern import SimpleAtomicPattern
from prototyping_inference_engine.api.data.constraint.position_constraint import GROUND
from prototyping_inference_engine.api.data.readable_data import ReadableData
from prototyping_inference_engine.api.data.basic_query import BasicQuery

FUNCTION_PREDICATE_PREFIX = "__func__"


def function_predicate_name(name: str) -> str:
    return f"{FUNCTION_PREDICATE_PREFIX}{name}"


def function_predicate(name: str, input_arity: int) -> Predicate:
    return Predicate(function_predicate_name(name), input_arity + 1)


@dataclass(frozen=True)
class FunctionSpec:
    name: str
    predicate: Predicate
    func: Callable[..., Any]
    mode: str
    input_arity: int
    output_position: int
    required_positions: frozenset[int]
    min_bound: Optional[int]
    solver: Optional[Callable[[list[Optional[Any]]], Iterable[list[Any]]]]
    returns_multiple: bool
    type_hints: dict[str, Any]
    param_names: list[str]


class PythonFunctionReadable(ReadableData):
    """
    ReadableData for Python functions exposed as computed predicates.

    Each function is registered with a mode:
    - "terms": function receives Term objects
    - "python": function receives native Python values from Literals
    """

    def __init__(self, literal_factory: LiteralFactory):
        self._literal_factory = literal_factory
        self._specs_by_predicate: dict[Predicate, FunctionSpec] = {}
        self._specs_by_name: dict[str, FunctionSpec] = {}

    def register_function(
        self,
        name: str,
        func: Callable[..., Any],
        *,
        mode: str = "terms",
        input_arity: Optional[int] = None,
        output_position: Optional[int] = None,
        required_positions: Optional[Iterable[int]] = None,
        min_bound: Optional[int] = None,
        solver: Optional[Callable[[list[Optional[Any]]], Iterable[list[Any]]]] = None,
        returns_multiple: bool = False,
    ) -> FunctionSpec:
        if mode not in {"terms", "python"}:
            raise ValueError(f"Unsupported function mode: {mode}")

        signature = inspect.signature(func)
        param_names = [
            p.name
            for p in signature.parameters.values()
            if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
        ]

        if input_arity is None:
            input_arity = len(param_names)

        if len(param_names) < input_arity:
            raise ValueError("input_arity exceeds positional parameter count")

        if output_position is None:
            output_position = input_arity

        if required_positions is None:
            if min_bound is None:
                required_positions = tuple(range(input_arity))
            else:
                required_positions = tuple()

        if min_bound is not None and solver is None:
            raise ValueError("min_bound requires a solver")

        pred = function_predicate(name, input_arity)
        type_hints = get_type_hints(func)

        spec = FunctionSpec(
            name=name,
            predicate=pred,
            func=func,
            mode=mode,
            input_arity=input_arity,
            output_position=output_position,
            required_positions=frozenset(required_positions),
            min_bound=min_bound,
            solver=solver,
            returns_multiple=returns_multiple,
            type_hints=type_hints,
            param_names=param_names,
        )
        self._specs_by_predicate[pred] = spec
        self._specs_by_name[name] = spec
        return spec

    def get_spec_by_name(self, name: str) -> Optional[FunctionSpec]:
        return self._specs_by_name.get(name)

    def function_names(self) -> set[str]:
        return set(self._specs_by_name.keys())

    def get_predicates(self) -> Iterator[Predicate]:
        return iter(self._specs_by_predicate.keys())

    def has_predicate(self, predicate: Predicate) -> bool:
        return predicate in self._specs_by_predicate

    def get_atomic_pattern(self, predicate: Predicate) -> SimpleAtomicPattern:
        if predicate not in self._specs_by_predicate:
            raise KeyError(f"No function predicate: {predicate}")
        spec = self._specs_by_predicate[predicate]
        constraints = {pos: GROUND for pos in spec.required_positions}
        return SimpleAtomicPattern(predicate, constraints)

    def can_evaluate(self, query: BasicQuery) -> bool:
        spec = self._specs_by_predicate.get(query.predicate)
        if spec is None:
            return False

        bound_positions = set(query.bound_positions.keys())
        if spec.required_positions and not spec.required_positions.issubset(
            bound_positions
        ):
            return False
        if spec.min_bound is not None and len(bound_positions) < spec.min_bound:
            return False
        return True

    def evaluate(self, query: BasicQuery) -> Iterator[Tuple[Term, ...]]:
        spec = self._specs_by_predicate.get(query.predicate)
        if spec is None:
            return iter(())

        if not self.can_evaluate(query):
            return iter(())

        arity = query.predicate.arity
        bound_positions = query.bound_positions
        answer_positions = sorted(query.answer_variables.keys())

        values: list[Optional[Any]] = [None] * arity
        for pos, term in bound_positions.items():
            values[pos] = term

        assignments = self._evaluate_assignments(spec, values)

        results: list[Tuple[Term, ...]] = []
        for assignment in assignments:
            if not self._matches_bound(bound_positions, assignment):
                continue
            answer_tuple = tuple(
                self._to_term(assignment[pos], spec) for pos in answer_positions
            )
            results.append(answer_tuple)
        return iter(results)

    def estimate_bound(self, query: BasicQuery) -> int | None:
        spec = self._specs_by_predicate.get(query.predicate)
        if spec is None:
            return None
        if not self.can_evaluate(query):
            return None
        if spec.returns_multiple:
            return None
        return 1

    def _evaluate_assignments(
        self, spec: FunctionSpec, values: list[Optional[Any]]
    ) -> Iterable[list[Any]]:
        if spec.solver is not None:
            prepared_values = self._prepare_solver_values(spec, values)
            if prepared_values is None:
                return []
            return spec.solver(list(prepared_values))

        input_values = []
        for pos in range(spec.input_arity):
            input_values.append(values[pos])

        prepared = self._prepare_inputs(spec, input_values)
        if prepared is None:
            return []

        result = spec.func(*prepared)
        if spec.returns_multiple:
            result_iter = result
        else:
            result_iter = [result]

        assignments: list[list[Any]] = []
        for item in result_iter:
            assignment = list(values)
            assignment[spec.output_position] = item
            assignments.append(assignment)
        return assignments

    def _prepare_inputs(
        self, spec: FunctionSpec, inputs: list[Optional[Any]]
    ) -> Optional[list[Any]]:
        if any(value is None for value in inputs):
            return None

        if spec.mode == "terms":
            for value in inputs:
                if not isinstance(value, Term):
                    return None
            return inputs

        converted: list[Any] = []
        for idx, value in enumerate(inputs):
            if not isinstance(value, Literal):
                return None
            native = value.value
            if not self._matches_type_hint(spec, idx, native):
                return None
            converted.append(native)
        return converted

    def _prepare_solver_values(
        self,
        spec: FunctionSpec,
        values: list[Optional[Any]],
    ) -> Optional[list[Optional[Any]]]:
        if spec.mode == "terms":
            for value in values:
                if value is None:
                    continue
                if not isinstance(value, Term):
                    return None
            return values

        converted: list[Optional[Any]] = []
        for idx, value in enumerate(values):
            if value is None:
                converted.append(None)
                continue
            if not isinstance(value, Literal):
                return None
            native = value.value
            if not self._matches_type_hint(spec, idx, native):
                return None
            converted.append(native)
        return converted

    def _matches_type_hint(self, spec: FunctionSpec, index: int, value: Any) -> bool:
        if index >= len(spec.param_names):
            return True
        name = spec.param_names[index]
        if name not in spec.type_hints:
            return True
        hint = spec.type_hints[name]
        return _matches_hint(value, hint)

    def _matches_bound(
        self, bound_positions: Mapping[int, Term], assignment: list[Any]
    ) -> bool:
        for pos, term in bound_positions.items():
            assigned = assignment[pos]
            if assigned is None:
                return False
            if isinstance(assigned, Term):
                if assigned != term:
                    return False
            else:
                if self._to_term(assigned, None) != term:
                    return False
        return True

    def _to_term(self, value: Any, spec: Optional[FunctionSpec]) -> Term:
        if isinstance(value, Term):
            return value
        if spec is not None and spec.mode == "terms":
            return Constant(str(value))
        return _python_value_to_term(value, self._literal_factory)


def _matches_hint(value: Any, hint: Any) -> bool:
    if hint is Any:
        return True
    origin = get_origin(hint)
    if origin is None:
        return isinstance(value, hint)
    if origin is list:
        return isinstance(value, list)
    if origin is tuple:
        return isinstance(value, tuple)
    if origin is dict:
        return isinstance(value, dict)
    if origin is set:
        return isinstance(value, set)
    if origin is Union:
        return any(_matches_hint(value, a) for a in get_args(hint))
    return True


def _python_value_to_term(value: Any, literal_factory: LiteralFactory) -> Term:
    if isinstance(value, Term):
        return value
    if isinstance(value, bool):
        return literal_factory.create(str(value).lower(), f"{XSD_PREFIX}boolean")
    if isinstance(value, int):
        return literal_factory.create(str(value), f"{XSD_PREFIX}integer")
    if isinstance(value, Decimal):
        return literal_factory.create(str(value), f"{XSD_PREFIX}decimal")
    if isinstance(value, float):
        return literal_factory.create(str(value), f"{XSD_PREFIX}double")
    if isinstance(value, datetime):
        return literal_factory.create(value.isoformat(), f"{XSD_PREFIX}dateTime")
    if isinstance(value, date) and not isinstance(value, datetime):
        return literal_factory.create(value.isoformat(), f"{XSD_PREFIX}date")
    if isinstance(value, time):
        return literal_factory.create(value.isoformat(), f"{XSD_PREFIX}time")
    if isinstance(value, str):
        return literal_factory.create(value, f"{XSD_PREFIX}string")
    if isinstance(value, (list, tuple, set, dict)):
        return literal_factory.create_from_value(value)
    return Constant(str(value))
