"""
Import resolver for DLGPE @import directives.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

from prototyping_inference_engine.session.parse_result import ParseResult
from prototyping_inference_engine.io.registry.import_context import ImportContext
from prototyping_inference_engine.io.registry.parser_registry import ParserRegistry


@dataclass(frozen=True)
class ImportResolution:
    results: list[ParseResult]


class ImportResolver:
    def __init__(self, registry: ParserRegistry, context: ImportContext) -> None:
        self._registry = registry
        self._context = context
        self._visited: set[Path] = set()

    def resolve_all(
        self, imports: Iterable[str], base_dir: Path | None
    ) -> ImportResolution:
        results: list[ParseResult] = []
        for raw in imports:
            resolved = self._resolve_path(raw, base_dir)
            results.extend(self._resolve_path_recursive(resolved))
        return ImportResolution(results=results)

    def _resolve_path_recursive(self, path: Path) -> list[ParseResult]:
        if path in self._visited:
            return []
        self._visited.add(path)
        outcome = self._registry.parse_file(path, self._context)
        results = [outcome.result]
        for child in outcome.imports:
            resolved = self._resolve_path(child, path.parent)
            results.extend(self._resolve_path_recursive(resolved))
        return results

    @staticmethod
    def _resolve_path(raw: str, base_dir: Path | None) -> Path:
        raw = raw.strip()
        if raw.startswith("file://"):
            parsed = urlparse(raw)
            return Path(parsed.path).resolve()
        parsed = urlparse(raw)
        if parsed.scheme and parsed.scheme != "file":
            raise ValueError(f"Unsupported import scheme: {parsed.scheme}")
        path = Path(raw)
        if not path.is_absolute():
            if base_dir is None:
                base_dir = Path.cwd()
            path = base_dir / path
        return path.resolve()
