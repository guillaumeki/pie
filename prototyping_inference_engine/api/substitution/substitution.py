"""
A substitution mapping variables to terms.
"""
from collections.abc import Iterable
from typing import Union, TypeVar

from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.substitution.substitutable import Substitutable

S = TypeVar("S", bound=Substitutable)


class Substitution(dict[Variable, Term]):
    """A mapping from variables to terms, representing a substitution."""

    def __init__(self, initial: Union["Substitution", dict[Variable, Term]] = None):
        super().__init__(initial or {})

    @property
    def graph(self):
        return self.items()

    @property
    def domain(self):
        return self.keys()

    @property
    def image(self):
        return self.values()

    def restrict_to(self, variables: Iterable[Variable]) -> "Substitution":
        return Substitution({v: self.apply(v) for v in variables if v != self.apply(v)})

    def apply(self, other: S) -> S:
        """Apply this substitution to a Substitutable object."""
        if isinstance(other, Substitutable):
            return other.apply_substitution(self)
        # Handle iterables (tuples, lists) of Substitutable objects
        elif isinstance(other, (tuple, list)):
            return other.__class__(self.apply(item) for item in other)
        else:
            raise TypeError(f"Cannot apply substitution to object of type {type(other).__name__}. "
                            f"Expected Substitutable, tuple, or list.")

    def compose(self, other: "Substitution") -> "Substitution":
        """Compose this substitution with another (self . other)."""
        new_sub = {k: self.apply(v) for k, v in other.items()}
        for k, v in self.items():
            if k not in new_sub:
                new_sub[k] = v
        # Remove identity mappings
        return Substitution({k: v for k, v in new_sub.items() if k != v})

    def aggregate(self, other: "Substitution") -> "Substitution":
        """Merge two substitutions (union of mappings)."""
        return Substitution(self | other)

    def __call__(self, other):
        """Shorthand: compose if Substitution, apply otherwise."""
        if isinstance(other, Substitution):
            return self.compose(other)
        return self.apply(other)

    def __str__(self):
        return "{" + ", ".join(f"{v} \u21A6 {t}" for v, t in self.graph) + "}"

    def __repr__(self):
        return f"<Substitution:{self}>"
