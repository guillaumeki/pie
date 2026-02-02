"""
Literal term with optional datatype and language.
"""
from __future__ import annotations

from typing import Optional, Any

from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.literal_xsd import (
    datatype_local_name,
    is_xsd_datatype,
    XSD_BOOLEAN,
    XSD_DECIMAL,
    XSD_DOUBLE,
    XSD_FLOAT,
    XSD_INTEGER,
    XSD_STRING,
)


class Literal(Term):
    def __init__(
        self,
        value: object,
        datatype: Optional[str],
        lexical: Optional[str],
        lang: Optional[str],
        comparison_key: object,
    ) -> None:
        identifier = lexical if lexical is not None else value
        Term.__init__(self, identifier)
        self._value = value
        self._datatype = datatype
        self._lexical = lexical
        self._lang = lang
        self._comparison_key = comparison_key

    @property
    def value(self) -> object:
        return self._value

    @property
    def datatype(self) -> Optional[str]:
        return self._datatype

    @property
    def lexical(self) -> Optional[str]:
        return self._lexical

    @property
    def lang(self) -> Optional[str]:
        return self._lang

    @property
    def comparison_key(self) -> object:
        return self._comparison_key

    @property
    def is_ground(self) -> bool:
        return True

    @property
    def comparison_priority(self) -> int:
        return 0

    def apply_substitution(self, substitution) -> "Literal":
        return self

    def __str__(self) -> str:
        if self._lexical is None:
            lexical = str(self._value)
        else:
            lexical = self._lexical

        if self._lang:
            return f"\"{lexical}\"@{self._lang}"

        if self._datatype is None:
            return f"\"{lexical}\""

        local_name = datatype_local_name(self._datatype)
        if is_xsd_datatype(self._datatype):
            if local_name in {XSD_BOOLEAN, XSD_INTEGER, XSD_DECIMAL, XSD_DOUBLE, XSD_FLOAT}:
                return lexical
            if local_name == XSD_STRING:
                return f"\"{lexical}\""

        return f"\"{lexical}\"^^{self._datatype}"

    def __repr__(self) -> str:
        return f"Lit:{self.__str__()}"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Literal):
            return False
        return self._comparison_key == other._comparison_key

    def __hash__(self) -> int:
        return hash(self._comparison_key)
