from unittest import TestCase

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate, SpecialPredicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.substitution.substitution import Substitution


class TestAtom(TestCase):
    def test_creation(self):
        """Test basic atom creation."""
        p = Predicate("p", 2)
        a = Constant("a")
        b = Constant("b")
        atom = Atom(p, a, b)
        self.assertEqual(atom.predicate, p)
        self.assertEqual(atom.terms, (a, b))

    def test_predicate_property(self):
        """Test predicate property."""
        p = Predicate("p", 1)
        atom = Atom(p, Constant("a"))
        self.assertIs(atom.predicate, p)

    def test_terms_property(self):
        """Test terms property returns tuple of terms."""
        p = Predicate("p", 3)
        terms = (Constant("a"), Variable("X"), Constant("b"))
        atom = Atom(p, *terms)
        self.assertEqual(atom.terms, terms)

    def test_variables_property(self):
        """Test variables property returns set of variables."""
        p = Predicate("p", 3)
        x = Variable("X")
        y = Variable("Y")
        atom = Atom(p, x, Constant("a"), y)
        self.assertEqual(atom.variables, {x, y})

    def test_variables_empty(self):
        """Test variables property with ground atom."""
        p = Predicate("p", 2)
        atom = Atom(p, Constant("a"), Constant("b"))
        self.assertEqual(atom.variables, set())

    def test_constants_property(self):
        """Test constants property returns set of constants."""
        p = Predicate("p", 3)
        a = Constant("a")
        b = Constant("b")
        atom = Atom(p, a, Variable("X"), b)
        self.assertEqual(atom.constants, {a, b})

    def test_constants_empty(self):
        """Test constants property with all-variable atom."""
        p = Predicate("p", 2)
        atom = Atom(p, Variable("X"), Variable("Y"))
        self.assertEqual(atom.constants, set())

    def test_getitem(self):
        """Test indexing into atom terms."""
        p = Predicate("p", 3)
        a = Constant("a")
        x = Variable("X")
        b = Constant("b")
        atom = Atom(p, a, x, b)
        self.assertEqual(atom[0], a)
        self.assertEqual(atom[1], x)
        self.assertEqual(atom[2], b)

    def test_apply_substitution(self):
        """Test applying substitution to atom."""
        p = Predicate("p", 2)
        x = Variable("X")
        y = Variable("Y")
        atom = Atom(p, x, y)
        sub = Substitution({x: Constant("a"), y: Constant("b")})
        result = atom.apply_substitution(sub)
        self.assertEqual(result.predicate, p)
        self.assertEqual(result.terms, (Constant("a"), Constant("b")))

    def test_apply_substitution_partial(self):
        """Test applying partial substitution to atom."""
        p = Predicate("p", 2)
        x = Variable("X")
        y = Variable("Y")
        atom = Atom(p, x, y)
        sub = Substitution({x: Constant("a")})
        result = atom.apply_substitution(sub)
        self.assertEqual(result.terms, (Constant("a"), y))

    def test_apply_substitution_variable_to_variable(self):
        """Test applying substitution that maps variable to variable."""
        p = Predicate("p", 2)
        x = Variable("X")
        y = Variable("Y")
        z = Variable("Z")
        atom = Atom(p, x, y)
        sub = Substitution({x: z})
        result = atom.apply_substitution(sub)
        self.assertEqual(result.terms, (z, y))

    def test_equality_same_atoms(self):
        """Test equality of identical atoms."""
        p = Predicate("p", 2)
        atom1 = Atom(p, Constant("a"), Variable("X"))
        atom2 = Atom(p, Constant("a"), Variable("X"))
        self.assertEqual(atom1, atom2)

    def test_equality_different_predicates(self):
        """Test inequality of atoms with different predicates."""
        p1 = Predicate("p", 1)
        p2 = Predicate("q", 1)
        atom1 = Atom(p1, Constant("a"))
        atom2 = Atom(p2, Constant("a"))
        self.assertNotEqual(atom1, atom2)

    def test_equality_different_terms(self):
        """Test inequality of atoms with different terms."""
        p = Predicate("p", 1)
        atom1 = Atom(p, Constant("a"))
        atom2 = Atom(p, Constant("b"))
        self.assertNotEqual(atom1, atom2)

    def test_equality_with_non_atom(self):
        """Test inequality with non-Atom object."""
        p = Predicate("p", 1)
        atom = Atom(p, Constant("a"))
        self.assertNotEqual(atom, "not an atom")
        self.assertNotEqual(atom, None)

    def test_hash_equal_atoms(self):
        """Test that equal atoms have equal hash."""
        p = Predicate("p", 2)
        atom1 = Atom(p, Constant("a"), Variable("X"))
        atom2 = Atom(p, Constant("a"), Variable("X"))
        self.assertEqual(hash(atom1), hash(atom2))

    def test_hash_usable_in_set(self):
        """Test that atoms can be used in sets."""
        p = Predicate("p", 1)
        atom1 = Atom(p, Constant("a"))
        atom2 = Atom(p, Constant("a"))
        atom3 = Atom(p, Constant("b"))
        s = {atom1, atom2, atom3}
        self.assertEqual(len(s), 2)

    def test_repr_normal_atom(self):
        """Test repr for normal atom."""
        p = Predicate("p", 2)
        atom = Atom(p, Constant("a"), Variable("X"))
        self.assertEqual(repr(atom), "p(a, X)")

    def test_repr_equality_atom(self):
        """Test repr for equality atom shows infix notation."""
        eq = SpecialPredicate.EQUALITY.value
        atom = Atom(eq, Variable("X"), Constant("a"))
        self.assertEqual(repr(atom), "X=a")

    def test_zero_arity_atom(self):
        """Test atom with zero-arity predicate."""
        p = Predicate("prop", 0)
        atom = Atom(p)
        self.assertEqual(atom.terms, ())
        self.assertEqual(atom.variables, set())
        self.assertEqual(atom.constants, set())
        self.assertEqual(repr(atom), "prop()")
