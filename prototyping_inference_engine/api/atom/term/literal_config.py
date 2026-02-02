"""
Configuration for literal parsing, normalization, and comparison.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Mapping, Optional

from prototyping_inference_engine.api.atom.term.literal_xsd import (
    default_type_parsers,
    default_type_unparsers,
)


class LiteralNormalization(Enum):
    NORMALIZED = "normalized"
    RAW_LEXICAL = "raw_lexical"
    CUSTOM = "custom"


class LiteralComparison(Enum):
    BY_NORMALIZED_VALUE = "by_normalized_value"
    BY_LEXICAL = "by_lexical"
    CUSTOM = "custom"


class LiteralDatatypeResolution(Enum):
    AS_GIVEN = "as_given"
    RESOLVE_PREFIXES = "resolve_prefixes"


class NumericNormalization(Enum):
    FLOAT = "float"
    DECIMAL = "decimal"
    CUSTOM = "custom"


@dataclass(frozen=True)
class LiteralConfig:
    normalization: LiteralNormalization = LiteralNormalization.NORMALIZED
    comparison: LiteralComparison = LiteralComparison.BY_NORMALIZED_VALUE
    keep_lexical: bool = True
    datatype_resolution: LiteralDatatypeResolution = LiteralDatatypeResolution.AS_GIVEN
    numeric_normalization: NumericNormalization = NumericNormalization.FLOAT
    type_parsers: Optional[Mapping[str, Callable[[str], object]]] = None
    type_unparsers: Optional[Mapping[str, Callable[[object], str]]] = None
    comparison_key_builder: Optional[Callable[[object, Optional[str], Optional[str]], object]] = None
    custom_normalizer: Optional[Callable[[str, Optional[str], Optional[str]], object]] = None

    @classmethod
    def default(cls) -> "LiteralConfig":
        numeric_mode = cls().numeric_normalization.value
        return cls(
            type_parsers=default_type_parsers(numeric_mode),
            type_unparsers=default_type_unparsers(numeric_mode),
        )

    def with_overrides(
        self,
        *,
        type_parsers: Optional[Mapping[str, Callable[[str], object]]] = None,
        type_unparsers: Optional[Mapping[str, Callable[[object], str]]] = None,
        **kwargs,
    ) -> "LiteralConfig":
        updated = dict(self.__dict__)
        updated.update(kwargs)
        if type_parsers is not None:
            updated["type_parsers"] = type_parsers
        if type_unparsers is not None:
            updated["type_unparsers"] = type_unparsers
        return LiteralConfig(**updated)
