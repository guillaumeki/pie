"""
DLGPE arithmetic expression parsing tests.
"""

import unittest

from prototyping_inference_engine.api.atom.term.evaluable_function_term import (
    EvaluableFunctionTerm,
)
from prototyping_inference_engine.api.atom.term.factory.literal_factory import (
    LiteralFactory,
)
from prototyping_inference_engine.api.atom.term.literal_config import LiteralConfig
from prototyping_inference_engine.api.atom.term.literal_xsd import (
    XSD_INTEGER,
    XSD_PREFIX,
)
from prototyping_inference_engine.api.atom.term.storage.dict_storage import DictStorage
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser


class TestDlgpeArithmetic(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = DlgpeParser.instance()
        self.literal_factory = LiteralFactory(DictStorage(), LiteralConfig.default())

    def _literal(self, lexical: str):
        return self.literal_factory.create(lexical, f"{XSD_PREFIX}{XSD_INTEGER}")

    def _func(self, name: str, *args):
        return ("func", name, args)

    def _assert_term(self, term, expected) -> None:
        if isinstance(expected, tuple) and expected and expected[0] == "func":
            _, name, args = expected
            self.assertIsInstance(term, EvaluableFunctionTerm)
            self.assertEqual(term.name, name)
            self.assertEqual(len(term.args), len(args))
            for observed, expected_arg in zip(term.args, args):
                self._assert_term(observed, expected_arg)
            return
        if isinstance(expected, Variable):
            self.assertIsInstance(term, Variable)
            self.assertEqual(term.identifier, expected.identifier)
            return
        self.assertEqual(term, expected)

    def test_additive_and_multiplicative_precedence(self) -> None:
        result = self.parser.parse("p(1 + 2 * 3).")
        fact = result["facts"][0]
        term = fact.terms[0]
        expected = self._func(
            "stdfct:sum",
            self._literal("1"),
            self._func("stdfct:product", self._literal("2"), self._literal("3")),
        )
        self._assert_term(term, expected)

    def test_unary_minus(self) -> None:
        result = self.parser.parse("p(-X).")
        fact = result["facts"][0]
        term = fact.terms[0]
        expected = self._func("stdfct:minus", self._literal("0"), Variable("X"))
        self._assert_term(term, expected)

    def test_power_right_associative(self) -> None:
        result = self.parser.parse("p(2 ** 3 ** 2).")
        fact = result["facts"][0]
        term = fact.terms[0]
        expected = self._func(
            "stdfct:power",
            self._literal("2"),
            self._func("stdfct:power", self._literal("3"), self._literal("2")),
        )
        self._assert_term(term, expected)

    def test_comparison_with_arithmetic(self) -> None:
        result = self.parser.parse("?() :- (2 * 3) + 1 > 6.")
        query = result["queries"][0]
        atom = next(iter(query.atoms))
        left = atom.terms[0]
        expected_left = self._func(
            "stdfct:sum",
            self._func("stdfct:product", self._literal("2"), self._literal("3")),
            self._literal("1"),
        )
        self._assert_term(left, expected_left)


if __name__ == "__main__":
    unittest.main()
