"""Mandatory-parameter specialization for view queries."""

from __future__ import annotations

from dataclasses import dataclass

from prototyping_inference_engine.api.atom.term.literal import Literal
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.data.basic_query import BasicQuery
from prototyping_inference_engine.api.data.views.errors import (
    MissingMandatoryBindingError,
)
from prototyping_inference_engine.api.data.views.model import ViewDeclaration


@dataclass(frozen=True)
class SpecializedViewInvocation:
    """Specialized query payload for one view evaluation call."""

    query_text: str
    position: str | None
    selections: tuple[str | None, ...]
    mandatory_terms: tuple[Term | None, ...]


def specialize_view_invocation(
    declaration: ViewDeclaration,
    query_template: str,
    basic_query: BasicQuery,
) -> SpecializedViewInvocation:
    """Specialize query, position and selection strings with mandatory bindings."""
    query_text = query_template
    position = declaration.position
    selections = [entry.selection for entry in declaration.signature]
    mandatory_terms: list[Term | None] = [None] * declaration.arity

    for index, entry in enumerate(declaration.signature):
        placeholder = entry.mandatory
        if placeholder is None:
            continue

        term = basic_query.get_bound_term(index)
        if term is None or isinstance(term, Variable) or not term.is_ground:
            raise MissingMandatoryBindingError(
                (
                    f"View '{declaration.id}' requires a ground value for mandatory "
                    f"position {index} ({placeholder})"
                )
            )

        replacement = _term_to_placeholder_value(term)
        query_text = query_text.replace(placeholder, replacement)

        if position is not None:
            position = position.replace(placeholder, replacement)

        for pos, selection in enumerate(selections):
            if selection is not None:
                selections[pos] = selection.replace(placeholder, replacement)

        mandatory_terms[index] = term

    return SpecializedViewInvocation(
        query_text=query_text,
        position=position,
        selections=tuple(selections),
        mandatory_terms=tuple(mandatory_terms),
    )


def _term_to_placeholder_value(term: Term) -> str:
    if isinstance(term, Literal):
        if term.lexical is not None:
            return term.lexical
        return str(term.value)
    return str(term.identifier)
