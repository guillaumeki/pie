"""
Term factories for creating Variables, Constants, and Predicates.

Each factory uses a TermStorageStrategy to determine caching behavior,
enabling different memory management strategies per session.
"""

from prototyping_inference_engine.api.atom.term.factory.variable_factory import (
    VariableFactory,
)
from prototyping_inference_engine.api.atom.term.factory.constant_factory import (
    ConstantFactory,
)
from prototyping_inference_engine.api.atom.term.factory.predicate_factory import (
    PredicateFactory,
)
from prototyping_inference_engine.api.atom.term.factory.literal_factory import (
    LiteralFactory,
)

__all__ = [
    "VariableFactory",
    "ConstantFactory",
    "PredicateFactory",
    "LiteralFactory",
]
