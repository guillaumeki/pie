"""
Identity-based variable (no global caching).
"""

from typing import TYPE_CHECKING

from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.variable import Variable

if TYPE_CHECKING:
    from prototyping_inference_engine.api.substitution.substitution import Substitution


class IdentityVariable(Variable):
    def __new__(cls, identifier: str):
        return Term.__new__(cls)

    def __init__(self, identifier: str):
        Term.__init__(self, identifier)

    @property
    def is_ground(self) -> bool:
        return False

    @property
    def comparison_priority(self) -> int:
        return 1

    def apply_substitution(self, substitution: "Substitution") -> Term:
        if self in substitution:
            return substitution[self]
        return self

    def __repr__(self):
        return "VarId:" + str(self)
