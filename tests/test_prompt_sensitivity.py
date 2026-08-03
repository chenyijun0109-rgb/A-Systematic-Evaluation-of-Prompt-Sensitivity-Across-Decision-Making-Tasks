import csv
import hashlib
import json
import math
import random
import tempfile
import unittest
from pathlib import Path

from src.compute_prompt_sensitivity import (
    PromptSensitivityValidationError,
    bootstrap_independent_effect,
    bootstrap_paired_effect,
    compute_psi_row,
    compute_standardised_effect,
    run_prompt_sensitivity_analysis,
    summarise_values,
    validate_run_table,
)
from src.aggregate_experiment_results import run_aggregation
from src.prompt_loader import load_config


def policy():
    return {
        "zero_tolerance": 1e-12,
        "minimum_partial_metrics": 2,
        "bounded_metrics": [
            "advantageous_choice_rate",
            "explosion_rate",
        ],
        "low_variance_absolute_threshold": 1e-6,
        "low_variance_relative_threshold": 1e-6,
        "confidence_level": 0.95,
        "bootstrap_replicates": 200,
        "bootstrap_seed": 20260615,
    }


def minimal_config():
    return {
        "tasks": {
            "bart": {
                "prompt_conditions": ["baseline", "risk_emphasis"],
            }
        },
        "analysis": {
            "baseline_condition": "baseline",
            "prompt_sensitivity": {
                **policy(),
                "primary_metrics": {
                    "bart": [
                        "adjusted_average_pumps",
                        "explosion_rate",
                        "post_explosion_adjustment",
                    ]
                },
            },
        },
    }


