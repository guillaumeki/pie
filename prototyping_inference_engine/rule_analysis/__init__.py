"""Rule-analysis package for native PIE rule properties."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from prototyping_inference_engine.rule_analysis.analyser import RuleAnalyser
    from prototyping_inference_engine.rule_analysis.model import (
        AnalysisReport,
        PropertyId,
        PropertyResult,
        PropertyStatus,
    )

__all__ = [
    "AnalysisReport",
    "PropertyId",
    "PropertyResult",
    "PropertyStatus",
    "RuleAnalyser",
]


def __getattr__(name: str) -> object:
    if name == "RuleAnalyser":
        from prototyping_inference_engine.rule_analysis.analyser import RuleAnalyser

        return RuleAnalyser
    if name in {
        "AnalysisReport",
        "PropertyId",
        "PropertyResult",
        "PropertyStatus",
    }:
        from prototyping_inference_engine.rule_analysis.model import (
            AnalysisReport,
            PropertyId,
            PropertyResult,
            PropertyStatus,
        )

        values = {
            "AnalysisReport": AnalysisReport,
            "PropertyId": PropertyId,
            "PropertyResult": PropertyResult,
            "PropertyStatus": PropertyStatus,
        }
        return values[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
