"""
Created on 23 déc. 2021

@author: guillaume
"""
from builtins import property
from enum import Enum
from functools import cache
from typing import Optional

COMPARISON_OPERATORS = frozenset({"<", ">", "<=", ">=", "!="})


class Predicate:
    @cache  # type: ignore[misc]
    def __new__(cls, name: str, arity: int):
        return super(Predicate, cls).__new__(cls)

    def __init__(self, name: str, arity: int):
        if not hasattr(self, "_name"):
            self._name = name
        if not hasattr(self, "_arity"):
            self._arity = arity
        if not hasattr(self, "_display_mode"):
            self._display_mode: str = "functional"
        if not hasattr(self, "_display_symbol"):
            self._display_symbol: Optional[str] = None

    @property
    def arity(self):
        return self._arity

    @property
    def name(self) -> str:
        return self._name

    @property
    def display_mode(self) -> str:
        return self._display_mode

    @property
    def display_symbol(self) -> Optional[str]:
        return self._display_symbol

    def set_display_mode(self, mode: str, symbol: Optional[str] = None) -> None:
        if mode not in {"functional", "infix", "infix_no_spaces"}:
            raise ValueError(f"Unknown display mode: {mode}")
        self._display_mode = mode
        self._display_symbol = symbol

    def __repr__(self) -> str:
        return str(self)+"/"+str(self.arity)

    def __str__(self) -> str:
        return self.name


class SpecialPredicate(Enum):
    EQUALITY = Predicate("=", 2)


SpecialPredicate.EQUALITY.value.set_display_mode("infix_no_spaces", "=")


def comparison_predicate(symbol: str) -> Predicate:
    if symbol not in COMPARISON_OPERATORS:
        raise ValueError(f"Unknown comparison operator: {symbol}")
    predicate = Predicate(symbol, 2)
    predicate.set_display_mode("infix", symbol)
    return predicate


def is_comparison_predicate(predicate: Predicate) -> bool:
    return predicate.name in COMPARISON_OPERATORS
