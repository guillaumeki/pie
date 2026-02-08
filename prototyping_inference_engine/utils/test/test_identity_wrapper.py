from unittest import TestCase

from prototyping_inference_engine.utils.identity_wrapper import IdentityWrapper


class TestIdentityWrapper(TestCase):
    def test_identity_comparison(self):
        obj = []
        same_obj = obj
        other_obj = []
        w1 = IdentityWrapper(obj)
        w2 = IdentityWrapper(same_obj)
        w3 = IdentityWrapper(other_obj)
        self.assertEqual(w1, w2)
        self.assertNotEqual(w1, w3)
