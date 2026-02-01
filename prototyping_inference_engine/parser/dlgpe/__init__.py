"""
DLGPE Parser module.

Provides parsing capabilities for DLGPE (Datalog+- Grammar for Positive
Existential rules), an extended version of DLGP.
"""
from prototyping_inference_engine.parser.dlgpe.dlgpe_parser import (
    DlgpeParser,
    DlgpeUnsupportedFeatureError,
)

__all__ = ["DlgpeParser", "DlgpeUnsupportedFeatureError"]
