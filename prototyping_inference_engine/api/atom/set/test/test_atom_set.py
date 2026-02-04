from unittest import TestCase

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.set.frozen_atom_set import FrozenAtomSet
from prototyping_inference_engine.api.atom.set.mutable_atom_set import MutableAtomSet
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.parser.dlgp.dlgp2_parser import Dlgp2Parser


class TestFrozenAtomSet(TestCase):
    def test_empty_creation(self):
        """Test creating empty FrozenAtomSet."""
        s = FrozenAtomSet()
        self.assertEqual(len(s), 0)

    def test_creation_from_iterable(self):
        """Test creating FrozenAtomSet from iterable."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a), q(b).")
        s = FrozenAtomSet(atoms)
        self.assertEqual(len(s), 2)

    def test_contains(self):
        """Test __contains__ method."""
        p = Predicate("p", 1)
        atom = Atom(p, Constant("a"))
        s = FrozenAtomSet([atom])
        self.assertIn(atom, s)

    def test_not_contains(self):
        """Test __contains__ returns False for missing atom."""
        p = Predicate("p", 1)
        atom1 = Atom(p, Constant("a"))
        atom2 = Atom(p, Constant("b"))
        s = FrozenAtomSet([atom1])
        self.assertNotIn(atom2, s)

    def test_iter(self):
        """Test iteration over atoms."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a), q(b).")
        s = FrozenAtomSet(atoms)
        result = list(s)
        self.assertEqual(len(result), 2)

    def test_len(self):
        """Test __len__ method."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a), q(b), r(c).")
        s = FrozenAtomSet(atoms)
        self.assertEqual(len(s), 3)

    def test_terms_property(self):
        """Test terms property."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a,X), q(b).")
        s = FrozenAtomSet(atoms)
        terms = s.terms
        self.assertIn(Constant("a"), terms)
        self.assertIn(Constant("b"), terms)
        self.assertIn(Variable("X"), terms)

    def test_variables_property(self):
        """Test variables property."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X,Y), q(X,a).")
        s = FrozenAtomSet(atoms)
        self.assertEqual(s.variables, {Variable("X"), Variable("Y")})

    def test_constants_property(self):
        """Test constants property."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X,a), q(b,c).")
        s = FrozenAtomSet(atoms)
        self.assertEqual(s.constants, {Constant("a"), Constant("b"), Constant("c")})

    def test_predicates_property(self):
        """Test predicates property."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a), q(b), p(c).")
        s = FrozenAtomSet(atoms)
        predicates = s.predicates
        self.assertEqual(len(predicates), 2)
        self.assertIn(Predicate("p", 1), predicates)
        self.assertIn(Predicate("q", 1), predicates)

    def test_apply_substitution(self):
        """Test applying substitution to atom set."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X), q(Y).")
        s = FrozenAtomSet(atoms)
        sub = Substitution({Variable("X"): Constant("a"), Variable("Y"): Constant("b")})
        result = s.apply_substitution(sub)
        self.assertIsInstance(result, FrozenAtomSet)
        self.assertEqual(len(result), 2)
        self.assertIn(Atom(Predicate("p", 1), Constant("a")), result)
        self.assertIn(Atom(Predicate("q", 1), Constant("b")), result)

    def test_match_by_predicate(self):
        """Test match method returns atoms with matching predicate."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a,b), p(c,d), q(e).")
        s = FrozenAtomSet(atoms)
        query = Atom(Predicate("p", 2), Variable("X"), Variable("Y"))
        matches = list(s.match(query))
        self.assertEqual(len(matches), 2)

    def test_match_with_constant(self):
        """Test match method filters by constant in query."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a,b), p(a,c), p(d,e).")
        s = FrozenAtomSet(atoms)
        query = Atom(Predicate("p", 2), Constant("a"), Variable("Y"))
        matches = list(s.match(query))
        self.assertEqual(len(matches), 2)

    def test_hash(self):
        """Test that FrozenAtomSet is hashable."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a), q(b).")
        s = FrozenAtomSet(atoms)
        h = hash(s)
        self.assertIsInstance(h, int)

    def test_hash_equal_sets(self):
        """Test that equal sets have equal hash."""
        atoms1 = Dlgp2Parser.instance().parse_atoms("p(a), q(b).")
        atoms2 = Dlgp2Parser.instance().parse_atoms("q(b), p(a).")
        s1 = FrozenAtomSet(atoms1)
        s2 = FrozenAtomSet(atoms2)
        self.assertEqual(hash(s1), hash(s2))

    def test_usable_in_set(self):
        """Test that FrozenAtomSet can be used in a set."""
        atoms1 = Dlgp2Parser.instance().parse_atoms("p(a).")
        atoms2 = Dlgp2Parser.instance().parse_atoms("p(a).")
        s1 = FrozenAtomSet(atoms1)
        s2 = FrozenAtomSet(atoms2)
        container = {s1, s2}
        self.assertEqual(len(container), 1)

    def test_str(self):
        """Test string representation."""
        p = Predicate("p", 1)
        atom = Atom(p, Constant("a"))
        s = FrozenAtomSet([atom])
        self.assertIn("p(a)", str(s))

    def test_repr(self):
        """Test repr representation."""
        s = FrozenAtomSet()
        self.assertTrue(repr(s).startswith("FrozenAtomSet:"))


class TestMutableAtomSet(TestCase):
    def test_empty_creation(self):
        """Test creating empty MutableAtomSet."""
        s = MutableAtomSet()
        self.assertEqual(len(s), 0)

    def test_creation_from_iterable(self):
        """Test creating MutableAtomSet from iterable."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a), q(b).")
        s = MutableAtomSet(atoms)
        self.assertEqual(len(s), 2)

    def test_add(self):
        """Test add method."""
        s = MutableAtomSet()
        atom = Atom(Predicate("p", 1), Constant("a"))
        s.add(atom)
        self.assertEqual(len(s), 1)
        self.assertIn(atom, s)

    def test_add_duplicate(self):
        """Test adding duplicate atom does not increase size."""
        atom = Atom(Predicate("p", 1), Constant("a"))
        s = MutableAtomSet([atom])
        s.add(atom)
        self.assertEqual(len(s), 1)

    def test_discard(self):
        """Test discard method."""
        atom = Atom(Predicate("p", 1), Constant("a"))
        s = MutableAtomSet([atom])
        s.discard(atom)
        self.assertEqual(len(s), 0)
        self.assertNotIn(atom, s)

    def test_discard_missing(self):
        """Test discarding missing atom does not raise."""
        s = MutableAtomSet()
        atom = Atom(Predicate("p", 1), Constant("a"))
        s.discard(atom)  # Should not raise
        self.assertEqual(len(s), 0)

    def test_contains(self):
        """Test __contains__ method."""
        atom = Atom(Predicate("p", 1), Constant("a"))
        s = MutableAtomSet([atom])
        self.assertIn(atom, s)

    def test_iter(self):
        """Test iteration."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a), q(b).")
        s = MutableAtomSet(atoms)
        result = list(s)
        self.assertEqual(len(result), 2)

    def test_terms_property(self):
        """Test terms property."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a,X).")
        s = MutableAtomSet(atoms)
        terms = s.terms
        self.assertIn(Constant("a"), terms)
        self.assertIn(Variable("X"), terms)

    def test_variables_property(self):
        """Test variables property."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X,Y).")
        s = MutableAtomSet(atoms)
        self.assertEqual(s.variables, {Variable("X"), Variable("Y")})

    def test_constants_property(self):
        """Test constants property."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a,b).")
        s = MutableAtomSet(atoms)
        self.assertEqual(s.constants, {Constant("a"), Constant("b")})

    def test_predicates_property(self):
        """Test predicates property."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a), q(b).")
        s = MutableAtomSet(atoms)
        self.assertEqual(s.predicates, {Predicate("p", 1), Predicate("q", 1)})

    def test_apply_substitution(self):
        """Test applying substitution."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X).")
        s = MutableAtomSet(atoms)
        sub = Substitution({Variable("X"): Constant("a")})
        result = s.apply_substitution(sub)
        self.assertIn(Atom(Predicate("p", 1), Constant("a")), result)

    def test_match(self):
        """Test match method."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a), p(b), q(c).")
        s = MutableAtomSet(atoms)
        query = Atom(Predicate("p", 1), Variable("X"))
        matches = list(s.match(query))
        self.assertEqual(len(matches), 2)

    def test_repr(self):
        """Test repr representation."""
        s = MutableAtomSet()
        self.assertTrue(repr(s).startswith("MutableAtomSet:"))

    def test_is_mutable_set(self):
        """Test that MutableAtomSet is a MutableSet."""
        from collections.abc import MutableSet

        s = MutableAtomSet()
        self.assertIsInstance(s, MutableSet)
