"""Additional forward-chaining tests to cover low-level branches."""

from __future__ import annotations

import io
import time
import unittest
from contextlib import redirect_stdout
from threading import Event
from typing import cast

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.data.datalog_delegable import DatalogDelegable
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import (
    MutableInMemoryFactBase,
)
from prototyping_inference_engine.api.formula.conjunction_formula import (
    ConjunctionFormula,
)
from prototyping_inference_engine.api.formula.existential_formula import (
    ExistentialFormula,
)
from prototyping_inference_engine.api.kb.rule_base import RuleBase
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.forward_chaining.chase.chase import Chase
from prototyping_inference_engine.forward_chaining.chase.chase_builder import (
    ChaseBuilder,
)
from prototyping_inference_engine.forward_chaining.chase.data.chasable_data_impl import (
    ChasableDataImpl,
)
from prototyping_inference_engine.forward_chaining.chase.halting_condition.external_interruption import (
    ExternalInterruption,
)
from prototyping_inference_engine.forward_chaining.chase.halting_condition.limit_atoms import (
    LimitAtoms,
)
from prototyping_inference_engine.forward_chaining.chase.halting_condition.timeout import (
    Timeout,
)
from prototyping_inference_engine.forward_chaining.chase.lineage.federated_lineage_tracker import (
    get_ancestors_of,
)
from prototyping_inference_engine.forward_chaining.chase.lineage.lineage_tracker_impl import (
    LineageTrackerImpl,
)
from prototyping_inference_engine.forward_chaining.chase.lineage.no_lineage_tracker import (
    NoLineageTracker,
)
from prototyping_inference_engine.forward_chaining.chase.metachase.stratified.stratified_chase_builder import (
    StratifiedChaseBuilder,
)
from prototyping_inference_engine.forward_chaining.chase.rule_application_step_result import (
    RuleApplicationStepResult,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.source_delegated_datalog_rule_applier import (
    SourceDelegatedDatalogRuleApplier,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_computer.semi_naive_computer import (
    SemiNaiveComputer,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_computer.two_steps_computer import (
    TwoStepsComputer,
)
from prototyping_inference_engine.forward_chaining.chase.treatment.debug import Debug
from prototyping_inference_engine.forward_chaining.chase.treatment.predicate_filter_end_treatment import (
    PredicateFilterEndTreatment,
)


class _DummyChaseForComputer:
    def __init__(self, rb: RuleBase, created_atoms):
        self._rb = rb
        if created_atoms is None:
            self._last = RuleApplicationStepResult.initial()
        else:
            self._last = RuleApplicationStepResult.from_created(set(), created_atoms)

    def get_rule_base(self) -> RuleBase:
        return self._rb

    def get_last_step_results(self) -> RuleApplicationStepResult:
        return self._last


class _DelegableFactBase(MutableInMemoryFactBase, DatalogDelegable):
    def __init__(self):
        super().__init__()
        self.delegated_count = 0

    def delegate_rules(self, rules):
        rules = list(rules)
        self.delegated_count += len(rules)
        return bool(rules)

    def delegate_query(self, query, count_answers_only=False):
        return iter(())


class _HashableSubstitutionToken:
    def __hash__(self) -> int:
        return 1


class TestHaltingAndTreatmentsCoverage(unittest.TestCase):
    def test_halting_conditions_and_debug_and_predicate_filter(self) -> None:
        x = Variable("X")
        a = Constant("a")
        b = Constant("b")

        p = Predicate("p", 2)
        q = Predicate("q", 2)
        r = Predicate("r", 2)

        fb = MutableInMemoryFactBase([Atom(p, a, b)])
        rb = RuleBase({Rule(Atom(p, x, b), Atom(q, x, b), "to_q")})
        chase = ChaseBuilder.default_builder(fb, rb).build().get()

        limit_atoms = LimitAtoms(10)
        limit_atoms.init(chase)
        self.assertTrue(limit_atoms.check())

        timeout = Timeout(1)
        timeout.init(chase)
        self.assertTrue(timeout.check())
        time.sleep(0.005)
        self.assertFalse(timeout.check())

        stop_event = Event()
        external = ExternalInterruption(stop_event)
        external.init(chase)
        self.assertTrue(external.check())
        stop_event.set()
        self.assertFalse(external.check())

        debug = Debug()
        debug.init(chase)
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            debug.apply()
        self.assertGreater(len(buffer.getvalue()), 0)

        fb.add(Atom(r, a, b))
        predicate_filter = PredicateFilterEndTreatment({0: {r}})
        predicate_filter.init(chase)
        self.assertIn(Atom(r, a, b), fb)
        predicate_filter.apply()
        self.assertNotIn(Atom(r, a, b), fb)


class TestLineageCoverage(unittest.TestCase):
    def test_lineage_trackers_and_federation(self) -> None:
        a = Constant("a")
        b = Constant("b")
        c = Constant("c")
        p = Predicate("p", 1)
        q = Predicate("q", 1)

        body_atom = Atom(p, a)
        head_atom = Atom(q, b)
        second_head = Atom(q, c)
        rule = Rule(body_atom, head_atom, "lineage_rule")

        tracker = LineageTrackerImpl()
        subst = cast(Substitution, _HashableSubstitutionToken())
        added = tracker.track({body_atom}, {head_atom}, rule, subst)
        self.assertTrue(added)
        self.assertTrue(tracker.is_prime(body_atom))
        self.assertTrue(tracker.is_non_prime(head_atom))
        self.assertEqual({body_atom}, tracker.get_ancestors_of(head_atom))
        self.assertEqual({body_atom}, tracker.get_prime_ancestors_of(head_atom))
        self.assertIn(rule, tracker.get_rule_instances_yielding(head_atom))

        tracker.track({head_atom}, {second_head}, rule, subst)
        self.assertEqual({body_atom}, tracker.get_prime_ancestors_of(second_head))

        no_tracker = NoLineageTracker()
        self.assertEqual(set(), no_tracker.get_ancestors_of(head_atom))
        self.assertEqual(set(), no_tracker.get_prime_ancestors_of(head_atom))
        self.assertFalse(no_tracker.track({body_atom}, {head_atom}, rule, subst))
        self.assertEqual({}, no_tracker.get_rule_instances_yielding(head_atom))
        self.assertFalse(no_tracker.is_prime(head_atom))
        self.assertFalse(no_tracker.is_non_prime(head_atom))

        federated = get_ancestors_of(second_head, tracker, no_tracker)
        self.assertEqual({body_atom}, federated)


class TestComputersCoverage(unittest.TestCase):
    def test_semi_naive_and_two_steps_branches(self) -> None:
        x = Variable("X")
        y = Variable("Y")
        a = Constant("a")
        b = Constant("b")
        c = Constant("c")

        p = Predicate("p", 1)
        q = Predicate("q", 1)
        r = Predicate("r", 2)

        rule = Rule(Atom(p, x), Atom(q, x), "p_to_q")
        rb = RuleBase({rule})

        data = ChasableDataImpl(
            MutableInMemoryFactBase(
                [Atom(p, a), Atom(q, a), Atom(q, b), Atom(r, a, c), Atom(r, b, c)]
            )
        )

        body_idb = FOQuery(Atom(q, x), [x])
        body_no_idb = FOQuery(Atom(r, x, y), [x, y])
        body_two_atoms = FOQuery(ConjunctionFormula(Atom(q, x), Atom(r, x, y)), [x, y])

        semi = SemiNaiveComputer()
        # Branch: no chase -> fallback.
        self.assertGreater(len(list(semi.compute(body_idb, {rule}, data))), 0)

        # Branch: chase with no previous created facts -> fallback.
        semi.init(cast(Chase, _DummyChaseForComputer(rb, None)))
        self.assertGreater(len(list(semi.compute(body_idb, {rule}, data))), 0)

        # Branch: no IDB atoms in body -> fallback.
        semi.init(cast(Chase, _DummyChaseForComputer(rb, [Atom(q, b)])))
        self.assertEqual(2, len(list(semi.compute(body_no_idb, {rule}, data))))

        # Branch: full semi-naive path.
        semi_results = list(semi.compute(body_idb, {rule}, data))
        self.assertTrue(any(sub.get(x) == b for sub in semi_results))

        two_steps = TwoStepsComputer()
        # Branch: no chase -> fallback.
        self.assertGreater(len(list(two_steps.compute(body_idb, {rule}, data))), 0)

        # Branch: chase with no previous created facts -> fallback.
        two_steps.init(cast(Chase, _DummyChaseForComputer(rb, None)))
        self.assertGreater(len(list(two_steps.compute(body_idb, {rule}, data))), 0)

        # Branch: single-atom body with last-step facts.
        two_steps.init(cast(Chase, _DummyChaseForComputer(rb, [Atom(q, b)])))
        single_results = list(two_steps.compute(body_idb, {rule}, data))
        self.assertTrue(all(sub.get(x) == b for sub in single_results))

        # Branch: multi-atom body with merge path.
        multi_results = list(two_steps.compute(body_two_atoms, {rule}, data))
        self.assertTrue(any(sub.get(x) == b for sub in multi_results))


class TestStratifiedAndDelegationCoverage(unittest.TestCase):
    def test_source_delegated_applier_and_descriptions(self) -> None:
        x = Variable("X")
        y = Variable("Y")
        a = Constant("a")

        p = Predicate("p", 1)
        q = Predicate("q", 1)

        datalog_rule = Rule(Atom(p, x), Atom(q, x), "datalog")
        existential_rule = Rule(Atom(p, a), ExistentialFormula(y, Atom(q, y)), "exists")

        delegable_target = _DelegableFactBase()
        delegable_target.add(Atom(p, a))
        applier = SourceDelegatedDatalogRuleApplier()
        applier.init(
            ChaseBuilder.default_builder(delegable_target, RuleBase()).build().get()
        )
        result = applier.apply({datalog_rule}, ChasableDataImpl(delegable_target))
        self.assertIsNotNone(result.created_facts)
        if result.created_facts is None:
            self.fail("created_facts should be initialized for delegated datalog path")
        self.assertEqual(0, len(result.created_facts))
        self.assertEqual(1, delegable_target.delegated_count)
        self.assertGreater(len(applier.describe()), 0)
        self.assertGreater(len(applier.describe_json()), 0)

        result_with_exists = applier.apply(
            {datalog_rule, existential_rule}, ChasableDataImpl(delegable_target)
        )
        self.assertIsNotNone(result_with_exists.applied_rules)

    def test_stratified_builder_and_chase_paths(self) -> None:
        x = Variable("X")
        a = Constant("a")

        base = Predicate("base", 1)
        mid = Predicate("mid", 1)
        out = Predicate("out", 1)

        rb1 = RuleBase({Rule(Atom(base, x), Atom(mid, x), "to_mid")})
        rb2 = RuleBase({Rule(Atom(mid, x), Atom(out, x), "to_out")})

        fb = MutableInMemoryFactBase([Atom(base, a)])
        chasable_data = ChasableDataImpl(fb)

        stratified = (
            StratifiedChaseBuilder()
            .set_chase_builder(ChaseBuilder())
            .set_chasable_data(chasable_data)
            .set_rule_base(RuleBase(set(rb1.rules | rb2.rules)))
            .set_strata([rb1, rb2])
            .set_final_predicates([out])
            .add_halting_conditions()
            .add_global_pretreatments()
            .add_step_pretreatments()
            .add_global_end_treatments()
            .add_end_of_step_treatments()
            .debug()
            .build()
            .get()
        )
        stratified.execute()

        self.assertIn(Atom(out, a), fb)
        self.assertGreater(len(stratified.describe()), 0)
        self.assertGreater(len(stratified.get_description().to_json()), 0)
        self.assertGreater(len(stratified.get_description().to_pretty_string()), 0)

        # Build path coverage for optional return None.
        none_build = StratifiedChaseBuilder().build().or_else_none()
        self.assertIsNone(none_build)

        # Ensure alternate stratification switches are exercised.
        default_build = (
            StratifiedChaseBuilder.default_builder(chasable_data, rb1)
            .use_stratification()
            .build()
            .get()
        )
        self.assertIsNotNone(default_build)

        single_eval = (
            StratifiedChaseBuilder.default_builder(chasable_data, rb1)
            .use_single_evaluation_stratification()
            .build()
            .get()
        )
        self.assertIsNotNone(single_eval)

        pseudo_minimal = (
            StratifiedChaseBuilder.default_builder(chasable_data, rb1)
            .use_pseudo_minimal_stratification()
            .build()
            .get()
        )
        self.assertIsNotNone(pseudo_minimal)

        self.assertEqual(2, stratified.get_step_count())
        self.assertIsNotNone(stratified.get_last_step_results())
        self.assertIsNotNone(stratified.get_rule_scheduler())
        self.assertEqual(chasable_data, stratified.get_chasable_data())
        with self.assertRaises(NotImplementedError):
            stratified.set_rule_base(rb1)


if __name__ == "__main__":
    unittest.main()
