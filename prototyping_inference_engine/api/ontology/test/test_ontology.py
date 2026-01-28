from unittest import TestCase

from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.ontology.constraint.negative_constraint import NegativeConstraint
from prototyping_inference_engine.api.ontology.ontology import Ontology
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.parser.dlgp.dlgp2_parser import Dlgp2Parser


class TestOntology(TestCase):
    def test_creation_empty(self):
        """Test creating empty Ontology."""
        ont = Ontology()
        self.assertEqual(len(ont.rules), 0)
        self.assertEqual(len(ont.negative_constraints), 0)

    def test_creation_with_rules(self):
        """Test creating Ontology with rules."""
        body_atoms = Dlgp2Parser.instance().parse_atoms("p(X,Y).")
        head_atoms = Dlgp2Parser.instance().parse_atoms("q(X).")
        x = Variable("X")
        body = ConjunctiveQuery(body_atoms, [x])
        head = ConjunctiveQuery(head_atoms, [x])
        rule = Rule(body, [head])

        ont = Ontology(rules={rule})
        self.assertEqual(len(ont.rules), 1)
        self.assertIn(rule, ont.rules)

    def test_creation_with_negative_constraints(self):
        """Test creating Ontology with negative constraints."""
        body_atoms = Dlgp2Parser.instance().parse_atoms("p(X), q(X).")
        x = Variable("X")
        body = ConjunctiveQuery(body_atoms, [x])
        nc = NegativeConstraint(body)

        ont = Ontology(negative_constraints={nc})
        self.assertEqual(len(ont.negative_constraints), 1)
        self.assertIn(nc, ont.negative_constraints)

    def test_rules_property(self):
        """Test rules property."""
        body_atoms = Dlgp2Parser.instance().parse_atoms("p(X).")
        head_atoms = Dlgp2Parser.instance().parse_atoms("q(X).")
        x = Variable("X")
        body = ConjunctiveQuery(body_atoms, [x])
        head = ConjunctiveQuery(head_atoms, [x])
        rule = Rule(body, [head])

        ont = Ontology(rules={rule})
        self.assertIs(ont.rules, ont._rules)

    def test_negative_constraints_property(self):
        """Test negative_constraints property."""
        body_atoms = Dlgp2Parser.instance().parse_atoms("p(X).")
        x = Variable("X")
        body = ConjunctiveQuery(body_atoms, [x])
        nc = NegativeConstraint(body)

        ont = Ontology(negative_constraints={nc})
        self.assertIs(ont.negative_constraints, ont._negative_constraints)


class TestNegativeConstraint(TestCase):
    def test_creation(self):
        """Test basic NegativeConstraint creation."""
        body_atoms = Dlgp2Parser.instance().parse_atoms("p(X), q(X).")
        x = Variable("X")
        body = ConjunctiveQuery(body_atoms, [x])
        nc = NegativeConstraint(body)
        self.assertEqual(len(nc.body.atoms), 2)

    def test_body_has_no_answer_variables(self):
        """Test that constraint body has no answer variables."""
        body_atoms = Dlgp2Parser.instance().parse_atoms("p(X), q(X).")
        x = Variable("X")
        body = ConjunctiveQuery(body_atoms, [x])
        nc = NegativeConstraint(body)
        # NegativeConstraint should have empty answer variables
        self.assertEqual(nc.body.answer_variables, ())

    def test_body_property(self):
        """Test body property."""
        body_atoms = Dlgp2Parser.instance().parse_atoms("p(X).")
        x = Variable("X")
        body = ConjunctiveQuery(body_atoms, [x])
        nc = NegativeConstraint(body)
        self.assertIsNotNone(nc.body)

    def test_label_property(self):
        """Test label property."""
        body_atoms = Dlgp2Parser.instance().parse_atoms("p(X).")
        x = Variable("X")
        body = ConjunctiveQuery(body_atoms, [x])
        nc = NegativeConstraint(body, label="nc1")
        self.assertEqual(nc.label, "nc1")

    def test_label_default_none(self):
        """Test that label defaults to None."""
        body_atoms = Dlgp2Parser.instance().parse_atoms("p(X).")
        x = Variable("X")
        body = ConjunctiveQuery(body_atoms, [x])
        nc = NegativeConstraint(body)
        self.assertIsNone(nc.label)

    def test_str_without_label(self):
        """Test string representation without label."""
        body_atoms = Dlgp2Parser.instance().parse_atoms("p(X).")
        x = Variable("X")
        body = ConjunctiveQuery(body_atoms, [x])
        nc = NegativeConstraint(body)
        s = str(nc)
        self.assertIn("p(X)", s)
        self.assertIn("\u22A5", s)  # bottom symbol

    def test_str_with_label(self):
        """Test string representation with label."""
        body_atoms = Dlgp2Parser.instance().parse_atoms("p(X).")
        x = Variable("X")
        body = ConjunctiveQuery(body_atoms, [x])
        nc = NegativeConstraint(body, label="nc1")
        s = str(nc)
        self.assertIn("[nc1]", s)

    def test_repr(self):
        """Test repr representation."""
        body_atoms = Dlgp2Parser.instance().parse_atoms("p(X).")
        x = Variable("X")
        body = ConjunctiveQuery(body_atoms, [x])
        nc = NegativeConstraint(body)
        r = repr(nc)
        self.assertTrue(r.startswith("Constraint:"))
