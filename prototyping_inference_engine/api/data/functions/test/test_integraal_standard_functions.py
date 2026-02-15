"""
Tests for Integraal standard functions.
"""

from __future__ import annotations

import unittest

from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.factory.literal_factory import (
    LiteralFactory,
)
from prototyping_inference_engine.api.atom.term.literal_config import LiteralConfig
from prototyping_inference_engine.api.atom.term.storage.dict_storage import DictStorage
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.data.basic_query import BasicQuery
from prototyping_inference_engine.api.data.functions.integraal_standard_functions import (
    IntegraalStandardFunctionSource,
    standard_function_definitions,
)

BASE_IRI = "http://example.org/functions#"


class TestIntegraalStandardFunctions(unittest.TestCase):
    def setUp(self) -> None:
        self.literal_factory = LiteralFactory(DictStorage(), LiteralConfig.default())

    def _literal(self, lexical: str, datatype: str):
        return self.literal_factory.create(lexical, datatype)

    def _literal_from_value(self, value: object):
        return self.literal_factory.create_from_value(value)

    def _evaluate(self, name: str, inputs, output=None):
        predicate = Predicate(BASE_IRI + name, len(inputs) + 1)
        source = IntegraalStandardFunctionSource(
            self.literal_factory, {"ig": BASE_IRI}, [predicate]
        )
        bound_positions = {idx: term for idx, term in enumerate(inputs)}
        answer_variables = {}
        if output is None:
            answer_variables[len(inputs)] = Variable("X")
        else:
            bound_positions[len(inputs)] = output
        query = BasicQuery(predicate, bound_positions, answer_variables)
        return list(source.evaluate(query))

    def _evaluate_single(self, name: str, inputs):
        results = self._evaluate(name, inputs)
        self.assertTrue(results)
        return results[0][0]

    def _evaluate_with_bound_positions(
        self,
        name: str,
        arity: int,
        bound_positions: dict[int, Term],
        answer_positions: list[int],
    ):
        predicate = Predicate(BASE_IRI + name, arity)
        source = IntegraalStandardFunctionSource(
            self.literal_factory, {"ig": BASE_IRI}, [predicate]
        )
        answer_variables = {
            pos: Variable(f"X{pos}") for pos in sorted(answer_positions)
        }
        query = BasicQuery(predicate, bound_positions, answer_variables)
        return list(source.evaluate(query))

    def test_numeric_functions(self):
        one = self._literal("1", "xsd:integer")
        two = self._literal("2", "xsd:integer")
        three = self._literal("3", "xsd:integer")
        eight = self._literal("8", "xsd:double")
        two_double = self._literal("2", "xsd:double")

        self.assertEqual(
            self._evaluate_single("sum", [one, two, three]),
            self._literal("6", "xsd:integer"),
        )
        self.assertEqual(
            self._evaluate_single("min", [three, two]),
            self._literal("2", "xsd:integer"),
        )
        self.assertEqual(
            self._evaluate_single("max", [three, two]),
            self._literal("3", "xsd:integer"),
        )
        self.assertEqual(
            self._evaluate_single("minus", [three, two]),
            self._literal("1", "xsd:integer"),
        )
        self.assertEqual(
            self._evaluate_single("product", [two, three]),
            self._literal("6", "xsd:integer"),
        )
        self.assertEqual(
            self._evaluate_single("divide", [eight, two_double]),
            self._literal("4", "xsd:double"),
        )
        self.assertEqual(
            self._evaluate_single("power", [two, three]),
            self._literal("8", "xsd:integer"),
        )
        self.assertEqual(
            self._evaluate_single("average", [two, three]),
            self._literal("2.5", "xsd:double"),
        )
        self.assertEqual(
            self._evaluate_single("median", [one, three, two]),
            self._literal("2", "xsd:double"),
        )

    def test_numeric_functions_with_collection_argument(self):
        values = self._literal_from_value(
            [
                self._literal("1", "xsd:integer"),
                self._literal("2", "xsd:integer"),
            ]
        )
        results = self._evaluate(
            "sum", [values], output=self._literal("3", "xsd:integer")
        )
        self.assertEqual(results, [tuple()])

    def test_numeric_solver_missing_input(self):
        one = self._literal("1", "xsd:integer")
        three = self._literal("3", "xsd:integer")
        seven = self._literal("7", "xsd:integer")
        results = self._evaluate_with_bound_positions(
            "sum",
            4,
            {0: one, 2: three, 3: seven},
            [1],
        )
        self.assertEqual(results[0][0], self._literal("3", "xsd:integer"))

    def test_divide_by_zero_returns_no_result(self):
        one = self._literal("1", "xsd:integer")
        zero = self._literal("0", "xsd:integer")
        self.assertEqual(self._evaluate("divide", [one, zero]), [])

    def test_numeric_functions_invalid_arguments_return_no_result(self):
        invalid = self._literal("invalid", "xsd:string")
        numeric = self._literal("2", "xsd:integer")
        cases = [
            ("sum", [invalid]),
            ("min", [invalid]),
            ("max", [invalid]),
            ("minus", [invalid, numeric]),
            ("product", [invalid, numeric]),
            ("divide", [invalid, numeric]),
            ("power", [invalid, numeric]),
            ("average", [invalid]),
            ("median", [invalid]),
        ]
        for name, inputs in cases:
            with self.subTest(name=name):
                self.assertEqual(self._evaluate(name, inputs), [])

    def test_predicates_boolean(self):
        two = self._literal("2", "xsd:integer")
        three = self._literal("3", "xsd:integer")
        self.assertEqual(
            self._evaluate_single("isEven", [two]),
            self._literal("true", "xsd:boolean"),
        )
        self.assertEqual(
            self._evaluate_single("isOdd", [three]),
            self._literal("true", "xsd:boolean"),
        )
        self.assertEqual(
            self._evaluate_single("isGreaterThan", [three, two]),
            self._literal("true", "xsd:boolean"),
        )
        self.assertEqual(
            self._evaluate_single("isGreaterOrEqualsTo", [two, two]),
            self._literal("true", "xsd:boolean"),
        )
        self.assertEqual(
            self._evaluate_single("isSmallerThan", [two, three]),
            self._literal("true", "xsd:boolean"),
        )
        self.assertEqual(
            self._evaluate_single("isSmallerOrEqualsTo", [two, two]),
            self._literal("true", "xsd:boolean"),
        )

    def test_numeric_predicates_invalid_arguments_return_no_result(self):
        invalid = self._literal("invalid", "xsd:string")
        numeric = self._literal("2", "xsd:integer")
        non_literal = Constant("a")
        cases = [
            ("isEven", [invalid]),
            ("isOdd", [invalid]),
            ("isEven", [non_literal]),
            ("isOdd", [non_literal]),
            ("isGreaterThan", [invalid, numeric]),
            ("isGreaterThan", [numeric, invalid]),
            ("isGreaterOrEqualsTo", [invalid, numeric]),
            ("isGreaterOrEqualsTo", [numeric, invalid]),
            ("isSmallerThan", [invalid, numeric]),
            ("isSmallerThan", [numeric, invalid]),
            ("isSmallerOrEqualsTo", [invalid, numeric]),
            ("isSmallerOrEqualsTo", [numeric, invalid]),
        ]
        for name, inputs in cases:
            with self.subTest(name=name):
                self.assertEqual(self._evaluate(name, inputs), [])

    def test_lexicographic_predicates(self):
        a = self._literal("a", "xsd:string")
        b = self._literal("b", "xsd:string")
        self.assertEqual(
            self._evaluate_single("isLexicographicallyGreaterThan", [b, a]),
            self._literal("true", "xsd:boolean"),
        )
        self.assertEqual(
            self._evaluate_single("isLexicographicallyGreaterOrEqualsTo", [a, a]),
            self._literal("true", "xsd:boolean"),
        )
        self.assertEqual(
            self._evaluate_single("isLexicographicallySmallerThan", [a, b]),
            self._literal("true", "xsd:boolean"),
        )
        self.assertEqual(
            self._evaluate_single("isLexicographicallySmallerOrEqualsTo", [a, a]),
            self._literal("true", "xsd:boolean"),
        )

    def test_lexicographic_invalid_arguments_return_no_result(self):
        not_string = self._literal("1", "xsd:integer")
        a = self._literal("a", "xsd:string")
        non_literal = Constant("a")
        cases = [
            ("isLexicographicallyGreaterThan", [not_string, a]),
            ("isLexicographicallyGreaterThan", [a, not_string]),
            ("isLexicographicallyGreaterThan", [non_literal, a]),
            ("isLexicographicallyGreaterThan", [a, non_literal]),
            ("isLexicographicallyGreaterOrEqualsTo", [not_string, a]),
            ("isLexicographicallyGreaterOrEqualsTo", [a, not_string]),
            ("isLexicographicallySmallerThan", [not_string, a]),
            ("isLexicographicallySmallerThan", [a, not_string]),
            ("isLexicographicallySmallerOrEqualsTo", [not_string, a]),
            ("isLexicographicallySmallerOrEqualsTo", [a, not_string]),
        ]
        for name, inputs in cases:
            with self.subTest(name=name):
                self.assertEqual(self._evaluate(name, inputs), [])

    def test_misc_numeric_predicates(self):
        seven = self._literal("7", "xsd:integer")
        self.assertEqual(
            self._evaluate_single("isPrime", [seven]),
            self._literal("true", "xsd:boolean"),
        )
        one = self._literal("1", "xsd:integer")
        self.assertEqual(
            self._evaluate_single("isPrime", [one]),
            self._literal("false", "xsd:boolean"),
        )
        self.assertEqual(
            self._evaluate_single("equals", [seven, seven]),
            self._literal("true", "xsd:boolean"),
        )
        self.assertEqual(
            self._evaluate_single("equals", [seven, one]),
            self._literal("false", "xsd:boolean"),
        )

    def test_is_prime_edge_cases(self):
        negative = self._literal("-1", "xsd:integer")
        zero = self._literal("0", "xsd:integer")
        self.assertEqual(
            self._evaluate_single("isPrime", [negative]),
            self._literal("false", "xsd:boolean"),
        )
        self.assertEqual(
            self._evaluate_single("isPrime", [zero]),
            self._literal("false", "xsd:boolean"),
        )

    def test_equals_multiple_arguments(self):
        a = Constant("a")
        b = Constant("b")
        self.assertEqual(
            self._evaluate_single("equals", [a, a, a]),
            self._literal("true", "xsd:boolean"),
        )
        self.assertEqual(
            self._evaluate_single("equals", [a, b, a]),
            self._literal("false", "xsd:boolean"),
        )

    def test_string_functions(self):
        hello = self._literal("Hello", "xsd:string")
        world = self._literal("World", "xsd:string")
        self.assertEqual(
            self._evaluate_single("concat", [hello, world]),
            self._literal("HelloWorld", "xsd:string"),
        )
        list_concat = self._evaluate_single(
            "concat",
            [
                self._literal_from_value([hello]),
                self._literal_from_value([world]),
            ],
        )
        self.assertEqual(list_concat.value, [hello, world])
        self.assertEqual(
            self._evaluate("concat", [hello, self._literal("1", "xsd:integer")]),
            [],
        )
        self.assertEqual(
            self._evaluate(
                "concat",
                [self._literal_from_value([hello]), self._literal("x", "xsd:string")],
            ),
            [],
        )
        self.assertEqual(
            self._evaluate_single("toLowerCase", [hello]),
            self._literal("hello", "xsd:string"),
        )
        self.assertEqual(
            self._evaluate_single("toUpperCase", [hello]),
            self._literal("HELLO", "xsd:string"),
        )
        self.assertEqual(
            self._evaluate_single(
                "replace",
                [
                    self._literal("aba", "xsd:string"),
                    self._literal("a", "xsd:string"),
                    self._literal("c", "xsd:string"),
                ],
            ),
            self._literal("cbc", "xsd:string"),
        )
        self.assertEqual(
            self._evaluate_single("length", [hello]),
            self._literal("5", "xsd:integer"),
        )

    def test_string_predicate_errors(self):
        self.assertEqual(
            self._evaluate("toLowerCase", [self._literal("1", "xsd:integer")]),
            [],
        )
        self.assertEqual(
            self._evaluate("length", [self._literal("1", "xsd:integer")]),
            [],
        )

    def test_weighted_functions(self):
        pair1 = self._literal_from_value(
            [self._literal("3", "xsd:integer"), self._literal("1", "xsd:integer")]
        )
        pair2 = self._literal_from_value(
            [self._literal("6", "xsd:integer"), self._literal("3", "xsd:integer")]
        )
        self.assertEqual(
            self._evaluate_single("weightedAverage", [pair1, pair2]),
            self._literal("5.25", "xsd:double"),
        )
        self.assertEqual(
            self._evaluate_single("weightedMedian", [pair1, pair2]),
            self._literal("6", "xsd:double"),
        )

    def test_weighted_functions_edge_cases(self):
        pair1 = self._literal_from_value(
            [self._literal("2", "xsd:integer"), self._literal("1", "xsd:integer")]
        )
        pair2 = self._literal_from_value(
            [self._literal("4", "xsd:integer"), self._literal("1", "xsd:integer")]
        )
        self.assertEqual(
            self._evaluate_single("weightedMedian", [pair1, pair2]),
            self._literal("3.0", "xsd:double"),
        )
        negative_weight = self._literal_from_value(
            [self._literal("4", "xsd:integer"), self._literal("-1", "xsd:integer")]
        )
        self.assertEqual(
            self._evaluate("weightedAverage", [negative_weight]),
            [],
        )

    def test_collection_functions(self):
        a = Constant("a")
        b = Constant("b")
        c = Constant("c")
        set_term = self._evaluate_single("set", [a, b])
        self.assertEqual(set_term.value, {a, b})

        subset = self._literal_from_value({a})
        superset = self._literal_from_value({a, b})
        self.assertEqual(
            self._evaluate_single("isSubset", [subset, superset]),
            self._literal("true", "xsd:boolean"),
        )
        self.assertEqual(
            self._evaluate_single("isStrictSubset", [subset, superset]),
            self._literal("true", "xsd:boolean"),
        )

        union = self._evaluate_single(
            "union",
            [self._literal_from_value({a}), self._literal_from_value({b})],
        )
        self.assertEqual(union.value, {a, b})

        intersection = self._evaluate_single(
            "intersection",
            [
                self._literal_from_value({a, b}),
                self._literal_from_value({b, c}),
            ],
        )
        self.assertEqual(intersection.value, {b})

        self.assertEqual(
            self._evaluate_single("size", [self._literal_from_value({a, b})]),
            self._literal("2", "xsd:integer"),
        )

        contains = self._evaluate_single(
            "contains",
            [self._literal_from_value([a, b]), a],
        )
        self.assertEqual(contains, self._literal("true", "xsd:boolean"))

        contains_string = self._evaluate_single(
            "contains",
            [self._literal("hello", "xsd:string"), self._literal("ell", "xsd:string")],
        )
        self.assertEqual(contains_string, self._literal("true", "xsd:boolean"))

        self.assertEqual(
            self._evaluate_single("isEmpty", [self._literal_from_value([])]),
            self._literal("true", "xsd:boolean"),
        )
        self.assertEqual(
            self._evaluate_single("isBlank", [self._literal("  ", "xsd:string")]),
            self._literal("true", "xsd:boolean"),
        )

        self.assertEqual(
            self._evaluate_single("isEmpty", [self._literal("", "xsd:string")]),
            self._literal("true", "xsd:boolean"),
        )
        self.assertEqual(
            self._evaluate_single("isEmpty", [self._literal("a", "xsd:string")]),
            self._literal("false", "xsd:boolean"),
        )

        self.assertEqual(
            self._evaluate("contains", [self._literal("abc", "xsd:string"), a]),
            [],
        )
        self.assertEqual(
            self._evaluate("isBlank", [self._literal("1", "xsd:integer")]),
            [],
        )

    def test_numeric_string_conversions(self):
        self.assertEqual(
            self._evaluate_single("isNumeric", [self._literal("12", "xsd:string")]),
            self._literal("true", "xsd:boolean"),
        )
        self.assertEqual(
            self._evaluate_single("isNumeric", [self._literal("NaN", "xsd:string")]),
            self._literal("false", "xsd:boolean"),
        )
        self.assertEqual(
            self._evaluate_single("isNumeric", [self._literal("inf", "xsd:string")]),
            self._literal("false", "xsd:boolean"),
        )
        self.assertEqual(
            self._evaluate_single("toInt", [self._literal("12", "xsd:string")]),
            self._literal("12", "xsd:integer"),
        )
        self.assertEqual(
            self._evaluate_single("toInt", [self._literal("3.9", "xsd:double")]),
            self._literal("3", "xsd:integer"),
        )
        self.assertEqual(
            self._evaluate_single("toFloat", [self._literal("12", "xsd:string")]),
            self._literal("12", "xsd:double"),
        )
        self.assertEqual(
            self._evaluate_single("toFloat", [self._literal("true", "xsd:boolean")]),
            self._literal("1.0", "xsd:double"),
        )
        self.assertEqual(
            self._evaluate_single("toBoolean", [self._literal("false", "xsd:string")]),
            self._literal("false", "xsd:boolean"),
        )
        self.assertEqual(
            self._evaluate_single("toBoolean", [self._literal("0", "xsd:string")]),
            self._literal("false", "xsd:boolean"),
        )
        self.assertEqual(
            self._evaluate_single("toBoolean", [self._literal("  ", "xsd:string")]),
            self._literal("false", "xsd:boolean"),
        )
        self.assertEqual(
            self._evaluate_single("toBoolean", [self._literal("yes", "xsd:string")]),
            self._literal("true", "xsd:boolean"),
        )
        self.assertEqual(
            self._evaluate_single("toBoolean", [self._literal_from_value(["x"])]),
            self._literal("true", "xsd:boolean"),
        )
        self.assertEqual(
            self._evaluate_single("toBoolean", [self._literal_from_value([])]),
            self._literal("false", "xsd:boolean"),
        )

    def test_to_string_functions(self):
        literal = self._literal("12", "xsd:integer")
        self.assertEqual(
            self._evaluate_single("toString", [literal]),
            self._literal("12", "xsd:string"),
        )
        value = self._evaluate_single("toStringWithDatatype", [literal])
        self.assertEqual(value.datatype, "xsd:string")
        self.assertEqual(value.value, "Literal<int> 12")

    def test_tuple_and_dict_functions(self):
        a = Constant("a")
        b = Constant("b")
        c = Constant("c")

        tuple_term = self._evaluate_single("tuple", [a, b, c])
        self.assertEqual(tuple_term.value, [a, b, c])

        to_tuple = self._evaluate_single("toTuple", [self._literal_from_value({a, b})])
        self.assertEqual(set(to_tuple.value), {a, b})

        to_set = self._evaluate_single("toSet", [self._literal_from_value([a, b])])
        self.assertEqual(to_set.value, {a, b})

        pair = self._literal_from_value([a, b])
        pair2 = self._literal_from_value([b, c])
        mapping = self._evaluate_single("dict", [pair, pair2])
        self.assertEqual(mapping.value, {a: b, b: c})

        merged = self._evaluate_single(
            "mergeDicts",
            [
                self._literal_from_value({a: b}),
                self._literal_from_value({b: c}),
            ],
        )
        self.assertEqual(merged.value, {a: b, b: c})

        keys = self._evaluate_single("dictKeys", [merged])
        self.assertEqual(keys.value, {a, b})

        values = self._evaluate_single("dictValues", [merged])
        self.assertEqual(set(values.value), {b, c})

        get_value = self._evaluate_single(
            "get", [self._literal_from_value([a, b]), self._literal("1", "xsd:integer")]
        )
        self.assertEqual(get_value, b)

        missing_key = self._evaluate_single(
            "get", [self._literal_from_value({a: b}), c]
        )
        self.assertEqual(missing_key, Constant("null"))

        self.assertEqual(
            self._evaluate(
                "get",
                [
                    self._literal_from_value([a, b]),
                    self._literal("3", "xsd:integer"),
                ],
            ),
            [],
        )

        contains_key = self._evaluate_single("containsKey", [merged, b])
        self.assertEqual(contains_key, self._literal("true", "xsd:boolean"))

        contains_value = self._evaluate_single("containsValue", [merged, c])
        self.assertEqual(contains_value, self._literal("true", "xsd:boolean"))

        self.assertEqual(
            self._evaluate("toSet", [self._literal("a", "xsd:string")]),
            [],
        )
        self.assertEqual(
            self._evaluate("toTuple", [self._literal("a", "xsd:string")]),
            [],
        )
        self.assertEqual(
            self._evaluate("dict", [self._literal_from_value(["a", "b"])]),
            [],
        )
        self.assertEqual(
            self._evaluate("mergeDicts", [self._literal("a", "xsd:string"), merged]),
            [],
        )
        self.assertEqual(
            self._evaluate("containsKey", [self._literal_from_value([a, b]), a]),
            [],
        )
        self.assertEqual(
            self._evaluate("containsValue", [self._literal_from_value([a, b]), a]),
            [],
        )

    def test_function_bindings_are_exposed(self):
        definitions = standard_function_definitions()
        self.assertIn("sum", definitions)

    def test_function_binding_respects_arity_bounds(self):
        sum_pred = Predicate(BASE_IRI + "sum", 1)
        is_even_pred = Predicate(BASE_IRI + "isEven", 3)
        concat_pred = Predicate(BASE_IRI + "concat", 4)
        equals_pred = Predicate(BASE_IRI + "equals", 2)
        source = IntegraalStandardFunctionSource(
            self.literal_factory,
            {"ig": BASE_IRI},
            [sum_pred, is_even_pred, concat_pred, equals_pred],
        )
        self.assertFalse(source.has_predicate(sum_pred))
        self.assertFalse(source.has_predicate(is_even_pred))
        self.assertFalse(source.has_predicate(concat_pred))
        self.assertFalse(source.has_predicate(equals_pred))
        query = BasicQuery(sum_pred)
        self.assertEqual(list(source.evaluate(query)), [])
