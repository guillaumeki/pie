"""
IRI utilities for parsing, resolving, normalizing, and managing IRIs.
"""

from prototyping_inference_engine.api.iri.iri import IRIRef, IRIParseError
from prototyping_inference_engine.api.iri.normalization import (
    RFCNormalizationScheme,
    IRINormalizer,
    StandardComposableNormalizer,
    ExtendedComposableNormalizer,
)
from prototyping_inference_engine.api.iri.preparator import (
    StringPreparator,
    BasicStringPreparator,
)
from prototyping_inference_engine.api.iri.manager import IRIManager, PrefixedIRIRef

__all__ = [
    "IRIRef",
    "IRIParseError",
    "RFCNormalizationScheme",
    "IRINormalizer",
    "StandardComposableNormalizer",
    "ExtendedComposableNormalizer",
    "StringPreparator",
    "BasicStringPreparator",
    "IRIManager",
    "PrefixedIRIRef",
]
