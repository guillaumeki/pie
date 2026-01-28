from unittest import TestCase

from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.term_partition import TermPartition
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.parser.dlgp.dlgp2_parser import Dlgp2Parser


class TestTermPartition(TestCase):
    def test_creation_empty(self):
        """Test creating empty TermPartition."""
        tp = TermPartition()
        self.assertEqual(len(list(tp.classes)), 0)

    def test_add_class(self):
        """Test adding a class to partition."""
        tp = TermPartition()
        x = Variable("X")
        y = Variable("Y")
        tp.add_class([x, y])
        self.assertEqual(len(list(tp.classes)), 1)
        self.assertEqual(tp.get_class(x), tp.get_class(y))

    def test_default_comparator_constants(self):
        """Test default comparator with two constants returns 0."""
        result = TermPartition.default_comparator(Constant("a"), Constant("b"))
        self.assertEqual(result, 0)

    def test_default_comparator_constant_variable(self):
        """Test default comparator prefers constants."""
        result = TermPartition.default_comparator(Constant("a"), Variable("X"))
        self.assertEqual(result, -1)  # Constant comes first

        result = TermPartition.default_comparator(Variable("X"), Constant("a"))
        self.assertEqual(result, 1)  # Variable comes after

    def test_default_comparator_variables(self):
        """Test default comparator with two variables returns 0."""
        result = TermPartition.default_comparator(Variable("X"), Variable("Y"))
        self.assertEqual(result, 0)

    def test_get_representative_constant(self):
        """Test that constant becomes representative when mixed with variables."""
        tp = TermPartition()
        x = Variable("X")
        a = Constant("a")
        tp.add_class([x, a])
        self.assertEqual(tp.get_representative(x), a)
        self.assertEqual(tp.get_representative(a), a)

    def test_is_admissible_no_two_constants(self):
        """Test is_admissible returns True when classes don't have two constants."""
        tp = TermPartition()
        x = Variable("X")
        a = Constant("a")
        tp.add_class([x, a])
        self.assertTrue(tp.is_admissible)

    def test_is_admissible_false_with_two_constants(self):
        """Test is_admissible returns False when class has two different constants."""
        tp = TermPartition()
        a = Constant("a")
        b = Constant("b")
        tp.add_class([a, b])
        self.assertFalse(tp.is_admissible)

    def test_associated_substitution_simple(self):
        """Test associated_substitution with simple case."""
        tp = TermPartition()
        x = Variable("X")
        a = Constant("a")
        tp.add_class([x, a])
        sub = tp.associated_substitution()
        self.assertIsNotNone(sub)
        self.assertEqual(sub[x], a)

    def test_associated_substitution_two_variables(self):
        """Test associated_substitution with two variables."""
        tp = TermPartition()
        x = Variable("X")
        y = Variable("Y")
        tp.add_class([x, y])
        sub = tp.associated_substitution()
        self.assertIsNotNone(sub)
        # One variable should map to the other
        if x in sub:
            self.assertEqual(sub[x], y)
        else:
            self.assertEqual(sub[y], x)

    def test_associated_substitution_fails_with_two_constants(self):
        """Test associated_substitution returns None when class has two constants."""
        tp = TermPartition()
        a = Constant("a")
        b = Constant("b")
        tp.add_class([a, b])
        sub = tp.associated_substitution()
        self.assertIsNone(sub)

    def test_is_valid_simple_rule(self):
        """Test is_valid with a simple valid partition."""
        # Rule: p(X) -> q(X)
        body_atoms = Dlgp2Parser.instance().parse_atoms("p(X).")
        head_atoms = Dlgp2Parser.instance().parse_atoms("q(X).")
        x = Variable("X")
        body = ConjunctiveQuery(body_atoms, [x])
        head = ConjunctiveQuery(head_atoms, [x])
        rule = Rule(body, [head])

        tp = TermPartition()
        tp.add_class([x, Constant("a")])
        self.assertTrue(tp.is_valid(rule))

    def test_is_valid_existential_not_with_constant(self):
        """Test is_valid returns False when existential variable is with constant."""
        # Rule: p(X) -> q(X,Y) where Y is existential
        body_atoms = Dlgp2Parser.instance().parse_atoms("p(X).")
        head_atoms = Dlgp2Parser.instance().parse_atoms("q(X,Y).")
        x = Variable("X")
        body = ConjunctiveQuery(body_atoms, [x])
        head = ConjunctiveQuery(head_atoms, [x])
        rule = Rule(body, [head])

        y = Variable("Y")  # Y is existential in the rule
        tp = TermPartition()
        tp.add_class([y, Constant("a")])  # Existential with constant - invalid
        self.assertFalse(tp.is_valid(rule))

    def test_is_valid_existential_not_with_frontier(self):
        """Test is_valid returns False when existential is with frontier variable."""
        # Rule: p(X) -> q(X,Y) where Y is existential, X is frontier
        body_atoms = Dlgp2Parser.instance().parse_atoms("p(X).")
        head_atoms = Dlgp2Parser.instance().parse_atoms("q(X,Y).")
        x = Variable("X")
        body = ConjunctiveQuery(body_atoms, [x])
        head = ConjunctiveQuery(head_atoms, [x])
        rule = Rule(body, [head])

        y = Variable("Y")  # Y is existential
        tp = TermPartition()
        tp.add_class([x, y])  # Frontier with existential - invalid
        self.assertFalse(tp.is_valid(rule))

    def test_union(self):
        """Test union of partition classes."""
        tp = TermPartition()
        x = Variable("X")
        y = Variable("Y")
        z = Variable("Z")
        tp.add_class([x])
        tp.add_class([y])
        tp.add_class([z])

        tp.union(x, y)
        self.assertEqual(tp.get_class(x), tp.get_class(y))
        self.assertNotEqual(tp.get_class(x), tp.get_class(z))
