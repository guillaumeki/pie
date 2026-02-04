import unittest

from prototyping_inference_engine.api.atom.term.factory.literal_factory import (
    LiteralFactory,
)
from prototyping_inference_engine.api.atom.term.storage.dict_storage import DictStorage
from prototyping_inference_engine.api.data.basic_query import BasicQuery
from prototyping_inference_engine.api.data.python_function_data import (
    PythonFunctionReadable,
    function_predicate,
)
from prototyping_inference_engine.api.atom.term.variable import Variable


def add(a: int, b: int) -> int:
    return a + b


def add_solver(values):
    a, b, res = values
    results = []
    if a is not None and b is not None:
        results.append([a, b, a + b])
    elif a is not None and res is not None:
        results.append([a, res - a, res])
    elif b is not None and res is not None:
        results.append([res - b, b, res])
    return results


class TestPythonFunctionReadable(unittest.TestCase):
    def setUp(self):
        self.literal_factory = LiteralFactory(DictStorage())
        self.data = PythonFunctionReadable(self.literal_factory)

    def test_python_mode_strict_type_hints(self):
        self.data.register_function("add", add, mode="python")
        pred = function_predicate("add", 2)
        a = self.literal_factory.create("1", "xsd:integer")
        b = self.literal_factory.create("2", "xsd:integer")
        query = BasicQuery(pred, {0: a, 1: b}, {2: Variable("R")})
        results = list(self.data.evaluate(query))
        self.assertEqual(len(results), 1)
        self.assertEqual(str(results[0][0]), "3")

    def test_min_bound_with_solver(self):
        self.data.register_function(
            "add",
            add,
            mode="python",
            min_bound=2,
            solver=add_solver,
        )
        pred = function_predicate("add", 2)
        a = self.literal_factory.create("5", "xsd:integer")
        res = self.literal_factory.create("9", "xsd:integer")
        query = BasicQuery(pred, {0: a, 2: res}, {1: Variable("B")})
        results = list(self.data.evaluate(query))
        self.assertEqual(len(results), 1)
        self.assertEqual(str(results[0][0]), "4")


if __name__ == "__main__":
    unittest.main()
