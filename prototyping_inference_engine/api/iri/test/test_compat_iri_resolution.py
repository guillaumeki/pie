from unittest import TestCase

from prototyping_inference_engine.api.iri.compat import resolve_iri_reference


class TestIriResolution(TestCase):
    def test_remove_dot_segments_examples(self):
        base = "ex:"
        cases = (
            ("/a/b/c/./../../g", "ex:/a/g"),
            ("mid/content=5/../6", "ex:mid/6"),
            ("/a/b/c/../..", "ex:/a/"),
        )
        for reference, expected in cases:
            with self.subTest(reference=reference):
                self.assertEqual(resolve_iri_reference(reference, base), expected)

    def test_resolution_rfc_examples(self):
        base = "http://a/b/c/d;p?q"
        cases = (
            ("g:h", "g:h"),
            ("g", "http://a/b/c/g"),
            ("./g", "http://a/b/c/g"),
            ("g/", "http://a/b/c/g/"),
            ("/g", "http://a/g"),
            ("//g", "http://g"),
            ("?y", "http://a/b/c/d;p?y"),
            ("g?y", "http://a/b/c/g?y"),
            ("#s", "http://a/b/c/d;p?q#s"),
            ("g#s", "http://a/b/c/g#s"),
            ("g?y#s", "http://a/b/c/g?y#s"),
            (";x", "http://a/b/c/;x"),
            ("g;x", "http://a/b/c/g;x"),
            ("g;x?y#s", "http://a/b/c/g;x?y#s"),
            ("", "http://a/b/c/d;p?q"),
            (".", "http://a/b/c/"),
            ("./", "http://a/b/c/"),
            ("..", "http://a/b/"),
            ("../", "http://a/b/"),
            ("../g", "http://a/b/g"),
            ("../..", "http://a/"),
            ("../../", "http://a/"),
            ("../../g", "http://a/g"),
        )
        for reference, expected in cases:
            with self.subTest(reference=reference):
                self.assertEqual(resolve_iri_reference(reference, base), expected)
