"""Ensure documentation examples are accurate and covered by tests."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import textwrap
import unittest
from typing import Callable, cast

from prototyping_inference_engine.api.atom.term.literal import Literal
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.io import Dlgp2Parser
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
        return str(term)
    return term


def _normalize_value(value: object) -> object:
    if isinstance(value, Literal):
        return _normalize_value(value.value)
    if isinstance(value, Term):
        return _normalize_term(value)
    if isinstance(value, dict):
        return {str(_normalize_term(k)): _normalize_term(v) for k, v in value.items()}
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


def _run_usage_parsing_example(source: str) -> None:
    namespace: dict[str, object] = {}
    exec(source, namespace)  # nosec B102 - trusted doc example execution in tests
    projected = cast(list[tuple[Term, ...]], namespace["projected"])
    self_check = _normalize_projected(projected)
    expected = {("a", "c"), ("b", "d")}
    if set(self_check) != expected:
        raise AssertionError(f"Unexpected projected answers: {self_check}")


def _run_usage_session_example(source: str) -> None:
    namespace: dict[str, object] = {}
    exec(source, namespace)  # nosec B102 - trusted doc example execution in tests
    answers = cast(list[tuple[Term, ...]], namespace["answers"])
    normalized = _normalize_projected(answers)
    if normalized != [("b",)]:
        raise AssertionError(f"Unexpected session answers: {normalized}")


def _run_iri_example(source: str) -> None:
    namespace: dict[str, object] = {}
    exec(source, namespace)  # nosec B102 - trusted doc example execution in tests
    value = namespace["value"]
    if value != "http://example.org/ns/resource":
        raise AssertionError(f"Unexpected IRI value: {value}")


def _run_export_example(source: str) -> None:
    namespace: dict[str, object] = {}
    exec(source, namespace)  # nosec B102 - trusted doc example execution in tests
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


def _run_index_quick_start_example(source: str) -> None:
    namespace: dict[str, object] = {}
    exec(source, namespace)  # nosec B102 - trusted doc example execution in tests
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


def _run_function_term_example(source: str) -> None:
    _, answers = _evaluate_dlgpe_queries(source)[0]
    if answers != [tuple()]:
        raise AssertionError(f"Unexpected functional-term answers: {answers}")


def _run_negated_function_term_example(source: str) -> None:
    _, answers = _evaluate_dlgpe_queries(source)[0]
    if answers != [tuple()]:
        raise AssertionError(f"Unexpected negated functional-term answers: {answers}")


def _run_collection_functions_example(source: str) -> None:
    results = _evaluate_dlgpe_queries(source)
    if len(results) != 5:
        raise AssertionError("Expected 5 queries in collection example.")

    observed: dict[str, object] = {}
    for query, query_answers in results:
        if len(query_answers) != 1:
            raise AssertionError("Expected exactly one answer per query.")
        atom = next(iter(query.atoms))
        observed[str(atom.predicate)] = _normalize_term(query_answers[0][0])

    normalized_observed = {
        key.replace("ig:", "stdfct:", 1): value for key, value in observed.items()
    }
    expected = {
        "stdfct:tuple": ["a", "b", "c"],
        "stdfct:dict": {"a": "b", "b": "c"},
        "stdfct:dictKeys": {"a", "b"},
        "stdfct:get": "b",
        "stdfct:union": {"a", "b", "c"},
    }

    if normalized_observed != expected:
        raise AssertionError(
            f"Unexpected collection result: {observed} (expected {expected})"
        )


def _run_dlgp_example(source: str) -> None:
    parser = Dlgp2Parser.instance()
    rules = list(parser.parse_rules(source))
    queries = list(parser.parse_conjunctive_queries(source))
    if len(rules) != 1 or len(queries) != 1:
        raise AssertionError("DLGP example did not parse as expected.")


DOC_EXAMPLES: dict[str, list[DocExample]] = {
    "docs/index.md": [
        DocExample("bash", "pip install -e ."),
        DocExample(
            "python",
            textwrap.dedent(
                '''
                from prototyping_inference_engine.io import DlgpeParser
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
                answers = sorted(answers, key=lambda row: tuple(str(term) for term in row))
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
                from prototyping_inference_engine.io import DlgpeParser
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
                projected = sorted(projected, key=lambda row: tuple(str(term) for term in row))

                print(answers)
                print(projected)
                '''
            ).strip("\n"),
            runner=_run_usage_parsing_example,
        ),
        DocExample(
            "python",
            textwrap.dedent(
                '''
                from prototyping_inference_engine.session.reasoning_session import ReasoningSession
                from prototyping_inference_engine.io import DlgpeParser

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
                    print(answers)
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
                print(value)  # http://example.org/ns/resource
                """
            ).strip("\n"),
            runner=_run_iri_example,
        ),
        DocExample(
            "python",
            textwrap.dedent(
                '''
                from prototyping_inference_engine.io import DlgpeWriter
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
            "prolog",
            textwrap.dedent(
                """
                @computed ig: <stdfct>.

                @queries
                ?(T) :- ig:tuple(a, b, c, T).
                ?(D) :- ig:dict(ig:tuple(a, b), ig:tuple(b, c), D).
                ?(K) :- ig:dictKeys(ig:dict(ig:tuple(a, b), ig:tuple(b, c)), K).
                ?(V) :- ig:get(ig:tuple(a, b, c), 1, V).
                ?(U) :- ig:union(ig:set(a, b), ig:set(b, c), U).
                """
            ).strip("\n"),
            runner=_run_collection_functions_example,
        ),
        DocExample(
            "prolog",
            textwrap.dedent(
                """
                q(X); r(Y) :- p(X,Y).
                ?(X) :- p(X,Y), q(Y).
                """
            ).strip("\n"),
            runner=_run_dlgp_example,
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
