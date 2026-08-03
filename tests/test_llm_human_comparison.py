import csv
import json
import tempfile
import unittest
from pathlib import Path

from src.compare_llm_human import (
    compare_llm_to_human,
    empirical_quantile,
    reference_position,
    run_llm_human_comparison,
    summarise,
)


class LlmHumanComparisonTests(unittest.TestCase):
    def test_summarise_uses_sample_sd_and_reference_interval(self):
        summary = summarise([1.0, 2.0, 3.0, 4.0, 5.0])

        self.assertEqual(summary["n"], 5)
        self.assertEqual(summary["mean"], 3.0)
        self.assertAlmostEqual(summary["sd"], 1.5811388300841898)
        self.assertEqual(summary["median"], 3.0)
        self.assertEqual(summary["reference_lower"], 1.1)
        self.assertEqual(summary["reference_upper"], 4.9)

    def test_reference_position_labels_below_within_and_above(self):
        self.assertEqual(reference_position(0.0, 1.0, 2.0), "below")
        self.assertEqual(reference_position(1.5, 1.0, 2.0), "within")
        self.assertEqual(reference_position(3.0, 1.0, 2.0), "above")

    def test_empirical_quantile_reports_fraction_below_or_equal(self):
        self.assertEqual(empirical_quantile(2.0, [1.0, 2.0, 3.0, 4.0]), 0.5)

    def test_compare_llm_to_human_computes_distance_and_coverage(self):
        row = compare_llm_to_human(
            task="igt",
            prompt_condition="detailed",
            metric="advantageous_choice_rate",
            llm_values=[0.4, 0.5, 0.6],
            human_values=[0.3, 0.4, 0.5, 0.6, 0.7],
        )

        self.assertEqual(row["llm_n"], 3)
        self.assertEqual(row["human_n"], 5)
        self.assertEqual(row["llm_mean"], 0.5)
        self.assertEqual(row["human_mean"], 0.5)
        self.assertEqual(row["human_sd_standardised_distance"], 0.0)
        self.assertEqual(row["llm_mean_reference_position"], "within")
        self.assertEqual(row["llm_runs_within_human_reference_proportion"], 1.0)

    def test_end_to_end_writes_expected_outputs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            llm_path = root / "llm_run_metrics.csv"
            human_dir = root / "human"
            output_dir = root / "out"
            human_dir.mkdir()
            self._write_csv(
                llm_path,
                [
                    "task",
                    "prompt_condition",
                    "seed",
                    "advantageous_choice_rate",
                    "post_loss_switching_rate",
                ],
                [
                    {
                        "task": "igt",
                        "prompt_condition": "baseline",
                        "seed": "1",
                        "advantageous_choice_rate": "0.5",
                        "post_loss_switching_rate": "0.6",
                    },
                    {
                        "task": "igt",
                        "prompt_condition": "baseline",
                        "seed": "2",
                        "advantageous_choice_rate": "0.7",
                        "post_loss_switching_rate": "0.8",
                    },
                    {
                        "task": "igt",
                        "prompt_condition": "detailed",
                        "seed": "1",
                        "advantageous_choice_rate": "0.4",
                        "post_loss_switching_rate": "0.7",
                    },
                    {
                        "task": "igt",
                        "prompt_condition": "detailed",
                        "seed": "2",
                        "advantageous_choice_rate": "0.6",
                        "post_loss_switching_rate": "0.9",
                    },
                ],
            )
            self._write_csv(
                human_dir / "igt_human_metrics.csv",
                [
                    "task",
                    "participant_id",
                    "advantageous_choice_rate",
                    "post_loss_switching_rate",
                ],
                [
                    {
                        "task": "igt",
                        "participant_id": "h1",
                        "advantageous_choice_rate": "0.3",
                        "post_loss_switching_rate": "0.5",
                    },
                    {
                        "task": "igt",
                        "participant_id": "h2",
                        "advantageous_choice_rate": "0.5",
                        "post_loss_switching_rate": "0.7",
                    },
                    {
                        "task": "igt",
                        "participant_id": "h3",
                        "advantageous_choice_rate": "0.7",
                        "post_loss_switching_rate": "0.9",
                    },
                ],
            )

            summary = run_llm_human_comparison(
                llm_metrics_path=llm_path,
                human_metrics_dir=human_dir,
                output_dir=output_dir,
                metrics_by_task={
                    "igt": [
                        "advantageous_choice_rate",
                        "post_loss_switching_rate",
                    ]
                },
            )

            self.assertTrue((output_dir / "human_metric_summary.csv").exists())
            self.assertTrue((output_dir / "llm_human_comparison.csv").exists())
            self.assertTrue((output_dir / "closest_prompt_by_metric.csv").exists())
            self.assertTrue((output_dir / "human_comparison_summary.json").exists())
            self.assertEqual(summary["comparison_rows"], 4)
            saved = json.loads(
                (output_dir / "human_comparison_summary.json").read_text()
            )
            self.assertEqual(saved["task_participants"]["igt"], 3)

    @staticmethod
    def _write_csv(path, fieldnames, rows):
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)


if __name__ == "__main__":
    unittest.main()
