from unittest import TestCase

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.set.frozen_atom_set import FrozenAtomSet
from prototyping_inference_engine.api.atom.set.index.index_by_predicate import (
    IndexByPredicate,
)
from prototyping_inference_engine.api.atom.set.index.index_by_term import IndexByTerm
from prototyping_inference_engine.api.atom.set.index.index_by_term_and_predicate import (
    IndexByTermAndPredicate,
)
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.parser.dlgp.dlgp2_parser import Dlgp2Parser


class TestIndexByPredicate(TestCase):
    def test_creation(self):
        """Test creating IndexByPredicate."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a,b), p(c,d), q(e).")
        atom_set = FrozenAtomSet(atoms)
        index = IndexByPredicate(atom_set)
        self.assertIsNotNone(index)

    def test_atoms_by_predicate(self):
        """Test atoms_by_predicate returns atoms with given predicate."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a,b), p(c,d), q(e).")
        atom_set = FrozenAtomSet(atoms)
        index = IndexByPredicate(atom_set)

        p_atoms = index.atoms_by_predicate(Predicate("p", 2))
        self.assertEqual(len(p_atoms), 2)

        q_atoms = index.atoms_by_predicate(Predicate("q", 1))
        self.assertEqual(len(q_atoms), 1)

    def test_atoms_by_predicate_empty(self):
        """Test atoms_by_predicate returns empty for non-existent predicate."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a).")
        atom_set = FrozenAtomSet(atoms)
        index = IndexByPredicate(atom_set)

        r_atoms = index.atoms_by_predicate(Predicate("r", 1))
        self.assertEqual(len(r_atoms), 0)

    def test_domain(self):
        """Test domain returns atoms with matching predicate."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a,b), p(c,d), q(e).")
        atom_set = FrozenAtomSet(atoms)
        index = IndexByPredicate(atom_set)

        query = Atom(Predicate("p", 2), Variable("X"), Variable("Y"))
        domain = index.domain(query, Substitution())
        self.assertEqual(len(domain), 2)

    def test_match(self):
        """Test match returns atoms that can specialize query."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a,b), p(c,d), q(e).")
        atom_set = FrozenAtomSet(atoms)
        index = IndexByPredicate(atom_set)

        query = Atom(Predicate("p", 2), Variable("X"), Variable("Y"))
        matches = list(index.match(query))
        self.assertEqual(len(matches), 2)

    def test_match_with_constant(self):
        """Test match filters by constant in query."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a,b), p(a,c), p(d,e).")
        atom_set = FrozenAtomSet(atoms)
        index = IndexByPredicate(atom_set)

        query = Atom(Predicate("p", 2), Constant("a"), Variable("Y"))
        matches = list(index.match(query))
        self.assertEqual(len(matches), 2)

    def test_domain_size(self):
        """Test domain_size returns correct size."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a), p(b), p(c).")
        atom_set = FrozenAtomSet(atoms)
        index = IndexByPredicate(atom_set)

        query = Atom(Predicate("p", 1), Variable("X"))
        size = index.domain_size(query, Substitution())
        self.assertEqual(size, 3)

    def test_extend_substitution(self):
        """Test extend_substitution yields valid substitutions."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a), p(b).")
        atom_set = FrozenAtomSet(atoms)
        index = IndexByPredicate(atom_set)

        query = Atom(Predicate("p", 1), Variable("X"))
        subs = list(index.extend_substitution(query, Substitution()))
        self.assertEqual(len(subs), 2)
        # Each substitution should map X to a constant
        x = Variable("X")
        values = {sub[x] for sub in subs}
        self.assertEqual(values, {Constant("a"), Constant("b")})


