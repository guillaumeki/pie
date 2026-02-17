"""Tests for piece splitter implementations."""

import unittest

from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser
from prototyping_inference_engine.api.atom.set.frozen_atom_set import FrozenAtomSet
from prototyping_inference_engine.utils.piece_splitter import (
    PieceSplitter,
    VariableInducedPieceSplitter,
)


class TestVariableInducedPieceSplitter(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = DlgpeParser.instance()
        self.splitter = VariableInducedPieceSplitter()

    def test_is_protocol_compatible(self) -> None:
        self.assertIsInstance(self.splitter, PieceSplitter)

    def test_empty_active_variables(self) -> None:
        atom_set = FrozenAtomSet(self.parser.parse_atoms("p(X), q(Y)."))
        self.assertEqual(self.splitter.split(atom_set, ()), tuple())

    def test_single_piece_connected_by_active_variable(self) -> None:
        atom_set = FrozenAtomSet(self.parser.parse_atoms("p(X), q(X), r(a)."))
        pieces = self.splitter.split(atom_set, (Variable("X"),))
        self.assertEqual(len(pieces), 1)
        self.assertEqual(len(pieces[0]), 2)

    def test_multiple_disconnected_pieces(self) -> None:
        atom_set = FrozenAtomSet(
            self.parser.parse_atoms("p(X), q(X), r(Y), s(Y), t(a).")
        )
        pieces = self.splitter.split(atom_set, (Variable("X"), Variable("Y")))
        sizes = sorted(len(piece) for piece in pieces)
        self.assertEqual(sizes, [2, 2])


if __name__ == "__main__":
    unittest.main()
