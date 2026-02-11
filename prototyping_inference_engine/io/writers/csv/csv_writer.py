"""
CSV writer for atoms.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
from typing import Iterable

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.term.literal import Literal


@dataclass(frozen=True)
class CSVWriterConfig:
    separator: str = ","


class CSVWriter:
    def __init__(self, config: CSVWriterConfig | None = None) -> None:
        self._config = config or CSVWriterConfig()

    def write_atoms(self, path: Path, atoms: Iterable[Atom]) -> None:
        atoms = list(atoms)
        if not atoms:
            Path(path).write_text("", encoding="utf-8")
            return
        predicate = atoms[0].predicate
        for atom in atoms:
            if atom.predicate != predicate:
                raise ValueError("CSVWriter expects atoms with a single predicate.")
        with Path(path).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle, delimiter=self._config.separator)
            for atom in atoms:
                writer.writerow([_term_to_csv_value(term) for term in atom.terms])


def _term_to_csv_value(term: object) -> str:
    if isinstance(term, Literal):
        if term.lexical is not None:
            return term.lexical
        return str(term.value)
    return str(getattr(term, "identifier", term))
