"""
RDF parser producing atoms using translation modes.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from rdflib import Graph  # type: ignore[import-not-found]

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.rdf.translator import (
    RDFTranslationContext,
    RDFTranslationMode,
    RawRDFTranslator,
    NaturalRDFTranslator,
    NaturalFullRDFTranslator,
)
from prototyping_inference_engine.session.term_factories import TermFactories


@dataclass(frozen=True)
class RDFParserConfig:
    translation_mode: RDFTranslationMode = RDFTranslationMode.NATURAL_FULL
    format_hint: Optional[str] = None


class RDFParser:
    def __init__(
        self,
        path: Path,
        term_factories: TermFactories,
        config: Optional[RDFParserConfig] = None,
    ) -> None:
        self._path = Path(path)
        self._term_factories = term_factories
        self._config = config or RDFParserConfig()

    def parse_atoms(self) -> Iterable[Atom]:
        graph = Graph()
        graph.parse(self._path, format=self._config.format_hint)
        translator = self._translator()
        for subject, predicate, obj in graph:
            yield translator.statement_to_atom(subject, predicate, obj)

    def _translator(self):
        context = RDFTranslationContext(self._term_factories)
        mode = self._config.translation_mode
        if mode == RDFTranslationMode.RAW:
            return RawRDFTranslator(context)
        if mode == RDFTranslationMode.NATURAL:
            return NaturalRDFTranslator(context)
        return NaturalFullRDFTranslator(context)
