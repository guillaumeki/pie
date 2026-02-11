"""
Import context for IO parsers.
"""

from __future__ import annotations

from dataclasses import dataclass

from prototyping_inference_engine.rdf.translator import RDFTranslationMode
from prototyping_inference_engine.session.io_config import SessionIOConfig
from prototyping_inference_engine.session.term_factories import TermFactories


@dataclass(frozen=True)
class ImportContext:
    term_factories: TermFactories
    io_config: SessionIOConfig
    python_function_names: set[str]

    @property
    def rdf_translation_mode(self) -> RDFTranslationMode:
        return self.io_config.rdf_translation_mode

    @property
    def csv_separator(self) -> str:
        return self.io_config.csv_separator

    @property
    def csv_prefix(self) -> str:
        return self.io_config.csv_prefix

    @property
    def csv_header_size(self) -> int:
        return self.io_config.csv_header_size

    @property
    def rls_header_size(self) -> int:
        return self.io_config.rls_header_size
