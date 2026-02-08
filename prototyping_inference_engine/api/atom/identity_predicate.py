"""
Identity-based predicate (no global caching).
"""

from prototyping_inference_engine.api.atom.predicate import Predicate


class IdentityPredicate(Predicate):
    def __new__(cls, name: str, arity: int):
        return object.__new__(cls)

    def __init__(self, name: str, arity: int):
        Predicate.__init__(self, name, arity)
