from typing import Callable
from unittest import TestCase

from prototyping_inference_engine.utils.partition import Partition


class TestPartition(TestCase):
    data = (
        {"elements": {1, 2}, "partition": ({1, 2},), "unions": ((1, 2),)},
        {"elements": {1, 2, 3, 4, 5, 6, 7, 8},
         "partition": ({1, 2, 5, 6, 8}, {3, 4}, {7}),
         "unions": ((1, 2), (3, 4), (2, 5), (1, 6), (2, 8))},
        {"elements": {1, 2, 3, 4, 5, 6},
         "partition": [{1, 2, 3, 4, 5}, {6}],
         "unions": ((1, 2), (3, 4), (1, 3), (2, 5))}
    )

    not_equal_data = (
        {"partition1": ({1, 2},), "partition2": ({1, 2, 5, 6, 8}, {3, 4}, {7})},
        {"partition1": ({1, 2, 5, 6, 8}, {3, 4}, {7}), "partition2": ({1, 2, 3, 4, 5}, {6})},
        {"partition1": ({1, 2, 3, 4, 5}, {6}), "partition2": ()},
        {"partition1": ({1, 2, 3, 4, 5}, {6}), "partition2": ({1, 2, 3, 4, 6}, {5})},
        {"partition1": ({1, 2, 3, 4, 5}, {6}), "partition2": ({1, 2, 3, 4, 6}, {8})}
    )

    @classmethod
    def check_on_data(cls, fun: Callable[[set[int], tuple[set[int]], tuple[tuple[int, int]]], None]):
        for d in cls.data:
            fun(d["elements"], d["partition"], d["unions"])

    @classmethod
    def check_on_not_equal_data(cls, fun: Callable[[tuple[set[int]], tuple[set[int]]], None]):
        for d in cls.not_equal_data:
            fun(d["partition1"], d["partition2"])

    def test_add_class(self):
        def test(elements, partition, unions):
            part = Partition()
            for cl in partition:
                part.add_class(cl)

            classes = set(frozenset(cl) for cl in part.classes)
            self.assertTrue(all(cl in partition for cl in classes))
            self.assertTrue(all(cl in classes for cl in partition))
            self.assertEqual(elements, set(part.elements))
        self.check_on_data(test)

    def test_get_representative(self):
        def test(elements, partition, unions):
            part = Partition(partition)

            for cl in partition:
                it = iter(cl)
                representative = part.get_representative(next(it))
                self.assertTrue(representative in cl)

                for element in it:
                    self.assertEqual(representative, part.get_representative(element))
        self.check_on_data(test)

    def test_get_class(self):
        def test(elements, partition, unions):
            part = Partition(partition)

            for cl in partition:
                for i in cl:
                    s = set(c for c in part.get_class(i))
                    self.assertEqual(cl, s)
        self.check_on_data(test)

    def test_union(self):
        def test(elements, partition, unions):
            part: Partition[int] = Partition(initial_elements=elements)

            for u in unions:
                part.union(u[0], u[1])

            self.assertTrue(all(cl in partition for cl in part))
        self.check_on_data(test)

    def test_classes(self):
        def test(elements, partition, unions):
            part = Partition(partition)
            self.assertTrue(all(cl in partition for cl in part.classes))
        self.check_on_data(test)

    def test_elements(self):
        def test(elements, partition, unions):
            part = Partition(partition)
            self.assertEqual(elements, set(part.elements))
        self.check_on_data(test)

    def test__eq__(self):
        def test(elements, partition, unions):
            part1: Partition[int] = Partition(initial_elements=elements)
            for u in unions:
                part1.union(u[0], u[1])
            part2: Partition[int] = Partition(partition)
            self.assertEqual(part1, part2)
        self.check_on_data(test)

        def test_not_equal(partition1, partition2):
            part1: Partition[int] = Partition(partition1)
            part2: Partition[int] = Partition(partition2)
            self.assertNotEqual(part1, part2)
        self.check_on_not_equal_data(test_not_equal)

    """def test__hash__(self):
        def test(elements, partition, unions):
            part1: Partition[int] = Partition(initial_elements=elements)
            for u in unions:
                part1.union(u[0], u[1])
            part2: Partition[int] = Partition(partition)

            self.assertEqual(hash(part1), hash(part2))
        self.test_on_data(test)

    def test_representatives(self):
        self.fail()

    def test_join(self):
        self.fail()
    """
