import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.data.basic_query import BasicQuery
from prototyping_inference_engine.api.data.storage.in_memory_graph_storage import (
    InMemoryGraphStorage,
)
from prototyping_inference_engine.api.data.storage.virtual_delete_storage import (
    VirtualDeleteStorage,
)


class TestVirtualDeleteStorageMore(unittest.TestCase):
    def test_properties_and_update_branches(self):
        p = Predicate("p", 2)
        a = Atom(p, Variable("X"), Constant("b"))
        base = InMemoryGraphStorage()
        wrapper = VirtualDeleteStorage(base)
        wrapper.update([a])

        self.assertEqual(wrapper.removed_atoms, set())
        self.assertTrue(wrapper.has_predicate(p))
        self.assertIsNotNone(wrapper.get_atomic_pattern(p))
        self.assertIsNone(
            wrapper.estimate_bound(
                BasicQuery(
                    predicate=p,
                    bound_positions={},
                    answer_variables={0: Variable("A")},
                )
            )
        )
        self.assertTrue(wrapper.variables)
        self.assertTrue(wrapper.constants)
        self.assertTrue(wrapper.terms)

    def test_interface_methods(self):
        p = Predicate("p", 2)
        a = Atom(p, Constant("a"), Constant("b"))
        b = Atom(p, Constant("a"), Constant("c"))
        base = InMemoryGraphStorage([a, b])
        wrapper = VirtualDeleteStorage(base)

        self.assertTrue(wrapper.has_predicate(p))
        self.assertIn(p, set(wrapper.get_predicates()))
        self.assertEqual(len(wrapper), 2)

        query = BasicQuery(
            predicate=p,
            bound_positions={0: Constant("a")},
            answer_variables={1: Variable("Y")},
        )
        rows = list(wrapper.evaluate(query))
        self.assertEqual(set(rows), {(Constant("b"),), (Constant("c"),)})

        wrapper.remove(a)
        self.assertNotIn(a, wrapper)
        self.assertIn(a, base)

        wrapper.add(a)
        self.assertIn(a, wrapper)

        wrapper.remove_all([a, b])
        self.assertEqual(len(wrapper), 0)
        self.assertEqual(wrapper.variables, set())
        self.assertEqual(wrapper.constants, set())
        self.assertEqual(wrapper.terms, set())
        self.assertEqual(wrapper.removed_atoms, {a, b})
        wrapper.concrete_deletions()
        self.assertEqual(wrapper.removed_atoms, set())

        q2 = BasicQuery(
            predicate=p,
            bound_positions={0: Constant("a")},
            answer_variables={1: Variable("Y")},
        )
        self.assertIsNone(wrapper.estimate_bound(q2))
        self.assertIsNotNone(wrapper.get_atomic_pattern(p))

    def test_constructor_requires_writable(self):
        class _ReadOnly:
            pass

        with self.assertRaises(TypeError):
            VirtualDeleteStorage(_ReadOnly())  # type: ignore[arg-type]
