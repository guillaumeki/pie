"""
Factory for creating Literal instances with configurable normalization.
"""
from __future__ import annotations

from typing import Optional, Callable

from prototyping_inference_engine.api.atom.term.literal import Literal
from prototyping_inference_engine.api.atom.term.literal_config import (
    LiteralConfig,
    LiteralNormalization,
    LiteralComparison,
    LiteralDatatypeResolution,
    NumericNormalization,
)
from prototyping_inference_engine.api.atom.term.literal_xsd import (
    datatype_local_name,
    default_type_parsers,
    default_type_unparsers,
    RDF_NAMESPACE,
    XSD_NAMESPACE,
    XSD_PREFIX,
    RDF_PREFIX,
    RDF_LANG_STRING,
    XSD_STRING,
)


def _make_hashable(value: object) -> object:
    try:
        hash(value)
        return value
    except TypeError:
        pass

    if isinstance(value, list):
        return tuple(_make_hashable(v) for v in value)
    if isinstance(value, tuple):
        return tuple(_make_hashable(v) for v in value)
    if isinstance(value, set):
        return frozenset(_make_hashable(v) for v in value)
    if isinstance(value, dict):
        return tuple(sorted((k, _make_hashable(v)) for k, v in value.items()))
    return repr(value)


def _resolve_builtin_prefix(datatype: Optional[str]) -> Optional[str]:
    if datatype is None:
        return None
    if datatype.startswith(XSD_PREFIX):
        return XSD_NAMESPACE + datatype[len(XSD_PREFIX):]
    if datatype.startswith(RDF_PREFIX):
        return RDF_NAMESPACE + datatype[len(RDF_PREFIX):]
    return datatype


class LiteralFactory:
    def __init__(self, storage, config: Optional[LiteralConfig] = None) -> None:
        self._storage = storage
        self._config = config or LiteralConfig.default()
        self._parsers = self._merge_type_parsers(self._config)
        self._unparsers = self._merge_type_unparsers(self._config)

    @staticmethod
    def _merge_type_parsers(config: LiteralConfig) -> dict[str, Callable[[str], object]]:
        numeric_mode = config.numeric_normalization.value
        defaults = default_type_parsers(numeric_mode)
        if config.type_parsers is None:
            return defaults
        merged = dict(defaults)
        for key, parser in config.type_parsers.items():
            merged[datatype_local_name(key)] = parser
        return merged

    @staticmethod
    def _merge_type_unparsers(config: LiteralConfig) -> dict[str, Callable[[object], str]]:
        numeric_mode = config.numeric_normalization.value
        defaults = default_type_unparsers(numeric_mode)
        if config.type_unparsers is None:
            return defaults
        merged = dict(defaults)
        for key, unparser in config.type_unparsers.items():
            merged[datatype_local_name(key)] = unparser
        return merged

    def create(
        self,
        lexical: str,
        datatype: Optional[str] = None,
        lang: Optional[str] = None,
    ) -> Literal:
        raw_lexical = lexical
        datatype = self._normalize_datatype(datatype, lang)

        if self._config.normalization == LiteralNormalization.CUSTOM:
            if self._config.custom_normalizer is None:
                raise ValueError("custom_normalizer must be set for CUSTOM normalization")
            value = self._config.custom_normalizer(raw_lexical, datatype, lang)
            normalized_lexical = self._unparse(value, datatype)
        elif self._config.normalization == LiteralNormalization.RAW_LEXICAL:
            value = raw_lexical
            normalized_lexical = raw_lexical
        else:
            value, normalized_lexical = self._normalize_value(raw_lexical, datatype, lang)

        stored_lexical = None
        if self._config.keep_lexical:
            if self._config.comparison == LiteralComparison.BY_LEXICAL:
                stored_lexical = raw_lexical
            else:
                stored_lexical = normalized_lexical

        comparison_key = self._build_comparison_key(value, raw_lexical, datatype, lang)
        return self._storage.get_or_create(
            comparison_key,
            lambda: Literal(value, datatype, stored_lexical, lang, comparison_key),
        )

    def _normalize_value(
        self,
        lexical: str,
        datatype: Optional[str],
        lang: Optional[str],
    ) -> tuple[object, str]:
        if datatype is None:
            return lexical, lexical

        local_name = datatype_local_name(datatype)
        parser = self._parsers.get(local_name)
        if parser is None:
            return lexical, lexical

        try:
            value = parser(lexical)
        except Exception:
            return lexical, lexical

        normalized_lexical = self._unparse(value, datatype)
        return value, normalized_lexical

    def _unparse(self, value: object, datatype: Optional[str]) -> str:
        if datatype is None:
            return str(value)
        local_name = datatype_local_name(datatype)
        unparser = self._unparsers.get(local_name)
        if unparser is None:
            return str(value)
        return unparser(value)

    def _build_comparison_key(
        self,
        value: object,
        raw_lexical: str,
        datatype: Optional[str],
        lang: Optional[str],
    ) -> object:
        if self._config.comparison == LiteralComparison.CUSTOM:
            if self._config.comparison_key_builder is None:
                raise ValueError("comparison_key_builder must be set for CUSTOM comparison")
            key = self._config.comparison_key_builder(value, datatype, lang)
            return _make_hashable(key)
        if self._config.comparison == LiteralComparison.BY_LEXICAL:
            return (datatype, raw_lexical, lang)
        return (datatype, _make_hashable(value), lang)

    def _normalize_datatype(self, datatype: Optional[str], lang: Optional[str]) -> Optional[str]:
        if datatype is None:
            datatype = XSD_PREFIX + XSD_STRING

        if lang:
            datatype = RDF_PREFIX + RDF_LANG_STRING

        if self._config.datatype_resolution == LiteralDatatypeResolution.RESOLVE_PREFIXES:
            datatype = _resolve_builtin_prefix(datatype)
        return datatype
