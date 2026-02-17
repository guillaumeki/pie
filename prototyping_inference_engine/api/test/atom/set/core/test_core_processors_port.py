"""Ported core-processor tests inspired by Integraal core suite."""

import unittest

from prototyping_inference_engine.api.atom.set.frozen_atom_set import FrozenAtomSet
from prototyping_inference_engine.api.atom.set.core.by_piece_and_variable_core_processor import (
    ByPieceAndVariableCoreProcessor,
)
from prototyping_inference_engine.api.atom.set.core.by_piece_core_processor import (
    ByPieceCoreProcessor,
)
from prototyping_inference_engine.api.atom.set.core.core_algorithm import CoreAlgorithm
from prototyping_inference_engine.api.atom.set.core.core_variants import (
    CoreRetractionVariant,
)
from prototyping_inference_engine.api.atom.set.core.multithread_by_piece_core_processor import (
    MultiThreadsByPieceCoreProcessor,
)
from prototyping_inference_engine.api.atom.set.core.naive_core_processor import (
    NaiveCoreProcessor,
)
from prototyping_inference_engine.api.atom.set.homomorphism.backtrack.naive_backtrack_homomorphism_algorithm import (
    NaiveBacktrackHomomorphismAlgorithm,
)
from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser


def _is_core(atom_set: FrozenAtomSet) -> bool:
    algo = NaiveBacktrackHomomorphismAlgorithm.instance()
    for hom in algo.compute_homomorphisms(atom_set, atom_set):
        if len(hom(atom_set)) < len(atom_set):
            return False
    return True


def _is_equivalent(left: FrozenAtomSet, right: FrozenAtomSet) -> bool:
    algo = NaiveBacktrackHomomorphismAlgorithm.instance()
    return algo.exist_homomorphism(left, right) and algo.exist_homomorphism(right, left)


class TestCoreProcessorsPort(unittest.TestCase):
    DATA = (
        "p(T,X), p(X,Z), p(T,Y), p(Y,Y), p(Y,U).",
        "p(Z,Z), p(Z,X), p(Y,X), p(U,U), p(U,Z), p(X,a), p(a,a).",
        "p(a,X),p(X,X),p(X,Y),p(a,U),p(U,U), p(b,U),p(a,Z),p(Z,Z),p(Z,T),p(b,S),p(S,V).",
        "p(a,X),p(Y,X),p(Y,Z),p(V,Z),p(V,U),p(b,U),p(a,J), p(J,c),p(b,J),p(a,I),p(I,c),p(b,I).",
        "r(X), t(X,a,b), s(a,z), r(Y), t(Y,a,b), relatedTo(Y,z).",
        "p(a,X), p(X,Z), p(X,Y), p(Y,Z).",
        "p(Z,b), p(a,Z), p(a,Y), p(Y,b).",
        "p(a,b), p(a,X), p(X,Y), p(Y,Z), p(a,U), p(U,V), p(V,W), p(a,I), p(I,J), p(J,K), p(K,L).",
        "p(a,X), p(X,Z), p(X,Y), p(Y,Z), p(a,a).",
        "p(Z0,V0), q(a, Z0), q(Z0,a), q(Z0,c), q(c,Z0), p(a,b), p(c,d), p(Z1,V1), q(a, Z1), q(Z1,a), q(Z1,c), q(c,Z1).",
    )

    def setUp(self) -> None:
        self.parser = DlgpeParser.instance()
        self.processors: tuple[CoreAlgorithm, ...] = (
            ByPieceCoreProcessor(CoreRetractionVariant.BY_SPECIALISATION),
            ByPieceCoreProcessor(CoreRetractionVariant.BY_DELETION),
            ByPieceCoreProcessor(CoreRetractionVariant.EXHAUSTIVE),
            MultiThreadsByPieceCoreProcessor(
                8, CoreRetractionVariant.BY_SPECIALISATION
            ),
            MultiThreadsByPieceCoreProcessor(8, CoreRetractionVariant.BY_DELETION),
            MultiThreadsByPieceCoreProcessor(8, CoreRetractionVariant.EXHAUSTIVE),
            NaiveCoreProcessor(),
            ByPieceAndVariableCoreProcessor(),
        )

    def test_variants_compute_equivalent_core(self) -> None:
        for atom_set_str in self.DATA:
            source = FrozenAtomSet(self.parser.parse_atoms(atom_set_str))
            for processor in self.processors:
                core = processor.compute_core(source)
                self.assertTrue(_is_core(core), processor.__class__.__name__)
                self.assertTrue(
                    _is_equivalent(source, core), processor.__class__.__name__
                )

    def test_variants_with_frozen_variable(self) -> None:
        atom_set = FrozenAtomSet(self.parser.parse_atoms(self.DATA[0]))
        variable = next(iter(atom_set.variables), None)
        self.assertIsNotNone(variable)
        assert variable is not None

        for processor in self.processors:
            core = processor.compute_core(atom_set, freeze=(variable,))
            self.assertTrue(
                _is_equivalent(atom_set, core), processor.__class__.__name__
            )


if __name__ == "__main__":
    unittest.main()
