"""
Session management for Pie reasoning engine.

This package provides ReasoningSession for scoped vocabulary management,
fact base creation, and reasoning operations.
"""
from prototyping_inference_engine.session.providers import (
    FactBaseFactoryProvider,
    RewritingAlgorithmProvider,
    ParserProvider,
    DefaultFactBaseFactoryProvider,
    DefaultRewritingAlgorithmProvider,
    Dlgp2ParserProvider,
    DlgpeParserProvider,
)
from prototyping_inference_engine.session.parse_result import ParseResult
from prototyping_inference_engine.session.cleanup_stats import SessionCleanupStats
from prototyping_inference_engine.session.term_factories import TermFactories
from prototyping_inference_engine.session.reasoning_session import ReasoningSession

__all__ = [
    # Main class
    "ReasoningSession",
    # Term factory registry
    "TermFactories",
    # Providers
    "FactBaseFactoryProvider",
    "RewritingAlgorithmProvider",
    "ParserProvider",
    "DefaultFactBaseFactoryProvider",
    "DefaultRewritingAlgorithmProvider",
    "Dlgp2ParserProvider",
    "DlgpeParserProvider",
    # Support classes
    "ParseResult",
    "SessionCleanupStats",
]
