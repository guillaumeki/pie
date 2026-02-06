"""
Conversion helpers between FO queries and CQ/UCQ forms.
"""

from typing import List

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.formula.conjunction_formula import (
    ConjunctionFormula,
)
from prototyping_inference_engine.api.formula.disjunction_formula import (
    DisjunctionFormula,
)
from prototyping_inference_engine.api.formula.existential_formula import (
    ExistentialFormula,
)
from prototyping_inference_engine.api.formula.formula import Formula
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.api.query.union_conjunctive_queries import (
    UnionConjunctiveQueries,
)


def _formula_to_atom_sets(formula: Formula) -> List[frozenset[Atom]]:
    if isinstance(formula, Atom):
        return [frozenset([formula])]
    if isinstance(formula, ConjunctionFormula):
        left_sets = _formula_to_atom_sets(formula.left)
        right_sets = _formula_to_atom_sets(formula.right)
        return [left | right for left in left_sets for right in right_sets]
    if isinstance(formula, DisjunctionFormula):
        left_sets = _formula_to_atom_sets(formula.left)
        right_sets = _formula_to_atom_sets(formula.right)
        return left_sets + right_sets
    if isinstance(formula, ExistentialFormula):
        return _formula_to_atom_sets(formula.inner)
    raise ValueError(
        f"Unsupported formula for UCQ conversion: {type(formula).__name__}"
    )


def try_convert_fo_query(fo_query: FOQuery):
    """
    Convert an FOQuery to CQ or UCQ when it only uses atoms, conjunction, disjunction.

    Falls back to the original FOQuery if conversion is not possible.
    """
    try:
        atom_sets = _formula_to_atom_sets(fo_query.formula)
    except ValueError:
        return fo_query

    if not atom_sets:
        return fo_query

    try:
        if len(atom_sets) == 1:
            return ConjunctiveQuery(
                atom_sets[0],
                fo_query.answer_variables,
                fo_query.label,
            )
        cqs = [
            ConjunctiveQuery(
                atoms,
                fo_query.answer_variables,
                fo_query.label,
            )
            for atoms in atom_sets
        ]
        return UnionConjunctiveQueries(
            cqs,
            fo_query.answer_variables,
            fo_query.label,
        )
    except ValueError:
        return fo_query


def fo_query_to_ucq(fo_query: FOQuery) -> UnionConjunctiveQueries:
    atom_sets = _formula_to_atom_sets(fo_query.formula)
    if not atom_sets:
        raise ValueError("Unsupported empty formula for UCQ conversion")
    cqs = [
        ConjunctiveQuery(
            atoms,
            fo_query.answer_variables,
            fo_query.label,
        )
        for atoms in atom_sets
    ]
    return UnionConjunctiveQueries(
        cqs,
        fo_query.answer_variables,
        fo_query.label,
    )
