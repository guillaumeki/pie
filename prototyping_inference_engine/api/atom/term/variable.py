'''
Created on 23 déc. 2021

@author: guillaume
'''
from typing import TYPE_CHECKING, Iterable

from prototyping_inference_engine.api.atom.term.term import Term

if TYPE_CHECKING:
    from prototyping_inference_engine.api.substitution.substitution import Substitution


class Variable(Term):
    fresh_counter: int = 0
    variables: dict[object, "Variable"] = {}

    def __new__(cls, identifier):
        if identifier not in cls.variables:
            cls.variables[identifier] = Term.__new__(cls)
        return cls.variables[identifier]

    def __init__(self, identifier):
        Term.__init__(self, identifier)

    @property
    def is_ground(self) -> bool:
        return False

    @property
    def comparison_priority(self) -> int:
        return 1  # Variables have lower priority than constants

    def __repr__(self):
        return "Var:"+str(self)

    def apply_substitution(self, substitution: "Substitution") -> Term:
        if self in substitution:
            return substitution[self]
        return self

    @classmethod
    def fresh_variable(cls) -> "Variable":
        identifier = "V" + str(cls.fresh_counter)
        while identifier in cls.variables:
            cls.fresh_counter += 1
            identifier = "V" + str(cls.fresh_counter)
        return Variable(identifier)

    @classmethod
    def safe_renaming(cls, v: "Variable") -> "Variable":
        # identifier = str(v.identifier) + str(cls.fresh_counter)
        # while identifier in cls.variables:
        #     cls.fresh_counter += 1
        #     identifier = str(v.identifier) + str(cls.fresh_counter)
        # return Variable(identifier)
        return cls.fresh_variable()

    @classmethod
    def safe_renaming_substitution(cls, variables: Iterable["Variable"]) -> "Substitution":
        """Create a substitution that renames all given variables to fresh ones."""
        from prototyping_inference_engine.api.substitution.substitution import Substitution
        return Substitution({v: cls.safe_renaming(v) for v in variables})
