"""By-piece-and-variable core processor."""

from __future__ import annotations

from functools import cache
from typing import Optional, TypeVar

from prototyping_inference_engine.api.atom.set.atom_set import AtomSet
from prototyping_inference_engine.api.atom.set.core.core_algorithm import CoreAlgorithm
from prototyping_inference_engine.api.atom.set.core.core_helpers import (
    atoms_with_variable,
    freeze_substitution,
    to_same_type,
    without_atoms,
)
from prototyping_inference_engine.api.atom.set.frozen_atom_set import FrozenAtomSet
from prototyping_inference_engine.api.atom.set.core.naive_core_processor import (
    NaiveCoreProcessor,
)
from prototyping_inference_engine.api.atom.set.homomorphism.homomorphism_algorithm import (
    HomomorphismAlgorithm,
)
from prototyping_inference_engine.api.atom.set.homomorphism.homomorphism_algorithm_provider import (
    DefaultHomomorphismAlgorithmProvider,
    HomomorphismAlgorithmProvider,
)
from prototyping_inference_engine.api.atom.set.mutable_atom_set import MutableAtomSet
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.utils.piece_splitter import (
    PieceSplitter,
    VariableInducedPieceSplitter,
)

AS = TypeVar("AS", bound=AtomSet)


class ByPieceAndVariableCoreProcessor(CoreAlgorithm):
    """Compute core by testing each variable inside each piece."""

    def __init__(
        self,
        algorithm_provider: Optional[HomomorphismAlgorithmProvider] = None,
        piece_splitter: Optional[PieceSplitter] = None,
    ) -> None:
        if algorithm_provider is None:
            algorithm_provider = DefaultHomomorphismAlgorithmProvider()
        if piece_splitter is None:
            piece_splitter = VariableInducedPieceSplitter()

        self._homomorphism_algorithm: HomomorphismAlgorithm = (
            algorithm_provider.get_algorithm()
        )
        self._piece_splitter = piece_splitter

    @staticmethod
    @cache
    def instance() -> "ByPieceAndVariableCoreProcessor":
        return ByPieceAndVariableCoreProcessor()

    def compute_core(
        self, atom_set: AS, freeze: Optional[tuple[Variable, ...]] = None
    ) -> AS:
        freeze = tuple() if freeze is None else freeze
        frozen_set = set(freeze)
        pre_sub = freeze_substitution(freeze)

        target = MutableAtomSet(atom_set)
        pieces = self._piece_splitter.split(target, target.variables - frozen_set)

        for piece in pieces:
            piece_mut = MutableAtomSet(piece)
            for var in list(piece_mut.variables):
                atoms_using_var = atoms_with_variable(piece_mut, var)
                if not atoms_using_var:
                    continue
                virtual_target = without_atoms(target, atoms_using_var)
                if self._homomorphism_algorithm.exist_homomorphism(
                    FrozenAtomSet(piece_mut), virtual_target, pre_sub
                ):
                    for atom in atoms_using_var:
                        target.discard(atom)

        target = MutableAtomSet(
            NaiveCoreProcessor.instance().compute_core(target, freeze=freeze)
        )
        return to_same_type(atom_set, target)  # type: ignore[return-value]
