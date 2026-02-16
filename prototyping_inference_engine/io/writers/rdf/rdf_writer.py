"""
RDF writer for atoms using RDF translators.
"""

# References:
# - "RDF 1.1 Concepts and Abstract Syntax" —
#   Richard Cyganiak, David Wood, Markus Lanthaler.
#   Link: https://www.w3.org/TR/rdf11-concepts/
#
# Summary:
# RDF defines a graph-based data model with triples that can be serialized into
# standard syntaxes such as Turtle.
#
# Properties used here:
# - Standard RDF graph semantics for triples and IRIs.
#
# Implementation notes:
# This writer uses rdflib to serialize triples produced by PIE translators.

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
class RDFWriterConfig:
    translation_mode: RDFTranslationMode = RDFTranslationMode.NATURAL_FULL
    format_hint: Optional[str] = "turtle"


class RDFWriter:
    def __init__(
        self, term_factories: TermFactories, config: RDFWriterConfig | None = None
    ) -> None:
        self._term_factories = term_factories
        self._config = config or RDFWriterConfig()

    def write_atoms(self, path: Path, atoms: Iterable[Atom]) -> None:
        graph = Graph()
        translator = self._translator()
        for atom in atoms:
            for triple in translator.atom_to_triples(atom):
                graph.add(triple)
        format_hint = self._config.format_hint or "turtle"
        graph.serialize(destination=str(path), format=format_hint)

    def _translator(self):
        context = RDFTranslationContext(self._term_factories)
        mode = self._config.translation_mode
        if mode == RDFTranslationMode.RAW:
            return RawRDFTranslator(context)
        if mode == RDFTranslationMode.NATURAL:
            return NaturalRDFTranslator(context)
        return NaturalFullRDFTranslator(context)
