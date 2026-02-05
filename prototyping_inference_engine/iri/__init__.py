"""
IRI utilities for parsing, resolving, normalizing, and managing IRIs.
"""

from prototyping_inference_engine.iri.iri import IRIRef, IRIParseError
from prototyping_inference_engine.iri.normalization import (
    RFCNormalizationScheme,
    IRINormalizer,
    StandardComposableNormalizer,
    ExtendedComposableNormalizer,
)
from prototyping_inference_engine.iri.preparator import (
    StringPreparator,
    BasicStringPreparator,
)
from prototyping_inference_engine.iri.manager import IRIManager, PrefixedIRIRef

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
