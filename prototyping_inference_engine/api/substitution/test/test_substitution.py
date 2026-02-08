from unittest import TestCase

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.substitution.substitution import Substitution


class TestSubstitution(TestCase):
    def test_empty_substitution(self):
        """Test creating empty substitution."""
        sub = Substitution()
        self.assertEqual(len(sub), 0)

    def test_creation_from_dict(self):
        """Test creating substitution from dict."""
        x = Variable("X")
        a = Constant("a")
        sub = Substitution({x: a})
        self.assertEqual(sub[x], a)

    def test_creation_from_substitution(self):
        """Test creating substitution from another substitution."""
        x = Variable("X")
        a = Constant("a")
        sub1 = Substitution({x: a})
        sub2 = Substitution(sub1)
        self.assertEqual(sub2[x], a)

    def test_domain_property(self):
        """Test domain property returns keys."""
        x = Variable("X")
        y = Variable("Y")
        sub = Substitution({x: Constant("a"), y: Constant("b")})
        domain = set(sub.domain)
        self.assertEqual(domain, {x, y})

    def test_image_property(self):
        """Test image property returns values."""
        x = Variable("X")
        y = Variable("Y")
        a = Constant("a")
        b = Constant("b")
        sub = Substitution({x: a, y: b})
        image = set(sub.image)
        self.assertEqual(image, {a, b})

    def test_graph_property(self):
        """Test graph property returns items."""
        x = Variable("X")
        a = Constant("a")
        sub = Substitution({x: a})
        graph = list(sub.graph)
        self.assertEqual(graph, [(x, a)])

    def test_apply_to_variable(self):
        """Test applying substitution to variable."""
        x = Variable("X")
        a = Constant("a")
        sub = Substitution({x: a})
        result = sub.apply(x)
        self.assertEqual(result, a)

    def test_apply_to_unmapped_variable(self):
        """Test applying substitution to unmapped variable returns itself."""
        x = Variable("X")
        y = Variable("Y")
        a = Constant("a")
        sub = Substitution({x: a})
        result = sub.apply(y)
        self.assertEqual(result, y)

    def test_apply_to_constant(self):
        """Test applying substitution to constant returns itself."""
        x = Variable("X")
        a = Constant("a")
        b = Constant("b")
        sub = Substitution({x: a})
        result = sub.apply(b)
        self.assertEqual(result, b)

    def test_apply_to_atom(self):
        """Test applying substitution to atom."""
        p = Predicate("p", 2)
        x = Variable("X")
        y = Variable("Y")
        atom = Atom(p, x, y)
        sub = Substitution({x: Constant("a"), y: Constant("b")})
        result = sub.apply(atom)
        self.assertEqual(result.terms, (Constant("a"), Constant("b")))

    def test_apply_to_tuple(self):
        """Test applying substitution to tuple of substitutables."""
        x = Variable("X")
        y = Variable("Y")
        a = Constant("a")
        b = Constant("b")
        sub = Substitution({x: a, y: b})
        result = sub.apply((x, y))
        self.assertEqual(result, (a, b))

    def test_apply_to_list(self):
        """Test applying substitution to list of substitutables."""
        x = Variable("X")
        a = Constant("a")
        sub = Substitution({x: a})
        result = sub.apply([x])
        self.assertEqual(result, [a])

    def test_compose_basic(self):
        """Test basic composition of substitutions."""
        x = Variable("X")
        y = Variable("Y")
        a = Constant("a")
        sub1 = Substitution({y: a})
        sub2 = Substitution({x: y})
        composed = sub1.compose(sub2)
        # sub1 . sub2 means: apply sub2, then apply sub1
        # x -> y in sub2, then y -> a in sub1, so x -> a
        self.assertEqual(composed[x], a)

    def test_compose_removes_identity(self):
        """Test that composition removes identity mappings."""
        x = Variable("X")
        sub1 = Substitution({x: x})
        sub2 = Substitution()
        composed = sub1.compose(sub2)
        self.assertNotIn(x, composed)

    def test_compose_preserves_non_overlapping(self):
        """Test that composition preserves non-overlapping mappings."""
        x = Variable("X")
        y = Variable("Y")
        a = Constant("a")
        b = Constant("b")
        sub1 = Substitution({x: a})
        sub2 = Substitution({y: b})
        composed = sub1.compose(sub2)
        self.assertEqual(composed[x], a)
        self.assertEqual(composed[y], b)

    def test_aggregate_basic(self):
        """Test aggregating (merging) two substitutions."""
        x = Variable("X")
        y = Variable("Y")
        a = Constant("a")
        b = Constant("b")
        sub1 = Substitution({x: a})
        sub2 = Substitution({y: b})
        aggregated = sub1.aggregate(sub2)
        self.assertEqual(aggregated[x], a)
        self.assertEqual(aggregated[y], b)

    def test_aggregate_second_overrides(self):
        """Test that aggregation gives priority to second substitution on conflict."""
        x = Variable("X")
        a = Constant("a")
        b = Constant("b")
        sub1 = Substitution({x: a})
        sub2 = Substitution({x: b})
        aggregated = sub1.aggregate(sub2)
        self.assertEqual(aggregated[x], b)

    def test_restrict_to(self):
        """Test restricting substitution to subset of variables."""
        x = Variable("X")
        y = Variable("Y")
        z = Variable("Z")
        a = Constant("a")
        b = Constant("b")
        c = Constant("c")
        sub = Substitution({x: a, y: b, z: c})
        restricted = sub.restrict_to([x, z])
        self.assertEqual(restricted[x], a)
        self.assertEqual(restricted[z], c)
        self.assertNotIn(y, restricted)

    def test_restrict_to_excludes_identity(self):
        """Test that restrict_to excludes identity mappings."""
        x = Variable("X")
        y = Variable("Y")
        a = Constant("a")
        sub = Substitution({x: a, y: y})
        restricted = sub.restrict_to([x, y])
        self.assertIn(x, restricted)
        self.assertNotIn(y, restricted)

    def test_call_with_substitution_composes(self):
        """Test that calling substitution with substitution composes."""
        x = Variable("X")
        y = Variable("Y")
        a = Constant("a")
        sub1 = Substitution({y: a})
        sub2 = Substitution({x: y})
        result = sub1(sub2)
        self.assertEqual(result[x], a)

    def test_call_with_term_applies(self):
        """Test that calling substitution with term applies."""
        x = Variable("X")
        a = Constant("a")
        sub = Substitution({x: a})
        result = sub(x)
        self.assertEqual(result, a)

    def test_str(self):
        """Test string representation."""
        x = Variable("X")
        a = Constant("a")
        sub = Substitution({x: a})
        self.assertEqual(sub[x], a)

    def test_repr(self):
        """Test repr representation."""
        sub = Substitution()
        self.assertEqual(len(sub), 0)

    def test_is_dict_subclass(self):
        """Test that Substitution is a dict subclass."""
        sub = Substitution()
        self.assertIsInstance(sub, dict)

    def test_apply_invalid_type_raises(self):
        """Test that applying to invalid type raises TypeError."""
        sub = Substitution()
        with self.assertRaises(TypeError):
            sub.apply(42)
