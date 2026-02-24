import unittest

from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.logical_function_term import (
    LogicalFunctionalTerm,
)
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.data.basic_query import BasicQuery
from prototyping_inference_engine.api.data.views.model import (
    MissingValuePolicy,
    ViewAttributeSpec,
    ViewDeclaration,
)
from prototyping_inference_engine.api.data.views.source import (
    CompiledView,
    ViewRuntimeSource,
    build_relation_schema,
)
from prototyping_inference_engine.api.data.views.missing_values import (
    MISSING_VALUE_CONSTANT,
)


class _NullOnlyBackend:
    def fetch_rows(self, compiled_view, invocation):
        del compiled_view
        del invocation
        yield (None,)


class TestMissingValuePolicies(unittest.TestCase):
    def test_ignore_policy_drops_row(self):
        source = _build_source(MissingValuePolicy.IGNORE)
        predicate = Predicate("p", 1)
        query = BasicQuery(predicate, {}, {0: Variable("X")})

        answers = list(source.evaluate(query))
        self.assertEqual(answers, [])

    def test_freeze_policy_uses_missing_constant(self):
        source = _build_source(MissingValuePolicy.FREEZE)
        predicate = Predicate("p", 1)
        query = BasicQuery(predicate, {}, {0: Variable("X")})

        answers = list(source.evaluate(query))
        self.assertEqual(len(answers), 1)
        self.assertEqual(answers[0][0], MISSING_VALUE_CONSTANT)

    def test_optional_policy_creates_variable(self):
        source = _build_source(MissingValuePolicy.OPTIONAL)
        predicate = Predicate("p", 1)
        query = BasicQuery(predicate, {}, {0: Variable("X")})

        answers = list(source.evaluate(query))
        self.assertEqual(len(answers), 1)
        self.assertIsInstance(answers[0][0], Variable)
        self.assertFalse(answers[0][0].is_ground)

    def test_exist_policy_creates_logical_function_term(self):
        source = _build_source(MissingValuePolicy.EXIST)
        predicate = Predicate("p", 1)
        query = BasicQuery(predicate, {}, {0: Variable("X")})

        answers = list(source.evaluate(query))
        self.assertEqual(len(answers), 1)
        self.assertIsInstance(answers[0][0], LogicalFunctionalTerm)


def _build_source(policy: MissingValuePolicy) -> ViewRuntimeSource:
    declaration = ViewDeclaration(
        id="p",
        datasource="d",
        signature=(ViewAttributeSpec(if_missing=policy),),
        query="SELECT NULL",
    )
    predicate = Predicate("p", 1)
    compiled = CompiledView(
        declaration=declaration,
        predicate=predicate,
        query_template="SELECT NULL",
        non_mandatory_positions=(0,),
        schema=build_relation_schema(predicate, declaration),
    )
    return ViewRuntimeSource(name="d", backend=_NullOnlyBackend(), views=(compiled,))


if __name__ == "__main__":
    unittest.main()
