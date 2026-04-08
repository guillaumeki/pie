"""Shared helpers for rule-analysis tests."""

from pathlib import Path

from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser

_PARSER = DlgpeParser.instance()


def parse_rules(text: str) -> tuple[Rule, ...]:
    return tuple(_PARSER.parse_rules(text))


def only_rule(text: str) -> Rule:
    return parse_rules(text)[0]


def rule_labels(rules: tuple[Rule, ...]) -> tuple[str | None, ...]:
    return tuple(rule.label for rule in rules)


def repo_file(*parts: str) -> Path:
    return Path(__file__).resolve().parents[3].joinpath(*parts)
