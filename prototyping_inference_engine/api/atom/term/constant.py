'''
Created on 23 déc. 2021

@author: guillaume
'''
from functools import cache
from typing import TYPE_CHECKING

from prototyping_inference_engine.api.atom.term.term import Term

if TYPE_CHECKING:
    from prototyping_inference_engine.api.substitution.substitution import Substitution


class Constant(Term):
    @cache  # type: ignore[misc]
    def __new__(cls, identifier: object):
        return Term.__new__(cls)

    def __init__(self, identifier: object):
        Term.__init__(self, identifier)

    @property
    def is_ground(self) -> bool:
        return True

    @property
    def comparison_priority(self) -> int:
        return 0  # Constants have highest priority as representatives

    def apply_substitution(self, substitution: "Substitution") -> "Constant":
        return self  # Constants are unchanged by substitution

    def __repr__(self):
        return "Cst:" + str(self)
