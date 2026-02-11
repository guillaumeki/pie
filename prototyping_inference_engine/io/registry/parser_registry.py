"""
Parser registry for format-aware imports.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from prototyping_inference_engine.api.atom.set.frozen_atom_set import FrozenAtomSet
from prototyping_inference_engine.session.parse_result import ParseResult

from prototyping_inference_engine.io.registry.format_detection import detect_format
from prototyping_inference_engine.io.registry.import_context import ImportContext


@dataclass(frozen=True)
class ImportParseOutcome:
    result: ParseResult
    imports: list[str]


class ImportParser(Protocol):
    def parse_file(self, path: Path, context: ImportContext) -> ImportParseOutcome: ...


class ParserRegistry:
    def __init__(self) -> None:
        self._parsers: dict[str, ImportParser] = {}

    @classmethod
    def default(cls) -> "ParserRegistry":
        registry = cls()
        registry._register_defaults()
        return registry

    def register(self, format_name: str, parser: ImportParser) -> None:
        self._parsers[format_name] = parser

    def parse_file(self, path: Path, context: ImportContext) -> ImportParseOutcome:
        sample = _read_sample(path)
        detection = detect_format(path, sample)
        parser = self._parsers.get(detection.format)
        if parser is None:
            raise ValueError(f"No parser registered for format: {detection.format}")
        return parser.parse_file(path, context)

    def _register_defaults(self) -> None:
        self.register("dlgpe", _DlgpeImportParser())
        self.register("csv", _CSVImportParser())
        self.register("rls", _RLSImportParser())
        self.register("rdf", _RDFImportParser())


def _read_sample(path: Path, max_chars: int = 512) -> str | None:
    try:
        return path.read_text(encoding="utf-8")[:max_chars]
    except Exception:
        return None


class _DlgpeImportParser:
    def parse_file(self, path: Path, context: ImportContext) -> ImportParseOutcome:
        from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser
        from prototyping_inference_engine.io.parsers.dlgpe.dlgpe_transformer import (
            DlgpeTransformer,
        )
        from prototyping_inference_engine.api.atom.term.literal import Literal

        literal_factory = None
        if context.term_factories.has(Literal):
            literal_factory = context.term_factories.get(Literal)

        transformer = DlgpeTransformer(
            literal_factory=literal_factory,
            term_factories=context.term_factories,
            python_function_names=context.python_function_names,
        )
        text = path.read_text(encoding="utf-8")
        parsed = DlgpeParser.instance().parse(text, transformer)

        facts = list(parsed.get("facts", []))
        rules = set(parsed.get("rules", []))
        queries = set(parsed.get("queries", []))
        constraints = set(parsed.get("constraints", []))
        header = parsed.get("header", {}) or {}
        imports = parsed.get("imports", []) or []

        result = ParseResult(
            facts=FrozenAtomSet(facts),
            rules=frozenset(rules),
            queries=frozenset(queries),
            constraints=frozenset(constraints),
            sources=tuple(),
            base_iri=header.get("base"),
            prefixes=tuple((header.get("prefixes") or {}).items()),
            computed_prefixes=tuple((header.get("computed") or {}).items()),
        )
        return ImportParseOutcome(
            result=result, imports=[str(item) for item in imports]
        )


class _CSVImportParser:
    def parse_file(self, path: Path, context: ImportContext) -> ImportParseOutcome:
        from prototyping_inference_engine.io.parsers.csv.csv_parser import (
            CSVParser,
            CSVParserConfig,
        )

        config = CSVParserConfig(
            separator=context.csv_separator,
            prefix=context.csv_prefix,
            header_size=context.csv_header_size,
        )
        parser = CSVParser(path, context.term_factories, config=config)
        facts = list(parser.parse_atoms())
        result = ParseResult(
            facts=FrozenAtomSet(facts),
            rules=frozenset(),
            queries=frozenset(),
            constraints=frozenset(),
        )
        return ImportParseOutcome(result=result, imports=[])


class _RLSImportParser:
    def parse_file(self, path: Path, context: ImportContext) -> ImportParseOutcome:
        from prototyping_inference_engine.io.parsers.csv.rls_csv_parser import (
            RLSCSVsParser,
        )
        from prototyping_inference_engine.io.parsers.csv.csv_parser import (
            CSVParserConfig,
        )

        config = CSVParserConfig(
            separator=context.csv_separator,
            prefix=context.csv_prefix,
            header_size=context.rls_header_size,
        )
        parser = RLSCSVsParser(path, context.term_factories, config=config)
        facts = list(parser.parse_atoms())
        result = ParseResult(
            facts=FrozenAtomSet(facts),
            rules=frozenset(),
            queries=frozenset(),
            constraints=frozenset(),
        )
        return ImportParseOutcome(result=result, imports=[])


class _RDFImportParser:
    def parse_file(self, path: Path, context: ImportContext) -> ImportParseOutcome:
        from prototyping_inference_engine.io.parsers.rdf.rdf_parser import (
            RDFParser,
            RDFParserConfig,
        )
        from prototyping_inference_engine.io.registry.format_detection import (
            detect_format,
        )

        detection = detect_format(path, _read_sample(path))
        config = RDFParserConfig(
            translation_mode=context.rdf_translation_mode,
            format_hint=detection.rdf_format_hint,
        )
        parser = RDFParser(path, context.term_factories, config=config)
        facts = list(parser.parse_atoms())
        result = ParseResult(
            facts=FrozenAtomSet(facts),
            rules=frozenset(),
            queries=frozenset(),
            constraints=frozenset(),
        )
        return ImportParseOutcome(result=result, imports=[])
