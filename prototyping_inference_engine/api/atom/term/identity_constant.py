"""
Identity-based constant (no global caching).
"""

from typing import TYPE_CHECKING

from prototyping_inference_engine.api.atom.term.term import Term

if TYPE_CHECKING:
    from prototyping_inference_engine.api.substitution.substitution import Substitution


class IdentityConstant(Term):
    def __init__(self, identifier: object):
        Term.__init__(self, identifier)

    @property
    def is_ground(self) -> bool:
        return True

    @property
    def comparison_priority(self) -> int:
        return 0

    def apply_substitution(self, substitution: "Substitution") -> "IdentityConstant":
        return self

    def __repr__(self):
        return "CstId:" + str(self)
