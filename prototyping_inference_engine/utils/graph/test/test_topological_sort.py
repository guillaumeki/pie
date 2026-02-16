import unittest

from prototyping_inference_engine.utils.graph.topological_sort import (
    topological_sort,
)


class TestTopologicalSort(unittest.TestCase):
    def test_orders_by_dependencies(self) -> None:
        nodes: list[str] = ["a", "b", "c"]
        edges: list[tuple[str, str]] = [("a", "b"), ("a", "c")]
        order = topological_sort(nodes, edges)
        self.assertEqual(["a", "b", "c"], order)

    def test_cycle_returns_sorted_nodes(self) -> None:
        nodes: list[str] = ["b", "a", "c"]
        edges: list[tuple[str, str]] = [("a", "b"), ("b", "a")]
        order = topological_sort(nodes, edges, key=lambda v: v)
        self.assertEqual(["a", "b", "c"], order)

    def test_custom_key_controls_order(self) -> None:
        nodes: list[str] = ["b", "aa", "c"]
        edges: list[tuple[str, str]] = []
        order = topological_sort(nodes, edges, key=lambda v: str(len(v)))
        self.assertEqual(["b", "c", "aa"], order)


if __name__ == "__main__":
    unittest.main()
