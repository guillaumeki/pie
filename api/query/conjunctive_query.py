"""
Created on 26 déc. 2021

@author: guillaume
"""
import typing

from api.atom.atom import Atom
from api.atom.term.constant import Constant
from api.atom.frozen_atom_set import FrozenAtomSet
from api.query.query import Query
from api.atom.term.term import Term
from api.atom.term.variable import Variable


class ConjunctiveQuery(Query):
    def __init__(self,
                 atoms: typing.Iterable[Atom] = None,
                 answer_variables: typing.Iterable[Variable] = None,
                 label: typing.Optional[str] = None):
        Query.__init__(answer_variables, label)
        if not atoms:
            self._atoms = FrozenAtomSet()
        elif isinstance(atoms, FrozenAtomSet):
            self._atoms = atoms
        else:
            self._atoms = FrozenAtomSet(a for a in atoms)

    @property
    def atoms(self) -> FrozenAtomSet:
        return self._atoms

    @property
    def variables(self) -> set[Variable]:
        return self.atoms.variables

    @property
    def constants(self) -> set[Constant]:
        return self.atoms.constants

    @property
    def terms(self) -> set[Term]:
        return self.atoms.terms

    def query_with_other_answer_variables(self, answers_variables: tuple[Variable]) -> 'ConjunctiveQuery':
        return ConjunctiveQuery(self._atoms, answers_variables)

    @property
    def str_without_answer_variables(self) -> str:
        return ", ".join(map(str, self._atoms))

    def __repr__(self):
        return "ConjunctiveQuery: "+str(self)

    def __str__(self):
        return "({}) :- {}".format(
            ", ".join(map(str, self.answer_variables)),
            ", ".join(map(str, self.atoms)))
