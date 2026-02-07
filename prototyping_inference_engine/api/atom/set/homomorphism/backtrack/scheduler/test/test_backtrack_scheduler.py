from unittest import TestCase

from prototyping_inference_engine.api.atom.set.frozen_atom_set import FrozenAtomSet
from prototyping_inference_engine.api.atom.set.homomorphism.backtrack.scheduler.backtrack_scheduler import (
    BacktrackScheduler,
)
from prototyping_inference_engine.api.atom.set.homomorphism.backtrack.scheduler.by_variable_backtrack_scheduler import (
    ByVariableBacktrackScheduler,
)
from prototyping_inference_engine.api.atom.set.homomorphism.backtrack.scheduler.dynamic_backtrack_scheduler import (
    DynamicBacktrackScheduler,
)
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser


class TestByVariableBacktrackScheduler(TestCase):
    def test_creation(self):
        """Test creating ByVariableBacktrackScheduler."""
        atoms = DlgpeParser.instance().parse_atoms("p(X,Y), q(Y,Z).")
        atom_set = FrozenAtomSet(atoms)
        scheduler = ByVariableBacktrackScheduler(atom_set)
        self.assertIsNotNone(scheduler)

    def test_is_backtrack_scheduler(self):
        """Test that ByVariableBacktrackScheduler is a BacktrackScheduler."""
        atoms = DlgpeParser.instance().parse_atoms("p(X).")
        atom_set = FrozenAtomSet(atoms)
        scheduler = ByVariableBacktrackScheduler(atom_set)
        self.assertIsInstance(scheduler, BacktrackScheduler)

    def test_has_next_atom_level_0(self):
        """Test has_next_atom at level 0 with non-empty atom set."""
        atoms = DlgpeParser.instance().parse_atoms("p(X,Y), q(Y,Z).")
        atom_set = FrozenAtomSet(atoms)
        scheduler = ByVariableBacktrackScheduler(atom_set)
        self.assertTrue(scheduler.has_next_atom(0))

    def test_has_next_atom_level_exceeded(self):
        """Test has_next_atom returns False when level exceeds atom count."""
        atoms = DlgpeParser.instance().parse_atoms("p(X,Y), q(Y,Z).")
        atom_set = FrozenAtomSet(atoms)
        scheduler = ByVariableBacktrackScheduler(atom_set)
        self.assertFalse(scheduler.has_next_atom(2))

    def test_has_next_atom_empty(self):
        """Test has_next_atom with empty atom set."""
        atom_set = FrozenAtomSet()
        scheduler = ByVariableBacktrackScheduler(atom_set)
        self.assertFalse(scheduler.has_next_atom(0))

    def test_next_atom(self):
        """Test next_atom returns an atom."""
        atoms = DlgpeParser.instance().parse_atoms("p(X,Y), q(Y,Z).")
        atom_set = FrozenAtomSet(atoms)
        scheduler = ByVariableBacktrackScheduler(atom_set)
        sub = Substitution()

        atom0 = scheduler.next_atom(sub, 0)
        self.assertIn(atom0, atom_set)

        atom1 = scheduler.next_atom(sub, 1)
        self.assertIn(atom1, atom_set)
        self.assertIn(atom1, atom_set)
        self.assertNotEqual(atom0, atom1)

    def test_iteration_covers_all_atoms(self):
        """Test that iterating through all levels covers all atoms."""
        atoms = DlgpeParser.instance().parse_atoms("p(X,Y), q(Y,Z), r(Z,W).")
        atom_set = FrozenAtomSet(atoms)
        scheduler = ByVariableBacktrackScheduler(atom_set)
        sub = Substitution()

        scheduled_atoms = set()
        level = 0
        while scheduler.has_next_atom(level):
            scheduled_atoms.add(scheduler.next_atom(sub, level))
            level += 1

        self.assertEqual(scheduled_atoms, set(atom_set))

    def test_with_frozen_atom_set_uses_index(self):
        """Test that FrozenAtomSet uses its index."""
        atoms = DlgpeParser.instance().parse_atoms("p(X,Y), q(Y,Z).")
        atom_set = FrozenAtomSet(atoms)  # Has index_by_term
        scheduler = ByVariableBacktrackScheduler(atom_set)
        self.assertTrue(scheduler.has_next_atom(0))


