import pathlib
import unittest

from prototyping_inference_engine.grd.grd import GRD
from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser


class TestGrdFunctions(unittest.TestCase):
    def test_grd_with_functions(self) -> None:
        base_dir = pathlib.Path(__file__).parent / "resources"
        file_path = base_dir / "functions_grd.dlgp"

        result = DlgpeParser.instance().parse_file(file_path)
        rules = set(result["rules"])
        grd = GRD(rules)

        for rule in rules:
            if rule.label == "ROOT":
                computed = grd.get_triggered_rules(rule)
                self.assertIn(rule, computed)

                start_path = None
                for candidate in computed:
                    if candidate != rule:
                        start_path = candidate
                        break
                self.assertIsNotNone(start_path)
                assert start_path is not None
                self.assertEqual(2, len(computed))

                computed = grd.get_triggered_rules(start_path)
                self.assertEqual(1, len(computed))

                computed = grd.get_triggered_rules(next(iter(computed)))
                self.assertEqual(0, len(computed))

            elif rule.label == "ALONE":
                computed = grd.get_triggered_rules(rule)
                self.assertEqual(0, len(computed))
