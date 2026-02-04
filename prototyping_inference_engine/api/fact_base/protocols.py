from typing import Protocol, Set, Iterator, Iterable, runtime_checkable

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.variable import Variable


@runtime_checkable
class TermInspectable(Protocol):
    """Fact bases that expose their terms."""

    @property
    def variables(self) -> Set[Variable]: ...

    @property
    def constants(self) -> Set[Constant]: ...

    @property
    def terms(self) -> Set[Term]: ...


@runtime_checkable
class Writable(Protocol):
    """Fact bases that support mutation."""

    def add(self, atom: Atom) -> None: ...

    def update(self, atoms: Iterable[Atom]) -> None: ...


@runtime_checkable
class Enumerable(Protocol):
    """Fact bases that support enumeration."""

    def __len__(self) -> int: ...

    def __iter__(self) -> Iterator[Atom]: ...

    def __contains__(self, atom: Atom) -> bool: ...
