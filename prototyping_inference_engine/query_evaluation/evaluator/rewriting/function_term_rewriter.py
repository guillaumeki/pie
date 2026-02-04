"""
Helpers to rewrite functional terms into computed atoms.
"""

from __future__ import annotations


from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.term.function_term import FunctionTerm
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.formula.formula import Formula
from prototyping_inference_engine.api.formula.negation_formula import NegationFormula


def expand_function_terms(formulas: list[Formula]) -> list[Formula]:
    expanded: list[Formula] = []
    for formula in formulas:
        if isinstance(formula, Atom):
            expanded.extend(rewrite_atom_function_terms(formula))
        elif isinstance(formula, NegationFormula) and formula_contains_function(
            formula
        ):
            raise ValueError("Functional terms are not supported under negation.")
        else:
            expanded.append(formula)
    return expanded


def rewrite_atom_function_terms(atom: Atom) -> list[Atom]:
    new_atoms: list[Atom] = []
    new_terms: list[Term] = []

    for term in atom.terms:
        rewritten_term, extra_atoms = _rewrite_term(term)
        new_atoms.extend(extra_atoms)
        new_terms.append(rewritten_term)

    if new_atoms:
        new_atoms.append(Atom(atom.predicate, *new_terms))
        return new_atoms
    return [atom]


def formula_contains_function(formula: Formula) -> bool:
    if isinstance(formula, Atom):
        return any(term_contains_function(t) for t in formula.terms)
    if isinstance(formula, NegationFormula):
        return formula_contains_function(formula.inner)
    return False


def term_contains_function(term: Term) -> bool:
    if isinstance(term, FunctionTerm):
        return True
    args = getattr(term, "args", None)
    if args:
        return any(term_contains_function(a) for a in args)
    return False


def _rewrite_term(term: Term) -> tuple[Term, list[Atom]]:
    from prototyping_inference_engine.api.data.python_function_data import (
        function_predicate,
    )

    if isinstance(term, FunctionTerm):
        rewritten_args: list[Term] = []
        extra_atoms: list[Atom] = []
        for arg in term.args:
            rewritten_arg, nested_atoms = _rewrite_term(arg)
            extra_atoms.extend(nested_atoms)
            rewritten_args.append(rewritten_arg)
        result_var = Variable.fresh_variable()
        func_predicate = function_predicate(term.name, len(rewritten_args))
        extra_atoms.append(Atom(func_predicate, *rewritten_args, result_var))
        return result_var, extra_atoms
    return term, []
