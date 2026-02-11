"""
Session-level IO configuration.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from prototyping_inference_engine.rdf.translator import RDFTranslationMode


@dataclass(frozen=True)
class SessionIOConfig:
    rdf_translation_mode: RDFTranslationMode = RDFTranslationMode.NATURAL_FULL
    csv_separator: str = ","
    csv_prefix: str = ""
    csv_header_size: int = 0
    rls_header_size: int = 0

    def with_rdf_translation_mode(self, mode: RDFTranslationMode) -> "SessionIOConfig":
        return replace(self, rdf_translation_mode=mode)