class PromptSensitivityTests(unittest.TestCase):
    def test_formal_experiment_freeze_manifest_matches_prompt_files(self):
        path = Path("configs/formal_experiment_freeze.json")
        self.assertTrue(path.exists())
        manifest = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(manifest["status"], "frozen_for_validation_rerun")
        self.assertEqual(manifest["experiment_model"]["temperature"], 0.7)
        self.assertEqual(manifest["experiment_model"]["top_p"], 1.0)
        self.assertEqual(manifest["experiment_model"]["max_output_tokens"], 16)
        self.assertEqual(len(manifest["prompts"]), 12)
        for prompt in manifest["prompts"]:
            prompt_path = Path(prompt["path"])
            expected_hash = hashlib.sha256(
                prompt_path.read_bytes()
            ).hexdigest()
            self.assertEqual(prompt["sha256"], expected_hash)

        self.assertEqual(
            manifest["metrics"]["primary_psi"]["igt"],
            [
                "advantageous_choice_rate",
                "post_loss_switching_rate",
            ],
        )
        self.assertEqual(
            manifest["horizon_random_exploration"]["shrinkage_grid"],
            [0.25, 0.5, 1.0],
        )
        self.assertFalse(
            manifest["exclusion_rules"]["llm_runs"][
                "exclude_zero_variance_or_extreme_behavior"
            ]
        )

    def test_config_freezes_primary_metrics_and_variance_policy(self):
        config = load_config(Path("configs/experiment_config_stage01.json"))
        analysis = config["analysis"]["prompt_sensitivity"]

        self.assertEqual(
            analysis["primary_metrics"]["horizon"],
            [
                "directed_exploration",
                "horizon_effect",
                "random_exploration_effect",
            ],
        )
        self.assertEqual(
            analysis["primary_metrics"]["igt"],
            [
                "advantageous_choice_rate",
                "post_loss_switching_rate",
            ],
        )
        self.assertEqual(
            analysis["supplementary_metrics"]["igt"],
            [
                "learning_slope",
                "learning_curve_change",
                "block_wise_learning_curve",
            ],
        )
        self.assertEqual(
            analysis["primary_metrics"]["bart"],
            [
                "adjusted_average_pumps",
                "explosion_rate",
                "post_explosion_adjustment",
            ],
        )
        self.assertEqual(analysis["zero_tolerance"], 1e-12)
        self.assertEqual(analysis["minimum_partial_metrics"], 2)

    def test_summarise_metric_uses_sample_standard_deviation(self):
        summary = summarise_values([1.0, 2.0, 3.0])

        self.assertEqual(summary["n"], 3)
        self.assertEqual(summary["mean"], 2.0)
        self.assertEqual(summary["sd"], 1.0)
        self.assertEqual(summary["median"], 2.0)
        self.assertEqual(summary["minimum"], 1.0)
        self.assertEqual(summary["maximum"], 3.0)

    def test_standardised_effect_uses_pooled_sd_and_hedges_correction(self):
        result = compute_standardised_effect(
            baseline_values=[1.0, 2.0, 3.0],
            condition_values=[3.0, 4.0, 5.0],
            metric="adjusted_average_pumps",
            policy=policy(),
            allow_incomplete=False,
        )

        self.assertEqual(result["raw_mean_difference"], 2.0)
        self.assertEqual(result["denominator"], 1.0)
        self.assertEqual(result["sd_source"], "pooled")
        self.assertAlmostEqual(result["hedges_correction"], 0.8)
        self.assertAlmostEqual(result["signed_standardised_effect"], 1.6)
        self.assertAlmostEqual(result["absolute_standardised_effect"], 1.6)
        self.assertEqual(result["baseline_sd_standardised_effect"], 2.0)

    def test_zero_baseline_sd_still_uses_pooled_sd(self):
        result = compute_standardised_effect(
            baseline_values=[1.0, 1.0, 1.0],
            condition_values=[1.0, 2.0, 3.0],
            metric="adjusted_average_pumps",
            policy=policy(),
            allow_incomplete=False,
        )

        self.assertEqual(result["sd_source"], "pooled")
        self.assertGreater(result["denominator"], 0.0)

    def test_equal_constant_groups_have_zero_effect(self):
        result = compute_standardised_effect(
            baseline_values=[1.0, 1.0, 1.0],
            condition_values=[1.0, 1.0, 1.0],
            metric="adjusted_average_pumps",
            policy=policy(),
            allow_incomplete=False,
        )

        self.assertEqual(result["sd_source"], "constant_equal")
        self.assertEqual(result["signed_standardised_effect"], 0.0)

    def test_unequal_constant_groups_are_undefined(self):
        with self.assertRaises(PromptSensitivityValidationError) as context:
            compute_standardised_effect(
                baseline_values=[1.0, 1.0, 1.0],
                condition_values=[2.0, 2.0, 2.0],
                metric="adjusted_average_pumps",
                policy=policy(),
                allow_incomplete=False,
            )

        self.assertIn(
            "zero_variance_undefined_effect",
            context.exception.issue_codes,
        )

    def test_small_positive_baseline_sd_warns_without_replacement(self):
        result = compute_standardised_effect(
            baseline_values=[0.5, 0.5000001, 0.4999999],
            condition_values=[0.6, 0.6, 0.6],
            metric="advantageous_choice_rate",
            policy=policy(),
            allow_incomplete=False,
        )

        self.assertEqual(result["sd_source"], "pooled")
        self.assertIn("low_baseline_variance", result["warning_flags"])

    def test_paired_bootstrap_preserves_constant_seed_difference(self):
        result = bootstrap_paired_effect(
            baseline_by_seed={1: 1.0, 2: 10.0, 3: 100.0},
            condition_by_seed={1: 11.0, 2: 20.0, 3: 110.0},
            metric="adjusted_average_pumps",
            policy=policy(),
            replicates=200,
            bootstrap_seed=123,
            confidence_level=0.95,
        )

        self.assertEqual(result["raw_difference_ci_lower"], 10.0)
        self.assertEqual(result["raw_difference_ci_upper"], 10.0)
        self.assertEqual(result["bootstrap_replicates"], 200)
        self.assertGreater(result["standardised_valid_replicates"], 0)

    def test_independent_bootstrap_does_not_preserve_arbitrary_seed_pairs(self):
        result = bootstrap_independent_effect(
            baseline_values=[1.0, 10.0, 100.0],
            condition_values=[11.0, 20.0, 110.0],
            metric="advantageous_choice_rate",
            policy=policy(),
            replicates=200,
            bootstrap_seed=123,
            confidence_level=0.95,
        )

        self.assertEqual(result["bootstrap_unit"], "independent_cell")
        self.assertLess(result["raw_difference_ci_lower"], 10.0)
        self.assertGreater(result["raw_difference_ci_upper"], 10.0)

    def test_igt_end_to_end_uses_independent_cell_bootstrap(self):
        config = minimal_config()
        config["tasks"] = {"igt": {"prompt_conditions": ["baseline", "detailed"]}}
        config["analysis"]["prompt_sensitivity"]["primary_metrics"] = {
            "igt": ["advantageous_choice_rate", "post_loss_switching_rate"]
        }
        rows = []
        for condition, offset in (("baseline", 0.0), ("detailed", 0.1)):
            for seed, value in zip((1, 2, 3), (0.2, 0.5, 0.8)):
                rows.append({
                    "task": "igt", "prompt_condition": condition, "seed": seed,
                    "advantageous_choice_rate": value + offset,
                    "post_loss_switching_rate": 1.0 - value + offset,
                })
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_path = root / "metrics.csv"
            with input_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                writer.writeheader(); writer.writerows(rows)
            config_path = root / "config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            result = run_prompt_sensitivity_analysis(
                input_path, output_dir=root / "out", expected_runs_per_cell=3,
                allow_incomplete=False, config_path=config_path,
            )
        self.assertTrue(all(row["bootstrap_unit"] == "independent_cell" for row in result["effect_rows"]))
        self.assertEqual(result["psi_rows"][0]["bootstrap_unit"], "independent_cell")

    def test_complete_psi_averages_three_absolute_effects(self):
        row = compute_psi_row(
            task="bart",
            condition="risk_emphasis",
            expected_metrics=[
                "adjusted_average_pumps",
                "explosion_rate",
                "post_explosion_adjustment",
            ],
            effect_rows=[
                {
                    "metric": "adjusted_average_pumps",
                    "absolute_standardised_effect": 1.0,
                },
                {
                    "metric": "explosion_rate",
                    "absolute_standardised_effect": 2.0,
                },
                {
                    "metric": "post_explosion_adjustment",
                    "absolute_standardised_effect": 3.0,
                },
            ],
            minimum_partial_metrics=2,
            allow_incomplete=False,
        )

        self.assertEqual(row["psi"], 2.0)
        self.assertEqual(row["valid_metric_count"], 3)
        self.assertEqual(row["status"], "complete")

    def test_partial_psi_requires_explicit_incomplete_mode(self):
        effects = [
            {
                "metric": "adjusted_average_pumps",
                "absolute_standardised_effect": 1.0,
            },
            {
                "metric": "explosion_rate",
                "absolute_standardised_effect": 3.0,
            },
        ]
        with self.assertRaises(PromptSensitivityValidationError):
            compute_psi_row(
                task="bart",
                condition="risk_emphasis",
                expected_metrics=[
                    "adjusted_average_pumps",
                    "explosion_rate",
                    "post_explosion_adjustment",
                ],
                effect_rows=effects,
                minimum_partial_metrics=2,
                allow_incomplete=False,
            )

        partial = compute_psi_row(
            task="bart",
            condition="risk_emphasis",
            expected_metrics=[
                "adjusted_average_pumps",
                "explosion_rate",
                "post_explosion_adjustment",
            ],
            effect_rows=effects,
            minimum_partial_metrics=2,
            allow_incomplete=True,
        )

        self.assertEqual(partial["psi"], 2.0)
        self.assertEqual(partial["status"], "partial")
        self.assertIn("post_explosion_adjustment", partial["excluded_metrics"])

    def test_validate_run_table_checks_counts_and_paired_seeds(self):
        rows = []
        for condition, seeds in (
            ("baseline", (1, 2, 3)),
            ("risk_emphasis", (1, 2, 4)),
        ):
            for seed in seeds:
                rows.append(
                    {
                        "task": "bart",
                        "prompt_condition": condition,
                        "seed": seed,
                    }
                )

        with self.assertRaises(PromptSensitivityValidationError) as context:
            validate_run_table(
                rows,
                config=minimal_config(),
                expected_runs_per_cell=3,
                allow_incomplete=False,
            )

        self.assertIn("unpaired_seed", context.exception.issue_codes)

    def test_end_to_end_analysis_writes_expected_tables(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_path = root / "llm_run_metrics.csv"
            output_dir = root / "analysis"
            fieldnames = [
                "run_id",
                "task",
                "prompt_condition",
                "seed",
                "adjusted_average_pumps",
                "explosion_rate",
                "post_explosion_adjustment",
            ]
            with input_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                writer.writeheader()
                for condition, shift in (("baseline", 0.0), ("risk_emphasis", 1.0)):
                    for seed in (1, 2, 3):
                        writer.writerow(
                            {
                                "run_id": f"bart:{condition}:{seed}",
                                "task": "bart",
                                "prompt_condition": condition,
                                "seed": seed,
                                "adjusted_average_pumps": seed + shift,
                                "explosion_rate": seed / 10 + shift / 10,
                                "post_explosion_adjustment": seed * 2 + shift,
                            }
                        )
            config_path = root / "config.json"
            config_path.write_text(
                json.dumps(minimal_config()),
                encoding="utf-8",
            )

            result = run_prompt_sensitivity_analysis(
                input_path,
                output_dir=output_dir,
                expected_runs_per_cell=3,
                allow_incomplete=False,
                config_path=config_path,
            )

            self.assertTrue((output_dir / "metric_summary.csv").exists())
            self.assertTrue((output_dir / "prompt_effects.csv").exists())
            self.assertTrue((output_dir / "prompt_sensitivity.csv").exists())
            self.assertTrue((output_dir / "analysis_summary.json").exists())
            self.assertEqual(len(result["effect_rows"]), 3)
            self.assertEqual(len(result["psi_rows"]), 1)
            self.assertEqual(result["psi_rows"][0]["status"], "complete")
            self.assertIn(
                "standardised_effect_ci_lower",
                result["effect_rows"][0],
            )
            self.assertIn("psi_ci_lower", result["psi_rows"][0])
            self.assertEqual(
                result["psi_rows"][0]["bootstrap_replicates"],
                policy()["bootstrap_replicates"],
            )

    def test_complete_36_run_fixture_produces_nine_complete_psi_rows(self):
        config = load_config(Path("configs/experiment_config_stage01.json"))
        config["analysis"]["prompt_sensitivity"]["bootstrap_replicates"] = 3
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            raw_dir = root / "raw"
            output_dir = root / "processed"
            base_seeds = (101, 202, 303)

            for task, task_config in config["tasks"].items():
                for condition_index, condition in enumerate(
                    task_config["prompt_conditions"]
                ):
                    for run_index, base_seed in enumerate(base_seeds):
                        task_offset = {"horizon": 0, "igt": 1, "bart": 2}[task]
                        seed = base_seed + task_offset
                        if task == "horizon":
                            records = self._horizon_records(
                                seed,
                                condition_index,
                            )
                            metrics = {
                                "n_games": 40,
                                "n_trials": 300,
                                "directed_exploration": (
                                    0.45 + run_index * 0.04
                                    + condition_index * 0.02
                                ),
                                "horizon_effect": (
                                    0.08 + run_index * 0.03
                                    + condition_index * 0.01
                                ),
                                "exploration_rate": 0.3 + run_index * 0.02,
                            }
                        elif task == "igt":
                            records = []
                            first = -6 + run_index
                            metrics = {
                                "n_trials": 100,
                                "advantageous_choice_rate": (
                                    0.55 + run_index * 0.04
                                    + condition_index * 0.02
                                ),
                                "post_loss_switching_rate": (
                                    0.35 + run_index * 0.05
                                    + condition_index * 0.01
                                ),
                                "block_wise_learning_curve": {
                                    "1": first,
                                    "2": first + 2,
                                    "3": first + 4,
                                    "4": first + 6,
                                    "5": (
                                        first + 8 + condition_index
                                        + run_index
                                    ),
                                },
                            }
                        else:
                            records = []
                            metrics = {
                                "n_balloons": 40,
                                "adjusted_average_pumps": (
                                    6.0 + run_index * 0.6
                                    + condition_index * 0.3
                                ),
                                "explosion_rate": (
                                    0.15 + run_index * 0.04
                                    + condition_index * 0.02
                                ),
                                "post_explosion_adjustment": (
                                    -1.0 + run_index * 0.5
                                    + condition_index * 0.2
                                ),
                            }
                        payload = {
                            "task": task,
                            "prompt_condition": condition,
                            "model": "gpt-test",
                            "seed": seed,
                            "done": True,
                            "config_name": config["config_name"],
                            "config_version": config["version"],
                            "prompt_path": task_config["prompt_paths"][condition],
                            "prompt_sha256": (
                                f"{task}:{condition}".encode().hex() + "0" * 64
                            )[:64],
                            "trial_records": records,
                            "invalid_responses": [],
                            "parse_success_rate": 1.0,
                            "run_metrics": metrics,
                        }
                        path = (
                            raw_dir
                            / task
                            / condition
                            / f"{task}_{condition}_seed-{seed}.json"
                        )
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_text(
                            json.dumps(payload),
                            encoding="utf-8",
                        )

            aggregation = run_aggregation(
                [raw_dir],
                output_dir=output_dir,
                expected_runs_per_cell=3,
                duplicate_policy="error",
                allow_incomplete=False,
                config_path=Path("configs/experiment_config_stage01.json"),
            )
            test_config_path = root / "test_config.json"
            test_config_path.write_text(json.dumps(config), encoding="utf-8")
            analysis = run_prompt_sensitivity_analysis(
                output_dir / "llm_run_metrics.csv",
                output_dir=output_dir,
                expected_runs_per_cell=3,
                allow_incomplete=False,
                config_path=test_config_path,
            )

            self.assertEqual(len(aggregation.rows), 36)
            self.assertEqual(len(analysis["effect_rows"]), 24)
            self.assertEqual(len(analysis["psi_rows"]), 9)
            self.assertTrue(
                all(row["status"] == "complete" for row in analysis["psi_rows"])
            )
            horizon_rows = [
                row for row in aggregation.rows
                if row["task"] == "horizon"
            ]
            self.assertEqual(len(horizon_rows), 12)
            self.assertTrue(
                all(
                    math.isfinite(float(row["random_exploration_effect"]))
                    for row in horizon_rows
                )
            )

    @staticmethod
    def _horizon_records(seed: int, condition_index: int) -> list[dict]:
        rng = random.Random(seed + condition_index * 10_000)
        records = []
        reward_differences = (-20, -12, -8, -4, 4, 8, 12, 20)
        for game_index in range(40):
            horizon = "horizon_1" if game_index % 2 == 0 else "horizon_6"
            delta_reward = reward_differences[game_index % len(reward_differences)]
            unequal = game_index % 3 != 0
            if unequal and game_index % 2 == 0:
                n_a, n_b = 1, 3
                information_value = 1.0
            elif unequal:
                n_a, n_b = 3, 1
                information_value = -1.0
            else:
                n_a, n_b = 2, 2
                information_value = 0.0
            noise = (
                5.0 + condition_index * 0.3
                if horizon == "horizon_1"
                else 10.0 + condition_index * 0.5
            )
            information_bonus = 2.0 if horizon == "horizon_1" else 3.0
            predictor = (
                delta_reward + information_bonus * information_value
            ) / noise
            probability_a = 1.0 / (1.0 + math.exp(-predictor))
            records.append(
                {
                    "first_free_choice": True,
                    "horizon_type": horizon,
                    "choice": "A" if rng.random() < probability_a else "B",
                    "observed_mean_A": 50.0 + delta_reward,
                    "observed_mean_B": 50.0,
                    "n_observed_A": n_a,
                    "n_observed_B": n_b,
                }
            )
        return records


if __name__ == "__main__":
    unittest.main()
