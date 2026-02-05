"""String preparation utilities for IRIs."""

from __future__ import annotations

from typing import Callable, Iterable
import html
import re


class StringPreparator:
    """Interface for string preparation before IRI parsing."""

    def transform(self, value: str) -> str:
        return value


class BasicStringPreparator(StringPreparator):
    """Basic preparator with pluggable transformations (html4/xml)."""

    _TRANSFORMERS: dict[str, Callable[[str], str]] = {}

    def __init__(self, transformers: Iterable[str] | None = None) -> None:
        self._transformer_names = list(transformers or [])
        for name in self._transformer_names:
            if name not in self._TRANSFORMERS:
                raise ValueError(f"Unknown preparator transformer: {name}")

    def transform(self, value: str) -> str:
        result = value
        for name in self._transformer_names:
            result = self._TRANSFORMERS[name](result)
        return result

    @classmethod
    def register_transformer(cls, name: str, transformer: Callable[[str], str]) -> None:
        cls._TRANSFORMERS[name] = transformer


def _html4_unescape(value: str) -> str:
    return html.unescape(value)


def _xml_unescape(value: str) -> str:
    def repl(match: re.Match[str]) -> str:
        entity = match.group(1)
        if entity.startswith("#x"):
            try:
                return chr(int(entity[2:], 16))
            except ValueError:
                return match.group(0)
        if entity.startswith("#"):
            try:
                return chr(int(entity[1:], 10))
            except ValueError:
                return match.group(0)
        if entity == "lt":
            return "<"
        if entity == "gt":
            return ">"
        if entity == "amp":
            return "&"
        if entity == "quot":
            return '"'
        if entity == "apos":
            return "'"
        return match.group(0)

    return re.sub(r"&([^;]+);", repl, value)


BasicStringPreparator.register_transformer("html4", _html4_unescape)
BasicStringPreparator.register_transformer("xml", _xml_unescape)
