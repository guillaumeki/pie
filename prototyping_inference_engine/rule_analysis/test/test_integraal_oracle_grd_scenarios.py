import unittest

from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser
from prototyping_inference_engine.rule_analysis.analyser import RuleAnalyser
from prototyping_inference_engine.rule_analysis.model import PropertyId, PropertyStatus
from prototyping_inference_engine.rule_analysis.test._helpers import repo_file


class TestIntegraalOracleGrdScenarios(unittest.TestCase):
    def test_function_fixture_keeps_path_and_isolates_alone_rule(self):
        file_path = repo_file(
            "prototyping_inference_engine",
            "grd",
            "test",
            "resources",
            "functions_grd.dlgp",
        )
        result = DlgpeParser.instance().parse_file(file_path)
        analyser = RuleAnalyser(result["rules"])

        path_rule = next(
            rule for rule in analyser.snapshot.rules if rule.label == "PathR1"
        )
        alone_rule = next(
            rule for rule in analyser.snapshot.rules if rule.label == "ALONE"
        )
        triggered = analyser.snapshot.grd.get_triggered_rules(path_rule)
        triggered_labels = {rule.label for rule in triggered}

        self.assertEqual(triggered_labels, {"PathR2"})
        self.assertEqual(analyser.snapshot.grd.get_triggered_rules(alone_rule), set())

    def test_function_fixture_exposes_non_sticky_body_repetition(self):
        file_path = repo_file(
            "prototyping_inference_engine",
            "grd",
            "test",
            "resources",
            "functions_grd_simpler.dlgp",
        )
        result = DlgpeParser.instance().parse_file(file_path)
        analyser = RuleAnalyser(result["rules"])

        report = analyser.analyse([PropertyId.STICKY])

        self.assertEqual(
            report.get(PropertyId.STICKY).status,
            PropertyStatus.VIOLATED,
        )


if __name__ == "__main__":
    unittest.main()
