import unittest

from prototyping_inference_engine.iri.iri import IRIRef
from prototyping_inference_engine.iri.preparator import BasicStringPreparator


class TestBasicStringPreparator(unittest.TestCase):
    def test_preparation_html4(self) -> None:
        data = [
            ("Ros&eacute;", "Ros\u00e9"),
            ("&lt;b&gt;Bold&lt;/b&gt;", "<b>Bold</b>"),
            ("5 &lt; 10 &amp;&amp; 10 &gt; 5", "5 < 10 && 10 > 5"),
            ("Price&nbsp;=&nbsp;10&nbsp;&euro;", "Price\u00a0=\u00a010\u00a0\u20ac"),
            ("Smiley: &#128512;", "Smiley: \U0001f600"),
            ("Hex: &#x1F600;", "Hex: \U0001f600"),
            ("Already decoded \u00e9 and \u20ac", "Already decoded \u00e9 and \u20ac"),
            ("Unknown &madeup; stays", "Unknown &madeup; stays"),
            ("X &lt; Y &unknown; &gt; Z", "X < Y &unknown; > Z"),
        ]
        preparator = BasicStringPreparator(["html4"])
        for input_value, expected in data:
            with self.subTest(value=input_value):
                self.assertEqual(expected, preparator.transform(input_value))

    def test_preparation_xml(self) -> None:
        data = [
            ("Ros&eacute;", "Ros&eacute;"),
            ("&lt;b&gt;Bold&lt;/b&gt;", "<b>Bold</b>"),
            ("5 &lt; 10 &amp;&amp; 10 &gt; 5", "5 < 10 && 10 > 5"),
            (
                "Price&nbsp;=&nbsp;10&nbsp;&euro;",
                "Price&nbsp;=&nbsp;10&nbsp;&euro;",
            ),
            ("Smiley: &#128512;", "Smiley: \U0001f600"),
            ("Hex: &#x1F600;", "Hex: \U0001f600"),
            ("Already decoded \u00e9 and \u20ac", "Already decoded \u00e9 and \u20ac"),
            ("Unknown &madeup; stays", "Unknown &madeup; stays"),
            ("X &lt; Y &unknown; &gt; Z", "X < Y &unknown; > Z"),
        ]
        preparator = BasicStringPreparator(["xml"])
        for input_value, expected in data:
            with self.subTest(value=input_value):
                self.assertEqual(expected, preparator.transform(input_value))

    def test_preparation_for_iriref(self) -> None:
        data = [
            ("http://example.com/Ros&eacute;", "http://example.com/Ros\u00e9"),
            (
                "http://example.com/caf&eacute;-noir",
                "http://example.com/caf\u00e9-noir",
            ),
            ("../R&eacute;sum&eacute;.html", "../R\u00e9sum\u00e9.html"),
            (
                "http://example.com/search?q=Tom&amp;Jerry",
                "http://example.com/search?q=Tom&Jerry",
            ),
            (
                "http://example.com/page#Section&nbsp;1",
                "http://example.com/page#Section\u00a01",
            ),
            (
                "http://example.com/smiley-&#128512;",
                "http://example.com/smiley-\U0001f600",
            ),
            (
                "http:&#47;&#47;example.com&#47;path&#47;to&#47;file",
                "http://example.com/path/to/file",
            ),
            ("../dir&#47;subdir&#47;file.html", "../dir/subdir/file.html"),
        ]
        preparator = BasicStringPreparator(["html4"])
        for input_value, expected in data:
            with self.subTest(value=input_value):
                self.assertEqual(IRIRef(expected), IRIRef(input_value, preparator))


if __name__ == "__main__":
    unittest.main()
