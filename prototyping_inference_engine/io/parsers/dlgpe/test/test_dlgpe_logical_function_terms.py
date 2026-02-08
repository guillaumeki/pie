import unittest

from prototyping_inference_engine.api.atom.term.evaluable_function_term import (
    EvaluableFunctionTerm,
)
from prototyping_inference_engine.api.atom.term.logical_function_term import (
    LogicalFunctionalTerm,
)
from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser


class TestDlgpeLogicalFunctionTerms(unittest.TestCase):
    def setUp(self):
        self.parser = DlgpeParser.instance()

    def test_logical_function_term_without_computed_prefix(self):
        result = self.parser.parse("p(f(a)).")
        atom = result["facts"][0]
        self.assertIsInstance(atom.terms[0], LogicalFunctionalTerm)

    def test_evaluable_function_term_with_computed_prefix(self):
        result = self.parser.parse(
            """
            @computed ig: <stdfct>.

            @facts
            p(ig:sum(1, 2)).
            """
        )
        atom = result["facts"][0]
        self.assertIsInstance(atom.terms[0], EvaluableFunctionTerm)


if __name__ == "__main__":
    unittest.main()
