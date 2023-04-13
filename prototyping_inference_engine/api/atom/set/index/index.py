from abc import ABC, abstractmethod
from typing import Iterator

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.substitution.substitution import Substitution


class Index(ABC):
    def match(self, atom: Atom, sub: Substitution = None) -> Iterator[Atom]:
        if sub is None:
            sub = Substitution()

        for a in self.domain(atom, sub):
            if Substitution.specialize(atom, a, sub) is not None:
                yield a

    @abstractmethod
    def domain(self, atom: Atom, sub: Substitution) -> frozenset[Atom]:
        pass

    def domain_size(self, atom: Atom, sub: Substitution) -> int:
        return len(self.domain(atom, sub))

    def extend_substitution(self, atom: Atom, sub: Substitution) -> Iterator[Substitution]:
        for a in self.domain(atom, sub):
            spec = Substitution.specialize(atom, a, sub)
            if spec is not None:
                yield spec
