"""
Tests for the DLGPE parser.
"""

import unittest

from prototyping_inference_engine.parser.dlgpe import (
    DlgpeParser,
    DlgpeUnsupportedFeatureError,
)
from prototyping_inference_engine.api.atom.term.function_term import FunctionTerm


class TestDlgpeParserBasics(unittest.TestCase):
    """Test basic DLGPE parsing functionality."""

    def setUp(self):
        self.parser = DlgpeParser.instance()

    def test_singleton(self):
        """Test that instance() returns the same parser."""
        parser1 = DlgpeParser.instance()
        parser2 = DlgpeParser.instance()
        self.assertIs(parser1, parser2)

    def test_parse_simple_fact(self):
        """Test parsing a simple fact."""
        result = self.parser.parse("p(a).")
        self.assertEqual(len(result["facts"]), 1)
        atom = result["facts"][0]
        self.assertEqual(str(atom.predicate), "p")

    def test_parse_multiple_facts(self):
        """Test parsing multiple facts."""
        result = self.parser.parse("p(a). q(b). r(c, d).")
        self.assertEqual(len(result["facts"]), 3)

    def test_parse_fact_with_variable(self):
        """Test that facts can't contain free variables (should still parse)."""
        result = self.parser.parse("p(X).")
        self.assertEqual(len(result["facts"]), 1)


class TestDlgpeParserRules(unittest.TestCase):
    """Test DLGPE rule parsing."""

    def setUp(self):
        self.parser = DlgpeParser.instance()

    def test_parse_simple_rule(self):
        """Test parsing a simple rule."""
        result = self.parser.parse("h(X) :- b(X).")
        self.assertEqual(len(result["rules"]), 1)

    def test_parse_rule_with_conjunction(self):
        """Test parsing a rule with conjunction in body."""
        result = self.parser.parse("h(X, Y) :- p(X), q(Y).")
        self.assertEqual(len(result["rules"]), 1)

    def test_parse_rule_with_disjunctive_head(self):
        """Test parsing a rule with disjunctive head."""
        result = self.parser.parse("p(X) | q(X) :- r(X).")
        self.assertEqual(len(result["rules"]), 1)
        rule = result["rules"][0]
        self.assertEqual(len(rule.head), 2)

    def test_parse_rule_with_label(self):
        """Test parsing a rule with a label."""
        result = self.parser.parse("[myRule] h(X) :- b(X).")
        self.assertEqual(len(result["rules"]), 1)
        rule = result["rules"][0]
        self.assertIsNotNone(rule.label)


class TestDlgpeParserQueries(unittest.TestCase):
    """Test DLGPE query parsing."""

    def setUp(self):
        self.parser = DlgpeParser.instance()

    def test_parse_simple_query(self):
        """Test parsing a simple query."""
        result = self.parser.parse("?(X) :- p(X).")
        self.assertEqual(len(result["queries"]), 1)

    def test_parse_boolean_query(self):
        """Test parsing a boolean query (no answer variables)."""
        result = self.parser.parse("?() :- p(a).")
        self.assertEqual(len(result["queries"]), 1)

    def test_parse_query_with_star(self):
        """Test parsing a query with * for all variables."""
        result = self.parser.parse("?(*) :- p(X, Y).")
        self.assertEqual(len(result["queries"]), 1)


class TestDlgpeParserConstraints(unittest.TestCase):
    """Test DLGPE constraint parsing."""

    def setUp(self):
        self.parser = DlgpeParser.instance()

    def test_parse_simple_constraint(self):
        """Test parsing a simple constraint."""
        result = self.parser.parse("! :- p(X), q(X).")
        self.assertEqual(len(result["constraints"]), 1)


class TestDlgpeParserNegation(unittest.TestCase):
    """Test DLGPE negation parsing."""

    def setUp(self):
        self.parser = DlgpeParser.instance()

    def test_parse_negated_atom(self):
        """Test parsing a rule with negated atom."""
        result = self.parser.parse("h(X) :- p(X), not q(X).")
        self.assertEqual(len(result["rules"]), 1)

    def test_parse_negated_formula(self):
        """Test parsing a rule with negated formula."""
        result = self.parser.parse("h(X) :- not (p(X), q(X)).")
        self.assertEqual(len(result["rules"]), 1)


class TestDlgpeParserDisjunction(unittest.TestCase):
    """Test DLGPE disjunction parsing."""

    def setUp(self):
        self.parser = DlgpeParser.instance()

    def test_parse_body_disjunction(self):
        """Test parsing a rule with disjunction in body."""
        result = self.parser.parse("h(X) :- p(X) | q(X).")
        self.assertEqual(len(result["rules"]), 1)

    def test_parse_complex_disjunction(self):
        """Test parsing a rule with complex disjunction."""
        result = self.parser.parse("h(X) :- (p(X), r(X)) | (q(X), s(X)).")
        self.assertEqual(len(result["rules"]), 1)


