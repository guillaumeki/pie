"""Tests for evaluating DLGPE-parsed queries."""

import textwrap
import unittest

from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.factory.literal_factory import (
    LiteralFactory,
)
from prototyping_inference_engine.api.atom.term.literal_config import LiteralConfig
from prototyping_inference_engine.api.atom.term.storage.dict_storage import DictStorage
from prototyping_inference_engine.api.data.collection.builder import (
    ReadableCollectionBuilder,
)
from prototyping_inference_engine.api.data.functions.integraal_standard_functions import (
    IntegraalStandardFunctionSource,
)
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import (
    MutableInMemoryFactBase,
)
from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser
from prototyping_inference_engine.query_evaluation.evaluator.fo_query.fo_query_evaluators import (
    GenericFOQueryEvaluator,
)


class TestDlgpeQueryEvaluation(unittest.TestCase):
    def setUp(self):
        self._parser = DlgpeParser.instance()
        self._literal_factory = LiteralFactory(DictStorage(), LiteralConfig.default())

    def _build_collection_with_stdfct(self, fact_base, predicates):
        stdfct_source = IntegraalStandardFunctionSource(
            self._literal_factory, {"std": "stdfct:"}, predicates
        )
        return (
            ReadableCollectionBuilder()
            .add_all_predicates_from(fact_base)
            .add_all_predicates_from(stdfct_source)
            .build()
        )

    def test_boolean_query_from_dlgpe(self):
        dlgpe = "p(a, b). ? :- p(X, Y)."
        result = self._parser.parse(dlgpe)
        query = result["queries"][0]
        fact_base = MutableInMemoryFactBase(result["facts"])

        evaluator = GenericFOQueryEvaluator()
        results = list(evaluator.evaluate(query, fact_base))

        self.assertEqual(len(results), 1)

    def test_function_term_in_conjunction(self):
        dlgpe = textwrap.dedent(
            """
            @computed std: <stdfct>.

            @facts
            p(1, 2).
            s(3).

            @queries
            ?() :- s(std:sum(X, Y)), p(X, Y).
            """
        ).strip()
        result = self._parser.parse(dlgpe)
        query = result["queries"][0]
        fact_base = MutableInMemoryFactBase(result["facts"])

        sum_predicate = Predicate("stdfct:sum", 3)
        collection = self._build_collection_with_stdfct(fact_base, [sum_predicate])

        evaluator = GenericFOQueryEvaluator()
        results = list(evaluator.evaluate(query, collection))

        self.assertEqual(len(results), 1)


if __name__ == "__main__":
    unittest.main()
