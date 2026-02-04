"""
Functional term (function symbol applied to terms).
"""
from __future__ import annotations

from typing import Iterable

from prototyping_inference_engine.api.atom.term.term import Term


class FunctionTerm(Term):
    def __init__(self, name: str, args: Iterable[Term]):
        self._name = name
        self._args = tuple(args)
        identifier = (self._name, self._args)
        Term.__init__(self, identifier)

    @property
    def name(self) -> str:
        return self._name

    @property
    def args(self) -> tuple[Term, ...]:
        return self._args

    @property
    def is_ground(self) -> bool:
        return all(arg.is_ground for arg in self._args)

    @property
    def comparison_priority(self) -> int:
        return 2

    def apply_substitution(self, substitution) -> "FunctionTerm":
        return FunctionTerm(self._name, (arg.apply_substitution(substitution) for arg in self._args))

    def __str__(self) -> str:
        return f"{self._name}({', '.join(str(a) for a in self._args)})"

    def __repr__(self) -> str:
        return f"Func:{self.__str__()}"
