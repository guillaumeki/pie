"""Facade for rule-set analysis over PIE native rule objects."""

# References:
# - "On Rules with Existential Variables: Walking the Decidability Line" —
#   Jean-François Baget, Michel Leclère, Marie-Laure Mugnier, Eric Salvat.
#   Link: https://www.lirmm.fr/~mugnier/ArticlesPostscript/BLMSDecidabilityLine-PreAIJ2011.pdf
# - "Frontier-Guarded Existential Rules and Their Relationships" —
#   Jean-François Baget, Michel Leclère, Marie-Laure Mugnier, Eric Salvat.
#   Link: https://www.ijcai.org/Proceedings/11/Papers/126.pdf
# - "Towards More Expressive Ontology Languages: The Query Answering Problem" —
#   Andrea Calì, Georg Gottlob, Andreas Pieris.
#   Link: https://www.research.ed.ac.uk/en/publications/towards-more-expressive-ontology-languages-the-query-answering-pr/
#
# Summary:
# Rule-set analysis classifies a fixed set of existential rules into decidable
# fragments such as guarded, frontier-guarded, weakly acyclic, sticky, and
# weakly sticky. The analyser orchestrates reusable data analyses and a
# declarative implication registry rather than embedding the hierarchy in one
# monolithic service.
#
# Properties used here:
# - Local properties are evaluated directly on normalized rule fragments.
# - Global properties are evaluated on shared fixpoint data and dependency
#   graphs.
# - Satisfied properties can imply weaker properties through a single registry.
#
# Implementation source:
# This orchestrator is a PIE-native redesign inspired by the literature and the
# legacy Integraal feature set, without copying the legacy Java structure.

from __future__ import annotations

from typing import Iterable

from prototyping_inference_engine.api.kb.rule_base import RuleBase
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.rule_analysis.model import (
    AnalysisReport,
    PropertyId,
    PropertyResult,
    PropertyStatus,
)
from prototyping_inference_engine.rule_analysis.property_registry import (
    DEFAULT_PROPERTY_REGISTRY,
    DEFAULT_PROPERTY_SPECS,
)
from prototyping_inference_engine.rule_analysis.snapshot import AnalysisSnapshot


class RuleAnalyser:
    """Analyse PIE rule sets against a registry of rule properties."""

    def __init__(self, rules: RuleBase | Iterable[Rule]):
        self._snapshot = AnalysisSnapshot(rules)

    @property
    def snapshot(self) -> AnalysisSnapshot:
        return self._snapshot

    def analyse(
        self,
        selected_properties: Iterable[PropertyId] | None = None,
    ) -> AnalysisReport:
        selected = (
            set(DEFAULT_PROPERTY_REGISTRY.keys())
            if selected_properties is None
            else set(selected_properties)
        )

        results: dict[PropertyId, PropertyResult] = {}
        for spec in DEFAULT_PROPERTY_SPECS:
            if spec.property_id not in selected:
                continue
            if spec.property_id in results:
                continue
            result = spec.evaluator(self._snapshot)
            results[spec.property_id] = result
            if result.status == PropertyStatus.SATISFIED:
                self._mark_implied_results(
                    spec.property_id,
                    selected,
                    results,
                )

        return AnalysisReport(snapshot=self._snapshot, results=results)

    def _mark_implied_results(
        self,
        property_id: PropertyId,
        selected: set[PropertyId],
        results: dict[PropertyId, PropertyResult],
    ) -> None:
        spec = DEFAULT_PROPERTY_REGISTRY[property_id]
        for implied_id in spec.implies:
            if implied_id not in selected or implied_id in results:
                continue
            results[implied_id] = PropertyResult(
                property_id=implied_id,
                status=PropertyStatus.SATISFIED,
                explanation=f"Implied by {property_id.value}.",
                evidence=(property_id.value,),
            )
            self._mark_implied_results(implied_id, selected, results)
