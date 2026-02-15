"""
DLGPE arithmetic expressions in query evaluation.
"""

import unittest
from typing import cast

from prototyping_inference_engine.api.atom.term.factory.literal_factory import (
    LiteralFactory,
)
from prototyping_inference_engine.api.atom.term.literal_config import LiteralConfig
from prototyping_inference_engine.api.atom.term.literal_xsd import (
    XSD_INTEGER,
    XSD_PREFIX,
)
from prototyping_inference_engine.api.atom.term.storage.dict_storage import DictStorage
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.session.reasoning_session import ReasoningSession


class TestDlgpeArithmeticEvaluation(unittest.TestCase):
    def setUp(self) -> None:
        self.literal_factory = LiteralFactory(DictStorage(), LiteralConfig.default())

    def test_arithmetic_term_in_atom(self) -> None:
        dlgp = """
        @facts
        p(3).

        @queries
        ?(X) :- p(X + 1).
        """
        with ReasoningSession.create() as session:
            result = session.parse(dlgp)
            fact_base = session.create_fact_base(result.facts)
            query = cast(FOQuery, next(iter(result.queries)))
            answers = list(
                session.evaluate_query_with_sources(query, fact_base, result.sources)
            )

        expected = self.literal_factory.create("2", f"{XSD_PREFIX}{XSD_INTEGER}")
        self.assertEqual(len(answers), 1)
        self.assertEqual(answers[0][0], expected)

    def test_arithmetic_comparison(self) -> None:
        dlgp = """
        @facts
        p(2).

        @queries
        ?() :- p(X), X + 1 > 2.
        """
        with ReasoningSession.create() as session:
            result = session.parse(dlgp)
            fact_base = session.create_fact_base(result.facts)
            query = cast(FOQuery, next(iter(result.queries)))
            answers = list(
                session.evaluate_query_with_sources(query, fact_base, result.sources)
            )

        self.assertEqual(answers, [tuple()])


if __name__ == "__main__":
    unittest.main()
