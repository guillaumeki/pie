"""Missing-value policies for view tuple materialization."""

from __future__ import annotations

from typing import Iterable

from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.logical_function_term import (
    LogicalFunctionalTerm,
)
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.data.views.model import MissingValuePolicy


MISSING_VALUE_CONSTANT = Constant("__missing_value__")


def apply_missing_value_policy(
    policy: MissingValuePolicy,
    *,
    view_name: str,
    row_index: int,
    position: int,
    row_values: Iterable[object],
    mandatory_terms: Iterable[Term],
    optional_counter: int,
) -> Term | None:
    """Convert a missing value according to the declared policy."""
    if policy == MissingValuePolicy.IGNORE:
        return None

    if policy == MissingValuePolicy.FREEZE:
        return MISSING_VALUE_CONSTANT

    if policy == MissingValuePolicy.OPTIONAL:
        return Variable(
            f"__view_optional_{view_name}_{row_index}_{position}_{optional_counter}"
        )

    if policy == MissingValuePolicy.EXIST:
        function_name = f"skolem:{view_name}:{position}"
        args: list[Term] = [
            Constant(str(row_index)),
            Constant(str(position)),
        ]
        args.extend(mandatory_terms)
        args.extend(Constant(str(value)) for value in row_values)
        return LogicalFunctionalTerm(function_name, args)

    raise ValueError(f"Unsupported missing value policy: {policy}")
