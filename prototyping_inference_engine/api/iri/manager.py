"""IRI manager for base/prefix resolution and normalization."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from prototyping_inference_engine.api.iri.iri import IRIRef
from prototyping_inference_engine.api.iri.normalization import (
    IRINormalizer,
    RFCNormalizationScheme,
    StandardComposableNormalizer,
)
from prototyping_inference_engine.api.iri.preparator import StringPreparator


@dataclass(frozen=True)
class PrefixedIRIRef:
    prefix: Optional[str]
    iri: IRIRef


class IRIManager:
    DEFAULT_BASE = "http://www.boreal.inria.fr/"

    def __init__(
        self,
        preparator: Optional[StringPreparator] = None,
        normalizer: Optional[IRINormalizer] = None,
        iri_base: Optional[str] = None,
        use_default_base: bool = True,
    ) -> None:
        self._preparator = preparator
        self._normalizer = normalizer or StandardComposableNormalizer(
            RFCNormalizationScheme.STRING
        )
        self._prefixes: dict[str, IRIRef] = {}
        self._base: Optional[IRIRef] = None
        if iri_base is not None:
            self.set_base(iri_base)
        elif use_default_base:
            self._base = IRIRef(self.DEFAULT_BASE)

    def get_base(self) -> Optional[str]:
        return self._base.recompose() if self._base is not None else None

    def get_prefix(self, prefix_key: str) -> str:
        return self._get(prefix_key).recompose()

    def get_all_prefixes(self) -> set[str]:
        return set(self._prefixes.keys())

    def create_iri(self, iri_string: str, base: Optional[IRIRef] = None) -> IRIRef:
        target_base = base or self._base
        iri = IRIRef(iri_string, self._preparator)
        if target_base is not None:
            iri.resolve_in_place(target_base)
        return iri.normalize_in_place(self._normalizer)

    def create_iri_with_prefix(self, prefix: str, iri_string: str) -> IRIRef:
        return self.create_iri(iri_string, self._get(prefix))

    def set_base(self, iri_string: str) -> None:
        self._base = self._require_absolute(self.create_iri(iri_string))

    def set_base_from_prefix(self, prefix: str, iri_string: str) -> None:
        self._base = self._require_absolute(
            self.create_iri_with_prefix(prefix, iri_string)
        )

    def set_base_ref(self, base: IRIRef) -> None:
        self._base = self._require_absolute(base)

    def set_prefix(self, prefix_key: str, iri_string: str) -> None:
        self._prefixes[prefix_key] = self._require_absolute(self.create_iri(iri_string))

    def set_prefix_from_prefix(
        self, prefix_key: str, prefix: str, iri_string: str
    ) -> None:
        self._prefixes[prefix_key] = self._require_absolute(
            self.create_iri_with_prefix(prefix, iri_string)
        )

    def set_prefix_ref(self, prefix_key: str, base: IRIRef) -> None:
        self._prefixes[prefix_key] = self._require_absolute(base)

    def relativize(self, iri: IRIRef) -> IRIRef:
        if self._base is None:
            raise ValueError("Base IRI is not set")
        return iri.relativize(self._base)

    def relativize_with_prefix(self, prefix_key: str, iri: IRIRef) -> IRIRef:
        return iri.relativize(self._get(prefix_key))

    def relativize_best(self, iri: IRIRef) -> PrefixedIRIRef:
        best_prefix: Optional[str] = None
        best_ref = self.relativize(iri)
        best_len = len(best_ref.recompose())

        for prefix_key in self._prefixes.keys():
            tested = self.relativize_with_prefix(prefix_key, iri)
            length = len(tested.recompose()) + len(prefix_key) + 1
            if length < best_len:
                best_len = length
                best_ref = tested
                best_prefix = prefix_key

        return PrefixedIRIRef(best_prefix, best_ref)

    def _get(self, prefix_key: str) -> IRIRef:
        if prefix_key not in self._prefixes:
            raise ValueError(f"Unknown prefix: {prefix_key}")
        return self._prefixes[prefix_key]

    @staticmethod
    def _require_absolute(iri: IRIRef) -> IRIRef:
        if not iri.is_absolute():
            raise ValueError("Base IRI must be absolute")
        return iri


__all__ = ["IRIManager", "PrefixedIRIRef"]
