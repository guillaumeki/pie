from typing import Generic, TypeVar, Callable, Iterable, Iterator, Type, Union
from collections.abc import Set

T = TypeVar('T')


class Partition(Generic[T]):
    """
    @author Guillaume Pérution-Kihli
    This class represents the partition of a set which contains elements of type T
    The data structure used to manage the partition is union-find, which is optimal in terms of algorithmic
    complexity for this problem
    """
    def __init__(self,
                 other_partition: Union["Partition", Iterable[Set[T]]] = None,
                 initial_elements: Iterable[T] = None,
                 comparator: Callable[[T, T], int] = None):
        """
        @param other_partition: the partition to copy
        @param initial_elements: the initial elements of this partition
        @param comparator: the comparator to choose the representative of a class
        """
        self._nodes: dict[T, _Node] = {}
        self._representatives: set[_Node] = set()
        self._comparator = comparator
        if initial_elements is not None:
            for ie in initial_elements:
                self._add_node(ie)
        if other_partition is not None:
            if isinstance(other_partition, Partition):
                self.join(other_partition)
            elif isinstance(other_partition, Iterable):
                for c in other_partition:
                    self.add_class(c)

    @property
    def representatives(self) -> Iterable[T]:
        """
        All the representatives of all the classes of the partition
        @return: an iterable of representatives
        """
        for n in self._representatives:
            yield n.value

    def add_class(self, c: set[T]):
        """
        Add a class to the partition
        If there are some common elements with existing classes,
        @param c : the class to add
        """
        if c:
            i = iter(c)
            root = self._get_node(next(i))
            for e in i:
                self._union(self._get_node(e), root)

    def get_representative(self, x: T) -> T:
        """
        Returns a class' representative of x
        If x is not already in the partition, it is added in its own class
        The returned representative is always the same if the partition is not modified
        @param x : the element from which we want the class' representative
        @return a class' representative of x
        """
        return self._find(self._get_node(x)).value

    def get_class(self, x: T) -> Set[T]:
        """
        Returns an immutable Set containing all the class' elements of x
        @param x : the element from which we want the class
        @return an iterator on the class' elements of x
        """
        return self._ClassView(x, self)

    def union(self, x: T, y: T):
        """
        Merge the classes of x and y
        If x or y are not yet in the partition, they are be added to it
        @param x : the first element of the couple
        @param y : the second element of the couple
        """
        self._union(self._get_node(x), self._get_node(y))

    def join(self, other: "Partition[T]"):
        """
        Join the class of another partition
        This operation consists of merge the classes of this partition and the other one when they share a common
        element
        @param other : the partition we want to join
         """
        for e in other._nodes:
            self.union(e, other.get_representative(e))

    @property
    def classes(self) -> Iterable[Set[T]]:
        """
        Return all the classes of the partition
        @return an iterable of immutable sets that is the list of all classes
        """
        for r in self.representatives:
            yield self.get_class(r)

    @property
    def elements(self) -> Iterable[T]:
        """
        Return all the elements contained in the partition
        @return an iterable containing all the elements of the partition
        """
        for e in self._nodes:
            yield e

    def __iter__(self):
        return self.classes

    def __contains__(self, item: T):
        return item in self._nodes
    
    def __hash__(self):
        return sum(hash(c) * len(c) for c in self)

    def __eq__(self, other) -> bool:
        if other is self:
            return True
        if not isinstance(other, Partition):
            return False
        if len(self._nodes) != len(other._nodes):
            return False
        if self._nodes.keys() != other._nodes.keys():
            return False
        other_classes = set(c for c in other)
        return all(c in other_classes for c in self)

    def __repr__(self):
        return "<Partition: {" + ", ".join(str(c) for c in self) + "}>"

    def _add_node(self, x: T):
        if x not in self._nodes:
            n = self._Node(x)
            self._nodes[x] = n
            self._representatives.add(n)

    def _get_node(self, x: T):
        if x not in self._nodes:
            self._add_node(x)
        return self._nodes[x]

    def _order(self, x: "_Node", y: "_Node"):
        if self._comparator is not None and self._comparator(x.value, y.value) > 0:
            x.value, y.value = y.value, x.value

    def _link(self, x: "_Node", y: "_Node"):
        if x is not y:
            if x.size <= y.size:
                x, y = y, x
            self._order(x, y)
            y.parent = x
            self._representatives.remove(y)
            x.children.add(y)
            x.size += y.size

    def _find(self, x: "_Node") -> "_Node":
        if x is not x.parent:
            x.parent.children.remove(x)
            x.parent.size -= 1
            x.parent = self._find(x.parent)
            x.parent.children.add(x)
            x.parent.size += 1
        return x.parent

    def _union(self, x: "_Node", y: "_Node"):
        self._link(self._find(x), self._find(y))

    class _ClassView(Set):
        def __init__(self, x: T, partition):
            self.x = x
            self.partition = partition

        def __contains__(self, o: object) -> bool:
            if o not in self.partition._nodes:
                return False
            return (self.partition._find(self.partition._get_node(self.x))
                    is self.partition._find(self.partition._get_node(o)))

        def __len__(self) -> int:
            return self.partition._find(self.partition._get_node(self.x)).size

        def __iter__(self) -> Iterator[T]:
            queue = [self.partition._find(self.partition._get_node(self.x))]
            while queue:
                n = queue.pop()
                queue += list(n.children)
                yield n.value

        def __repr__(self):
            return "{" + ", ".join(str(e) for e in self) + "}"

        def __hash__(self):
            result = 0
            for elt in self:
                result ^= hash(elt)
            return result

        def __eq__(self, other):
            return len(other) == len(self) and all(e in other for e in self)

    class _Node:
        def __init__(self, value: T):
            self.size: int = 1
            self.parent: "_Node" = self
            self.children: set[_Node] = set()
            self.value: T = value

        def __len__(self):
            return self.size

        def __repr__(self):
            return ("<_Node: {size : " + str(self.size)
                    + ", parent: " + str(self.parent.value)
                    + ", children: " + str([c.value for c in self.children])
                    + ", value: " + str(self.value)+"}>")
