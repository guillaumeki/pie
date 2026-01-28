"""
Atom-related operations extracted from Substitution class.

@author: guillaume
"""
from typing import Optional

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.substitution.substitution import Substitution


def specialize(from_atom: Atom, to_atom: Atom, sub: Substitution = None) -> Optional[Substitution]:
    """
    Compute a substitution that specializes from_atom to to_atom, if possible.

    Returns None if specialization is not possible (e.g., predicate mismatch or
    conflicting constant assignments).
    """
    if from_atom.predicate != to_atom.predicate:
        return None

    sub = Substitution(sub)

    for i in range(from_atom.predicate.arity):
        from_term = from_atom.terms[i]
        to_term = to_atom.terms[i]

        if from_term.is_rigid:
            if from_term != to_term:
                return None
        else:  # flexible term (Variable)
            if from_term in sub.domain and sub[from_term] != to_term:
                return None
            sub[from_term] = to_term

    return sub