class TestDlgpeParserDirectives(unittest.TestCase):
    """Test DLGPE directive parsing."""

    def setUp(self):
        self.parser = DlgpeParser.instance()

    def test_parse_base_directive(self):
        """Test parsing @base directive."""
        result = self.parser.parse("@base <http://example.org/>. p(a).")
        self.assertEqual(result["header"]["base"], "http://example.org/")

    def test_parse_prefix_directive(self):
        """Test parsing @prefix directive."""
        result = self.parser.parse("@prefix ex: <http://example.org/>. p(a).")
        self.assertIn("ex", result["header"]["prefixes"])

    def test_parse_una_directive(self):
        """Test parsing @una directive."""
        result = self.parser.parse("@una p(a).")
        self.assertTrue(result["header"]["una"])


class TestDlgpeParserSections(unittest.TestCase):
    """Test DLGPE section parsing."""

    def setUp(self):
        self.parser = DlgpeParser.instance()

    def test_parse_facts_section(self):
        """Test parsing @facts section."""
        result = self.parser.parse("@facts p(a). q(b).")
        self.assertEqual(len(result["facts"]), 2)

    def test_parse_rules_section(self):
        """Test parsing @rules section."""
        result = self.parser.parse("@rules h(X) :- b(X). g(X) :- f(X).")
        self.assertEqual(len(result["rules"]), 2)

    def test_parse_mixed_sections(self):
        """Test parsing multiple sections."""
        result = self.parser.parse("""
            @facts
            p(a).
            q(b).

            @rules
            h(X) :- p(X).

            @queries
            ?(X) :- h(X).
        """)
        self.assertEqual(len(result["facts"]), 2)
        self.assertEqual(len(result["rules"]), 1)
        self.assertEqual(len(result["queries"]), 1)


class TestDlgpeParserUnsupportedFeatures(unittest.TestCase):
    """Test that unsupported features raise appropriate errors."""

    def setUp(self):
        self.parser = DlgpeParser.instance()

    def test_import_directive_raises_error(self):
        """Test that @import raises an error."""
        with self.assertRaises(DlgpeUnsupportedFeatureError) as ctx:
            self.parser.parse("@import <file.dlgpe>.")
        self.assertIn("@import", str(ctx.exception))

    def test_computed_directive_is_supported(self):
        """Test that @computed is parsed into the header."""
        result = self.parser.parse("@computed ig: <http://example.org/functions#>.")
        header = result.get("header", {})
        self.assertIn("computed", header)
        self.assertEqual(header["computed"].get("ig"), "http://example.org/functions#")

    def test_view_directive_raises_error(self):
        """Test that @view raises an error."""
        with self.assertRaises(DlgpeUnsupportedFeatureError) as ctx:
            self.parser.parse("@view ex: <http://example.org/>.")
        self.assertIn("@view", str(ctx.exception))

    def test_patterns_directive_raises_error(self):
        """Test that @patterns raises an error."""
        with self.assertRaises(DlgpeUnsupportedFeatureError) as ctx:
            self.parser.parse("@patterns p(a).")
        self.assertIn("@patterns", str(ctx.exception))


class TestDlgpeParserComments(unittest.TestCase):
    """Test DLGPE comment handling."""

    def setUp(self):
        self.parser = DlgpeParser.instance()

    def test_line_comment(self):
        """Test that line comments are ignored."""
        result = self.parser.parse("""
            % This is a comment
            p(a).  % Another comment
        """)
        self.assertEqual(len(result["facts"]), 1)


class TestDlgpeParserLiterals(unittest.TestCase):
    """Test DLGPE literal parsing."""

    def setUp(self):
        self.parser = DlgpeParser.instance()

    def test_integer_literal(self):
        """Test parsing integer literals."""
        result = self.parser.parse("p(42).")
        self.assertEqual(len(result["facts"]), 1)

    def test_string_literal(self):
        """Test parsing string literals."""
        result = self.parser.parse('p("hello").')
        self.assertEqual(len(result["facts"]), 1)

    def test_boolean_literal(self):
        """Test parsing boolean literals."""
        result = self.parser.parse("p(true). q(false).")
        self.assertEqual(len(result["facts"]), 2)


class TestDlgpeParserEquality(unittest.TestCase):
    """Test DLGPE equality atom parsing."""

    def setUp(self):
        self.parser = DlgpeParser.instance()

    def test_equality_in_body(self):
        """Test parsing equality in rule body."""
        result = self.parser.parse("h(X) :- p(X, Y), X = Y.")
        self.assertEqual(len(result["rules"]), 1)


class TestDlgpeParserFunctionalTerms(unittest.TestCase):
    """Test parsing functional terms."""

    def setUp(self):
        self.parser = DlgpeParser.instance()

    def test_function_term_in_fact(self):
        result = self.parser.parse("p(f(a)).")
        atom = result["facts"][0]
        self.assertIsInstance(atom.terms[0], FunctionTerm)


class TestDlgpeParserComparison(unittest.TestCase):
    """Test DLGPE comparison operator parsing."""

    def setUp(self):
        self.parser = DlgpeParser.instance()

    def test_comparison_in_body(self):
        result = self.parser.parse("h(X) :- p(X), X < 3.")
        self.assertEqual(len(result["rules"]), 1)
        rule = result["rules"][0]
        atoms = list(rule.body.atoms)
        self.assertTrue(any(str(atom) == "X < 3" for atom in atoms))

    def test_comparison_sources(self):
        result = self.parser.parse("?(X) :- X != 1.")
        self.assertIn("sources", result)
        self.assertEqual(len(result["sources"]), 1)


if __name__ == "__main__":
    unittest.main()
