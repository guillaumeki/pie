"""
RLS CSV parsers.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable, Optional

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.io.parsers.csv.csv_parser import (
    CSVParser,
    CSVParserConfig,
)
from prototyping_inference_engine.session.term_factories import TermFactories


@dataclass(frozen=True)
class RLSCSVResult:
    predicate_name: str
    predicate_arity: int
    csv_filepath: str


class RLSCSVParser:
    _pattern = re.compile(r"^@source\s+(.*)\[(\d+)\]:\s+load-csv\(\"(.*)\"\)\s*\.$")

    def __init__(self, path: Path) -> None:
        self._path = Path(path)

    def parse(self) -> Iterable[RLSCSVResult]:
        for line in self._path.read_text(encoding="utf-8").splitlines():
            match = self._pattern.match(line.strip())
            if not match:
                continue
            predicate, arity, csv_path = match.groups()
            resolved = self._resolve_csv_path(csv_path)
            yield RLSCSVResult(predicate, int(arity), resolved)

    def _resolve_csv_path(self, csv_path: str) -> str:
        csv_path = csv_path.strip()
        path = Path(csv_path)
        if not path.is_absolute():
            path = self._path.parent / path
        if not path.exists():
            raise FileNotFoundError(f"CSV file does not exist: {path}")
        return str(path.resolve())


class RLSCSVsParser:
    def __init__(
        self,
        path: Path,
        term_factories: TermFactories,
        config: Optional[CSVParserConfig] = None,
    ) -> None:
        self._path = Path(path)
        self._term_factories = term_factories
        self._config = config or CSVParserConfig()

    def parse_atoms(self) -> Iterable[Atom]:
        rls_parser = RLSCSVParser(self._path)
        for entry in rls_parser.parse():
            csv_parser = CSVParser(
                Path(entry.csv_filepath),
                term_factories=self._term_factories,
                predicate_name=entry.predicate_name,
                predicate_arity=entry.predicate_arity,
                config=self._config,
            )
            yield from csv_parser.parse_atoms()
