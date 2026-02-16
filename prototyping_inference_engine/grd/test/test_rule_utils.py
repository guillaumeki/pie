import unittest
from typing import cast

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.formula.conjunction_formula import (
    ConjunctionFormula,
)
from prototyping_inference_engine.api.formula.disjunction_formula import (
    DisjunctionFormula,
)
from prototyping_inference_engine.api.formula.existential_formula import (
    ExistentialFormula,
)
from prototyping_inference_engine.api.formula.formula import Formula
from prototyping_inference_engine.api.formula.negation_formula import NegationFormula
from prototyping_inference_engine.api.formula.universal_formula import UniversalFormula
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.grd import rule_utils


class TestRuleUtils(unittest.TestCase):
    def setUp(self) -> None:
        self.p = Predicate("p", 1)
        self.q = Predicate("q", 1)
        self.r = Predicate("r", 1)
        self.s = Predicate("s", 2)
        self.x = Variable("X")
        self.y = Variable("Y")

    def test_split_head_disjuncts(self) -> None:
        head = DisjunctionFormula(Atom(self.p, self.x), Atom(self.q, self.x))
        body = Atom(self.r, self.x)
        rule = Rule(body, head)
        disjuncts = rule_utils.split_head_disjuncts(rule)
        self.assertEqual(2, len(disjuncts))
        self.assertIn(Atom(self.p, self.x), disjuncts)
        self.assertIn(Atom(self.q, self.x), disjuncts)

    def test_extract_positive_and_negative_body(self) -> None:
        body = ConjunctionFormula(
            Atom(self.p, self.x), NegationFormula(Atom(self.q, self.x))
        )
        rule = Rule(body, Atom(self.r, self.x))
        positive = rule_utils.extract_positive_body(rule)
        negative = rule_utils.extract_negative_body(rule)
        self.assertEqual({Atom(self.p, self.x)}, set(positive.atoms))
        self.assertEqual({Atom(self.q, self.x)}, set(negative.atoms))

    def test_extract_positive_body_rejects_disjunction(self) -> None:
        body = DisjunctionFormula(Atom(self.p, self.x), Atom(self.q, self.x))
        rule = Rule(body, Atom(self.r, self.x))
        with self.assertRaises(ValueError):
            rule_utils.extract_positive_body(rule)

    def test_extract_head_conjunction_rejects_negation(self) -> None:
        with self.assertRaises(ValueError):
            rule_utils.extract_head_conjunction(NegationFormula(Atom(self.p, self.x)))

    def test_ensure_safe_negation_raises_on_unbound_variable(self) -> None:
        body = ConjunctionFormula(
            Atom(self.p, self.x), NegationFormula(Atom(self.q, self.y))
        )
        head = Atom(self.s, self.x, self.y)
        rule = Rule(body, head)
        with self.assertRaises(ValueError):
            rule_utils.ensure_safe_negation(rule)

    def test_extract_conjunctive_atoms_allows_quantifiers(self) -> None:
        inner = ConjunctionFormula(Atom(self.p, self.x), Atom(self.q, self.y))
        formula = ExistentialFormula(self.y, UniversalFormula(self.x, inner))
        atoms = rule_utils._extract_conjunctive_atoms(formula, allow_negation=False)
        self.assertEqual({Atom(self.p, self.x), Atom(self.q, self.y)}, set(atoms))

    def test_extract_conjunctive_atoms_with_negation(self) -> None:
        formula = NegationFormula(Atom(self.p, self.x))
        atoms = rule_utils._extract_conjunctive_atoms(formula, allow_negation=True)
        self.assertEqual({Atom(self.p, self.x)}, set(atoms))

    def test_extract_negative_atoms_empty_on_atoms(self) -> None:
        atoms = rule_utils._extract_negative_atoms(Atom(self.p, self.x))
        self.assertEqual(set(), set(atoms))

    def test_extract_positive_atoms_on_quantified(self) -> None:
        formula = ExistentialFormula(self.x, Atom(self.p, self.x))
        atoms = rule_utils._extract_positive_atoms(formula)
        self.assertEqual({Atom(self.p, self.x)}, set(atoms))

    def test_extract_conjunctive_atoms_rejects_disjunction(self) -> None:
        formula = DisjunctionFormula(Atom(self.p, self.x), Atom(self.q, self.x))
        with self.assertRaises(ValueError):
            rule_utils._extract_conjunctive_atoms(formula, allow_negation=False)

    def test_extract_negative_atoms_with_binary_formula(self) -> None:
        neg = NegationFormula(Atom(self.q, self.x))
        formula = ConjunctionFormula(Atom(self.p, self.x), neg)
        atoms = rule_utils._extract_negative_atoms(formula)
        self.assertEqual({Atom(self.q, self.x)}, set(atoms))

    def test_extract_positive_atoms_with_binary_formula(self) -> None:
        formula = ConjunctionFormula(Atom(self.p, self.x), Atom(self.q, self.x))
        atoms = rule_utils._extract_positive_atoms(formula)
        self.assertEqual({Atom(self.p, self.x), Atom(self.q, self.x)}, set(atoms))

    def test_extract_head_conjunction_collects_variables(self) -> None:
        formula = ConjunctionFormula(Atom(self.p, self.x), Atom(self.q, self.y))
        cq = rule_utils.extract_head_conjunction(formula)
        self.assertEqual({self.x, self.y}, set(cq.variables))

    def test_extract_positive_atoms_rejects_unsupported(self) -> None:
        class Unsupported:
            pass

        with self.assertRaises(ValueError):
            rule_utils._extract_positive_atoms(Unsupported())  # type: ignore[arg-type]

    def test_extract_negative_atoms_rejects_unsupported(self) -> None:
        class Unsupported:
            pass

        with self.assertRaises(ValueError):
            rule_utils._extract_negative_atoms(Unsupported())  # type: ignore[arg-type]

    def test_extract_conjunctive_atoms_rejects_unsupported(self) -> None:
        class Unsupported:
            pass

        with self.assertRaises(ValueError):
            rule_utils._extract_conjunctive_atoms(
                cast(Formula, Unsupported()), allow_negation=False
            )

    def test_extract_head_conjunction_with_constants(self) -> None:
        const = Constant("a")
        formula = ConjunctionFormula(Atom(self.p, const), Atom(self.q, self.x))
        cq = rule_utils.extract_head_conjunction(formula)
        self.assertEqual({const}, cq.constants)


if __name__ == "__main__":
    unittest.main()
