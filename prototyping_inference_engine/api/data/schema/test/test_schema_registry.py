import unittest

from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.data.schema import (
    IncompatiblePredicateSchemaError,
    LogicalType,
    PositionSpec,
    RelationSchema,
    SessionSchemaRegistry,
)


class TestSchemaRegistry(unittest.TestCase):
    def test_relation_schema_compatibility_variants(self):
        predicate = Predicate("p", 2)
        left = RelationSchema(
            predicate,
            (
                PositionSpec("c0", LogicalType.STRING, False),
                PositionSpec("c1", LogicalType.INTEGER, True),
            ),
        )
        same = RelationSchema(
            predicate,
            (
                PositionSpec("c0", LogicalType.STRING, False),
                PositionSpec("c1", LogicalType.INTEGER, True),
            ),
        )
        different_name = RelationSchema(
            predicate,
            (
                PositionSpec("x0", LogicalType.STRING, False),
                PositionSpec("c1", LogicalType.INTEGER, True),
            ),
        )
        different_type = RelationSchema(
            predicate,
            (
                PositionSpec("c0", LogicalType.FLOAT, False),
                PositionSpec("c1", LogicalType.INTEGER, True),
            ),
        )
        different_nullable = RelationSchema(
            predicate,
            (
                PositionSpec("c0", LogicalType.STRING, True),
                PositionSpec("c1", LogicalType.INTEGER, True),
            ),
        )
        different_predicate = RelationSchema(
            Predicate("q", 2),
            (
                PositionSpec("c0", LogicalType.STRING, False),
                PositionSpec("c1", LogicalType.INTEGER, True),
            ),
        )
        different_arity = RelationSchema(
            Predicate("p", 1),
            (PositionSpec("c0", LogicalType.STRING, False),),
        )

        self.assertTrue(left.is_compatible_with(same))
        self.assertFalse(left.is_compatible_with(different_name))
        self.assertTrue(
            left.is_compatible_with(different_name, strict_position_names=False)
        )
        self.assertFalse(left.is_compatible_with(different_type))
        self.assertFalse(left.is_compatible_with(different_nullable))
        self.assertFalse(left.is_compatible_with(different_predicate))
        self.assertFalse(left.is_compatible_with(different_arity))

    def test_registry_register_validate_and_get(self):
        predicate = Predicate("r", 1)
        schema = RelationSchema(
            predicate,
            (PositionSpec("id", LogicalType.INTEGER, False),),
        )
        registry = SessionSchemaRegistry()

        self.assertIsNone(registry.get(predicate))
        registry.register_or_validate(schema)
        self.assertEqual(registry.get(predicate), schema)
        self.assertEqual(registry.schemas, (schema,))
        registry.register_or_validate(schema)
        registry.register_many([schema])

    def test_registry_raises_for_incompatible_schema(self):
        predicate = Predicate("s", 1)
        left = RelationSchema(
            predicate,
            (PositionSpec("id", LogicalType.INTEGER, False),),
        )
        right = RelationSchema(
            predicate,
            (PositionSpec("id", LogicalType.STRING, False),),
        )
        registry = SessionSchemaRegistry()
        registry.register_or_validate(left)

        with self.assertRaises(IncompatiblePredicateSchemaError):
            registry.register_or_validate(right)
