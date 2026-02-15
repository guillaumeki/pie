"""
Created on 23 déc. 2021

@author: guillaume
"""

from typing import Set, Type, TypeVar, TYPE_CHECKING

from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.formula.formula import Formula

T = TypeVar("T", bound=Term)

if TYPE_CHECKING:
    from prototyping_inference_engine.api.atom.term.constant import Constant
    from prototyping_inference_engine.api.atom.term.variable import Variable
    from prototyping_inference_engine.api.substitution.substitution import Substitution


class Atom(Formula):
    def __init__(self, predicate: Predicate, *terms: Term):
        self._predicate = predicate
        self._terms = terms

    @property
    def predicate(self) -> Predicate:
        return self._predicate

    @property
    def terms(self) -> tuple[Term, ...]:
        return self._terms

    def terms_of_type(self, term_type: Type[T]) -> Set[T]:
        """Return all terms that are instances of the given type."""
        return {t for t in self.terms if isinstance(t, term_type)}

    @property
    def variables(self) -> Set["Variable"]:
        from prototyping_inference_engine.api.atom.term.variable import Variable

        variables: set[Variable] = set()
        for term in self.terms:
            variables.update(self._collect_terms_of_type(term, Variable))
        return variables

    @property
    def constants(self) -> Set["Constant"]:
        from prototyping_inference_engine.api.atom.term.constant import Constant

        constants: set[Constant] = set()
        for term in self.terms:
            constants.update(self._collect_terms_of_type(term, Constant))
        return constants

    @staticmethod
    def _collect_terms_of_type(term: Term, term_type: Type[T]) -> Set[T]:
        found: set[T] = set()
        if isinstance(term, term_type):
            found.add(term)
        args = getattr(term, "args", None)
        if args:
            for arg in args:
                found.update(Atom._collect_terms_of_type(arg, term_type))
        return found

    # Formula interface implementation
    @property
    def free_variables(self) -> frozenset["Variable"]:
        """An atom has no quantifiers, so all variables are free."""
        return frozenset(self.variables)

    @property
    def bound_variables(self) -> frozenset["Variable"]:
        """An atom has no quantifiers, so no variables are bound."""
        return frozenset()

    @property
    def atoms(self) -> frozenset["Atom"]:
        """An atom contains only itself."""
        return frozenset([self])

    def apply_substitution(self, substitution: "Substitution") -> "Atom":
        return Atom(
            self.predicate, *(t.apply_substitution(substitution) for t in self.terms)
        )

    def __getitem__(self, item: int):
        return self._terms[item]

    def __str__(self) -> str:
        if self.predicate.display_mode == "infix" and self.predicate.arity == 2:
            symbol = self.predicate.display_symbol or str(self.predicate)
            return f"{str(self.terms[0])} {symbol} {str(self.terms[1])}"
        if (
            self.predicate.display_mode == "infix_no_spaces"
            and self.predicate.arity == 2
        ):
            symbol = self.predicate.display_symbol or str(self.predicate)
            return f"{str(self.terms[0])}{symbol}{str(self.terms[1])}"

        return str(self.predicate) + "(" + ", ".join(map(str, self.terms)) + ")"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other):
        if not isinstance(other, Atom):
            return False
        else:
            return self.predicate == other.predicate and self.terms == other.terms

    def __hash__(self):
        return hash((self.predicate, self.terms))
