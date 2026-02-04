"""Integration tests for data collections with evaluators."""
import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.data.collection import (
    ReadableCollectionBuilder,
    MaterializedCollectionBuilder,
    WritableCollectionBuilder,
)
from prototyping_inference_engine.api.fact_base.frozen_in_memory_fact_base import (
    FrozenInMemoryFactBase,
)
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import (
    MutableInMemoryFactBase,
)
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.parser.dlgp.dlgp2_parser import Dlgp2Parser
from prototyping_inference_engine.query_evaluation.evaluator.atom.atom_evaluator import (
    AtomEvaluator,
)


class TestCollectionWithAtomEvaluator(unittest.TestCase):
    """Test collections work with AtomEvaluator."""

    def setUp(self):
        self.parser = Dlgp2Parser.instance()
        self.evaluator = AtomEvaluator()

        # Create fact bases
        self.fb_persons = FrozenInMemoryFactBase(
            self.parser.parse_atoms("person(alice), person(bob), person(carol).")
        )
        self.fb_knows = FrozenInMemoryFactBase(
            self.parser.parse_atoms("knows(alice, bob), knows(bob, carol).")
        )

        # Build collection
        self.collection = (
            MaterializedCollectionBuilder()
            .add_all_predicates_from(self.fb_persons)
            .add_all_predicates_from(self.fb_knows)
            .build()
        )

        # Predicates and variables
        self.person = Predicate("person", 1)
        self.knows = Predicate("knows", 2)
        self.X = Variable("X")
        self.Y = Variable("Y")

    def test_evaluate_simple_atom(self):
        """Test evaluating a simple atom with one variable."""
        atom = Atom(self.person, self.X)
        results = list(self.evaluator.evaluate(atom, self.collection))

        self.assertEqual(len(results), 3)
        values = {sub.apply(self.X) for sub in results}
        self.assertEqual(
            values,
            {Constant("alice"), Constant("bob"), Constant("carol")}
        )

    def test_evaluate_binary_atom(self):
        """Test evaluating a binary atom with two variables."""
        atom = Atom(self.knows, self.X, self.Y)
        results = list(self.evaluator.evaluate(atom, self.collection))

        self.assertEqual(len(results), 2)
        pairs = {(sub.apply(self.X), sub.apply(self.Y)) for sub in results}
        self.assertEqual(
            pairs,
            {
                (Constant("alice"), Constant("bob")),
                (Constant("bob"), Constant("carol")),
            }
        )

    def test_evaluate_with_initial_substitution(self):
        """Test evaluating with an initial substitution."""
        atom = Atom(self.knows, self.X, self.Y)
        initial_sub = Substitution({self.X: Constant("alice")})

        results = list(self.evaluator.evaluate(atom, self.collection, initial_sub))

        self.assertEqual(len(results), 1)
        sub = results[0]
        self.assertEqual(sub.apply(self.X), Constant("alice"))
        self.assertEqual(sub.apply(self.Y), Constant("bob"))

    def test_evaluate_ground_atom(self):
        """Test evaluating a ground atom."""
        atom = Atom(self.knows, Constant("alice"), Constant("bob"))
        results = list(self.evaluator.evaluate(atom, self.collection))

        self.assertEqual(len(results), 1)

    def test_evaluate_ground_atom_not_found(self):
        """Test evaluating a ground atom that doesn't exist."""
        atom = Atom(self.knows, Constant("alice"), Constant("carol"))
        results = list(self.evaluator.evaluate(atom, self.collection))

        self.assertEqual(len(results), 0)

    def test_evaluate_unknown_predicate_raises(self):
        """Test that evaluating unknown predicate raises KeyError."""
        unknown = Predicate("unknown", 1)
        atom = Atom(unknown, self.X)

        with self.assertRaises(KeyError):
            list(self.evaluator.evaluate(atom, self.collection))


class TestCollectionWithMultipleSources(unittest.TestCase):
    """Test collections aggregating many sources."""

    def setUp(self):
        self.parser = Dlgp2Parser.instance()
        self.evaluator = AtomEvaluator()

    def test_three_sources(self):
        """Test collection with three different sources."""
        fb1 = FrozenInMemoryFactBase(self.parser.parse_atoms("a(1)."))
        fb2 = FrozenInMemoryFactBase(self.parser.parse_atoms("b(2)."))
        fb3 = FrozenInMemoryFactBase(self.parser.parse_atoms("c(3)."))

        collection = (
            MaterializedCollectionBuilder()
            .add_all_predicates_from(fb1)
            .add_all_predicates_from(fb2)
            .add_all_predicates_from(fb3)
            .build()
        )

        self.assertEqual(len(collection), 3)
        predicates = set(collection.get_predicates())
        self.assertEqual(len(predicates), 3)

    def test_overlapping_constants(self):
        """Test sources with overlapping constants."""
        fb1 = FrozenInMemoryFactBase(self.parser.parse_atoms("p(a, b)."))
        fb2 = FrozenInMemoryFactBase(self.parser.parse_atoms("q(b, c)."))

        collection = (
            MaterializedCollectionBuilder()
            .add_all_predicates_from(fb1)
            .add_all_predicates_from(fb2)
            .build()
        )

        # Constants should include all unique constants
        self.assertEqual(
            collection.constants,
            {Constant("a"), Constant("b"), Constant("c")}
        )

    def test_empty_sources(self):
        """Test collection with empty sources."""
        fb1 = FrozenInMemoryFactBase()
        fb2 = FrozenInMemoryFactBase(self.parser.parse_atoms("p(a)."))

        collection = (
            MaterializedCollectionBuilder()
            .add_all_predicates_from(fb1)
            .add_all_predicates_from(fb2)
            .build()
        )

        self.assertEqual(len(collection), 1)


