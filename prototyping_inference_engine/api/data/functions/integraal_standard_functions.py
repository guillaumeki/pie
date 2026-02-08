"""
Integraal standard functions exposed as computed predicates.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Callable, Iterable, Iterator, Mapping, Optional, cast

from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.literal import Literal
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.factory.literal_factory import (
    LiteralFactory,
)
from prototyping_inference_engine.api.atom.term.literal_xsd import XSD_PREFIX
from prototyping_inference_engine.api.data.atomic_pattern import SimpleAtomicPattern
from prototyping_inference_engine.api.data.basic_query import BasicQuery
from prototyping_inference_engine.api.data.constraint.position_constraint import GROUND
from prototyping_inference_engine.api.data.readable_data import ReadableData


@dataclass(frozen=True)
class StandardFunction:
    name: str
    min_inputs: int
    max_inputs: Optional[int]
    evaluator: Callable[[list[Term], LiteralFactory], Term]
    solver: Optional[
        Callable[[list[Optional[Term]], LiteralFactory], Iterable[list[Term]]]
    ] = None


@dataclass(frozen=True)
class FunctionBinding:
    function: StandardFunction
    predicate: Predicate
    input_arity: int
    output_position: int


class IntegraalStandardFunctionSource(ReadableData):
    """
    ReadableData for Integraal standard functions using computed predicates.

    Predicates are expected to be full IRIs. Function names are extracted by
    matching predicate names against the configured computed prefix IRIs.
    """

    def __init__(
        self,
        literal_factory: LiteralFactory,
        computed_prefixes: Mapping[str, str],
        predicates: Iterable[Predicate],
    ) -> None:
        self._literal_factory = literal_factory
        self._computed_prefixes = dict(computed_prefixes)
        self._base_iris = sorted(
            self._computed_prefixes.values(), key=len, reverse=True
        )
        self._functions = _STANDARD_FUNCTIONS
        self._bindings: dict[Predicate, FunctionBinding] = {}

        for predicate in predicates:
            binding = self._bind_predicate(predicate)
            if binding is not None:
                self._bindings[predicate] = binding

    def _bind_predicate(self, predicate: Predicate) -> Optional[FunctionBinding]:
        func_name = self._resolve_function_name(predicate.name)
        if func_name is None:
            return None
        function = self._functions.get(func_name)
        if function is None:
            return None
        input_arity = predicate.arity - 1
        if input_arity < function.min_inputs:
            return None
        if function.max_inputs is not None and input_arity > function.max_inputs:
            return None
        return FunctionBinding(
            function=function,
            predicate=predicate,
            input_arity=input_arity,
            output_position=predicate.arity - 1,
        )

    def _resolve_function_name(self, predicate_name: str) -> Optional[str]:
        for base in self._base_iris:
            if predicate_name.startswith(base):
                name = predicate_name[len(base) :]
                return name or None
        return None

    def get_predicates(self) -> Iterator[Predicate]:
        return iter(self._bindings.keys())

    def has_predicate(self, predicate: Predicate) -> bool:
        return predicate in self._bindings

    def get_atomic_pattern(self, predicate: Predicate) -> SimpleAtomicPattern:
        binding = self._bindings.get(predicate)
        if binding is None:
            raise KeyError(f"No function predicate: {predicate}")
        required_positions = _required_positions(binding)
        constraints = {pos: GROUND for pos in required_positions}
        return SimpleAtomicPattern(predicate, constraints)

    def can_evaluate(self, query: BasicQuery) -> bool:
        binding = self._bindings.get(query.predicate)
        if binding is None:
            return False
        bound_positions = set(query.bound_positions.keys())
        missing = [
            pos for pos in range(query.predicate.arity) if pos not in bound_positions
        ]

        if binding.function.solver is None:
            required = set(range(binding.input_arity))
            return required.issubset(bound_positions)

        return len(missing) <= 1

    def evaluate(self, query: BasicQuery) -> Iterator[tuple[Term, ...]]:
        binding = self._bindings.get(query.predicate)
        if binding is None:
            return iter(())

        if not self.can_evaluate(query):
            return iter(())

        arity = query.predicate.arity
        values: list[Optional[Term]] = [None] * arity
        for pos, term in query.bound_positions.items():
            values[pos] = term

        missing = [idx for idx, value in enumerate(values) if value is None]

        if binding.function.solver is None:
            return self._evaluate_forward(binding, values, query)

        if not missing:
            return self._evaluate_forward(binding, values, query)

        if len(missing) == 1:
            try:
                assignments = binding.function.solver(values, self._literal_factory)
            except Exception:
                return iter(())
            return iter(
                _answer_tuple(query, assignment)
                for assignment in assignments
                if _matches_bound(query.bound_positions, assignment)
                if _assignment_consistent(binding, assignment, self._literal_factory)
            )

        return iter(())

    def _evaluate_forward(
        self,
        binding: FunctionBinding,
        values: list[Optional[Term]],
        query: BasicQuery,
    ) -> Iterator[tuple[Term, ...]]:
        if any(values[pos] is None for pos in range(binding.input_arity)):
            return iter(())

        inputs = [values[pos] for pos in range(binding.input_arity)]
        try:
            output = binding.function.evaluator(
                [term for term in inputs if term is not None], self._literal_factory
            )
        except Exception:
            return iter(())

        assignment = list(values)
        output_pos = binding.output_position
        if assignment[output_pos] is not None and assignment[output_pos] != output:
            return iter(())
        assignment[output_pos] = output
        if any(term is None for term in assignment):
            return iter(())
        typed_assignment = cast(list[Term], assignment)
        return iter([_answer_tuple(query, typed_assignment)])


def _required_positions(binding: FunctionBinding) -> list[int]:
    if binding.function.solver is None:
        return list(range(binding.input_arity))
    return []


def _answer_tuple(query: BasicQuery, assignment: list[Term]) -> tuple[Term, ...]:
    answer_positions = sorted(query.answer_variables.keys())
    return tuple(assignment[pos] for pos in answer_positions)


def _matches_bound(bound_positions: Mapping[int, Term], assignment: list[Term]) -> bool:
    for pos, term in bound_positions.items():
        if assignment[pos] != term:
            return False
    return True


def _assignment_consistent(
    binding: FunctionBinding, assignment: list[Term], literal_factory: LiteralFactory
) -> bool:
    try:
        inputs = assignment[: binding.input_arity]
        output = binding.function.evaluator(inputs, literal_factory)
    except Exception:
        return False
    return assignment[binding.output_position] == output


def _flatten_if_collection(args: list[Term]) -> list[Term]:
    if len(args) == 1 and isinstance(args[0], Literal):
        value = args[0].value
        if isinstance(value, (list, tuple, set)):
            return list(value)
    return args


def _literal_value(term: Term, function_name: str) -> object:
    if not isinstance(term, Literal):
        raise ValueError(f"{function_name} expects literal arguments.")
    return term.value


def _extract_number(term: Term, function_name: str) -> tuple[float | int, bool]:
    value = _literal_value(term, function_name)
    if isinstance(value, bool):
        raise ValueError(f"{function_name} does not accept boolean values.")
    if isinstance(value, int):
        return value, True
    if isinstance(value, (float, Decimal)):
        return float(value), False
    if isinstance(value, str):
        try:
            return int(value), True
        except ValueError:
            return float(value), False
    raise ValueError(f"{function_name} expects numeric literals.")


def _parse_numbers(
    args: list[Term], function_name: str
) -> tuple[list[float | int], bool]:
    numbers: list[float | int] = []
    all_ints = True
    for term in args:
        num, is_int = _extract_number(term, function_name)
        numbers.append(num)
        if not is_int:
            all_ints = False
    return numbers, all_ints


def _number_literal(
    value: float | int, all_ints: bool, literal_factory: LiteralFactory
) -> Term:
    if all_ints and isinstance(value, int):
        return literal_factory.create(str(value), f"{XSD_PREFIX}integer")
    return literal_factory.create(str(float(value)), f"{XSD_PREFIX}double")


def _string_literal(value: str, literal_factory: LiteralFactory) -> Term:
    return literal_factory.create(value, f"{XSD_PREFIX}string")


def _bool_literal(value: bool, literal_factory: LiteralFactory) -> Term:
    return literal_factory.create(str(value).lower(), f"{XSD_PREFIX}boolean")


def _term_literal(value: object, literal_factory: LiteralFactory) -> Term:
    if isinstance(value, Term):
        return value
    if isinstance(value, bool):
        return _bool_literal(value, literal_factory)
    if isinstance(value, int):
        return literal_factory.create(str(value), f"{XSD_PREFIX}integer")
    if isinstance(value, Decimal):
        return literal_factory.create(str(value), f"{XSD_PREFIX}decimal")
    if isinstance(value, float):
        return literal_factory.create(str(value), f"{XSD_PREFIX}double")
    if isinstance(value, str):
        return _string_literal(value, literal_factory)
    if isinstance(value, (list, tuple, set, dict)):
        return literal_factory.create_from_value(value)
    return Constant(str(value))


def _sum(args: list[Term], literal_factory: LiteralFactory) -> Term:
    args = _flatten_if_collection(args)
    numbers, all_ints = _parse_numbers(args, "sum")
    if not numbers:
        raise ValueError("sum requires at least one argument.")
    total = sum(numbers)
    if all_ints and float(total).is_integer():
        total = int(total)
    return _number_literal(total, all_ints, literal_factory)


def _minus(args: list[Term], literal_factory: LiteralFactory) -> Term:
    args = _flatten_if_collection(args)
    numbers, all_ints = _parse_numbers(args, "minus")
    if not numbers:
        raise ValueError("minus requires at least one argument.")
    result = numbers[0]
    for num in numbers[1:]:
        result -= num
    if all_ints and float(result).is_integer():
        result = int(result)
    return _number_literal(result, all_ints, literal_factory)


def _product(args: list[Term], literal_factory: LiteralFactory) -> Term:
    args = _flatten_if_collection(args)
    numbers, all_ints = _parse_numbers(args, "product")
    if not numbers:
        raise ValueError("product requires at least one argument.")
    result: float | int = 1
    for num in numbers:
        result *= num
    if all_ints and float(result).is_integer():
        result = int(result)
    return _number_literal(result, all_ints, literal_factory)


def _divide(args: list[Term], literal_factory: LiteralFactory) -> Term:
    args = _flatten_if_collection(args)
    numbers, _ = _parse_numbers(args, "divide")
    if len(numbers) < 2:
        raise ValueError("divide requires at least two arguments.")
    result = float(numbers[0])
    for num in numbers[1:]:
        if num == 0:
            raise ValueError("division by zero.")
        result /= float(num)
    return literal_factory.create(str(result), f"{XSD_PREFIX}double")


def _min(args: list[Term], literal_factory: LiteralFactory) -> Term:
    args = _flatten_if_collection(args)
    numbers, all_ints = _parse_numbers(args, "min")
    if not numbers:
        raise ValueError("min requires at least one argument.")
    result = min(numbers)
    if all_ints and float(result).is_integer():
        result = int(result)
    return _number_literal(result, all_ints, literal_factory)


def _max(args: list[Term], literal_factory: LiteralFactory) -> Term:
    args = _flatten_if_collection(args)
    numbers, all_ints = _parse_numbers(args, "max")
    if not numbers:
        raise ValueError("max requires at least one argument.")
    result = max(numbers)
    if all_ints and float(result).is_integer():
        result = int(result)
    return _number_literal(result, all_ints, literal_factory)


def _average(args: list[Term], literal_factory: LiteralFactory) -> Term:
    args = _flatten_if_collection(args)
    numbers, _ = _parse_numbers(args, "average")
    if not numbers:
        raise ValueError("average requires at least one argument.")
    result = float(sum(numbers)) / len(numbers)
    return literal_factory.create(str(result), f"{XSD_PREFIX}double")


def _median(args: list[Term], literal_factory: LiteralFactory) -> Term:
    args = _flatten_if_collection(args)
    numbers, _ = _parse_numbers(args, "median")
    if not numbers:
        raise ValueError("median requires at least one argument.")
    values = sorted(float(n) for n in numbers)
    mid = len(values) // 2
    if len(values) % 2 == 0:
        result = (values[mid - 1] + values[mid]) / 2.0
    else:
        result = values[mid]
    return literal_factory.create(str(result), f"{XSD_PREFIX}double")


def _is_even(args: list[Term], literal_factory: LiteralFactory) -> Term:
    number, _ = _extract_number(args[0], "isEven")
    return _bool_literal(int(number) % 2 == 0, literal_factory)


def _is_odd(args: list[Term], literal_factory: LiteralFactory) -> Term:
    number, _ = _extract_number(args[0], "isOdd")
    return _bool_literal(int(number) % 2 != 0, literal_factory)


def _is_greater(args: list[Term], literal_factory: LiteralFactory) -> Term:
    left, _ = _extract_number(args[0], "isGreaterThan")
    right, _ = _extract_number(args[1], "isGreaterThan")
    return _bool_literal(float(left) > float(right), literal_factory)


def _is_greater_or_equal(args: list[Term], literal_factory: LiteralFactory) -> Term:
    left, _ = _extract_number(args[0], "isGreaterOrEqualsTo")
    right, _ = _extract_number(args[1], "isGreaterOrEqualsTo")
    return _bool_literal(float(left) >= float(right), literal_factory)


def _is_smaller(args: list[Term], literal_factory: LiteralFactory) -> Term:
    left, _ = _extract_number(args[0], "isSmallerThan")
    right, _ = _extract_number(args[1], "isSmallerThan")
    return _bool_literal(float(left) < float(right), literal_factory)


def _is_smaller_or_equal(args: list[Term], literal_factory: LiteralFactory) -> Term:
    left, _ = _extract_number(args[0], "isSmallerOrEqualsTo")
    right, _ = _extract_number(args[1], "isSmallerOrEqualsTo")
    return _bool_literal(float(left) <= float(right), literal_factory)


def _lex_greater(args: list[Term], literal_factory: LiteralFactory) -> Term:
    left = _literal_value(args[0], "isLexicographicallyGreaterThan")
    right = _literal_value(args[1], "isLexicographicallyGreaterThan")
    if not isinstance(left, str) or not isinstance(right, str):
        raise ValueError("Lexicographic comparison requires string literals.")
    return _bool_literal(left > right, literal_factory)


def _lex_greater_or_equal(args: list[Term], literal_factory: LiteralFactory) -> Term:
    left = _literal_value(args[0], "isLexicographicallyGreaterOrEqualsTo")
    right = _literal_value(args[1], "isLexicographicallyGreaterOrEqualsTo")
    if not isinstance(left, str) or not isinstance(right, str):
        raise ValueError("Lexicographic comparison requires string literals.")
    return _bool_literal(left >= right, literal_factory)


def _lex_smaller(args: list[Term], literal_factory: LiteralFactory) -> Term:
    left = _literal_value(args[0], "isLexicographicallySmallerThan")
    right = _literal_value(args[1], "isLexicographicallySmallerThan")
    if not isinstance(left, str) or not isinstance(right, str):
        raise ValueError("Lexicographic comparison requires string literals.")
    return _bool_literal(left < right, literal_factory)


def _lex_smaller_or_equal(args: list[Term], literal_factory: LiteralFactory) -> Term:
    left = _literal_value(args[0], "isLexicographicallySmallerOrEqualsTo")
    right = _literal_value(args[1], "isLexicographicallySmallerOrEqualsTo")
    if not isinstance(left, str) or not isinstance(right, str):
        raise ValueError("Lexicographic comparison requires string literals.")
    return _bool_literal(left <= right, literal_factory)


def _is_prime(args: list[Term], literal_factory: LiteralFactory) -> Term:
    number, _ = _extract_number(args[0], "isPrime")
    n = int(number)
    if n <= 1:
        return _bool_literal(False, literal_factory)
    if n <= 3:
        return _bool_literal(True, literal_factory)
    if n % 2 == 0 or n % 3 == 0:
        return _bool_literal(False, literal_factory)
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return _bool_literal(False, literal_factory)
        i += 6
    return _bool_literal(True, literal_factory)


def _equals(args: list[Term], literal_factory: LiteralFactory) -> Term:
    first = args[0]
    return _bool_literal(all(term == first for term in args), literal_factory)


def _concat(args: list[Term], literal_factory: LiteralFactory) -> Term:
    left = _literal_value(args[0], "concat")
    right = _literal_value(args[1], "concat")
    if isinstance(left, list) and isinstance(right, list):
        return literal_factory.create_from_value(left + right)
    if isinstance(left, str) and isinstance(right, str):
        return _string_literal(left + right, literal_factory)
    raise ValueError("concat expects two strings or two lists.")


def _to_lower(args: list[Term], literal_factory: LiteralFactory) -> Term:
    value = _literal_value(args[0], "toLowerCase")
    if not isinstance(value, str):
        raise ValueError("toLowerCase expects a string literal.")
    return _string_literal(value.lower(), literal_factory)


def _to_upper(args: list[Term], literal_factory: LiteralFactory) -> Term:
    value = _literal_value(args[0], "toUpperCase")
    if not isinstance(value, str):
        raise ValueError("toUpperCase expects a string literal.")
    return _string_literal(value.upper(), literal_factory)


def _replace(args: list[Term], literal_factory: LiteralFactory) -> Term:
    target = _literal_value(args[0], "replace")
    old = _literal_value(args[1], "replace")
    new = _literal_value(args[2], "replace")
    if (
        not isinstance(target, str)
        or not isinstance(old, str)
        or not isinstance(new, str)
    ):
        raise ValueError("replace expects string literals.")
    return _string_literal(target.replace(old, new), literal_factory)


def _length(args: list[Term], literal_factory: LiteralFactory) -> Term:
    value = _literal_value(args[0], "length")
    if not isinstance(value, str):
        raise ValueError("length expects a string literal.")
    return literal_factory.create(str(len(value)), f"{XSD_PREFIX}integer")


def _weighted_average(args: list[Term], literal_factory: LiteralFactory) -> Term:
    args = _flatten_if_collection(args)
    values = _weighted_values(args, "weightedAverage")
    total_weight = sum(abs(weight) for _, weight in values)
    if total_weight == 0:
        raise ValueError("Total weight cannot be zero.")
    total = sum(value * weight for value, weight in values)
    return literal_factory.create(str(total / total_weight), f"{XSD_PREFIX}double")


def _weighted_median(args: list[Term], literal_factory: LiteralFactory) -> Term:
    args = _flatten_if_collection(args)
    values = _weighted_values(args, "weightedMedian")
    values.sort(key=lambda x: x[0])
    total_weight = sum(weight for _, weight in values)
    if total_weight == 0:
        raise ValueError("Total weight cannot be zero.")
    half = total_weight / 2.0
    cumulative = 0.0
    for idx, (value, weight) in enumerate(values):
        cumulative += weight
        if cumulative > half:
            return literal_factory.create(str(value), f"{XSD_PREFIX}double")
        if cumulative == half and idx + 1 < len(values):
            next_value = values[idx + 1][0]
            return literal_factory.create(
                str((value + next_value) / 2.0), f"{XSD_PREFIX}double"
            )
    raise ValueError("Could not compute weighted median.")


def _weighted_values(args: list[Term], function_name: str) -> list[tuple[float, float]]:
    values: list[tuple[float, float]] = []
    if _all_pairs(args):
        for term in args:
            pair = _literal_value(term, function_name)
            if not isinstance(pair, (list, tuple)) or len(pair) != 2:
                raise ValueError(f"{function_name} expects pairs.")
            value_term, weight_term = pair
            value, _ = _extract_number(value_term, function_name)
            weight, _ = _extract_number(weight_term, function_name)
            if weight < 0:
                raise ValueError("Weights cannot be negative.")
            values.append((float(value), float(weight)))
        return values

    if len(args) % 2 != 0:
        raise ValueError(f"{function_name} expects value-weight pairs.")
    for i in range(0, len(args), 2):
        value, _ = _extract_number(args[i], function_name)
        weight, _ = _extract_number(args[i + 1], function_name)
        if weight < 0:
            raise ValueError("Weights cannot be negative.")
        values.append((float(value), float(weight)))
    return values


def _all_pairs(args: list[Term]) -> bool:
    for term in args:
        if not isinstance(term, Literal):
            return False
        value = term.value
        if not isinstance(value, (list, tuple)) or len(value) != 2:
            return False
    return True


def _set_builder(args: list[Term], literal_factory: LiteralFactory) -> Term:
    return literal_factory.create_from_value(set(args))


def _is_subset(args: list[Term], literal_factory: LiteralFactory) -> Term:
    left = _literal_value(args[0], "isSubset")
    right = _literal_value(args[1], "isSubset")
    if not isinstance(left, set) or not isinstance(right, set):
        raise ValueError("isSubset expects set literals.")
    return _bool_literal(left.issubset(right), literal_factory)


def _is_strict_subset(args: list[Term], literal_factory: LiteralFactory) -> Term:
    left = _literal_value(args[0], "isStrictSubset")
    right = _literal_value(args[1], "isStrictSubset")
    if not isinstance(left, set) or not isinstance(right, set):
        raise ValueError("isStrictSubset expects set literals.")
    return _bool_literal(left < right, literal_factory)


def _union(args: list[Term], literal_factory: LiteralFactory) -> Term:
    args = _flatten_if_collection(args)
    union_set: set[object] = set()
    for term in args:
        value = _literal_value(term, "union")
        if not isinstance(value, (set, list, tuple)):
            raise ValueError("union expects collection literals.")
        union_set.update(value)
    return literal_factory.create_from_value(union_set)


def _size(args: list[Term], literal_factory: LiteralFactory) -> Term:
    value = _literal_value(args[0], "size")
    if isinstance(value, (set, list, tuple, dict)):
        return literal_factory.create(str(len(value)), f"{XSD_PREFIX}integer")
    raise ValueError("size expects a collection or map literal.")


def _intersection(args: list[Term], literal_factory: LiteralFactory) -> Term:
    args = _flatten_if_collection(args)
    intersection_set: Optional[set[object]] = None
    for term in args:
        value = _literal_value(term, "intersection")
        if not isinstance(value, (set, list, tuple)):
            raise ValueError("intersection expects collection literals.")
        current = set(value)
        if intersection_set is None:
            intersection_set = current
        else:
            intersection_set &= current
    if intersection_set is None:
        raise ValueError("intersection requires at least one collection.")
    return literal_factory.create_from_value(intersection_set)


def _contains(args: list[Term], literal_factory: LiteralFactory) -> Term:
    container = _literal_value(args[0], "contains")
    if isinstance(container, (list, tuple, set)):
        return _bool_literal(args[1] in container, literal_factory)
    if isinstance(container, str):
        value = _literal_value(args[1], "contains")
        if not isinstance(value, str):
            raise ValueError("contains expects a string literal as second argument.")
        return _bool_literal(value in container, literal_factory)
    raise ValueError("contains expects a collection or string literal.")


def _is_empty(args: list[Term], literal_factory: LiteralFactory) -> Term:
    value = _literal_value(args[0], "isEmpty")
    if isinstance(value, (list, tuple, set, dict)):
        return _bool_literal(len(value) == 0, literal_factory)
    if isinstance(value, str):
        return _bool_literal(value == "", literal_factory)
    raise ValueError("isEmpty expects a collection or string literal.")


def _is_blank(args: list[Term], literal_factory: LiteralFactory) -> Term:
    value = _literal_value(args[0], "isBlank")
    if not isinstance(value, str):
        raise ValueError("isBlank expects a string literal.")
    return _bool_literal(value.strip() == "", literal_factory)


def _is_numeric(args: list[Term], literal_factory: LiteralFactory) -> Term:
    value = _literal_value(args[0], "isNumeric")
    if isinstance(value, (int, float, Decimal)):
        return _bool_literal(True, literal_factory)
    if isinstance(value, str):
        try:
            parsed = float(value)
            return _bool_literal(
                parsed == parsed and parsed not in (float("inf"), float("-inf")),
                literal_factory,
            )
        except ValueError:
            return _bool_literal(False, literal_factory)
    return _bool_literal(False, literal_factory)


def _to_string(args: list[Term], literal_factory: LiteralFactory) -> Term:
    return _string_literal(str(args[0]), literal_factory)


def _to_string_with_datatype(args: list[Term], literal_factory: LiteralFactory) -> Term:
    term = args[0]
    result = type(term).__name__
    if isinstance(term, Literal):
        result += f"<{type(term.value).__name__}>"
    result += f" {term}"
    return _string_literal(result, literal_factory)


def _to_int(args: list[Term], literal_factory: LiteralFactory) -> Term:
    value = _literal_value(args[0], "toInt")
    if isinstance(value, bool):
        return literal_factory.create("1" if value else "0", f"{XSD_PREFIX}integer")
    if isinstance(value, int):
        return literal_factory.create(str(value), f"{XSD_PREFIX}integer")
    if isinstance(value, float):
        return literal_factory.create(str(int(value)), f"{XSD_PREFIX}integer")
    if isinstance(value, str):
        return literal_factory.create(str(int(value)), f"{XSD_PREFIX}integer")
    raise ValueError("toInt expects a numeric, boolean, or string literal.")


def _to_float(args: list[Term], literal_factory: LiteralFactory) -> Term:
    value = _literal_value(args[0], "toFloat")
    if isinstance(value, bool):
        return literal_factory.create("1.0" if value else "0.0", f"{XSD_PREFIX}double")
    if isinstance(value, (int, float, Decimal)):
        return literal_factory.create(str(float(value)), f"{XSD_PREFIX}double")
    if isinstance(value, str):
        return literal_factory.create(str(float(value)), f"{XSD_PREFIX}double")
    raise ValueError("toFloat expects a numeric, boolean, or string literal.")


def _to_boolean(args: list[Term], literal_factory: LiteralFactory) -> Term:
    value = _literal_value(args[0], "toBoolean")
    if isinstance(value, bool):
        return _bool_literal(value, literal_factory)
    if isinstance(value, (int, float, Decimal)):
        return _bool_literal(float(value) != 0, literal_factory)
    if isinstance(value, str):
        trimmed = value.strip()
        if trimmed == "":
            return _bool_literal(False, literal_factory)
        if trimmed.lower() in {"false", "0"}:
            return _bool_literal(False, literal_factory)
        return _bool_literal(True, literal_factory)
    if isinstance(value, (list, tuple, set, dict)):
        return _bool_literal(len(value) != 0, literal_factory)
    return _bool_literal(False, literal_factory)


def _to_set(args: list[Term], literal_factory: LiteralFactory) -> Term:
    value = _literal_value(args[0], "toSet")
    if not isinstance(value, (list, tuple, set)):
        raise ValueError("toSet expects a collection literal.")
    return literal_factory.create_from_value(set(value))


def _to_tuple(args: list[Term], literal_factory: LiteralFactory) -> Term:
    value = _literal_value(args[0], "toTuple")
    if not isinstance(value, (list, tuple, set)):
        raise ValueError("toTuple expects a collection literal.")
    return literal_factory.create_from_value(list(value))


def _dict_builder(args: list[Term], literal_factory: LiteralFactory) -> Term:
    mapping: dict[Term, Term] = {}
    for term in args:
        value = _literal_value(term, "dict")
        if not isinstance(value, (list, tuple)) or len(value) != 2:
            raise ValueError("dict expects pairs (tuple of size 2).")
        key, val = value
        if not isinstance(key, Term) or not isinstance(val, Term):
            raise ValueError("dict expects pairs of terms.")
        mapping[key] = val
    return literal_factory.create_from_value(mapping)


def _merge_dicts(args: list[Term], literal_factory: LiteralFactory) -> Term:
    left = _literal_value(args[0], "mergeDicts")
    right = _literal_value(args[1], "mergeDicts")
    if not isinstance(left, dict) or not isinstance(right, dict):
        raise ValueError("mergeDicts expects dictionary literals.")
    merged = dict(left)
    merged.update(right)
    return literal_factory.create_from_value(merged)


def _dict_keys(args: list[Term], literal_factory: LiteralFactory) -> Term:
    mapping = _literal_value(args[0], "dictKeys")
    if not isinstance(mapping, dict):
        raise ValueError("dictKeys expects a dictionary literal.")
    return literal_factory.create_from_value(set(mapping.keys()))


def _dict_values(args: list[Term], literal_factory: LiteralFactory) -> Term:
    mapping = _literal_value(args[0], "dictValues")
    if not isinstance(mapping, dict):
        raise ValueError("dictValues expects a dictionary literal.")
    return literal_factory.create_from_value(list(mapping.values()))


def _get_value(args: list[Term], literal_factory: LiteralFactory) -> Term:
    container = _literal_value(args[0], "get")
    if isinstance(container, (list, tuple)):
        index_value = _literal_value(args[1], "get")
        if not isinstance(index_value, (int, float, Decimal, str)):
            raise ValueError("get expects a numeric index for lists.")
        index = int(index_value)
        if index < 0 or index >= len(container):
            raise ValueError("Index out of bounds.")
        value = container[index]
        if isinstance(value, Term):
            return value
        return _term_literal(value, literal_factory)
    if isinstance(container, dict):
        return container.get(args[1], Constant("null"))
    raise ValueError("get expects a list or dictionary literal.")


def _tuple_builder(args: list[Term], literal_factory: LiteralFactory) -> Term:
    return literal_factory.create_from_value(list(args))


def _contains_key(args: list[Term], literal_factory: LiteralFactory) -> Term:
    mapping = _literal_value(args[0], "containsKey")
    if not isinstance(mapping, dict):
        raise ValueError("containsKey expects a dictionary literal.")
    return _bool_literal(args[1] in mapping, literal_factory)


def _contains_value(args: list[Term], literal_factory: LiteralFactory) -> Term:
    mapping = _literal_value(args[0], "containsValue")
    if not isinstance(mapping, dict):
        raise ValueError("containsValue expects a dictionary literal.")
    return _bool_literal(args[1] in mapping.values(), literal_factory)


def _solve_sum(
    values: list[Optional[Term]], literal_factory: LiteralFactory
) -> Iterable[list[Term]]:
    return _solve_linear(values, literal_factory, "sum")


def _solve_minus(
    values: list[Optional[Term]], literal_factory: LiteralFactory
) -> Iterable[list[Term]]:
    return _solve_linear(values, literal_factory, "minus")


def _solve_product(
    values: list[Optional[Term]], literal_factory: LiteralFactory
) -> Iterable[list[Term]]:
    return _solve_linear(values, literal_factory, "product")


def _solve_divide(
    values: list[Optional[Term]], literal_factory: LiteralFactory
) -> Iterable[list[Term]]:
    return _solve_linear(values, literal_factory, "divide")


def _solve_average(
    values: list[Optional[Term]], literal_factory: LiteralFactory
) -> Iterable[list[Term]]:
    return _solve_linear(values, literal_factory, "average")


def _solve_linear(
    values: list[Optional[Term]],
    literal_factory: LiteralFactory,
    function_name: str,
) -> Iterable[list[Term]]:
    arity = len(values)
    output_pos = arity - 1
    missing = [idx for idx, value in enumerate(values) if value is None]
    if len(missing) != 1:
        return []
    missing_pos = missing[0]

    inputs = values[:output_pos]
    output = values[output_pos]

    numeric_inputs: list[float | int] = []
    all_ints = True
    for term in inputs:
        if term is None:
            numeric_inputs.append(0)
            continue
        num, is_int = _extract_number(term, function_name)
        numeric_inputs.append(num)
        if not is_int:
            all_ints = False

    output_value = None
    if output is not None:
        output_value, output_is_int = _extract_number(output, function_name)
        if not output_is_int:
            all_ints = False

    def make_assignment(missing_value: float | int) -> list[Term]:
        assignment: list[Term] = []
        for idx, term in enumerate(values):
            if idx == missing_pos:
                assignment.append(
                    _number_literal(
                        int(missing_value)
                        if all_ints and float(missing_value).is_integer()
                        else float(missing_value),
                        all_ints,
                        literal_factory,
                    )
                )
            else:
                assignment.append(term if term is not None else Constant("null"))
        return assignment

    if function_name == "sum":
        if missing_pos == output_pos:
            total = sum(numeric_inputs)
            return [make_assignment(total)]
        if output_value is None:
            return []
        total_known = sum(
            num for idx, num in enumerate(numeric_inputs) if idx != missing_pos
        )
        return [make_assignment(output_value - total_known)]

    if function_name == "minus":
        if missing_pos == output_pos:
            result = numeric_inputs[0]
            for num in numeric_inputs[1:]:
                result -= num
            return [make_assignment(result)]
        if output_value is None:
            return []
        if missing_pos == 0:
            total = output_value
            for num in numeric_inputs[1:]:
                total += num
            return [make_assignment(total)]
        subtotal = numeric_inputs[0]
        for idx, num in enumerate(numeric_inputs[1:], start=1):
            if idx != missing_pos:
                subtotal -= num
        return [make_assignment(subtotal - output_value)]

    if function_name == "product":
        if missing_pos == output_pos:
            product_result: float | int = 1
            for num in numeric_inputs:
                product_result *= num
            return [make_assignment(product_result)]
        if output_value is None:
            return []
        product_known: float | int = 1
        for idx, num in enumerate(numeric_inputs):
            if idx != missing_pos:
                product_known *= num
        if product_known == 0:
            return []
        return [make_assignment(output_value / product_known)]

    if function_name == "divide":
        if missing_pos == output_pos:
            result = float(numeric_inputs[0])
            for num in numeric_inputs[1:]:
                if num == 0:
                    return []
                result /= float(num)
            return [make_assignment(result)]
        if output_value is None:
            return []
        if missing_pos == 0:
            denom = 1.0
            for num in numeric_inputs[1:]:
                denom *= float(num)
            return [make_assignment(float(output_value) * denom)]
        denom = float(output_value)
        for idx, num in enumerate(numeric_inputs[1:], start=1):
            if idx != missing_pos:
                denom *= float(num)
        if denom == 0:
            return []
        return [make_assignment(float(numeric_inputs[0]) / denom)]

    if function_name == "average":
        count = len(numeric_inputs)
        if missing_pos == output_pos:
            result = float(sum(numeric_inputs)) / count
            return [make_assignment(result)]
        if output_value is None:
            return []
        total_known = sum(
            num for idx, num in enumerate(numeric_inputs) if idx != missing_pos
        )
        missing_value = float(output_value) * count - total_known
        return [make_assignment(missing_value)]

    return []


def _standard_functions() -> dict[str, StandardFunction]:
    return {
        "sum": StandardFunction("sum", 1, None, _sum, _solve_sum),
        "min": StandardFunction("min", 1, None, _min),
        "max": StandardFunction("max", 1, None, _max),
        "minus": StandardFunction("minus", 1, None, _minus, _solve_minus),
        "product": StandardFunction("product", 1, None, _product, _solve_product),
        "divide": StandardFunction("divide", 2, None, _divide, _solve_divide),
        "average": StandardFunction("average", 1, None, _average, _solve_average),
        "median": StandardFunction("median", 1, None, _median),
        "isEven": StandardFunction("isEven", 1, 1, _is_even),
        "isOdd": StandardFunction("isOdd", 1, 1, _is_odd),
        "isGreaterThan": StandardFunction("isGreaterThan", 2, 2, _is_greater),
        "isGreaterOrEqualsTo": StandardFunction(
            "isGreaterOrEqualsTo", 2, 2, _is_greater_or_equal
        ),
        "isSmallerThan": StandardFunction("isSmallerThan", 2, 2, _is_smaller),
        "isSmallerOrEqualsTo": StandardFunction(
            "isSmallerOrEqualsTo", 2, 2, _is_smaller_or_equal
        ),
        "isLexicographicallyGreaterThan": StandardFunction(
            "isLexicographicallyGreaterThan", 2, 2, _lex_greater
        ),
        "isLexicographicallyGreaterOrEqualsTo": StandardFunction(
            "isLexicographicallyGreaterOrEqualsTo", 2, 2, _lex_greater_or_equal
        ),
        "isLexicographicallySmallerThan": StandardFunction(
            "isLexicographicallySmallerThan", 2, 2, _lex_smaller
        ),
        "isLexicographicallySmallerOrEqualsTo": StandardFunction(
            "isLexicographicallySmallerOrEqualsTo", 2, 2, _lex_smaller_or_equal
        ),
        "isPrime": StandardFunction("isPrime", 1, 1, _is_prime),
        "equals": StandardFunction("equals", 2, None, _equals),
        "concat": StandardFunction("concat", 2, 2, _concat),
        "toLowerCase": StandardFunction("toLowerCase", 1, 1, _to_lower),
        "toUpperCase": StandardFunction("toUpperCase", 1, 1, _to_upper),
        "replace": StandardFunction("replace", 3, 3, _replace),
        "length": StandardFunction("length", 1, 1, _length),
        "weightedAverage": StandardFunction(
            "weightedAverage", 2, None, _weighted_average
        ),
        "weightedMedian": StandardFunction("weightedMedian", 2, None, _weighted_median),
        "set": StandardFunction("set", 0, None, _set_builder),
        "isSubset": StandardFunction("isSubset", 2, 2, _is_subset),
        "isStrictSubset": StandardFunction("isStrictSubset", 2, 2, _is_strict_subset),
        "union": StandardFunction("union", 1, None, _union),
        "size": StandardFunction("size", 1, 1, _size),
        "intersection": StandardFunction("intersection", 1, None, _intersection),
        "contains": StandardFunction("contains", 2, 2, _contains),
        "isEmpty": StandardFunction("isEmpty", 1, 1, _is_empty),
        "isBlank": StandardFunction("isBlank", 1, 1, _is_blank),
        "isNumeric": StandardFunction("isNumeric", 1, 1, _is_numeric),
        "toString": StandardFunction("toString", 1, 1, _to_string),
        "toStringWithDatatype": StandardFunction(
            "toStringWithDatatype", 1, 1, _to_string_with_datatype
        ),
        "toInt": StandardFunction("toInt", 1, 1, _to_int),
        "toFloat": StandardFunction("toFloat", 1, 1, _to_float),
        "toBoolean": StandardFunction("toBoolean", 1, 1, _to_boolean),
        "toSet": StandardFunction("toSet", 1, 1, _to_set),
        "toTuple": StandardFunction("toTuple", 1, 1, _to_tuple),
        "dict": StandardFunction("dict", 0, None, _dict_builder),
        "mergeDicts": StandardFunction("mergeDicts", 2, 2, _merge_dicts),
        "dictKeys": StandardFunction("dictKeys", 1, 1, _dict_keys),
        "dictValues": StandardFunction("dictValues", 1, 1, _dict_values),
        "get": StandardFunction("get", 2, 2, _get_value),
        "tuple": StandardFunction("tuple", 0, None, _tuple_builder),
        "containsKey": StandardFunction("containsKey", 2, 2, _contains_key),
        "containsValue": StandardFunction("containsValue", 2, 2, _contains_value),
    }


_STANDARD_FUNCTIONS = _standard_functions()


def standard_function_definitions() -> dict[str, StandardFunction]:
    """Return the standard Integraal function definitions."""
    return dict(_STANDARD_FUNCTIONS)
