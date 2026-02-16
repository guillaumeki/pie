import unittest

from prototyping_inference_engine.grd.dependency_checker import (
    ProductivityChecker,
    RestrictedProductivityChecker,
)
from prototyping_inference_engine.grd.rule_utils import extract_positive_body
from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser
from prototyping_inference_engine.unifier.piece_unifier_algorithm import (
    PieceUnifierAlgorithm,
)
from prototyping_inference_engine.api.ontology.rule.rule import Rule


class TestDependencyChecker(unittest.TestCase):
    def _first_unifier(self, target_rule, head_rule):
        target_body = extract_positive_body(target_rule)
        head_conjunctive = Rule.extract_conjunctive_rule(head_rule, 0)
        unifiers = PieceUnifierAlgorithm.compute_most_general_mono_piece_unifiers(
            target_body, head_conjunctive
        )
        return next(iter(unifiers))

    def test_productivity_checker_positive_dependency(self) -> None:
        rules = list(
            DlgpeParser.instance().parse_rules(
                """
                p(X) :- q(X).
                r(X) :- p(X).
                """
            )
        )
        r1, r2 = rules
        unifier = self._first_unifier(r2, r1)
        checker = ProductivityChecker()
        self.assertTrue(checker.is_valid_positive_dependency(r1, r2, unifier))

    def test_productivity_checker_negative_dependency_false(self) -> None:
        rules = list(
            DlgpeParser.instance().parse_rules(
                """
                p(X) :- q(X).
                r(X) :- p(X), not q(X).
                """
            )
        )
        r1, r2 = rules
        unifier = self._first_unifier(r2, r1)
        checker = ProductivityChecker()
        self.assertFalse(checker.is_valid_negative_dependency(r1, r2, unifier))

    def test_restricted_checker_allows_non_homomorphic_head(self) -> None:
        rules = list(
            DlgpeParser.instance().parse_rules(
                """
                p(X) :- q(X).
                r(X) | s(X) :- p(X).
                """
            )
        )
        r1, r2 = rules
        unifier = self._first_unifier(r2, r1)
        checker = RestrictedProductivityChecker()
        self.assertTrue(checker.is_valid_positive_dependency(r1, r2, unifier))

    def test_restricted_checker_short_circuits_on_productivity(self) -> None:
        rules = list(
            DlgpeParser.instance().parse_rules(
                """
                p(X) :- q(X).
                q(X) :- p(X).
                """
            )
        )
        r1, r2 = rules
        unifier = self._first_unifier(r2, r1)
        checker = RestrictedProductivityChecker()
        self.assertFalse(checker.is_valid_positive_dependency(r1, r2, unifier))


if __name__ == "__main__":
    unittest.main()
