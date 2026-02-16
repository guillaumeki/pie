import unittest
from typing import Dict, List, Set, Tuple

from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.grd.dependency_checker import (
    ProductivityChecker,
    RestrictedProductivityChecker,
)
from prototyping_inference_engine.grd.grd import GRD
from prototyping_inference_engine.grd.stratification import (
    BySccStratification,
    MinimalStratification,
)
from prototyping_inference_engine.grd.test import test_data as data


class TestIntegraalGrdPort(unittest.TestCase):
    def test_productivity_grd(self) -> None:
        cases: List[Tuple[Set[Rule], Dict[Rule, Set[Rule]]]] = [
            (set(), {}),
            ({data.Rpx_qx}, {data.Rpx_qx: set()}),
            ({data.Rpx_py}, {data.Rpx_py: set()}),
            (
                {data.Rpx_qx, data.Rqx_rxy},
                {data.Rpx_qx: {data.Rqx_rxy}, data.Rqx_rxy: set()},
            ),
            (
                {data.Rpx_py, data.Rpx_qx, data.Rqx_rxy},
                {
                    data.Rpx_qx: {data.Rqx_rxy},
                    data.Rpx_py: set(),
                    data.Rqx_rxy: set(),
                },
            ),
            (
                {data.Rpxy_qzy, data.Rquv_pwv},
                {
                    data.Rpxy_qzy: set(),
                    data.Rquv_pwv: set(),
                },
            ),
            (
                {data.Rpxy_pyz, data.Rpxy_pyy},
                {
                    data.Rpxy_pyz: set(),
                    data.Rpxy_pyy: set(),
                },
            ),
        ]

        for rules, expected in cases:
            with self.subTest(rules={r.label for r in rules}):
                grd = GRD(rules, [ProductivityChecker()])
                for rule, expected_targets in expected.items():
                    computed = grd.get_triggered_rules(rule)
                    self.assertEqual(expected_targets, computed)

    def test_restricted_productivity_grd(self) -> None:
        cases: List[Tuple[Set[Rule], Dict[Rule, Set[Rule]]]] = [
            (set(), {}),
            ({data.Rpx_qx}, {data.Rpx_qx: set()}),
            ({data.Rpx_py}, {data.Rpx_py: set()}),
            (
                {data.Rpx_qx, data.Rqx_rxy},
                {data.Rpx_qx: {data.Rqx_rxy}, data.Rqx_rxy: set()},
            ),
            (
                {data.Rpx_py, data.Rpx_qx, data.Rqx_rxy},
                {
                    data.Rpx_qx: {data.Rqx_rxy},
                    data.Rpx_py: set(),
                    data.Rqx_rxy: set(),
                },
            ),
            (
                {data.Rpxy_qzy, data.Rquv_pwv},
                {data.Rpxy_qzy: set(), data.Rquv_pwv: set()},
            ),
            (
                {data.Rpxy_pyz, data.Rpxy_pyy},
                {
                    data.Rpxy_pyz: set(),
                    data.Rpxy_pyy: set(),
                },
            ),
        ]

        for rules, expected in cases:
            with self.subTest(rules={r.label for r in rules}):
                grd = GRD(rules, [RestrictedProductivityChecker()])
                for rule, expected_targets in expected.items():
                    computed = grd.get_triggered_rules(rule)
                    self.assertEqual(expected_targets, computed)

    def test_negation_grd(self) -> None:
        cases: List[Tuple[Set[Rule], Dict[Rule, Set[Rule]], Dict[Rule, Set[Rule]]]] = [
            (set(), {}, {}),
            (
                {data.Rsx_qx, data.Rpxnotqx_rx},
                {data.Rsx_qx: set(), data.Rpxnotqx_rx: set()},
                {data.Rsx_qx: {data.Rpxnotqx_rx}, data.Rpxnotqx_rx: set()},
            ),
            (
                {data.Rpx_qx, data.Rpxnotqx_rx},
                {data.Rpx_qx: set(), data.Rpxnotqx_rx: set()},
                {data.Rpx_qx: {data.Rpxnotqx_rx}, data.Rpxnotqx_rx: set()},
            ),
            (
                {data.Rpxnotqx_qx},
                {data.Rpxnotqx_qx: set()},
                {data.Rpxnotqx_qx: {data.Rpxnotqx_qx}},
            ),
            (
                {data.Rpxnotrx_qx, data.Rpxnotqx_rx},
                {data.Rpxnotrx_qx: set(), data.Rpxnotqx_rx: set()},
                {
                    data.Rpxnotrx_qx: {data.Rpxnotqx_rx},
                    data.Rpxnotqx_rx: {data.Rpxnotrx_qx},
                },
            ),
            (
                {data.Rpxynotqxy_rxy, data.Rpxxnotrxx_qxx},
                {data.Rpxynotqxy_rxy: set(), data.Rpxxnotrxx_qxx: set()},
                {
                    data.Rpxynotqxy_rxy: {data.Rpxxnotrxx_qxx},
                    data.Rpxxnotrxx_qxx: {data.Rpxynotqxy_rxy},
                },
            ),
            (
                {data.Rpxy_qxy, data.Rqxxnotpxx_rx},
                {data.Rpxy_qxy: set(), data.Rqxxnotpxx_rx: set()},
                {data.Rpxy_qxy: set(), data.Rqxxnotpxx_rx: set()},
            ),
            (
                {data.Rpxynotqxy_rxy, data.Rqxxnotrxx_sx},
                {data.Rpxynotqxy_rxy: set(), data.Rqxxnotrxx_sx: set()},
                {data.Rpxynotqxy_rxy: {data.Rqxxnotrxx_sx}, data.Rqxxnotrxx_sx: set()},
            ),
        ]

        for rules, expected_pos, expected_neg in cases:
            with self.subTest(rules={r.label for r in rules}):
                grd = GRD(rules, [RestrictedProductivityChecker()])
                for rule, expected_targets in expected_pos.items():
                    computed = grd.get_triggered_rules(rule)
                    self.assertEqual(expected_targets, computed)
                for rule, expected_targets in expected_neg.items():
                    computed = grd.get_prevented_rules(rule)
                    self.assertEqual(expected_targets, computed)

    def test_stratification(self) -> None:
        cases: List[Tuple[Set[Rule], bool, List[Set[Rule]]]] = [
            (set(), True, []),
            ({data.Rpx_qx}, True, [{data.Rpx_qx}]),
            (
                {data.Rsx_qx, data.Rpxnotqx_rx},
                True,
                [{data.Rsx_qx}, {data.Rpxnotqx_rx}],
            ),
            (
                {data.Rpxnotqx_rx, data.Rpxnotrx_sx, data.Rpxnotsx_tx},
                True,
                [{data.Rpxnotqx_rx}, {data.Rpxnotrx_sx}, {data.Rpxnotsx_tx}],
            ),
            (
                {data.Rpxnotsx_tx, data.Rpxnotqx_rx, data.Rpxnotrx_sx},
                True,
                [{data.Rpxnotqx_rx}, {data.Rpxnotrx_sx}, {data.Rpxnotsx_tx}],
            ),
            ({data.Rpxnotqx_qx}, False, []),
            ({data.Rpxnotqx_rx, data.Rpxnotrx_qx}, False, []),
            (
                {data.Rpx_qx, data.Rqx_rx, data.Rrx_sx, data.Rtxnotsx_pxx},
                True,
                [
                    {data.Rpx_qx},
                    {data.Rqx_rx},
                    {data.Rrx_sx},
                    {data.Rtxnotsx_pxx},
                ],
            ),
        ]

        for rules, stratifiable, expected_strata in cases:
            with self.subTest(rules={r.label for r in rules}):
                grd = GRD(rules, [RestrictedProductivityChecker()])
                self.assertEqual(stratifiable, grd.is_stratifiable())
                if stratifiable:
                    strata = grd.stratify(BySccStratification())
                    self.assertIsNotNone(strata)
                    computed = strata or []
                    self.assertEqual(len(expected_strata), len(computed))
                    for expected, computed_strate in zip(expected_strata, computed):
                        self.assertEqual(expected, computed_strate.rules)

    def test_pseudo_minimal_stratification(self) -> None:
        cases: List[Tuple[Set[Rule], bool, List[Set[Rule]]]] = [
            (set(), True, []),
            ({data.Rpx_qx}, True, [{data.Rpx_qx}]),
            (
                {data.Rsx_qx, data.Rpxnotqx_rx},
                True,
                [{data.Rsx_qx}, {data.Rpxnotqx_rx}],
            ),
            (
                {data.Rpxnotqx_rx, data.Rpxnotrx_sx, data.Rpxnotsx_tx},
                True,
                [{data.Rpxnotqx_rx}, {data.Rpxnotrx_sx}, {data.Rpxnotsx_tx}],
            ),
            (
                {data.Rpxnotsx_tx, data.Rpxnotqx_rx, data.Rpxnotrx_sx},
                True,
                [{data.Rpxnotqx_rx}, {data.Rpxnotrx_sx}, {data.Rpxnotsx_tx}],
            ),
            ({data.Rpxnotqx_qx}, False, []),
            ({data.Rpxnotqx_rx, data.Rpxnotrx_qx}, False, []),
            (
                {data.Rpx_qx, data.Rqx_rx, data.Rrx_sx, data.Rtxnotsx_pxx},
                True,
                [
                    {data.Rpx_qx, data.Rqx_rx, data.Rrx_sx},
                    {data.Rtxnotsx_pxx},
                ],
            ),
            (
                {
                    data.Rpx_qx,
                    data.Rqx_rx,
                    data.Rrx_sx,
                    data.Rtxnotsx_pxx,
                    data.Rqxx_sx,
                },
                True,
                [
                    {data.Rpx_qx, data.Rqx_rx, data.Rrx_sx, data.Rqxx_sx},
                    {data.Rtxnotsx_pxx},
                ],
            ),
        ]

        for rules, stratifiable, expected_strata in cases:
            with self.subTest(rules={r.label for r in rules}):
                grd = GRD(rules, [RestrictedProductivityChecker()])
                strata = grd.stratify(MinimalStratification())
                if stratifiable:
                    self.assertIsNotNone(strata)
                    computed = strata or []
                    self.assertEqual(len(expected_strata), len(computed))
                    for expected, computed_strate in zip(expected_strata, computed):
                        self.assertEqual(expected, computed_strate.rules)
                else:
                    self.assertIsNone(strata)
