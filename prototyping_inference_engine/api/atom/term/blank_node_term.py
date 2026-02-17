"""Blank node term for RDF anonymous resources."""

from typing import TYPE_CHECKING

from prototyping_inference_engine.api.atom.term.term import Term

if TYPE_CHECKING:
    from prototyping_inference_engine.api.substitution.substitution import Substitution


class BlankNodeTerm(Term):
    """RDF blank node term (existential, non-ground, non-variable)."""

    @staticmethod
    def _normalize(identifier: str) -> str:
        if identifier.startswith("_:"):
            return identifier
        return f"_:{identifier}"

    def __new__(cls, identifier: str):
        normalized = cls._normalize(identifier)
        if normalized not in cls._nodes:
            cls._nodes[normalized] = Term.__new__(cls)
        return cls._nodes[normalized]

    def __init__(self, identifier: str):
        Term.__init__(self, self._normalize(identifier))

    @property
    def is_ground(self) -> bool:
        return False

    @property
    def comparison_priority(self) -> int:
        return 2

    def apply_substitution(self, substitution: "Substitution") -> "BlankNodeTerm":
        return self

    def __repr__(self) -> str:
        return f"BNode:{self.identifier}"

    _nodes: dict[str, "BlankNodeTerm"] = {}
