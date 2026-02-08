from unittest import TestCase

from prototyping_inference_engine.api.kb.rule_base import RuleBase
from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser


class TestRuleBase(TestCase):
    def setUp(self):
        self.parser = DlgpeParser.instance()

    def test_empty_rule_base(self):
        rule_base = RuleBase()
        self.assertEqual(len(rule_base.rules), 0)
        self.assertEqual(len(rule_base.negative_constraints), 0)

    def test_add_rule(self):
        rule_base = RuleBase()
        rules = set(self.parser.parse_rules("q(X) :- p(X)."))
        rule = next(iter(rules))
        rule_base.add_rule(rule)
        self.assertIn(rule, rule_base.rules)

    def test_add_negative_constraint(self):
        rule_base = RuleBase()
        constraints = set(self.parser.parse_negative_constraints(":- p(X), q(X)."))
        constraint = next(iter(constraints))
        rule_base.add_negative_constraint(constraint)
        self.assertIn(constraint, rule_base.negative_constraints)
