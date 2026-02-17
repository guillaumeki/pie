"""By-piece core processor and strategy variants."""

from __future__ import annotations

from functools import cache
from typing import Optional, TypeVar

from prototyping_inference_engine.api.atom.set.atom_set import AtomSet
from prototyping_inference_engine.api.atom.set.core.core_algorithm import CoreAlgorithm
from prototyping_inference_engine.api.atom.set.core.core_helpers import (
    count_non_frozen_variables,
    freeze_substitution,
    identity_free,
    iter_homomorphisms,
    remove_atoms_with_variables,
    substitution_external_range_variables,
    to_same_type,
)
from prototyping_inference_engine.api.atom.set.core.core_variants import (
    CoreRetractionVariant,
)
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


class ByPieceCoreProcessor(CoreAlgorithm):
    """Compute core by retracting variable-induced pieces."""

    def __init__(
        self,
        variant: CoreRetractionVariant = CoreRetractionVariant.BY_DELETION,
        algorithm_provider: Optional[HomomorphismAlgorithmProvider] = None,
        piece_splitter: Optional[PieceSplitter] = None,
    ) -> None:
        if algorithm_provider is None:
            algorithm_provider = DefaultHomomorphismAlgorithmProvider()
        if piece_splitter is None:
            piece_splitter = VariableInducedPieceSplitter()

        self.variant = variant
        self._homomorphism_algorithm: HomomorphismAlgorithm = (
            algorithm_provider.get_algorithm()
        )
        self._piece_splitter = piece_splitter

    @staticmethod
    @cache
    def instance(
        variant: CoreRetractionVariant = CoreRetractionVariant.BY_DELETION,
    ) -> "ByPieceCoreProcessor":
        return ByPieceCoreProcessor(variant=variant)

    def compute_core(
        self, atom_set: AS, freeze: Optional[tuple[Variable, ...]] = None
    ) -> AS:
        freeze = tuple() if freeze is None else freeze
        frozen_set = set(freeze)
        pre_sub = freeze_substitution(freeze)

        target = MutableAtomSet(atom_set)
        pieces = self._piece_splitter.split(target, target.variables - frozen_set)

        for piece in pieces:
            self._process_piece(MutableAtomSet(piece), target, frozen_set, pre_sub)

        # Canonical cleanup pass to guarantee a core output.
        target = MutableAtomSet(
            NaiveCoreProcessor.instance().compute_core(target, freeze=freeze)
        )

        return to_same_type(atom_set, target)  # type: ignore[return-value]

    def _process_piece(
        self,
        piece: MutableAtomSet,
        target: MutableAtomSet,
        frozen_set: set[Variable],
        pre_sub,
    ) -> None:
        if self.variant == CoreRetractionVariant.EXHAUSTIVE:
            self._retract_piece_exhaustive(piece, target, frozen_set, pre_sub)
            return
        if self.variant == CoreRetractionVariant.BY_SPECIALISATION:
            self._retract_piece_by_specialisation(piece, target, frozen_set, pre_sub)
            return
        self._retract_piece_by_deletion(piece, target, frozen_set, pre_sub)

    def _retract_piece_exhaustive(
        self,
        piece: MutableAtomSet,
        target: MutableAtomSet,
        frozen_set: set[Variable],
        pre_sub,
    ) -> None:
        max_deleted: set[Variable] = set()
        piece_vars = set(piece.variables)

        for hom in iter_homomorphisms(
            self._homomorphism_algorithm, piece, target, pre_sub
        ):
            reduced = identity_free(hom)
            deleted_vars = set(reduced.keys())
            if not deleted_vars:
                continue
            external = substitution_external_range_variables(
                reduced, piece_vars, frozen_set
            )
            if external & deleted_vars:
                continue
            if len(deleted_vars) > len(max_deleted):
                max_deleted = deleted_vars

        if max_deleted:
            remove_atoms_with_variables(target, max_deleted)
            remove_atoms_with_variables(piece, max_deleted)

    def _retract_piece_by_deletion(
        self,
        piece: MutableAtomSet,
        target: MutableAtomSet,
        frozen_set: set[Variable],
        pre_sub,
    ) -> None:
        while True:
            changed = False
            piece_vars = set(piece.variables)
            non_frozen_count = count_non_frozen_variables(piece, frozen_set)
            if non_frozen_count == 0:
                return

            for hom in iter_homomorphisms(
                self._homomorphism_algorithm, piece, target, pre_sub
            ):
                reduced = identity_free(hom)
                deleted_vars = set(reduced.keys())
                if not deleted_vars:
                    continue

                external = substitution_external_range_variables(
                    reduced, piece_vars, frozen_set
                )
                if external & deleted_vars:
                    continue

                remove_atoms_with_variables(target, deleted_vars)
                remove_atoms_with_variables(piece, deleted_vars)
                changed = True
                if len(deleted_vars) >= non_frozen_count:
                    return
                break

            if not changed:
                return

    def _retract_piece_by_specialisation(
        self,
        piece: MutableAtomSet,
        target: MutableAtomSet,
        frozen_set: set[Variable],
        pre_sub,
    ) -> None:
        non_frozen_count = count_non_frozen_variables(piece, frozen_set)
        if non_frozen_count == 0:
            return

        piece_vars = set(piece.variables)
        local_pre_sub = pre_sub
        best_deleted: set[Variable] = set()
        best_size = 0

        while True:
            improved = False
            for hom in iter_homomorphisms(
                self._homomorphism_algorithm, piece, target, local_pre_sub
            ):
                reduced = identity_free(hom)
                if not reduced:
                    continue

                deleted_vars = set(reduced.keys()) | best_deleted
                external = substitution_external_range_variables(
                    reduced, piece_vars, frozen_set
                )
                if external & deleted_vars:
                    continue

                if len(deleted_vars) > best_size:
                    best_deleted = deleted_vars
                    best_size = len(deleted_vars)
                    improved = True

                    for var in deleted_vars:
                        image = reduced.get(var)
                        if isinstance(image, Variable) and image not in piece_vars:
                            local_pre_sub[var] = image

                    if best_size >= non_frozen_count:
                        break

            if not improved or best_size >= non_frozen_count:
                break

        if best_deleted:
            remove_atoms_with_variables(target, best_deleted)
            remove_atoms_with_variables(piece, best_deleted)
