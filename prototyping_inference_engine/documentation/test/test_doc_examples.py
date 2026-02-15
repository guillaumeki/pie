"""Ensure documentation examples are accurate and covered by tests."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import textwrap
import unittest
from typing import Callable, cast

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.term.literal import Literal
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.formula.fo_conjunction_fact_base_wrapper import (
    FOConjunctionFactBaseWrapper,
)
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser
from prototyping_inference_engine.io.parsers.dlgpe.conversions import (
    try_convert_fo_query,
)
from prototyping_inference_engine.session.reasoning_session import ReasoningSession


@dataclass(frozen=True)
class DocExample:
    language: str
    content: str
    runner: Callable[[str], None] | None = None


def _extract_code_blocks(text: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    in_block = False
    language = ""
    buffer: list[str] = []
    for line in text.splitlines():
        if line.startswith("```"):
            if in_block:
                blocks.append((language, "\n".join(buffer).strip("\n")))
                in_block = False
                language = ""
                buffer = []
            else:
                in_block = True
                language = line[3:].strip()
            continue
        if in_block:
            buffer.append(line)
    if in_block:
        raise AssertionError("Unclosed code block in documentation.")
    return blocks


def _find_neighbor_text_line(lines: list[str], start: int, step: int) -> str:
    index = start
    while 0 <= index < len(lines):
        line = lines[index].strip()
        if line and not line.startswith("```"):
            return line
        index += step
    return ""


def _extract_code_blocks_with_context(
    text: str,
) -> list[tuple[str, str, str, str]]:
    blocks: list[tuple[str, str, str, str]] = []
    lines = text.splitlines()
    in_block = False
    language = ""
    buffer: list[str] = []
    start_index = -1
    for index, line in enumerate(lines):
        if line.startswith("```"):
            if in_block:
                before = _find_neighbor_text_line(lines, start_index - 1, -1)
                after = _find_neighbor_text_line(lines, index + 1, 1)
                blocks.append((language, "\n".join(buffer).strip("\n"), before, after))
                in_block = False
                language = ""
                buffer = []
                start_index = -1
            else:
                in_block = True
                language = line[3:].strip()
                start_index = index
            continue
        if in_block:
            buffer.append(line)
    if in_block:
        raise AssertionError("Unclosed code block in documentation.")
    return blocks


def _normalize_term(term: object) -> object:
    if isinstance(term, Literal):
        return _normalize_value(term.value)
    if isinstance(term, Term):
        return term.identifier
    return term


def _normalize_value(value: object) -> object:
    if isinstance(value, Literal):
        return _normalize_value(value.value)
    if isinstance(value, Term):
        return _normalize_term(value)
    if isinstance(value, dict):
        return {_normalize_term(k): _normalize_term(v) for k, v in value.items()}
    if isinstance(value, set):
        return {_normalize_value(v) for v in value}
    if isinstance(value, list):
        return [_normalize_value(v) for v in value]
    if isinstance(value, tuple):
        return tuple(_normalize_value(v) for v in value)
    return value


def _normalize_projected(answers: list[tuple[Term, ...]]) -> list[tuple[object, ...]]:
    return [tuple(_normalize_term(term) for term in answer) for answer in answers]


def _evaluate_dlgpe_queries(
    text: str,
) -> list[tuple[FOQuery, list[tuple[Term, ...]]]]:
    with ReasoningSession.create() as session:
        result = session.parse(text)
        fb = session.create_fact_base(result.facts)
        results: list[tuple[FOQuery, list[tuple[Term, ...]]]] = []
        for query in result.queries:
            fo_query = cast(FOQuery, query)
            answers = list(
                session.evaluate_query_with_sources(fo_query, fb, result.sources)
            )
            results.append((fo_query, answers))
        return results


def _collect_single_answer_results(
    results: list[tuple[FOQuery, list[tuple[Term, ...]]]],
) -> dict[str, object]:
    observed: dict[str, object] = {}
    for query, query_answers in results:
        if len(query_answers) != 1:
            raise AssertionError("Expected exactly one answer per query.")
        atom = next(iter(query.atoms))
        observed[atom.predicate.name] = _normalize_term(query_answers[0][0])
    return {key.replace("ig:", "stdfct:", 1): value for key, value in observed.items()}


def _run_usage_parsing_example(source: str) -> None:
    namespace: dict[str, object] = {}
    exec(source, namespace)  # nosec B102
    projected = cast(list[tuple[Term, ...]], namespace["projected"])
    self_check = _normalize_projected(projected)
    expected = {("a", "c"), ("b", "d")}
    if set(self_check) != expected:
        raise AssertionError(f"Unexpected projected answers: {self_check}")


def _run_usage_session_example(source: str) -> None:
    namespace: dict[str, object] = {}
    exec(source, namespace)  # nosec B102
    answers = cast(list[tuple[Term, ...]], namespace["answers"])
    normalized = _normalize_projected(answers)
    if normalized != [("b",)]:
        raise AssertionError(f"Unexpected session answers: {normalized}")


def _run_iri_example(source: str) -> None:
    namespace: dict[str, object] = {}
    exec(source, namespace)  # nosec B102
    value = namespace["value"]
    if value != "http://example.org/ns/resource":
        raise AssertionError(f"Unexpected IRI value: {value}")


def _run_export_example(source: str) -> None:
    namespace: dict[str, object] = {}
    exec(source, namespace)  # nosec B102
    output = cast(str, namespace["output"])
    required = [
        "@base <http://example.org/base/>.",
        "@prefix ex: <http://example.org/ns/>.",
        "@facts",
        "<rel>(ex:obj).",
    ]
    for line in required:
        if line not in output:
            raise AssertionError(f"Missing '{line}' in exported DLGPE.")


def _run_dlgpe_file_example(source: str) -> None:
    namespace: dict[str, object] = {}
    exec(source, namespace)  # nosec B102
    atoms = cast(list[Atom], namespace["atoms"])
    predicates = [atom.predicate.name for atom in atoms]
    terms = [[term.identifier for term in atom.terms] for atom in atoms]
    if predicates != ["p", "q"] or terms != [["a"], ["b"]]:
        raise AssertionError(f"Unexpected file atoms: {atoms}")


def _run_csv_parser_example(source: str) -> None:
    namespace: dict[str, object] = {}
    exec(source, namespace)  # nosec B102
    atoms = cast(list[Atom], namespace["atoms"])
    predicates = [atom.predicate.name for atom in atoms]
    terms = [[term.identifier for term in atom.terms] for atom in atoms]
    if predicates != ["people", "people"]:
        raise AssertionError(f"Unexpected CSV predicates: {predicates}")
    if terms != [["alice", "bob"], ["carol", "dave"]]:
        raise AssertionError(f"Unexpected CSV atoms: {atoms}")


def _run_rls_csv_example(source: str) -> None:
    namespace: dict[str, object] = {}
    exec(source, namespace)  # nosec B102
    atoms = cast(list[Atom], namespace["atoms"])
    predicates = [atom.predicate.name for atom in atoms]
    terms = [[term.identifier for term in atom.terms] for atom in atoms]
    if predicates != ["p", "p", "q"]:
        raise AssertionError(f"Unexpected RLS predicates: {predicates}")
    if terms != [["a", "b"], ["c", "d"], ["e", "f"]]:
        raise AssertionError(f"Unexpected RLS atoms: {atoms}")


def _run_rdf_parser_example(source: str) -> None:
    namespace: dict[str, object] = {}
    exec(source, namespace)  # nosec B102
    atoms = cast(list[Atom], namespace["atoms"])
    observed = {
        (atom.predicate.name, tuple(term.identifier for term in atom.terms))
        for atom in atoms
    }
    expected = {
        ("http://example.org/Person", ("http://example.org/a",)),
        ("http://example.org/knows", ("http://example.org/a", "bob")),
    }
    if observed != expected:
        raise AssertionError(f"Unexpected RDF atoms: {atoms}")


def _run_imports_example(source: str) -> None:
    namespace: dict[str, object] = {}
    exec(source, namespace)  # nosec B102
    atoms = cast(list[Atom], namespace["atoms"])
    observed = {
        (atom.predicate.name, tuple(term.identifier for term in atom.terms))
        for atom in atoms
    }
    expected = {
        ("facts", ("a", "b")),
        ("p", ("a",)),
        (
            "triple",
            (
                "http://example.org/a",
                "http://example.org/knows",
                "http://example.org/b",
            ),
        ),
    }
    if observed != expected:
        raise AssertionError(f"Unexpected import atoms: {atoms}")


def _run_index_quick_start_example(source: str) -> None:
    namespace: dict[str, object] = {}
    exec(source, namespace)  # nosec B102
    answers = cast(list[tuple[Term, ...]], namespace["answers"])
    normalized = _normalize_projected(answers)
    expected = {("a", "c"), ("b", "d")}
    if set(normalized) != expected:
        raise AssertionError(f"Unexpected quick start answers: {normalized}")


def _run_computed_sum_example(source: str) -> None:
    _, answers = _evaluate_dlgpe_queries(source)[0]
    normalized = _normalize_projected(answers)
    if normalized != [(2,)]:
        raise AssertionError(f"Unexpected sum answers: {normalized}")


def _run_computed_sum_python_example(source: str) -> None:
    namespace: dict[str, object] = {}
    exec(source, namespace)  # nosec B102
    projected = cast(list[tuple[object, ...]], namespace["projected"])
    normalized = [tuple(_normalize_term(term) for term in row) for row in projected]
    if normalized != [(2,)]:
        raise AssertionError(f"Unexpected sum projected: {projected}")


def _run_computed_json_example(source: str) -> None:
    _, answers = _evaluate_dlgpe_queries(source)[0]
    if answers != [tuple()]:
        raise AssertionError(f"Unexpected computed JSON answers: {answers}")


def _run_computed_json_python_example(source: str) -> None:
    namespace: dict[str, object] = {}
    exec(source, namespace)  # nosec B102
    projected = cast(list[tuple[object, ...]], namespace["projected"])
    normalized = [tuple(_normalize_term(term) for term in row) for row in projected]
    if normalized != [tuple()]:
        raise AssertionError(f"Unexpected computed JSON projected: {projected}")


def _run_function_term_example(source: str) -> None:
    _, answers = _evaluate_dlgpe_queries(source)[0]
    if answers != [tuple()]:
        raise AssertionError(f"Unexpected functional-term answers: {answers}")


def _run_function_term_python_example(source: str) -> None:
    namespace: dict[str, object] = {}
    exec(source, namespace)  # nosec B102
    projected = cast(list[tuple[object, ...]], namespace["projected"])
    normalized = [tuple(_normalize_term(term) for term in row) for row in projected]
    if normalized != [tuple()]:
        raise AssertionError(f"Unexpected functional-term projected: {projected}")


def _run_negated_function_term_example(source: str) -> None:
    _, answers = _evaluate_dlgpe_queries(source)[0]
    if answers != [tuple()]:
        raise AssertionError(f"Unexpected negated functional-term answers: {answers}")


def _run_negated_function_term_python_example(source: str) -> None:
    namespace: dict[str, object] = {}
    exec(source, namespace)  # nosec B102
    projected = cast(list[tuple[object, ...]], namespace["projected"])
    normalized = [tuple(_normalize_term(term) for term in row) for row in projected]
    if normalized != [tuple()]:
        raise AssertionError(
            f"Unexpected negated functional-term projected: {projected}"
        )


def _run_arithmetic_expression_dlgpe_example(source: str) -> None:
    results = _evaluate_dlgpe_queries(source)
    normalized = [_normalize_projected(answers) for _, answers in results]
    expected = [[(2,)], [tuple()]]
    if normalized != expected:
        raise AssertionError(
            f"Unexpected arithmetic expression results: {normalized} (expected {expected})"
        )


def _run_arithmetic_expression_python_example(source: str) -> None:
    namespace: dict[str, object] = {}
    exec(source, namespace)  # nosec B102
    normalized = cast(list[list[tuple[object, ...]]], namespace["normalized"])
    expected = [[("2",)], [tuple()]]
    if normalized != expected:
        raise AssertionError(
            f"Unexpected arithmetic expression results: {normalized} (expected {expected})"
        )


def _run_arithmetic_functions_example(source: str) -> None:
    normalized_observed = _collect_single_answer_results(
        _evaluate_dlgpe_queries(source)
    )
    expected = {
        "stdfct:sum": 3,
        "stdfct:min": 1,
        "stdfct:max": 3,
        "stdfct:minus": 7,
        "stdfct:product": 6,
        "stdfct:divide": 4,
        "stdfct:power": 8,
        "stdfct:average": 3,
        "stdfct:median": 4,
        "stdfct:weightedAverage": 17.5,
        "stdfct:weightedMedian": 20,
    }

    if normalized_observed != expected:
        raise AssertionError(
            f"Unexpected arithmetic results: {normalized_observed} (expected {expected})"
        )


def _run_arithmetic_functions_python_example(source: str) -> None:
    namespace: dict[str, object] = {}
    exec(source, namespace)  # nosec B102
    pairs = cast(list[tuple[str, object]], namespace["pairs"])
    normalized = [(name, _normalize_term(value)) for name, value in pairs]
    expected = [
        ("stdfct:sum", 3),
        ("stdfct:min", 1),
        ("stdfct:max", 3),
        ("stdfct:minus", 7),
        ("stdfct:product", 6),
        ("stdfct:divide", 4),
        ("stdfct:power", 8),
        ("stdfct:average", 3),
        ("stdfct:median", 4),
        ("stdfct:weightedAverage", 17.5),
        ("stdfct:weightedMedian", 20),
    ]
    if normalized != expected:
        raise AssertionError(f"Unexpected arithmetic pairs: {pairs}")


def _run_comparison_functions_example(source: str) -> None:
    normalized_observed = _collect_single_answer_results(
        _evaluate_dlgpe_queries(source)
    )
    expected = {
        "stdfct:isEven": True,
        "stdfct:isOdd": True,
        "stdfct:isPrime": True,
        "stdfct:isGreaterThan": True,
        "stdfct:isGreaterOrEqualsTo": True,
        "stdfct:isSmallerThan": True,
        "stdfct:isSmallerOrEqualsTo": True,
        "stdfct:isLexicographicallyGreaterThan": True,
        "stdfct:isLexicographicallyGreaterOrEqualsTo": True,
        "stdfct:isLexicographicallySmallerThan": True,
        "stdfct:isLexicographicallySmallerOrEqualsTo": True,
        "stdfct:equals": True,
        "stdfct:contains": True,
        "stdfct:isEmpty": True,
        "stdfct:isBlank": True,
        "stdfct:isNumeric": True,
    }

    if normalized_observed != expected:
        raise AssertionError(
            f"Unexpected comparison results: {normalized_observed} (expected {expected})"
        )


def _run_comparison_functions_python_example(source: str) -> None:
    namespace: dict[str, object] = {}
    exec(source, namespace)  # nosec B102
    pairs = cast(list[tuple[str, object]], namespace["pairs"])
    normalized = [(name, _normalize_term(value)) for name, value in pairs]
    expected = [
        ("stdfct:isEven", True),
        ("stdfct:isOdd", True),
        ("stdfct:isPrime", True),
        ("stdfct:isGreaterThan", True),
        ("stdfct:isGreaterOrEqualsTo", True),
        ("stdfct:isSmallerThan", True),
        ("stdfct:isSmallerOrEqualsTo", True),
        ("stdfct:isLexicographicallyGreaterThan", True),
        ("stdfct:isLexicographicallyGreaterOrEqualsTo", True),
        ("stdfct:isLexicographicallySmallerThan", True),
        ("stdfct:isLexicographicallySmallerOrEqualsTo", True),
        ("stdfct:equals", True),
        ("stdfct:contains", True),
        ("stdfct:isEmpty", True),
        ("stdfct:isBlank", True),
        ("stdfct:isNumeric", True),
    ]
    if normalized != expected:
        raise AssertionError(f"Unexpected comparison pairs: {pairs}")


def _run_string_functions_example(source: str) -> None:
    normalized_observed = _collect_single_answer_results(
        _evaluate_dlgpe_queries(source)
    )
    expected = {
        "stdfct:concat": "foobar",
        "stdfct:toLowerCase": "abc",
        "stdfct:toUpperCase": "ABC",
        "stdfct:replace": "aBc",
        "stdfct:length": 4,
        "stdfct:toString": "1",
        "stdfct:toStringWithDatatype": "Literal<int> 1",
        "stdfct:toInt": 12,
        "stdfct:toFloat": 1.5,
        "stdfct:toBoolean": True,
    }

    if normalized_observed != expected:
        raise AssertionError(
            f"Unexpected string results: {normalized_observed} (expected {expected})"
        )


def _run_string_functions_python_example(source: str) -> None:
    namespace: dict[str, object] = {}
    exec(source, namespace)  # nosec B102
    pairs = cast(list[tuple[str, object]], namespace["pairs"])
    normalized = [(name, _normalize_term(value)) for name, value in pairs]
    expected = [
        ("stdfct:concat", "foobar"),
        ("stdfct:toLowerCase", "abc"),
        ("stdfct:toUpperCase", "ABC"),
        ("stdfct:replace", "aBc"),
        ("stdfct:length", 4),
        ("stdfct:toString", "1"),
        ("stdfct:toStringWithDatatype", "Literal<int> 1"),
        ("stdfct:toInt", 12),
        ("stdfct:toFloat", 1.5),
        ("stdfct:toBoolean", True),
    ]
    if normalized != expected:
        raise AssertionError(f"Unexpected string pairs: {pairs}")


def _run_collection_functions_example(source: str) -> None:
    normalized_observed = _collect_single_answer_results(
        _evaluate_dlgpe_queries(source)
    )
    expected = {
        "stdfct:set": {"a", "b"},
        "stdfct:tuple": ["a", "b"],
        "stdfct:union": {"a", "b", "c"},
        "stdfct:size": 2,
        "stdfct:intersection": {"b"},
        "stdfct:isSubset": True,
        "stdfct:isStrictSubset": True,
        "stdfct:dict": {"a": "b", "b": "c"},
        "stdfct:mergeDicts": {"a": "b", "c": "d"},
        "stdfct:dictKeys": {"a", "b"},
        "stdfct:dictValues": ["b", "c"],
        "stdfct:get": "b",
        "stdfct:containsKey": True,
        "stdfct:containsValue": True,
        "stdfct:toSet": {"a", "b"},
        "stdfct:toTuple": ["a", "b"],
    }

    if normalized_observed != expected:
        raise AssertionError(
            f"Unexpected collection result: {normalized_observed} (expected {expected})"
        )


def _run_collection_functions_python_example(source: str) -> None:
    namespace: dict[str, object] = {}
    exec(source, namespace)  # nosec B102
    pairs = cast(list[tuple[str, object]], namespace["pairs"])
    normalized = [(name, _normalize_term(value)) for name, value in pairs]
    expected = [
        ("stdfct:set", {"a", "b"}),
        ("stdfct:tuple", ["a", "b"]),
        ("stdfct:union", {"a", "b", "c"}),
        ("stdfct:size", 2),
        ("stdfct:intersection", {"b"}),
        ("stdfct:isSubset", True),
        ("stdfct:isStrictSubset", True),
        ("stdfct:dict", {"a": "b", "b": "c"}),
        ("stdfct:mergeDicts", {"a": "b", "c": "d"}),
        ("stdfct:dictKeys", {"a", "b"}),
        ("stdfct:dictValues", ["b", "c"]),
        ("stdfct:get", "b"),
        ("stdfct:containsKey", True),
        ("stdfct:containsValue", True),
        ("stdfct:toSet", {"a", "b"}),
        ("stdfct:toTuple", ["a", "b"]),
    ]
    if normalized != expected:
        raise AssertionError(f"Unexpected collection pairs: {pairs}")


def _run_knowledge_base_example(source: str) -> None:
    namespace: dict[str, object] = {}
    exec(source, namespace)  # nosec B102
    fact_atoms = cast(list[Atom], namespace["fact_atoms"])
    rules = cast(list, namespace["rules"])
    if len(fact_atoms) != 1:
        raise AssertionError(f"Unexpected fact atoms: {fact_atoms}")
    atom = fact_atoms[0]
    if atom.predicate.name != "p" or [t.identifier for t in atom.terms] != ["a"]:
        raise AssertionError(f"Unexpected fact atoms: {fact_atoms}")
    if len(rules) != 1:
        raise AssertionError(f"Unexpected rules: {rules}")
    rule = rules[0]
    if len(rule.body.atoms) != 1 or len(rule.head_disjuncts[0].atoms) != 1:
        raise AssertionError(f"Unexpected rule structure: {rule}")
    body = next(iter(rule.body.atoms))
    head = next(iter(rule.head_disjuncts[0].atoms))
    if body.predicate.name != "p" or head.predicate.name != "q":
        raise AssertionError(f"Unexpected rule predicates: {rule}")
    if [t.identifier for t in body.terms] != ["X"]:
        raise AssertionError(f"Unexpected rule body terms: {rule}")
    if [t.identifier for t in head.terms] != ["X"]:
        raise AssertionError(f"Unexpected rule head terms: {rule}")


def _run_prepared_query_example(source: str) -> None:
    namespace: dict[str, object] = {}
    exec(source, namespace)  # nosec B102
    answers = cast(list[dict], namespace["answers"])
    if len(answers) != 1 or not isinstance(answers[0], dict):
        raise AssertionError("Unexpected prepared query answers.")


def _run_fact_base_wrapper_example(source: str) -> None:
    namespace: dict[str, object] = {}
    exec(source, namespace)  # nosec B102
    formula = cast(FOConjunctionFactBaseWrapper, namespace["formula"])
    observed = {
        (atom.predicate.name, tuple(term.identifier for term in atom.terms))
        for atom in formula.atoms
    }
    expected = {("p", ("a",)), ("q", ("b",))}
    if observed != expected:
        raise AssertionError(f"Unexpected wrapper atoms: {formula.atoms}")


def _run_dlgp_reasoning_example(source: str) -> None:
    namespace: dict[str, object] = {}
    exec(source, namespace)  # nosec B102
    rule_strings = cast(list[str], namespace["rule_strings"])
    query_strings = cast(list[str], namespace["query_strings"])
    expected_rules = ["p(X, Y) → (q(X)) ∨ (r(Y))"]
    expected_queries = ["?(X, Y) :- (p(X, Y) ∧ q(Y))"]
    if rule_strings != expected_rules:
        raise AssertionError(f"Unexpected DLGP rules: {rule_strings}")
    if query_strings != expected_queries:
        raise AssertionError(f"Unexpected DLGP queries: {query_strings}")


def _run_delegation_example(source: str) -> None:
    namespace: dict[str, object] = {}
    exec(source, namespace)  # nosec B102
    delegated = _normalize_projected(
        cast(list[tuple[Term, ...]], namespace["delegated"])
    )
    filtered = _normalize_projected(
        cast(list[tuple[Term, ...]], namespace["filtered_results"])
    )
    if set(delegated) != {("a",), ("b",)}:
        raise AssertionError(f"Unexpected delegated results: {delegated}")
    if filtered != [("a",)]:
        raise AssertionError(f"Unexpected filtered results: {filtered}")


def _run_dlgp_example(source: str) -> None:
    parser = DlgpeParser.instance()
    rules = list(parser.parse_rules(source))
    queries = list(parser.parse_queries(source))
    if len(rules) != 1 or len(queries) != 1:
        raise AssertionError("DLGP example did not parse as expected.")
    converted = try_convert_fo_query(queries[0])
    if not isinstance(converted, ConjunctiveQuery):
        raise AssertionError("DLGP example is not a conjunctive query.")


DOC_EXAMPLES: dict[str, list[DocExample]] = {
    "docs/index.md": [
        DocExample("bash", "pip install -e ."),
        DocExample(
            "python",
            textwrap.dedent(
                '''
                from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser
                from prototyping_inference_engine.api.atom.term.variable import Variable
                from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import MutableInMemoryFactBase
                from prototyping_inference_engine.query_evaluation.evaluator.fo_query.fo_query_evaluators import GenericFOQueryEvaluator

                parser = DlgpeParser.instance()
                result = parser.parse("""
                    @facts
                    p(a,b).
                    p(b,c).
                    p(c,d).

                    @queries
                    ?(X,Z) :- p(X,Y), p(Y,Z).
                """)

                facts = result["facts"]
                query = result["queries"][0]

                fact_base = MutableInMemoryFactBase(facts)
                evaluator = GenericFOQueryEvaluator()

                variables = [Variable("X"), Variable("Z")]
                answers = list(evaluator.evaluate(query, fact_base))
                answers = [
                    tuple(sub.apply(var) for var in variables)
                    for sub in answers
                ]
                answers = sorted(
                    answers, key=lambda row: tuple(term.identifier for term in row)
                )
                print(answers)  # (a, c), (b, d)
                '''
            ).strip("\n"),
            runner=_run_index_quick_start_example,
        ),
    ],
    "docs/usage.md": [
        DocExample("bash", "pip install -e ."),
        DocExample(
            "python",
            textwrap.dedent(
                '''
                from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser
                from prototyping_inference_engine.api.atom.term.variable import Variable
                from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import MutableInMemoryFactBase
                from prototyping_inference_engine.query_evaluation.evaluator.fo_query.fo_query_evaluators import GenericFOQueryEvaluator

                parser = DlgpeParser.instance()
                result = parser.parse("""
                    @facts
                    p(a,b).
                    p(b,c).
                    p(c,d).

                    @queries
                    ?(X,Z) :- p(X,Y), p(Y,Z).
                """)

                facts = result["facts"]
                query = result["queries"][0]

                fact_base = MutableInMemoryFactBase(facts)
                evaluator = GenericFOQueryEvaluator()

                variables = [Variable("X"), Variable("Z")]
                answers = list(evaluator.evaluate(query, fact_base))
                projected = [
                    tuple(sub.apply(var) for var in variables)
                    for sub in answers
                ]
                projected = sorted(
                    projected, key=lambda row: tuple(term.identifier for term in row)
                )
                projected_ids = [tuple(term.identifier for term in row) for row in projected]

                print(projected_ids)
                '''
            ).strip("\n"),
            runner=_run_usage_parsing_example,
        ),
        DocExample(
            "python",
            textwrap.dedent(
                '''
                from prototyping_inference_engine.session.reasoning_session import ReasoningSession
                from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser

                with ReasoningSession.create() as session:
                    parser = DlgpeParser.instance()
                    result = parser.parse("""
                        @facts
                        p(a,b).
                        p(b,c).

                        @queries
                        ?(X) :- p(a,X).
                    """)

                    fb = session.create_fact_base(result["facts"])
                    answers = list(session.evaluate_query(result["queries"][0], fb))
                    normalized = [tuple(term.identifier for term in answer) for answer in answers]
                    print(normalized)
                '''
            ).strip("\n"),
            runner=_run_usage_session_example,
        ),
        DocExample(
            "python",
            textwrap.dedent(
                """
                from prototyping_inference_engine.api.iri import (
                    IRIManager,
                    StandardComposableNormalizer,
                    RFCNormalizationScheme,
                )

                manager = IRIManager(
                    normalizer=StandardComposableNormalizer(RFCNormalizationScheme.STRING),
                    iri_base="http://example.org/base/",
                )
                manager.set_prefix("ex", "http://example.org/ns/")

                iri = manager.create_iri_with_prefix("ex", "resource")
                value = iri.recompose()
                print(value)
                """
            ).strip("\n"),
            runner=_run_iri_example,
        ),
        DocExample(
            "python",
            textwrap.dedent(
                '''
                from prototyping_inference_engine.io.writers.dlgpe_writer import DlgpeWriter
                from prototyping_inference_engine.session.reasoning_session import ReasoningSession

                with ReasoningSession.create() as session:
                    result = session.parse("""
                        @base <http://example.org/base/>.
                        @prefix ex: <http://example.org/ns/>.
                        <rel>(ex:obj).
                    """)

                    writer = DlgpeWriter()
                    output = writer.write(result)
                    print(output)
                '''
            ).strip("\n"),
            runner=_run_export_example,
        ),
        DocExample(
            "python",
            textwrap.dedent(
                """
                import tempfile
                from pathlib import Path

                from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser

                with tempfile.TemporaryDirectory() as tmpdir:
                    path = Path(tmpdir) / "example.dlgp"
                    path.write_text(
                        \"\"\"
                        @facts
                        p(a).
                        q(b).
                        \"\"\",
                        encoding="utf-8",
                    )

                    result = DlgpeParser.instance().parse_file(path)
                    atoms = sorted(result[\"facts\"], key=str)
                    for atom in atoms:
                        print(atom)
                """
            ).strip("\n"),
            runner=_run_dlgpe_file_example,
        ),
        DocExample(
            "python",
            textwrap.dedent(
                """
                import tempfile
                from pathlib import Path

                from prototyping_inference_engine.io.parsers.csv import CSVParser
                from prototyping_inference_engine.session.reasoning_session import ReasoningSession

                with tempfile.TemporaryDirectory() as tmpdir:
                    path = Path(tmpdir) / "people.csv"
                    path.write_text("alice,bob\\ncarol,dave\\n", encoding="utf-8")

                    with ReasoningSession.create() as session:
                        parser = CSVParser(path, session.term_factories)
                        atoms = sorted(list(parser.parse_atoms()), key=str)
                        for atom in atoms:
                            print(atom)
                """
            ).strip("\n"),
            runner=_run_csv_parser_example,
        ),
        DocExample(
            "python",
            textwrap.dedent(
                """
                import tempfile
                from pathlib import Path

                from prototyping_inference_engine.io.parsers.csv import RLSCSVsParser
                from prototyping_inference_engine.session.reasoning_session import ReasoningSession

                with tempfile.TemporaryDirectory() as tmpdir:
                    base = Path(tmpdir)
                    (base / "csv1.csv").write_text("a,b\\nc,d\\n", encoding="utf-8")
                    (base / "csv2.csv").write_text("e,f\\n", encoding="utf-8")
                    rls_path = base / "data.rls"
                    rls_path.write_text(
                        '@source p[2]: load-csv("csv1.csv") .\\n'
                        '@source q[2]: load-csv("csv2.csv") .\\n',
                        encoding="utf-8",
                    )

                    with ReasoningSession.create() as session:
                        parser = RLSCSVsParser(rls_path, session.term_factories)
                        atoms = sorted(list(parser.parse_atoms()), key=str)
                        for atom in atoms:
                            print(atom)
                """
            ).strip("\n"),
            runner=_run_rls_csv_example,
        ),
        DocExample(
            "python",
            textwrap.dedent(
                """
                import tempfile
                from pathlib import Path

                from prototyping_inference_engine.io.parsers.rdf import RDFParser
                from prototyping_inference_engine.io.parsers.rdf.rdf_parser import RDFParserConfig
                from prototyping_inference_engine.rdf.translator import RDFTranslationMode
                from prototyping_inference_engine.session.reasoning_session import ReasoningSession

                with tempfile.TemporaryDirectory() as tmpdir:
                    path = Path(tmpdir) / "data.ttl"
                    path.write_text(
                        \"\"\"
                        @prefix ex: <http://example.org/> .
                        @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
                        ex:a rdf:type ex:Person .
                        ex:a ex:knows "bob" .
                        \"\"\",
                        encoding="utf-8",
                    )

                    with ReasoningSession.create() as session:
                        parser = RDFParser(
                            path,
                            session.term_factories,
                            RDFParserConfig(translation_mode=RDFTranslationMode.NATURAL_FULL),
                        )
                        atoms = sorted(list(parser.parse_atoms()), key=str)
                        for atom in atoms:
                            print(atom)
                """
            ).strip("\n"),
            runner=_run_rdf_parser_example,
        ),
        DocExample(
            "python",
            textwrap.dedent(
                """
                import tempfile
                from pathlib import Path

                from prototyping_inference_engine.rdf.translator import RDFTranslationMode
                from prototyping_inference_engine.session.reasoning_session import ReasoningSession

                with tempfile.TemporaryDirectory() as tmpdir:
                    base = Path(tmpdir)
                    (base / "facts.csv").write_text("a,b\\n", encoding="utf-8")
                    (base / "data.ttl").write_text(
                        \"\"\"
                        @prefix ex: <http://example.org/> .
                        ex:a ex:knows ex:b .
                        \"\"\",
                        encoding="utf-8",
                    )
                    (base / "main.dlgpe").write_text(
                        \"\"\"
                        @import <facts.csv>.
                        @import <data.ttl>.

                        @facts
                        p(a).
                        \"\"\",
                        encoding="utf-8",
                    )

                    with ReasoningSession.create(
                        rdf_translation_mode=RDFTranslationMode.RAW
                    ) as session:
                        result = session.parse_file(base / "main.dlgpe")
                        atoms = sorted(result.facts, key=str)
                        for atom in atoms:
                            print(atom)
                """
            ).strip("\n"),
            runner=_run_imports_example,
        ),
        DocExample(
            "prolog",
            textwrap.dedent(
                """
                @facts
                p(3).

                @queries
                ?(X) :- p(X + 1).
                ?() :- (2 * 3) + 1 > 6.
                """
            ).strip("\n"),
            runner=_run_arithmetic_expression_dlgpe_example,
        ),
        DocExample(
            "python",
            textwrap.dedent(
                """
                from prototyping_inference_engine.session.reasoning_session import ReasoningSession



                dlgp = \"\"\"
                @facts
                p(3).

                @queries
                ?(X) :- p(X + 1).
                ?() :- (2 * 3) + 1 > 6.
                \"\"\"

                with ReasoningSession.create() as session:
                    result = session.parse(dlgp)
                    fact_base = session.create_fact_base(result.facts)
                    answers = [
                        list(session.evaluate_query_with_sources(query, fact_base, result.sources))
                        for query in result.queries
                    ]
                    normalized = [
                        [tuple(term.identifier for term in row) for row in rows]
                        for rows in answers
                    ]
                    print(normalized)
                """
            ).strip("\n"),
            runner=_run_arithmetic_expression_python_example,
        ),
        DocExample(
            "prolog",
            textwrap.dedent(
                """
                @computed ig: <stdfct>.

                @queries
                ?(X) :- ig:sum(1, X, 3).
                """
            ).strip("\n"),
            runner=_run_computed_sum_example,
        ),
        DocExample(
            "python",
            textwrap.dedent(
                """
                from prototyping_inference_engine.session.reasoning_session import ReasoningSession



                dlgp = \"\"\"
                @computed ig: <stdfct>.

                @queries
                ?(X) :- ig:sum(1, X, 3).
                \"\"\"

                with ReasoningSession.create() as session:
                    result = session.parse(dlgp)
                    fact_base = session.create_fact_base(result.facts)
                    query = next(iter(result.queries))
                    answers = list(
                        session.evaluate_query_with_sources(query, fact_base, result.sources)
                    )
                    projected = [
                        tuple(answer) for answer in answers
                    ]
                    print(projected)
                """
            ).strip("\n"),
            runner=_run_computed_sum_python_example,
        ),
        DocExample(
            "python",
            textwrap.dedent(
                """
                def increment(value: int) -> int:
                    return value + 1
                """
            ).strip("\n"),
        ),
        DocExample(
            "json",
            textwrap.dedent(
                """
                {
                  "schema_version": 1,
                  "default": {
                    "functions": {
                      "path": ".",
                      "module": "computed_utils"
                    }
                  }
                }
                """
            ).strip("\n"),
        ),
        DocExample(
            "prolog",
            textwrap.dedent(
                """
                @computed ex: <docs/examples/computed/functions.json>.

                @facts
                p(2).

                @queries
                ?() :- p(ex:increment(1)).
                """
            ).strip("\n"),
            runner=_run_computed_json_example,
        ),
        DocExample(
            "python",
            textwrap.dedent(
                """
                from prototyping_inference_engine.session.reasoning_session import ReasoningSession



                dlgp = \"\"\"
                @computed ex: <docs/examples/computed/functions.json>.

                @facts
                p(2).

                @queries
                ?() :- p(ex:increment(1)).
                \"\"\"

                with ReasoningSession.create() as session:
                    result = session.parse(dlgp)
                    fact_base = session.create_fact_base(result.facts)
                    query = next(iter(result.queries))
                    answers = list(
                        session.evaluate_query_with_sources(query, fact_base, result.sources)
                    )
                    projected = [
                        tuple(answer) for answer in answers
                    ]
                    print(projected)
                """
            ).strip("\n"),
            runner=_run_computed_json_python_example,
        ),
        DocExample(
            "prolog",
            textwrap.dedent(
                """
                @computed ig: <stdfct>.

                @facts
                p(3).

                @queries
                ?() :- p(ig:sum(1, 2)).
                """
            ).strip("\n"),
            runner=_run_function_term_example,
        ),
        DocExample(
            "python",
            textwrap.dedent(
                """
                from prototyping_inference_engine.session.reasoning_session import ReasoningSession



                dlgp = \"\"\"
                @computed ig: <stdfct>.

                @facts
                p(3).

                @queries
                ?() :- p(ig:sum(1, 2)).
                \"\"\"

                with ReasoningSession.create() as session:
                    result = session.parse(dlgp)
                    fact_base = session.create_fact_base(result.facts)
                    query = next(iter(result.queries))
                    answers = list(
                        session.evaluate_query_with_sources(query, fact_base, result.sources)
                    )
                    projected = [
                        tuple(answer) for answer in answers
                    ]
                    print(projected)
                """
            ).strip("\n"),
            runner=_run_function_term_python_example,
        ),
        DocExample(
            "prolog",
            textwrap.dedent(
                """
                @computed ig: <stdfct>.

                @facts
                p(4).

                @queries
                ?() :- not p(ig:sum(1, 2)).
                """
            ).strip("\n"),
            runner=_run_negated_function_term_example,
        ),
        DocExample(
            "python",
            textwrap.dedent(
                """
                from prototyping_inference_engine.session.reasoning_session import ReasoningSession



                dlgp = \"\"\"
                @computed ig: <stdfct>.

                @facts
                p(4).

                @queries
                ?() :- not p(ig:sum(1, 2)).
                \"\"\"

                with ReasoningSession.create() as session:
                    result = session.parse(dlgp)
                    fact_base = session.create_fact_base(result.facts)
                    query = next(iter(result.queries))
                    answers = list(
                        session.evaluate_query_with_sources(query, fact_base, result.sources)
                    )
                    projected = [
                        tuple(answer) for answer in answers
                    ]
                    print(projected)
                """
            ).strip("\n"),
            runner=_run_negated_function_term_python_example,
        ),
        DocExample(
            "prolog",
            textwrap.dedent(
                """
                @computed ig: <stdfct>.

                @queries
                ?(S) :- ig:sum(1, 2, S).
                ?(Mi) :- ig:min(3, 1, Mi).
                ?(Ma) :- ig:max(3, 1, Ma).
                ?(D) :- ig:minus(10, 3, D).
                ?(P) :- ig:product(2, 3, P).
                ?(Q) :- ig:divide(8.0, 2.0, Q).
                ?(Pow) :- ig:power(2, 3, Pow).
                ?(A) :- ig:average(2.0, 4.0, A).
                ?(Md) :- ig:median(2, 9, 4, Md).
                ?(WA) :- ig:weightedAverage(ig:tuple(10, 1), ig:tuple(20, 3), WA).
                ?(WM) :- ig:weightedMedian(ig:tuple(10, 1), ig:tuple(20, 3), WM).
                """
            ).strip("\n"),
            runner=_run_arithmetic_functions_example,
        ),
        DocExample(
            "python",
            textwrap.dedent(
                """
                from prototyping_inference_engine.session.reasoning_session import ReasoningSession



                dlgp = \"\"\"
                @computed ig: <stdfct>.

                @queries
                ?(S) :- ig:sum(1, 2, S).
                ?(Mi) :- ig:min(3, 1, Mi).
                ?(Ma) :- ig:max(3, 1, Ma).
                ?(D) :- ig:minus(10, 3, D).
                ?(P) :- ig:product(2, 3, P).
                ?(Q) :- ig:divide(8.0, 2.0, Q).
                ?(Pow) :- ig:power(2, 3, Pow).
                ?(A) :- ig:average(2.0, 4.0, A).
                ?(Md) :- ig:median(2, 9, 4, Md).
                ?(WA) :- ig:weightedAverage(ig:tuple(10, 1), ig:tuple(20, 3), WA).
                ?(WM) :- ig:weightedMedian(ig:tuple(10, 1), ig:tuple(20, 3), WM).
                \"\"\"

                with ReasoningSession.create() as session:
                    result = session.parse(dlgp)
                    fact_base = session.create_fact_base(result.facts)
                    pairs = []
                    for query in result.queries:
                        atom = next(iter(query.atoms))
                        answers = list(
                            session.evaluate_query_with_sources(query, fact_base, result.sources)
                        )
                        value = answers[0][0]
                        pairs.append((atom.predicate.name, value))
                    print(pairs)
                """
            ).strip("\n"),
            runner=_run_arithmetic_functions_python_example,
        ),
        DocExample(
            "prolog",
            textwrap.dedent(
                """
                @computed ig: <stdfct>.

                @queries
                ?(E) :- ig:isEven(4, E).
                ?(O) :- ig:isOdd(3, O).
                ?(Pr) :- ig:isPrime(7, Pr).
                ?(Gt) :- ig:isGreaterThan(5, 2, Gt).
                ?(Ge) :- ig:isGreaterOrEqualsTo(2, 2, Ge).
                ?(Lt) :- ig:isSmallerThan(1, 3, Lt).
                ?(Le) :- ig:isSmallerOrEqualsTo(2, 2, Le).
                ?(Lg) :- ig:isLexicographicallyGreaterThan("b", "a", Lg).
                ?(Lge) :- ig:isLexicographicallyGreaterOrEqualsTo("a", "a", Lge).
                ?(Ls) :- ig:isLexicographicallySmallerThan("a", "b", Ls).
                ?(Lse) :- ig:isLexicographicallySmallerOrEqualsTo("a", "a", Lse).
                ?(Eq) :- ig:equals(5, 5, 5, Eq).
                ?(C) :- ig:contains(ig:tuple(a, b), a, C).
                ?(Em) :- ig:isEmpty(ig:set(), Em).
                ?(Bl) :- ig:isBlank("   ", Bl).
                ?(Nu) :- ig:isNumeric("12.5", Nu).
                """
            ).strip("\n"),
            runner=_run_comparison_functions_example,
        ),
        DocExample(
            "python",
            textwrap.dedent(
                """
                from prototyping_inference_engine.session.reasoning_session import ReasoningSession



                dlgp = \"\"\"
                @computed ig: <stdfct>.

                @queries
                ?(E) :- ig:isEven(4, E).
                ?(O) :- ig:isOdd(3, O).
                ?(Pr) :- ig:isPrime(7, Pr).
                ?(Gt) :- ig:isGreaterThan(5, 2, Gt).
                ?(Ge) :- ig:isGreaterOrEqualsTo(2, 2, Ge).
                ?(Lt) :- ig:isSmallerThan(1, 3, Lt).
                ?(Le) :- ig:isSmallerOrEqualsTo(2, 2, Le).
                ?(Lg) :- ig:isLexicographicallyGreaterThan("b", "a", Lg).
                ?(Lge) :- ig:isLexicographicallyGreaterOrEqualsTo("a", "a", Lge).
                ?(Ls) :- ig:isLexicographicallySmallerThan("a", "b", Ls).
                ?(Lse) :- ig:isLexicographicallySmallerOrEqualsTo("a", "a", Lse).
                ?(Eq) :- ig:equals(5, 5, 5, Eq).
                ?(C) :- ig:contains(ig:tuple(a, b), a, C).
                ?(Em) :- ig:isEmpty(ig:set(), Em).
                ?(Bl) :- ig:isBlank("   ", Bl).
                ?(Nu) :- ig:isNumeric("12.5", Nu).
                \"\"\"

                with ReasoningSession.create() as session:
                    result = session.parse(dlgp)
                    fact_base = session.create_fact_base(result.facts)
                    pairs = []
                    for query in result.queries:
                        atom = next(iter(query.atoms))
                        answers = list(
                            session.evaluate_query_with_sources(query, fact_base, result.sources)
                        )
                        value = answers[0][0]
                        pairs.append((atom.predicate.name, value))
                    print(pairs)
                """
            ).strip("\n"),
            runner=_run_comparison_functions_python_example,
        ),
        DocExample(
            "prolog",
            textwrap.dedent(
                """
                @computed ig: <stdfct>.

                @queries
                ?(C) :- ig:concat("foo", "bar", C).
                ?(Lo) :- ig:toLowerCase("AbC", Lo).
                ?(Up) :- ig:toUpperCase("AbC", Up).
                ?(Re) :- ig:replace("abc", "b", "B", Re).
                ?(Le) :- ig:length("abcd", Le).
                ?(Ts) :- ig:toString(1, Ts).
                ?(Td) :- ig:toStringWithDatatype(1, Td).
                ?(Ti) :- ig:toInt("12", Ti).
                ?(Tf) :- ig:toFloat("1.5", Tf).
                ?(Tb) :- ig:toBoolean("true", Tb).
                """
            ).strip("\n"),
            runner=_run_string_functions_example,
        ),
        DocExample(
            "python",
            textwrap.dedent(
                """
                from prototyping_inference_engine.session.reasoning_session import ReasoningSession



                dlgp = \"\"\"
                @computed ig: <stdfct>.

                @queries
                ?(C) :- ig:concat("foo", "bar", C).
                ?(Lo) :- ig:toLowerCase("AbC", Lo).
                ?(Up) :- ig:toUpperCase("AbC", Up).
                ?(Re) :- ig:replace("abc", "b", "B", Re).
                ?(Le) :- ig:length("abcd", Le).
                ?(Ts) :- ig:toString(1, Ts).
                ?(Td) :- ig:toStringWithDatatype(1, Td).
                ?(Ti) :- ig:toInt("12", Ti).
                ?(Tf) :- ig:toFloat("1.5", Tf).
                ?(Tb) :- ig:toBoolean("true", Tb).
                \"\"\"

                with ReasoningSession.create() as session:
                    result = session.parse(dlgp)
                    fact_base = session.create_fact_base(result.facts)
                    pairs = []
                    for query in result.queries:
                        atom = next(iter(query.atoms))
                        answers = list(
                            session.evaluate_query_with_sources(query, fact_base, result.sources)
                        )
                        value = answers[0][0]
                        pairs.append((atom.predicate.name, value))
                    print(pairs)
                """
            ).strip("\n"),
            runner=_run_string_functions_python_example,
        ),
        DocExample(
            "prolog",
            textwrap.dedent(
                """
                @computed ig: <stdfct>.

                @queries
                ?(S) :- ig:set(a, b, S).
                ?(T) :- ig:tuple(a, b, T).
                ?(U) :- ig:union(ig:set(a, b), ig:set(b, c), U).
                ?(Sz) :- ig:size(ig:set(a, b), Sz).
                ?(I) :- ig:intersection(ig:set(a, b), ig:set(b, c), I).
                ?(Su) :- ig:isSubset(ig:set(a), ig:set(a, b), Su).
                ?(Ss) :- ig:isStrictSubset(ig:set(a), ig:set(a, b), Ss).
                ?(D) :- ig:dict(ig:tuple(a, b), ig:tuple(b, c), D).
                ?(M) :- ig:mergeDicts(ig:dict(ig:tuple(a, b)), ig:dict(ig:tuple(c, d)), M).
                ?(K) :- ig:dictKeys(ig:dict(ig:tuple(a, b), ig:tuple(b, c)), K).
                ?(V) :- ig:dictValues(ig:dict(ig:tuple(a, b), ig:tuple(b, c)), V).
                ?(G) :- ig:get(ig:tuple(a, b, c), 1, G).
                ?(Ck) :- ig:containsKey(ig:dict(ig:tuple(a, b)), a, Ck).
                ?(Cv) :- ig:containsValue(ig:dict(ig:tuple(a, b)), b, Cv).
                ?(Ts) :- ig:toSet(ig:tuple(a, b), Ts).
                ?(Tt) :- ig:toTuple(ig:tuple(a, b), Tt).
                """
            ).strip("\n"),
            runner=_run_collection_functions_example,
        ),
        DocExample(
            "python",
            textwrap.dedent(
                """
                from prototyping_inference_engine.session.reasoning_session import ReasoningSession



                dlgp = \"\"\"
                @computed ig: <stdfct>.

                @queries
                ?(S) :- ig:set(a, b, S).
                ?(T) :- ig:tuple(a, b, T).
                ?(U) :- ig:union(ig:set(a, b), ig:set(b, c), U).
                ?(Sz) :- ig:size(ig:set(a, b), Sz).
                ?(I) :- ig:intersection(ig:set(a, b), ig:set(b, c), I).
                ?(Su) :- ig:isSubset(ig:set(a), ig:set(a, b), Su).
                ?(Ss) :- ig:isStrictSubset(ig:set(a), ig:set(a, b), Ss).
                ?(D) :- ig:dict(ig:tuple(a, b), ig:tuple(b, c), D).
                ?(M) :- ig:mergeDicts(ig:dict(ig:tuple(a, b)), ig:dict(ig:tuple(c, d)), M).
                ?(K) :- ig:dictKeys(ig:dict(ig:tuple(a, b), ig:tuple(b, c)), K).
                ?(V) :- ig:dictValues(ig:dict(ig:tuple(a, b), ig:tuple(b, c)), V).
                ?(G) :- ig:get(ig:tuple(a, b, c), 1, G).
                ?(Ck) :- ig:containsKey(ig:dict(ig:tuple(a, b)), a, Ck).
                ?(Cv) :- ig:containsValue(ig:dict(ig:tuple(a, b)), b, Cv).
                ?(Ts) :- ig:toSet(ig:tuple(a, b), Ts).
                ?(Tt) :- ig:toTuple(ig:tuple(a, b), Tt).
                \"\"\"

                with ReasoningSession.create() as session:
                    result = session.parse(dlgp)
                    fact_base = session.create_fact_base(result.facts)
                    pairs = []
                    for query in result.queries:
                        atom = next(iter(query.atoms))
                        answers = list(
                            session.evaluate_query_with_sources(query, fact_base, result.sources)
                        )
                        value = answers[0][0]
                        pairs.append((atom.predicate.name, value))
                    print(pairs)
                """
            ).strip("\n"),
            runner=_run_collection_functions_python_example,
        ),
        DocExample(
            "python",
            textwrap.dedent(
                '''
                from prototyping_inference_engine.session.reasoning_session import ReasoningSession

                with ReasoningSession.create() as session:
                    result = session.parse("""
                        @facts
                        p(a).

                        @rules
                        q(X) :- p(X).
                    """)

                    fb = session.create_fact_base(result.facts)
                    rb = session.create_rule_base(set(result.rules))
                    kb = session.create_knowledge_base(fb, rb)

                    fact_atoms = sorted(kb.fact_base, key=str)
                    rules = sorted(kb.rule_base.rules, key=str)
                    for atom in fact_atoms:
                        print(atom)
                    for rule in rules:
                        print(rule)
                '''
            ).strip("\n"),
            runner=_run_knowledge_base_example,
        ),
        DocExample(
            "python",
            textwrap.dedent(
                """
                from prototyping_inference_engine.query_evaluation.evaluator.fo_query.fo_query_evaluator_registry import (
                    FOQueryEvaluatorRegistry,
                )
                from prototyping_inference_engine.session.reasoning_session import ReasoningSession


                with ReasoningSession.create() as session:
                    result = session.parse('''
                        @facts
                        p(a).
                    ''')
                    fact_base = session.create_fact_base(result.facts)

                    query = session.fo_query().builder().atom("p", "a").build()
                    evaluator = FOQueryEvaluatorRegistry.instance().get_evaluator(query)
                    prepared = evaluator.prepare(query, fact_base)
                    answers = list(prepared.execute_empty())
                    print(len(answers))
                """
            ).strip("\n"),
            runner=_run_prepared_query_example,
        ),
        DocExample(
            "python",
            textwrap.dedent(
                """
                from prototyping_inference_engine.api.formula.fo_conjunction_fact_base_wrapper import (
                    FOConjunctionFactBaseWrapper,
                )
                from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import MutableInMemoryFactBase
                from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser

                facts = DlgpeParser.instance().parse_atoms("p(a), q(b).")
                fact_base = MutableInMemoryFactBase(facts)
                wrapper = FOConjunctionFactBaseWrapper(fact_base)
                formula = wrapper
                print(formula)
                """
            ).strip("\n"),
            runner=_run_fact_base_wrapper_example,
        ),
        DocExample(
            "python",
            textwrap.dedent(
                """
                from prototyping_inference_engine.api.atom.atom import Atom
                from prototyping_inference_engine.api.atom.predicate import Predicate
                from prototyping_inference_engine.api.atom.term.constant import Constant
                from prototyping_inference_engine.api.atom.term.variable import Variable
                from prototyping_inference_engine.api.data.basic_query import BasicQuery
                from prototyping_inference_engine.api.data.datalog_delegable import DatalogDelegable
                from prototyping_inference_engine.api.data.queryable_data_del_atoms_wrapper import (
                    QueryableDataDelAtomsWrapper,
                )
                from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import MutableInMemoryFactBase


                class DelegableFactBase(MutableInMemoryFactBase, DatalogDelegable):
                    def delegate_rules(self, rules):
                        return False

                    def delegate_query(self, query, count_answers_only=False):
                        return iter(self.evaluate(query))


                predicate = Predicate("p", 1)
                removed = Atom(predicate, Constant("b"))

                fact_base = DelegableFactBase(
                    [Atom(predicate, Constant("a")), removed]
                )
                query = BasicQuery(predicate, {}, {0: Variable("X")})

                delegated: list[tuple[Constant]] = []
                if isinstance(fact_base, DatalogDelegable):
                    delegated = list(fact_base.delegate_query(query))

                filtered = QueryableDataDelAtomsWrapper(fact_base, [removed])
                filtered_results = list(filtered.evaluate(query))

                delegated_ids = sorted([tuple(term.identifier for term in row) for row in delegated])
                filtered_ids = [tuple(term.identifier for term in row) for row in filtered_results]

                print(delegated_ids)
                print(filtered_ids)
                """
            ).strip("\n"),
            runner=_run_delegation_example,
        ),
        DocExample(
            "prolog",
            textwrap.dedent(
                """
                q(X) | r(Y) :- p(X,Y).
                ?(X,Y) :- p(X,Y), q(Y).
                """
            ).strip("\n"),
            runner=_run_dlgp_example,
        ),
        DocExample(
            "python",
            textwrap.dedent(
                """
                from prototyping_inference_engine.session.reasoning_session import ReasoningSession

                with ReasoningSession.create() as session:
                    result = session.parse(\"\"\"
                        q(X) | r(Y) :- p(X,Y).
                        ?(X,Y) :- p(X,Y), q(Y).
                    \"\"\")
                    rules = list(result.rules)
                    rule_strings = [str(rule) for rule in rules]
                    queries = list(result.queries)
                    query_strings = [str(query) for query in queries]
                    for rule in rules:
                        print(rule)
                    for query in queries:
                        print(query)
                """
            ).strip("\n"),
            runner=_run_dlgp_reasoning_example,
        ),
        DocExample("bash", "disjunctive-rewriter [file.dlgp] [-l LIMIT] [-v] [-m]"),
    ],
    "docs/architecture.md": [
        DocExample(
            "",
            textwrap.dedent(
                """
                QueryEvaluator[Q]
                └── FOQueryEvaluator
                    ├── AtomicFOQueryEvaluator
                    ├── ConjunctiveFOQueryEvaluator
                    ├── DisjunctiveFOQueryEvaluator
                    ├── NegationFOQueryEvaluator
                    ├── UniversalFOQueryEvaluator
                    ├── ExistentialFOQueryEvaluator
                    └── GenericFOQueryEvaluator
                """
            ).strip("\n"),
        ),
    ],
    "docs/contributing.md": [
        DocExample("bash", "pip install -r requirements-dev.txt"),
    ],
}


class TestDocumentationExamples(unittest.TestCase):
    def test_all_doc_examples_are_listed(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        for path, expected in DOC_EXAMPLES.items():
            doc_path = repo_root / path
            text = doc_path.read_text(encoding="utf-8")
            blocks = _extract_code_blocks(text)
            expected_blocks = [(ex.language, ex.content) for ex in expected]
            self.assertEqual(blocks, expected_blocks, msg=f"Mismatch in {path}")

    def test_doc_examples_execute(self) -> None:
        for examples in DOC_EXAMPLES.values():
            for example in examples:
                if example.runner is not None:
                    example.runner(example.content)

    def test_doc_examples_have_explanations(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        for path in DOC_EXAMPLES:
            doc_path = repo_root / path
            text = doc_path.read_text(encoding="utf-8")
            blocks = _extract_code_blocks_with_context(text)
            for language, content, before, after in blocks:
                if not before and not after:
                    raise AssertionError(
                        f"Code block in {path} lacks explanatory text. "
                        f"Language='{language}' Content='{content[:30]}...'"
                    )


if __name__ == "__main__":
    unittest.main()