class TestDynamicBacktrackScheduler(TestCase):
    def test_creation(self):
        """Test creating DynamicBacktrackScheduler."""
        atoms = DlgpeParser.instance().parse_atoms("p(X,Y), q(Y,Z).")
        atom_set = FrozenAtomSet(atoms)
        scheduler = DynamicBacktrackScheduler(atom_set)
        self.assertIsNotNone(scheduler)

    def test_is_backtrack_scheduler(self):
        """Test that DynamicBacktrackScheduler is a BacktrackScheduler."""
        atoms = DlgpeParser.instance().parse_atoms("p(X).")
        atom_set = FrozenAtomSet(atoms)
        scheduler = DynamicBacktrackScheduler(atom_set)
        self.assertIsInstance(scheduler, BacktrackScheduler)

    def test_has_next_atom_level_0(self):
        """Test has_next_atom at level 0 with non-empty atom set."""
        atoms = DlgpeParser.instance().parse_atoms("p(X), q(Y).")
        atom_set = FrozenAtomSet(atoms)
        scheduler = DynamicBacktrackScheduler(atom_set)
        self.assertTrue(scheduler.has_next_atom(0))

    def test_has_next_atom_level_exceeded(self):
        """Test has_next_atom returns False when level exceeds atom count."""
        atoms = DlgpeParser.instance().parse_atoms("p(X), q(Y).")
        atom_set = FrozenAtomSet(atoms)
        scheduler = DynamicBacktrackScheduler(atom_set)
        self.assertFalse(scheduler.has_next_atom(2))

    def test_has_next_atom_empty(self):
        """Test has_next_atom with empty atom set."""
        atom_set = FrozenAtomSet()
        scheduler = DynamicBacktrackScheduler(atom_set)
        self.assertFalse(scheduler.has_next_atom(0))

    def test_next_atom(self):
        """Test next_atom returns an atom."""
        atoms = DlgpeParser.instance().parse_atoms("p(X,Y), q(Y,Z).")
        atom_set = FrozenAtomSet(atoms)
        scheduler = DynamicBacktrackScheduler(atom_set)
        sub = Substitution()

        atom0 = scheduler.next_atom(sub, 0)
        self.assertIn(atom0, atom_set)

    def test_iteration_covers_all_atoms(self):
        """Test that iterating through all levels covers all atoms."""
        atoms = DlgpeParser.instance().parse_atoms("p(X), q(Y), r(Z).")
        atom_set = FrozenAtomSet(atoms)
        scheduler = DynamicBacktrackScheduler(atom_set)
        sub = Substitution()

        scheduled_atoms = set()
        level = 0
        while scheduler.has_next_atom(level):
            scheduled_atoms.add(scheduler.next_atom(sub, level))
            level += 1

        self.assertEqual(scheduled_atoms, set(atom_set))

    def test_dynamic_ordering_with_substitution(self):
        """Test that dynamic scheduler considers substitution for ordering."""
        atoms = DlgpeParser.instance().parse_atoms("p(X,Y), q(Y,Z).")
        atom_set = FrozenAtomSet(atoms)
        scheduler = DynamicBacktrackScheduler(atom_set)

        # With different substitutions, the order might differ
        sub = Substitution()
        atom0 = scheduler.next_atom(sub, 0)
        self.assertIn(atom0, atom_set)

    def test_backtrack_resets_order(self):
        """Test that going back to a previous level resets subsequent order."""
        atoms = DlgpeParser.instance().parse_atoms("p(X), q(Y), r(Z).")
        atom_set = FrozenAtomSet(atoms)
        scheduler = DynamicBacktrackScheduler(atom_set)
        sub = Substitution()

        # Get first two atoms
        atom0 = scheduler.next_atom(sub, 0)
        atom1 = scheduler.next_atom(sub, 1)
        self.assertIn(atom1, atom_set)

        # Backtrack to level 0 and get first atom again
        atom0_again = scheduler.next_atom(sub, 0)
        self.assertEqual(atom0, atom0_again)
