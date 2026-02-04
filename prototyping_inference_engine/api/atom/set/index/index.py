from abc import ABC, abstractmethod
from typing import Iterator, Optional, TYPE_CHECKING

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.atom_operations import specialize

if TYPE_CHECKING:
    from prototyping_inference_engine.api.substitution.substitution import Substitution


class Index(ABC):
    def match(self, atom: Atom, sub: Optional["Substitution"] = None) -> Iterator[Atom]:
        from prototyping_inference_engine.api.substitution.substitution import (
            Substitution,
        )

        if sub is None:
            sub = Substitution()

        for a in self.domain(atom, sub):
            if specialize(atom, a, sub) is not None:
                yield a

    @abstractmethod
    def domain(self, atom: Atom, sub: "Substitution") -> frozenset[Atom]:
        pass

    def domain_size(self, atom: Atom, sub: "Substitution") -> int:
        return len(self.domain(atom, sub))

    def extend_substitution(
        self, atom: Atom, sub: "Substitution"
    ) -> Iterator["Substitution"]:
        for a in self.domain(atom, sub):
            spec = specialize(atom, a, sub)
            if spec is not None:
                yield spec
