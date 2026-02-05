import unittest

from prototyping_inference_engine.iri.iri import IRIRef, IRIParseError
from prototyping_inference_engine.iri.normalization import (
    ExtendedComposableNormalizer,
    RFCNormalizationScheme,
)


class TestIRIRef(unittest.TestCase):
    def test_recomposition(self) -> None:
        inputs = [
            "scheme://user@host:2025/path.to/my.file?query#fragment",
            "scheme://host/path.to/my.file?query#fragment",
            "http://www.example.com/path/to/file?query=abc#frag",
            "https://host:8080/",
            "ftp://user@ftp.host.com:21/downloads/file.txt",
            "mailto:user@example.com",
            "file:///C:/path/to/file.txt",
            "urn:isbn:0451450523",
            "news:comp.infosystems.www.servers.unix",
            "tel:+1-816-555-1212",
            "ldap://[2001:db8::7]/c=GB?objectClass?one",
            "http://example.com./path",
            "//host",
            "//user@host",
            "//host:8080",
            "//user@host:8080",
            "//host/path",
            "//host/path?query",
            "//host/path#frag",
            "//host/path?query#frag",
            "//host?",
            "//host#",
            "//host?#",
            "//",
            "/",
            "/file",
            "/file.txt",
            "/file.ext?query",
            "/file.ext#frag",
            "/file.ext?query#frag",
            "/dir/file.ext",
            "/dir.with.dots/file.with.dots",
            "/path/to/file",
            "/path/to/file?query=abc",
            "/path/to/file#fragment",
            "/path/to/file?query#frag",
            "/?q=abc",
            "/#fragment",
            "/?#",
            "file",
            "file.ext",
            "path/file.ext",
            "path.to/file.ext",
            "path/to/file",
            "segment",
            "../up/one/level",
            "./same/level",
            ".",
            "..",
            "./file",
            "../file",
            "./",
            "../",
            "?query",
            "?query=value",
            "?query=1&another=2",
            "#fragment",
            "?query#fragment",
            "?#",
            "#",
            "?",
            "#a/b/c",
            "///path",
            "////host/path",
            "//host///extra",
            "scheme://",
            "scheme://host",
            "scheme://host#",
            "scheme://host?",
            "scheme://host?#",
            "file:///",
            "mailto:",
            "news:",
            "http://",
            "http://host",
            "http://host/",
            "http://host/path",
            "http://host?query",
            "http://host#frag",
            "http://host/path?query",
            "http://host/path#frag",
            "http://host/path?query#frag",
            "http://user@host",
            "http://user@host:80",
            "http://user@host:80/",
            "http://user@host:80/path",
            "http://user@host:80/path?query#frag",
            "./",
            "../",
            "././",
            "../../",
            "./../",
            ".././",
            "./a/b/../c/./d.html",
            "../a/./b/../c",
            "./a/../b/./c",
            "http://[2001:db8::1]/",
            "http://[2001:db8:0:0:8:800:200C:417A]/index.html",
            "http://[::1]",
            "http://[::1]:8080/path/to/file?query=abc#frag",
            "ftp://user@[2001:db8::7]:21/downloads/file.txt",
            "//[2001:db8::2]/network/path",
            "//[::1]/just/path",
            "ldap://[2001:db8::7]/c=GB?objectClass?one",
            "http://[2001:db8::1:0:0]/",
            "http://[::ffff:192.0.2.128]/",
            "http://[v7.fe80::abcd]/",
            "http://[v7.fe80::abcd]/path?query#frag",
            "https://[vF.FF-1~abc]/resource",
            "//[v7.fe80::abcd]/network/path",
            "//[vA.example-1]/foo/bar",
            "http://[v1.a-b_c~!$&'()*+,;=]/",
            "http://www.example.com/\u00e9l\u00e8ve/\u00e9cole?mati\u00e8re=\u00e9conomie#section-\u03c0",
            "http://m\u00fcnchen.example/stra\u00dfe/\u00fcberblick?jahr=2025#\u00fcbersicht",
            "http://www.example.com/\u043f\u0443\u0442\u044c/\u0441\u0442\u0440\u0430\u043d\u0438\u0446\u0430?\u043a\u043b\u044e\u0447=\u0437\u043d\u0430\u0447\u0435\u043d\u0438\u0435#\u0444\u0440\u0430\u0433\u043c\u0435\u043d\u0442",
            "http://www.example.com/\u30e6\u30fc\u30b6\u30fc/\u30d7\u30ed\u30d5\u30a3\u30fc\u30eb?\u8868\u793a=\u65e5\u672c\u8a9e#\u6982\u8981",
            "http://\u4f8b\u3048.\u30c6\u30b9\u30c8/\u30d1\u30b9/\u30da\u30fc\u30b8?\u30af\u30a8\u30ea=\u5024#\u30d5\u30e9\u30b0\u30e1\u30f3\u30c8",
            "http://\u0645\u062b\u0627\u0644.\u0625\u062e\u062a\u0628\u0627\u0631/\u0645\u0633\u0627\u0631/\u0635\u0641\u062d\u0629?\u0627\u0633\u062a\u0639\u0644\u0627\u0645=\u0642\u064a\u0645\u0629#\u062c\u0632\u0621",
            "http://emoji.example/\U0001f600/\U0001f607?q=\u03c0&x=\u03bb#\u03c3-\U0001f680",
            "//\u30db\u30b9\u30c8\u540d.example/\u30d1\u30b9/\u30ea\u30bd\u30fc\u30b9?\u7a2e\u985e=\u30c6\u30b9\u30c8#\u90e8\u5206",
            "chemin/\u0441\u043c\u0435\u0448\u0430\u043d\u043d\u044b\u0439/\u8def\u5f84",
            "\u8cc7\u6599/\u30c7\u30fc\u30bf/\u043f\u0440\u0438\u043c\u0435\u0440",
            "http://example.com/chemin?priv=\ue000\ue001",
            "http://example.com/\U0001f600/\U0001f680?earth=\U0001f30d#device=\U0001f4bb",
            "http://\U0001f600.example.com/path",
            "http://example.com/\U00010348\U00010400/section",
            "//\U0001f600\U0001f680.example/\U0001f30d/\U0001f4bb",
            "\u8cc7\u6599/\U0001f600/\u30c7\u30fc\u30bf/\U00010348",
        ]

        for input_value in inputs:
            with self.subTest(value=input_value):
                iri = IRIRef(input_value)
                self.assertEqual(input_value, iri.recompose())

    def test_malformed_iri_raises(self) -> None:
        invalid = [
            ":",
            ":/",
            "://",
            "://host/path",
            "1scheme:/path",
            "-scheme:/path",
            "http://host/path##frag",
            "http://host/path?query#frag#x",
        ]

        for input_value in invalid:
            with self.subTest(value=input_value):
                with self.assertRaises(IRIParseError):
                    IRIRef(input_value)

    def test_remove_dot_segments(self) -> None:
        base = IRIRef("ex:")
        cases = [
            ("/a/b/c/./../../g", "ex:/a/g"),
            ("mid/content=5/../6", "ex:mid/6"),
            ("/a/b/c/../..", "ex:/a/"),
        ]
        for reference, expected in cases:
            with self.subTest(reference=reference):
                iri = IRIRef(reference)
                result = iri.resolve_in_place(base).recompose()
                self.assertEqual(expected, result)

    def test_resolution(self) -> None:
        inputs = [
            (
                "http://www.lirmm.fr/me?query",
                "#bar",
                "http://www.lirmm.fr/me?query#bar",
            ),
            ("http://www.lirmm.fr/a/", "b", "http://www.lirmm.fr/a/b"),
            ("http://www.lirmm.fr/a/", "b", "http://www.lirmm.fr/a/b"),
            ("http:/a/?q", "#f", "http:/a/?q#f"),
            ("http:/a/b/?q=x", "#frag", "http:/a/b/?q=x#frag"),
        ]

        for base_value, relative_value, expected in inputs:
            with self.subTest(base=base_value, relative=relative_value):
                base = IRIRef(base_value)
                relative = IRIRef(relative_value)
                result = relative.resolve_in_place(base).recompose()
                self.assertEqual(expected, result)

    def test_resolution_rfc_examples(self) -> None:
        base = IRIRef("http://a/b/c/d;p?q")
        cases = [
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
        ]

        for reference, expected in cases:
            with self.subTest(reference=reference):
                relative = IRIRef(reference)
                result = relative.resolve_in_place(base).recompose()
                self.assertEqual(expected, result)

    def test_resolution_rfc_abnormal(self) -> None:
        base = IRIRef("http://a/b/c/d;p?q")
        cases = [
            ("../../../g", "http://a/g"),
            ("../../../../g", "http://a/g"),
            ("/./g", "http://a/g"),
            ("/../g", "http://a/g"),
            ("g.", "http://a/b/c/g."),
            (".g", "http://a/b/c/.g"),
            ("g..", "http://a/b/c/g.."),
            ("..g", "http://a/b/c/..g"),
            ("./../g", "http://a/b/g"),
            ("./g/.", "http://a/b/c/g/"),
            ("g/./h", "http://a/b/c/g/h"),
            ("g/../h", "http://a/b/c/h"),
            ("g;x=1/./y", "http://a/b/c/g;x=1/y"),
            ("g;x=1/../y", "http://a/b/c/y"),
            ("g?y/./x", "http://a/b/c/g?y/./x"),
            ("g?y/../x", "http://a/b/c/g?y/../x"),
            ("g#s/./x", "http://a/b/c/g#s/./x"),
            ("g#s/../x", "http://a/b/c/g#s/../x"),
        ]

        for reference, expected in cases:
            with self.subTest(reference=reference):
                relative = IRIRef(reference)
                result = relative.resolve_in_place(base).recompose()
                self.assertEqual(expected, result)

    def test_resolution_non_strict(self) -> None:
        base = IRIRef("http://a/b/c/d;p?q")
        relative = IRIRef("http:g")
        result = relative.resolve_in_place(base, strict=False).recompose()
        self.assertEqual("http://a/b/c/g", result)

    def test_relativization(self) -> None:
        data = [
            ("http://example.org/base/", "http://example.org/base/rel"),
            ("http://example.org/base/", "http://example.org/base/sub/rel"),
            ("http://example.org/base/dir/", "http://example.org/base/dir/rel"),
            ("http://example.org/base/dir/", "http://example.org/base/dir/sub/rel"),
            ("http:", "http:"),
            ("http:/", "http:/"),
            ("http:a", "http:a"),
            ("http:/a", "http:/a"),
            ("http:a/", "http:a/"),
            ("http:/a/", "http:/a/"),
            ("http:", "http:"),
            ("http:/", "http:/"),
            ("http:/", "http:"),
            ("http:", "http:/"),
            ("http:/a", "http:/a"),
            ("http:a", "http:a"),
            ("http:/a", "http:/"),
            ("http:/", "http:/a"),
            ("http:/a/", "http:/"),
            ("http:a/b/c/", "http:a/b/c/d/e/f"),
            ("http:a/b/c", "http:a/b/c/d/e/f"),
            ("http:a/b/c/d/e/f", "http:a/b/c"),
            ("http:a/b/c/d/e/f", "http:a/b/c/g/h/i"),
            ("http:a/b/c", "http:a/b"),
            ("http:/a/b", "http:/a/b"),
            ("http:/a/b/", "http:/a/b/"),
            ("http:/a/b/", "http:/a/b"),
            ("http:/a/b?q=x", "http:/a/b?q=x"),
            ("http:/a/b?q=x", "http:/a/b#frag"),
            ("http:/a/b/?q=x", "http:/a/b/#frag"),
            ("http:?q=x", "http:#frag"),
            ("http:/a/b?q=x", "http:/a/b"),
            ("http:?q", "http:#f"),
            ("http://a/b", "https://a/b"),
            ("http://a.example.com/path/x", "http://b.example.com/path/y"),
            ("http:a/b/c?q=x", "http:a/b/c"),
            ("http:a?q=x", "http:a"),
            ("http://host/a/b?q=x", "http://host/a/b"),
            ("http://host/a/b/?q=x", "http://host/a/b"),
            ("http:?q=x", "http:"),
            ("http:/a/b?q=x", "http:/a/b?q=y"),
            ("http:a/b?q=x", "http:a/b?q=y"),
            ("http:a/b?q=x", "http:a/b"),
            ("http:a/b?q=x", "http:a/b/"),
            ("http:a/b/?q=x", "http:a/b"),
            ("http:?q=x", "http:"),
            ("http:/?q=x", "http:"),
            ("http:q=x", "http:/"),
            ("http:/a/b/c/d/e/f", "http:/g"),
            ("http:/a/b/c/d/e/f", "http:/a/g"),
            ("http:a/b/c/d/e/f/g/h/i", "http:a"),
            ("http://example.org/ros\u00e9;", "http://example.org/"),
            ("http://host/a", "http://host/"),
            ("http://host/a/b", "http://host/a/"),
            ("http://host/a/b", "http://host/a//b/"),
            ("veryverylongscheme:a/b/c/d/e", "veryverylongscheme:a//b/"),
            ("http://host/", "http://host/"),
            ("http:?q", "http:#f"),
            ("http:a", "http:a/b"),
        ]

        for base_value, target_value in data:
            with self.subTest(base=base_value, target=target_value):
                base = IRIRef(base_value)
                target = IRIRef(target_value)
                relativized = target.relativize(base)
                resolved = relativized.resolve(base)
                self.assertEqual(target.recompose(), resolved.recompose())
                self.assertLessEqual(
                    len(relativized.recompose()), len(target.recompose())
                )

    def test_normalization(self) -> None:
        data = [
            (
                "HTTP://%7e%3a%4b%5C@www.lirmm.fr:80/../.",
                "http://~%3AK%5C@www.lirmm.fr/",
            ),
            ("HTTP://ExAmPle.Com:80/path", "http://example.com/path"),
            (
                "http://UsEr%7e%3a%4b@Example.Com",
                "http://UsEr~%3AK@example.com/",
            ),
            (
                "http://example.com/%7e/%C3%A9",
                "http://example.com/~/\u00e9",
            ),
            (
                "http://example.com/path?q=%7e%3a#frag%C3%A9%7e",
                "http://example.com/path?q=%7E%3A#frag%C3%A9%7E",
            ),
            (
                "http://example.com/%C3%28",
                "http://example.com/%C3%28",
            ),
        ]
        normalizer = ExtendedComposableNormalizer(
            RFCNormalizationScheme.SYNTAX,
            RFCNormalizationScheme.PATH,
            RFCNormalizationScheme.SCHEME,
            RFCNormalizationScheme.PCT,
        )
        for input_value, expected in data:
            with self.subTest(value=input_value):
                result = IRIRef(input_value).normalize(normalizer)
                self.assertEqual(expected, result.recompose())


if __name__ == "__main__":
    unittest.main()
