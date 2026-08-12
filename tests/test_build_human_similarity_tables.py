import csv
import tempfile
import unittest
from pathlib import Path

from src.build_human_similarity_tables import build_tables, latex_cell


class HumanSimilarityTableTests(unittest.TestCase):
    def test_builds_distance_coverage_and_direction_counts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            comparison = root / "comparison.csv"
            metrics = root / "metrics.csv"
            comparison_fields = [
                "task", "prompt_condition", "metric", "llm_n", "human_n",
                "llm_mean", "human_mean", "raw_mean_difference_llm_minus_human",
                "human_sd_standardised_distance", "llm_sd", "human_sd",
                "human_reference_lower", "human_reference_upper",
                "llm_mean_reference_position", "llm_mean_human_empirical_quantile",
                "llm_runs_within_human_reference_count",
                "llm_runs_within_human_reference_proportion",
            ]
            conditions = ["baseline", "detailed", "role_human", "risk_emphasis"]
            with comparison.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=comparison_fields)
                writer.writeheader()
                for condition in conditions:
                    writer.writerow({
                        "task": "bart", "prompt_condition": condition,
                        "metric": "explosion_rate", "llm_n": 3, "human_n": 10,
                        "llm_mean": 0.5, "human_mean": 0.5,
                        "raw_mean_difference_llm_minus_human": 0,
                        "human_sd_standardised_distance": 0, "llm_sd": 0.3,
                        "human_sd": 0.2, "human_reference_lower": 0.2,
                        "human_reference_upper": 0.8,
                        "llm_mean_reference_position": "within",
                        "llm_mean_human_empirical_quantile": 0.5,
                        "llm_runs_within_human_reference_count": 1,
                        "llm_runs_within_human_reference_proportion": 1 / 3,
                    })
            with metrics.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=["task", "prompt_condition", "explosion_rate"],
                )
                writer.writeheader()
                for condition in conditions:
                    for value in (0.1, 0.5, 0.9):
                        writer.writerow({
                            "task": "bart", "prompt_condition": condition,
                            "explosion_rate": value,
                        })

            references, details, matrix = build_tables(
                [("gpt-4.1", comparison, metrics)]
            )

            self.assertEqual(len(references), 1)
            self.assertEqual(len(details), 4)
            self.assertEqual(details[0]["llm_runs_below_human_reference_count"], 1)
            self.assertEqual(details[0]["llm_runs_within_human_reference_count"], 1)
            self.assertEqual(details[0]["llm_runs_above_human_reference_count"], 1)
            self.assertEqual(details[0]["display_cell"], "○ +0.00 | 33%")
            self.assertEqual(matrix[0]["task_specific_emphasis"], "○ +0.00 | 33%")

    def test_latex_cell_preserves_all_three_encodings(self):
        self.assertEqual(latex_cell("↑ +2.33 | 0%"), r"$\uparrow$ $+2.33$ / 0\%")


if __name__ == "__main__":
    unittest.main()
