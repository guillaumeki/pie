"""Helpers for forward-chaining test ports."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from prototyping_inference_engine.api.atom.set.frozen_atom_set import FrozenAtomSet
from prototyping_inference_engine.api.atom.set.homomorphism.backtrack.naive_backtrack_homomorphism_algorithm import (
    NaiveBacktrackHomomorphismAlgorithm,
)
from prototyping_inference_engine.api.data.readable_data import ReadableData
from prototyping_inference_engine.api.fact_base.fact_base import FactBase
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import (
    MutableInMemoryFactBase,
)
from prototyping_inference_engine.api.formula.conjunction_formula import (
    ConjunctionFormula,
)
from prototyping_inference_engine.api.formula.disjunction_formula import (
    DisjunctionFormula,
)
from prototyping_inference_engine.api.formula.existential_formula import (
    ExistentialFormula,
)
from prototyping_inference_engine.api.formula.formula import Formula
from prototyping_inference_engine.api.formula.negation_formula import NegationFormula
from prototyping_inference_engine.api.formula.universal_formula import UniversalFormula
from prototyping_inference_engine.api.kb.rule_base import RuleBase
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.forward_chaining.chase.chase_builder import (
    ChaseBuilder,
)
from prototyping_inference_engine.forward_chaining.chase.data.chasable_data import (
    ChasableData,
)
from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser
from prototyping_inference_engine.utils.piece_splitter import (
    VariableInducedPieceSplitter,
)

_PARSER = DlgpeParser.instance()
_HOMOMORPHISM = NaiveBacktrackHomomorphismAlgorithm.instance()
_PIECE_SPLITTER = VariableInducedPieceSplitter()
_RESOURCE_ROOT = Path(__file__).resolve().parent / "resources" / "knowledge_bases"


class SingleSourceChasableData(ChasableData):
    """Test helper keeping term enumeration support on the writing target."""

    def __init__(
        self,
        writing_target: FactBase,
        data_sources: tuple[ReadableData, ...] = (),
    ) -> None:
        self._writing_target = writing_target
        self._data_sources = data_sources

    def get_writing_target(self) -> FactBase:
        return self._writing_target

    def get_data_sources(self) -> tuple[ReadableData, ...]:
        return self._data_sources

    def set_data_sources(self, sources: Iterable[ReadableData]) -> None:
        self._data_sources = tuple(sources)

    def get_all_readable_data(self) -> ReadableData:
        if not self._data_sources:
            return self._writing_target
        return self._writing_target


def load_input_kb(file_name: str) -> tuple[MutableInMemoryFactBase, RuleBase]:
    parsed = _PARSER.parse_file(_RESOURCE_ROOT / file_name)
    fact_base = MutableInMemoryFactBase(parsed["facts"])
    normalized_rules = {_to_portable_rule(rule) for rule in parsed["rules"]}
    rule_base = RuleBase(normalized_rules)
    return fact_base, rule_base


def load_expected_fact_base(file_name: str) -> MutableInMemoryFactBase:
    parsed = _PARSER.parse_file(_RESOURCE_ROOT / file_name)
    return MutableInMemoryFactBase(parsed["facts"])


def parse_expected_atoms(text: str) -> MutableInMemoryFactBase:
    return MutableInMemoryFactBase(_PARSER.parse_atoms(text))


def test_builder(fact_base: FactBase, rule_base: RuleBase) -> ChaseBuilder:
    data = SingleSourceChasableData(fact_base)
    return ChaseBuilder.default_builder(data, rule_base)


def is_core(fact_base: FactBase) -> bool:
    atom_set = FrozenAtomSet(fact_base)
    expected_size = len(atom_set)

    for homomorphism in _HOMOMORPHISM.compute_homomorphisms(atom_set, atom_set):
        if len(homomorphism(atom_set)) != expected_size:
            return False
    return True


def is_equivalent(left: FactBase, right: FactBase) -> bool:
    left_set = FrozenAtomSet(left)
    right_set = FrozenAtomSet(right)

    for piece in _fact_base_pieces(left_set):
        if not _HOMOMORPHISM.exist_homomorphism(piece, right_set):
            return False

    for piece in _fact_base_pieces(right_set):
        if not _HOMOMORPHISM.exist_homomorphism(piece, left_set):
            return False

    return True


def _fact_base_pieces(atom_set: FrozenAtomSet) -> tuple[FrozenAtomSet, ...]:
    pieces = list(_PIECE_SPLITTER.split(atom_set, atom_set.variables))
    ground_atoms = {atom for atom in atom_set if not atom.variables}
    if ground_atoms:
        pieces.append(FrozenAtomSet(ground_atoms))
    return tuple(pieces)


class PortableRule(Rule):
    """Rule variant with explicit frontier override for parser portability."""

    def __init__(
        self,
        body: Formula,
        head: Formula,
        label: str | None = None,
        frontier_override=None,
    ) -> None:
        self._body = body
        self._head = head
        self._label = label
        if frontier_override is None:
            frontier_override = body.free_variables & head.free_variables
        self._frontier = frozenset(frontier_override)


def _to_portable_rule(rule: Rule) -> Rule:
    body = _strip_quantifiers(rule.body)
    head = _normalize_head(rule.head)
    return PortableRule(body, head, rule.label, frontier_override=rule.frontier)


def _strip_quantifiers(formula: Formula) -> Formula:
    if isinstance(formula, (UniversalFormula, ExistentialFormula)):
        return _strip_quantifiers(formula.inner)
    if isinstance(formula, ConjunctionFormula):
        return ConjunctionFormula(
            _strip_quantifiers(formula.left),
            _strip_quantifiers(formula.right),
        )
    if isinstance(formula, DisjunctionFormula):
        return DisjunctionFormula(
            _strip_quantifiers(formula.left),
            _strip_quantifiers(formula.right),
        )
    if isinstance(formula, NegationFormula):
        return NegationFormula(_strip_quantifiers(formula.inner))
    return formula


def _normalize_head(formula: Formula) -> Formula:
    if isinstance(formula, UniversalFormula):
        return _normalize_head(formula.inner)
    if isinstance(formula, ExistentialFormula):
        return ExistentialFormula(
            formula.variable,
            _normalize_head(formula.inner),
        )
    if isinstance(formula, ConjunctionFormula):
        return ConjunctionFormula(
            _normalize_head(formula.left),
            _normalize_head(formula.right),
        )
    if isinstance(formula, DisjunctionFormula):
        return DisjunctionFormula(
            _normalize_head(formula.left),
            _normalize_head(formula.right),
        )
    if isinstance(formula, NegationFormula):
        return NegationFormula(_normalize_head(formula.inner))
    return formula
