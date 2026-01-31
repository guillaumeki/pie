"""
Created on 26 déc. 2021

@author: guillaume
"""
import typing
from functools import cached_property, reduce
from typing import TYPE_CHECKING

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.set.frozen_atom_set import FrozenAtomSet
from prototyping_inference_engine.api.query.query import Query
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.substitution.substitutable import Substitutable
from prototyping_inference_engine.api.substitution.substitution import Substitution

if TYPE_CHECKING:
    from prototyping_inference_engine.api.query.fo_query import FOQuery


class ConjunctiveQuery(Query, Substitutable["ConjunctiveQuery"]):
    def __init__(self,
                 atoms: typing.Iterable[Atom] = None,
                 answer_variables: typing.Iterable[Variable] = None,
                 label: typing.Optional[str] = None,
                 pre_substitution: Substitution = None):
        Query.__init__(self, answer_variables, label)
        if not atoms:
            self._atoms = FrozenAtomSet()
        elif isinstance(atoms, FrozenAtomSet):
            self._atoms = atoms
        else:
            self._atoms = FrozenAtomSet(a for a in atoms)

        self._pre_substitution = Substitution() if pre_substitution is None else pre_substitution

        if any(v not in answer_variables for v in self._pre_substitution.domain):
            raise ValueError(f"A pre substitution can only be on answers variables: {self}")

        if any(v not in self._atoms.variables for v in self.answer_variables if v not in self.pre_substitution.domain):
            raise ValueError("All the answer variables of the CQ must appear in its atoms:" + repr(self))

    @property
    def pre_substitution(self) -> Substitution:
        return self._pre_substitution

    @property
    def atoms(self) -> FrozenAtomSet:
        return self._atoms

    @cached_property
    def variables(self) -> set[Variable]:
        return self.atoms.variables | set(self.answer_variables)

    @property
    def constants(self) -> set[Constant]:
        return self.atoms.constants

    @property
    def terms(self) -> set[Term]:
        return self.atoms.terms

    @cached_property
    def existential_variables(self) -> frozenset[Variable]:
        """Variables in the atoms that are not answer variables (implicitly ∃-quantified)."""
        return frozenset(self.atoms.variables - set(self.answer_variables))

    def to_fo_query(self) -> "FOQuery":
        """
        Convert this conjunctive query to a first-order query.

        The conversion wraps the atoms in a conjunction formula and adds
        explicit existential quantifiers for non-answer variables.

        Example:
            CQ: ?(X) :- p(X,Y), q(Y)
            FOQuery: ?(X) :- ∃Y.(p(X,Y) ∧ q(Y))
        """
        from prototyping_inference_engine.api.formula.conjunction_formula import ConjunctionFormula
        from prototyping_inference_engine.api.formula.existential_formula import ExistentialFormula
        from prototyping_inference_engine.api.formula.formula import Formula
        from prototyping_inference_engine.api.query.fo_query import FOQuery

        atoms_list = list(self.atoms)
        if not atoms_list:
            raise ValueError("Cannot convert empty conjunctive query to FOQuery")

        # Build conjunction from atoms
        formula: Formula = reduce(
            lambda acc, atom: ConjunctionFormula(acc, atom),
            atoms_list[1:],
            atoms_list[0]
        )

        # Wrap in existential quantifiers for non-answer variables
        for var in self.existential_variables:
            formula = ExistentialFormula(var, formula)

        return FOQuery(formula, self.answer_variables, self.label)

    def query_with_other_answer_variables(self, answers_variables: tuple[Variable]) -> 'ConjunctiveQuery':
        return ConjunctiveQuery(self._atoms, answers_variables)

    @property
    def str_without_answer_variables(self) -> str:
        return f"{self.atoms}" + \
            (' \u2227 ' + ' \u2227 '.join(f"{v}={t}" for v, t in self.pre_substitution.graph)
             if self.pre_substitution else '')

    def apply_substitution(self, substitution: Substitution) -> "ConjunctiveQuery":
        return ConjunctiveQuery(substitution(self._atoms),
                                [substitution(v) for v in self.answer_variables],
                                self.label,
                                substitution(self.pre_substitution).restrict_to(substitution(self.answer_variables)))

    def aggregate(self, other: "ConjunctiveQuery") -> "ConjunctiveQuery":
        return ConjunctiveQuery(self._atoms | other._atoms,
                                self.answer_variables + other.answer_variables,
                                self.label,
                                self.pre_substitution.aggregate(other.pre_substitution))

    def __eq__(self, other):
        if not isinstance(other, ConjunctiveQuery):
            return False
        return (self.pre_substitution(self.atoms) == other.pre_substitution(other.atoms)
                and self.pre_substitution(self.answer_variables) == other.pre_substitution(other.answer_variables)
                and self.label == other.label)

    def __hash__(self):
        return hash((self.atoms, self.answer_variables, self.label))

    def __repr__(self):
        return "ConjunctiveQuery: "+str(self)

    def __str__(self):
        return f"({', '.join(map(str, self.answer_variables))}) :- {self.str_without_answer_variables}"
