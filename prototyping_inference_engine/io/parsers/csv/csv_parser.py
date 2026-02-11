"""
CSV parser producing atoms.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
from typing import Iterable, Optional

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.literal import Literal
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.session.term_factories import TermFactories


@dataclass(frozen=True)
class CSVParserConfig:
    separator: str = ","
    prefix: str = ""
    header_size: int = 0


class CSVParser:
    def __init__(
        self,
        path: Path,
        term_factories: TermFactories,
        predicate_name: Optional[str] = None,
        predicate_arity: Optional[int] = None,
        config: Optional[CSVParserConfig] = None,
    ) -> None:
        self._path = Path(path)
        self._term_factories = term_factories
        self._predicate_name = predicate_name
        self._predicate_arity = predicate_arity
        self._config = config or CSVParserConfig()

    def parse_atoms(self) -> Iterable[Atom]:
        predicate = None
        with self._path.open(newline="", encoding="utf-8") as handle:
            reader = csv.reader(handle, delimiter=self._config.separator)
            for _ in range(self._config.header_size):
                next(reader, None)
            for row in reader:
                if predicate is None:
                    predicate = self._resolve_predicate(len(row))
                if len(row) != predicate.arity:
                    raise ValueError(
                        f"Row length {len(row)} does not match predicate arity {predicate.arity}"
                    )
                terms = tuple(self._to_term(value) for value in row)
                yield Atom(predicate, *terms)

    def _resolve_predicate(self, arity: int) -> Predicate:
        name = self._predicate_name
        if name is None:
            stem = self._path.stem.lower()
            name = f"{self._config.prefix}{stem}"
        if self._predicate_arity is not None:
            arity = self._predicate_arity
        from prototyping_inference_engine.api.atom.predicate import Predicate as Pred

        if self._term_factories.has(Pred):
            return self._term_factories.get(Pred).create(name, arity)
        return Pred(name, arity)

    def _to_term(self, value: str) -> Term:
        if self._term_factories.has(Literal):
            literal_factory = self._term_factories.get(Literal)
            return literal_factory.create(value)
        if self._term_factories.has(Constant):
            return self._term_factories.get(Constant).create(value)
        return Constant(value)
