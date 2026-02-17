import unittest

from prototyping_inference_engine.api.atom.term.blank_node_term import BlankNodeTerm
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.substitution.substitution import Substitution


class TestBlankNodeTerm(unittest.TestCase):
    def test_prefix_normalization(self):
        b = BlankNodeTerm("id1")
        self.assertEqual(b.identifier, "_:id1")

    def test_caching(self):
        b1 = BlankNodeTerm("id2")
        b2 = BlankNodeTerm("_:id2")
        self.assertIs(b1, b2)

    def test_non_ground(self):
        b = BlankNodeTerm("id3")
        self.assertFalse(b.is_ground)

    def test_apply_substitution_is_stable(self):
        b = BlankNodeTerm("id4")
        sub = Substitution({Variable("X"): Constant("a")})
        self.assertIs(b.apply_substitution(sub), b)