class TestIndexByTerm(TestCase):
    def test_creation(self):
        """Test creating IndexByTerm."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a,b), q(a,c).")
        atom_set = FrozenAtomSet(atoms)
        index = IndexByTerm(atom_set)
        self.assertIsNotNone(index)

    def test_atoms_by_term(self):
        """Test atoms_by_term returns atoms containing given term."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a,b), q(a,c), r(d).")
        atom_set = FrozenAtomSet(atoms)
        index = IndexByTerm(atom_set)

        a_atoms = index.atoms_by_term(Constant("a"))
        self.assertEqual(len(a_atoms), 2)  # p(a,b) and q(a,c)

        d_atoms = index.atoms_by_term(Constant("d"))
        self.assertEqual(len(d_atoms), 1)  # r(d)

    def test_atoms_by_term_empty(self):
        """Test atoms_by_term returns empty for non-existent term."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a).")
        atom_set = FrozenAtomSet(atoms)
        index = IndexByTerm(atom_set)

        z_atoms = index.atoms_by_term(Constant("z"))
        self.assertEqual(len(z_atoms), 0)

    def test_domain_with_constant(self):
        """Test domain uses constant term for filtering."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a,b), p(c,d), q(a).")
        atom_set = FrozenAtomSet(atoms)
        index = IndexByTerm(atom_set)

        # Query with constant 'a' - should filter to atoms containing 'a'
        query = Atom(Predicate("p", 2), Constant("a"), Variable("Y"))
        domain = index.domain(query, Substitution())
        # Should return atoms containing 'a': p(a,b) and q(a)
        self.assertEqual(len(domain), 2)

    def test_domain_with_substitution(self):
        """Test domain uses substitution for filtering."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a,b), p(c,d).")
        atom_set = FrozenAtomSet(atoms)
        index = IndexByTerm(atom_set)

        x = Variable("X")
        sub = Substitution({x: Constant("a")})
        query = Atom(Predicate("p", 2), x, Variable("Y"))
        domain = index.domain(query, sub)
        # Should filter to atoms containing 'a'
        self.assertIn(Atom(Predicate("p", 2), Constant("a"), Constant("b")), domain)

    def test_domain_all_variables(self):
        """Test domain returns all atoms when query has only unmapped variables."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a,b), p(c,d).")
        atom_set = FrozenAtomSet(atoms)
        index = IndexByTerm(atom_set)

        query = Atom(Predicate("p", 2), Variable("X"), Variable("Y"))
        domain = index.domain(query, Substitution())
        # Should return all atoms (no filtering possible)
        self.assertEqual(len(domain), 2)

    def test_match(self):
        """Test match returns correct atoms."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a,b), p(a,c), p(d,e).")
        atom_set = FrozenAtomSet(atoms)
        index = IndexByTerm(atom_set)

        query = Atom(Predicate("p", 2), Constant("a"), Variable("Y"))
        matches = list(index.match(query))
        self.assertEqual(len(matches), 2)


class TestIndexByTermAndPredicate(TestCase):
    def test_creation(self):
        """Test creating IndexByTermAndPredicate."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a,b), q(a,c).")
        atom_set = FrozenAtomSet(atoms)
        index = IndexByTermAndPredicate(atom_set)
        self.assertIsNotNone(index)

    def test_inherits_from_both(self):
        """Test that IndexByTermAndPredicate inherits from both indexes."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a,b).")
        atom_set = FrozenAtomSet(atoms)
        index = IndexByTermAndPredicate(atom_set)
        self.assertIsInstance(index, IndexByTerm)
        self.assertIsInstance(index, IndexByPredicate)

    def test_atoms_by_predicate(self):
        """Test atoms_by_predicate works."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a,b), p(c,d), q(e).")
        atom_set = FrozenAtomSet(atoms)
        index = IndexByTermAndPredicate(atom_set)

        p_atoms = index.atoms_by_predicate(Predicate("p", 2))
        self.assertEqual(len(p_atoms), 2)

    def test_atoms_by_term(self):
        """Test atoms_by_term works."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a,b), q(a,c).")
        atom_set = FrozenAtomSet(atoms)
        index = IndexByTermAndPredicate(atom_set)

        a_atoms = index.atoms_by_term(Constant("a"))
        self.assertEqual(len(a_atoms), 2)

    def test_domain_chooses_smaller(self):
        """Test domain chooses the smaller of term/predicate domains."""
        # Create a scenario where term index gives smaller domain
        atoms = Dlgp2Parser.instance().parse_atoms("p(a,b), p(c,d), p(e,f), q(a).")
        atom_set = FrozenAtomSet(atoms)
        index = IndexByTermAndPredicate(atom_set)

        # Query with constant 'a' - term index returns 2 atoms (p(a,b), q(a))
        # predicate index returns 3 atoms (all p atoms)
        query = Atom(Predicate("p", 2), Constant("a"), Variable("Y"))
        domain = index.domain(query, Substitution())
        # Should use smaller domain (term index)
        self.assertEqual(len(domain), 2)

    def test_match(self):
        """Test match works correctly."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a,b), p(a,c), p(d,e).")
        atom_set = FrozenAtomSet(atoms)
        index = IndexByTermAndPredicate(atom_set)

        query = Atom(Predicate("p", 2), Constant("a"), Variable("Y"))
        matches = list(index.match(query))
        self.assertEqual(len(matches), 2)
