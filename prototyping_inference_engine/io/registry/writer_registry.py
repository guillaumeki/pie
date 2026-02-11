"""
Writer registry for format-aware exports.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, Iterable

from prototyping_inference_engine.api.atom.atom import Atom


class AtomWriter(Protocol):
    def write_atoms(self, path: Path, atoms: Iterable[Atom]) -> None: ...


class WriterRegistry:
    def __init__(self) -> None:
        self._writers: dict[str, AtomWriter] = {}

    def register(self, format_name: str, writer: AtomWriter) -> None:
        self._writers[format_name] = writer

    def get(self, format_name: str) -> AtomWriter:
        if format_name not in self._writers:
            raise KeyError(f"No writer registered for format: {format_name}")
        return self._writers[format_name]
