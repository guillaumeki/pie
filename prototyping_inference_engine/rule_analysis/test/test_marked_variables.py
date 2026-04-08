import unittest

from prototyping_inference_engine.rule_analysis.marked_variables import (
    marked_variable_occurrences,
)
from prototyping_inference_engine.rule_analysis.snapshot import AnalysisSnapshot
from prototyping_inference_engine.rule_analysis.test._helpers import parse_rules


class TestMarkedVariables(unittest.TestCase):
    def test_marks_variables_missing_from_some_head_atom(self):
        rule = parse_rules("q(X) :- p(X, Y).")[0]

        snapshot = AnalysisSnapshot((rule,))
        marked = snapshot.marked_variables.marked_variables_for(rule)

        self.assertEqual({str(variable) for variable in marked}, {"Y"})

    def test_propagates_marking_through_head_positions(self):
        rules = parse_rules(
            """
            q(X) :- p(X), r(Y).
            r(Z) :- a(Z), b(Z).
            """
        )

        snapshot = AnalysisSnapshot(rules)
        marked = snapshot.marked_variables.marked_variables_for(rules[1])

        self.assertEqual({str(variable) for variable in marked}, {"Z"})
        occurrences = marked_variable_occurrences(
            snapshot.fragments_by_rule[rules[1]],
            next(iter(marked)),
        )
        self.assertEqual(len(occurrences), 2)

    def test_distinguishes_predicates_with_same_name_and_different_arity(self):
        rules = parse_rules(
            """
            q(X) :- t(Y).
            t(Z) :- a(Z).
            t(Z, W) :- b(Z), c(W).
            """
        )

        snapshot = AnalysisSnapshot(rules)
        unary_marked = snapshot.marked_variables.marked_variables_for(rules[1])
        binary_marked = snapshot.marked_variables.marked_variables_for(rules[2])

        self.assertEqual({str(variable) for variable in unary_marked}, {"Z"})
        self.assertEqual(binary_marked, frozenset())


if __name__ == "__main__":
    unittest.main()
