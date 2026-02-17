"""Multithreaded by-piece core processor."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from typing import Optional, TypeVar

from prototyping_inference_engine.api.atom.set.atom_set import AtomSet
from prototyping_inference_engine.api.atom.set.core.by_piece_core_processor import (
    ByPieceCoreProcessor,
)
from prototyping_inference_engine.api.atom.set.core.core_helpers import (
    freeze_substitution,
    to_same_type,
)
from prototyping_inference_engine.api.atom.set.core.core_variants import (
    CoreRetractionVariant,
)
from prototyping_inference_engine.api.atom.set.core.naive_core_processor import (
    NaiveCoreProcessor,
)
from prototyping_inference_engine.api.atom.set.homomorphism.homomorphism_algorithm_provider import (
    HomomorphismAlgorithmProvider,
)
from prototyping_inference_engine.api.atom.set.mutable_atom_set import MutableAtomSet
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.utils.piece_splitter import PieceSplitter

AS = TypeVar("AS", bound=AtomSet)


class MultiThreadsByPieceCoreProcessor(ByPieceCoreProcessor):
    """
    Multithreaded by-piece processor.

    Piece tasks are dispatched concurrently and synchronized on shared target
    updates. This keeps behavior consistent with sequential piece updates.
    """

    def __init__(
        self,
        max_workers: int = 32,
        variant: CoreRetractionVariant = CoreRetractionVariant.BY_DELETION,
        algorithm_provider: Optional[HomomorphismAlgorithmProvider] = None,
        piece_splitter: Optional[PieceSplitter] = None,
    ) -> None:
        super().__init__(variant, algorithm_provider, piece_splitter)
        self.max_workers = max_workers

    def compute_core(
        self, atom_set: AS, freeze: Optional[tuple[Variable, ...]] = None
    ) -> AS:
        freeze = tuple() if freeze is None else freeze
        frozen_set = set(freeze)
        pre_sub = freeze_substitution(freeze)

        target = MutableAtomSet(atom_set)
        pieces = self._piece_splitter.split(target, target.variables - frozen_set)
        lock = Lock()

        def work(piece) -> None:
            with lock:
                self._process_piece(MutableAtomSet(piece), target, frozen_set, pre_sub)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            list(executor.map(work, pieces))

        target = MutableAtomSet(
            NaiveCoreProcessor.instance().compute_core(target, freeze=freeze)
        )
        return to_same_type(atom_set, target)  # type: ignore[return-value]
