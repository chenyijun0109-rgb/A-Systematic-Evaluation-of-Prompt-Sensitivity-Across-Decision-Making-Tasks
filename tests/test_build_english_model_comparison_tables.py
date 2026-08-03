import unittest

from src.build_english_model_comparison_tables import add_reporting_labels, build_checklist, fmt


class BuildEnglishModelComparisonTablesTests(unittest.TestCase):
    def test_fmt_uses_fixed_three_decimal_reporting(self):
        self.assertEqual(fmt("1.23456"), "1.235")
        self.assertEqual(fmt(""), "NA")

    def test_checklist_statement_preserves_interval_and_source_key(self):
        table3 = [{"model": "A", "task": "igt", "prompt_condition": "detailed", "metric": "m", "raw_mean_difference": "0.1", "signed_standardised_effect": "0.2", "standardised_effect_ci_lower": "-0.1", "standardised_effect_ci_upper": "0.5"}]
        rows = build_checklist([], table3, [], [], [])
        self.assertEqual(rows[0]["result_id"], "W001")
        self.assertIn("95% bootstrap CI [-0.100, 0.500]", rows[0]["verified_statement"])
        self.assertIn("Instruction specificity", rows[0]["verified_statement"])
        self.assertEqual(rows[0]["source_key"], "A|igt|detailed|m")

    def test_reporting_labels_preserve_machine_identifiers(self):
        row = add_reporting_labels({
            "task": "horizon",
            "prompt_condition": "detailed",
            "metric": "horizon_effect",
        })
        self.assertEqual(row["prompt_condition"], "detailed")
        self.assertEqual(row["prompt_condition_label"], "Instruction specificity")
        self.assertEqual(
            row["metric_label"], "Horizon-related change in exploration rate"
        )


if __name__ == "__main__":
    unittest.main()