class TestWritableCollectionIntegration(unittest.TestCase):
    """Test writable collections with evaluators."""

    def setUp(self):
        self.parser = Dlgp2Parser.instance()
        self.evaluator = AtomEvaluator()

    def test_add_then_evaluate(self):
        """Test adding atoms then evaluating queries."""
        fb = MutableInMemoryFactBase()
        p = Predicate("p", 1)

        collection = (
            WritableCollectionBuilder()
            .add_all_predicates_from(fb)
            .set_default_writable(fb)
            .build()
        )

        # Initially empty - predicate not registered yet
        atom = Atom(p, Variable("X"))
        self.assertFalse(collection.has_predicate(p))

        # Add some atoms - this registers the predicate
        collection.add(Atom(p, Constant("a")))
        collection.add(Atom(p, Constant("b")))

        # Now predicate is registered and we can evaluate
        self.assertTrue(collection.has_predicate(p))
        results = list(self.evaluator.evaluate(atom, collection))
        self.assertEqual(len(results), 2)

    def test_update_then_evaluate(self):
        """Test bulk update then evaluating."""
        fb = MutableInMemoryFactBase()
        p = Predicate("p", 2)

        collection = (
            WritableCollectionBuilder()
            .set_default_writable(fb)
            .build()
        )

        # Bulk add
        atoms = [
            Atom(p, Constant("a"), Constant("1")),
            Atom(p, Constant("b"), Constant("2")),
            Atom(p, Constant("c"), Constant("3")),
        ]
        collection.update(atoms)

        # Evaluate
        X, Y = Variable("X"), Variable("Y")
        query_atom = Atom(p, X, Y)
        results = list(self.evaluator.evaluate(query_atom, collection))
        self.assertEqual(len(results), 3)


class TestCollectionAsDropInReplacement(unittest.TestCase):
    """Test that collections are true drop-in replacements for FactBase."""

    def test_same_results_as_fact_base(self):
        """Test that collection gives same results as direct fact base query."""
        parser = Dlgp2Parser.instance()
        evaluator = AtomEvaluator()

        atoms = parser.parse_atoms("p(a,b), p(c,d), p(e,f).")
        fb = FrozenInMemoryFactBase(atoms)

        # Create collection wrapping the same data
        collection = (
            MaterializedCollectionBuilder()
            .add_all_predicates_from(fb)
            .build()
        )

        # Query both
        p = Predicate("p", 2)
        X, Y = Variable("X"), Variable("Y")
        atom = Atom(p, X, Y)

        fb_results = set()
        for sub in evaluator.evaluate(atom, fb):
            fb_results.add((sub.apply(X), sub.apply(Y)))

        collection_results = set()
        for sub in evaluator.evaluate(atom, collection):
            collection_results.add((sub.apply(X), sub.apply(Y)))

        self.assertEqual(fb_results, collection_results)

    def test_collection_can_replace_fact_base_parameter(self):
        """Test that a function accepting FactBase works with collection."""
        parser = Dlgp2Parser.instance()

        def count_matches(data, predicate):
            """Function that accepts any ReadableData."""
            from prototyping_inference_engine.api.data.basic_query import BasicQuery
            query = BasicQuery(
                predicate,
                bound_positions={},
                answer_variables={i: Variable(f"V{i}") for i in range(predicate.arity)}
            )
            return sum(1 for _ in data.evaluate(query))

        fb = FrozenInMemoryFactBase(parser.parse_atoms("p(a), p(b), p(c)."))
        collection = (
            MaterializedCollectionBuilder()
            .add_all_predicates_from(fb)
            .build()
        )

        p = Predicate("p", 1)

        # Both should work identically
        self.assertEqual(count_matches(fb, p), 3)
        self.assertEqual(count_matches(collection, p), 3)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""

    def test_single_atom_collection(self):
        """Test collection with just one atom."""
        parser = Dlgp2Parser.instance()
        fb = FrozenInMemoryFactBase(parser.parse_atoms("p(a)."))

        collection = (
            MaterializedCollectionBuilder()
            .add_all_predicates_from(fb)
            .build()
        )

        self.assertEqual(len(collection), 1)
        self.assertEqual(len(list(collection.get_predicates())), 1)

    def test_high_arity_predicates(self):
        """Test predicates with high arity."""
        parser = Dlgp2Parser.instance()
        fb = FrozenInMemoryFactBase(
            parser.parse_atoms("p(a,b,c,d,e).")
        )

        collection = (
            MaterializedCollectionBuilder()
            .add_all_predicates_from(fb)
            .build()
        )

        p = Predicate("p", 5)
        self.assertTrue(collection.has_predicate(p))

    def test_special_constant_names(self):
        """Test constants with special names."""
        parser = Dlgp2Parser.instance()
        # Using quoted constants
        fb = FrozenInMemoryFactBase(
            parser.parse_atoms('p("hello world"), p("123").')
        )

        collection = (
            MaterializedCollectionBuilder()
            .add_all_predicates_from(fb)
            .build()
        )

        self.assertEqual(len(collection), 2)

    def test_same_source_multiple_predicates(self):
        """Test one source providing multiple predicates."""
        parser = Dlgp2Parser.instance()
        fb = FrozenInMemoryFactBase(
            parser.parse_atoms("p(a), q(b), r(c).")
        )

        collection = (
            MaterializedCollectionBuilder()
            .add_all_predicates_from(fb)
            .build()
        )

        predicates = list(collection.get_predicates())
        self.assertEqual(len(predicates), 3)

        # All should route to the same source
        for pred in predicates:
            self.assertIs(collection.get_source_for_predicate(pred), fb)


if __name__ == "__main__":
    unittest.main()
