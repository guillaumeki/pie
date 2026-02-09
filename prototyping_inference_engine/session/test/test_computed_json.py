from pathlib import Path
import unittest
from typing import cast

from prototyping_inference_engine.session.reasoning_session import ReasoningSession
from prototyping_inference_engine.api.query.fo_query import FOQuery


def _computed_config_path() -> Path:
    return (
        Path(__file__).resolve().parents[2]
        / "io"
        / "parsers"
        / "dlgpe"
        / "test"
        / "resources"
        / "functions.json"
    )


class TestComputedJson(unittest.TestCase):
    def test_computed_json_evaluation(self) -> None:
        config_path = _computed_config_path()
        text = (
            f"@computed ex: <{config_path}>.\n"
            "\n"
            "@facts\n"
            "p(2).\n"
            "\n"
            "@queries\n"
            "?() :- p(ex:increment(1)).\n"
        )

        with ReasoningSession.create() as session:
            result = session.parse(text)
            fact_base = session.create_fact_base(result.facts)
            query = cast(FOQuery, next(iter(result.queries)))
            answers = list(
                session.evaluate_query_with_sources(query, fact_base, result.sources)
            )

        self.assertEqual(len(answers), 1)

    def test_missing_function_raises(self) -> None:
        config_path = _computed_config_path()
        text = (
            f"@computed ex: <{config_path}>.\n"
            "\n"
            "@facts\n"
            "p(2).\n"
            "\n"
            "@queries\n"
            "?() :- p(ex:missing(1)).\n"
        )

        with ReasoningSession.create() as session:
            with self.assertRaises(ValueError):
                session.parse(text)

    def test_predicate_usage_rejected(self) -> None:
        config_path = _computed_config_path()
        text = (
            f"@computed ex: <{config_path}>.\n\n@queries\n?(X) :- ex:increment(1, X).\n"
        )

        with ReasoningSession.create() as session:
            with self.assertRaises(ValueError):
                session.parse(text)


if __name__ == "__main__":
    unittest.main()
