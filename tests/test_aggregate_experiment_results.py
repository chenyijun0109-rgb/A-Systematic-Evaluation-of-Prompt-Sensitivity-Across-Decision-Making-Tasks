import json
import os
import csv
import tempfile
import unittest
from pathlib import Path

from src.aggregate_experiment_results import (
    AggregationValidationError,
    aggregate_experiment_results,
    apply_horizon_run_estimates,
    discover_json_paths,
    extract_run_row,
    run_aggregation,
    write_aggregation_outputs,
    AggregationResult,
)
from src.horizon_random_exploration import llm_run_id


def minimal_config(tasks=("igt",)):
    conditions = {
        "horizon": ["baseline", "detailed"],
        "igt": ["baseline", "detailed"],
        "bart": ["baseline", "risk_emphasis"],
    }
    return {
        "config_name": "test_config",
        "version": "1",
        "tasks": {
            task: {"prompt_conditions": conditions[task]}
            for task in tasks
        },
    }


def write_pilot(
    path: Path,
    *,
    task: str,
    condition: str,
    seed: int,
    metrics: dict,
    done: bool = True,
    model: str = "gpt-test",
    prompt_hash: str | None = None,
    config_version: str = "1",
    trial_records: list[dict] | None = None,
) -> Path:
    payload = {
        "task": task,
        "prompt_condition": condition,
        "model": model,
        "seed": seed,
        "done": done,
        "config_name": "test_config",
        "config_version": config_version,
        "prompt_path": f"prompts/{task}/{condition}.md",
        "prompt_sha256": prompt_hash or (condition[0] * 64),
        "trial_records": trial_records or [],
        "invalid_responses": [],
        "parse_success_rate": 1.0,
        "run_metrics": metrics,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def igt_metrics(value=0.7):
    return {
        "n_trials": 100,
        "advantageous_choice_rate": value,
        "post_loss_switching_rate": 0.4,
        "block_wise_learning_curve": {
            "1": -4,
            "2": 0,
            "3": 4,
            "4": 8,
            "5": 12,
        },
    }


class AggregateExperimentResultsTests(unittest.TestCase):
    def test_extract_run_row_flattens_metrics_and_derives_igt_learning_change(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = write_pilot(
                Path(tmpdir) / "legacy_name.json",
                task="igt",
                condition="baseline",
                seed=11,
                metrics=igt_metrics(),
            )
            payload = json.loads(path.read_text(encoding="utf-8"))

            row = extract_run_row(path, payload)

        self.assertEqual(row["run_id"], "igt:baseline:11")
        self.assertEqual(row["n_trials"], 100)
        self.assertEqual(row["learning_curve_change"], 16.0)
        self.assertEqual(row["invalid_response_count"], 0)

    def test_discover_json_paths_recurses_and_does_not_require_seed_filename(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = write_pilot(
                root / "nested" / "old_pilot.json",
                task="igt",
                condition="baseline",
                seed=1,
                metrics=igt_metrics(),
            )

            paths = discover_json_paths([root])

        self.assertEqual(paths, [path.resolve()])

    def test_duplicate_runs_fail_by_default(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_pilot(
                root / "first.json",
                task="igt",
                condition="baseline",
                seed=1,
                metrics=igt_metrics(),
            )
            write_pilot(
                root / "second.json",
                task="igt",
                condition="baseline",
                seed=1,
                metrics=igt_metrics(0.8),
            )

            with self.assertRaises(AggregationValidationError) as context:
                aggregate_experiment_results(
                    [root],
                    expected_runs_per_cell=1,
                    duplicate_policy="error",
                    allow_incomplete=False,
                    config=minimal_config(),
                    include_horizon_model=False,
                )

        self.assertIn("duplicate_run", context.exception.issue_codes)

    def test_latest_duplicate_policy_selects_newest_successful_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            older = write_pilot(
                root / "older.json",
                task="igt",
                condition="baseline",
                seed=1,
                metrics=igt_metrics(0.6),
            )
            newer = write_pilot(
                root / "newer.json",
                task="igt",
                condition="baseline",
                seed=1,
                metrics=igt_metrics(0.9),
            )
            os.utime(older, (1, 1))
            os.utime(newer, (2, 2))
            write_pilot(
                root / "detailed.json",
                task="igt",
                condition="detailed",
                seed=1,
                metrics=igt_metrics(0.8),
            )

            result = aggregate_experiment_results(
                [root],
                expected_runs_per_cell=1,
                duplicate_policy="latest",
                allow_incomplete=False,
                config=minimal_config(),
                include_horizon_model=False,
            )

        baseline = next(
            row for row in result.rows
            if row["prompt_condition"] == "baseline"
        )
        self.assertEqual(baseline["advantageous_choice_rate"], 0.9)
        self.assertIn(
            "duplicate_run",
            {issue["code"] for issue in result.quality_report["issues"]},
        )

    def test_incomplete_mode_reports_missing_cell(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_pilot(
                root / "baseline.json",
                task="igt",
                condition="baseline",
                seed=1,
                metrics=igt_metrics(),
            )

            result = aggregate_experiment_results(
                [root],
                expected_runs_per_cell=1,
                duplicate_policy="error",
                allow_incomplete=True,
                config=minimal_config(),
                include_horizon_model=False,
            )

        self.assertFalse(result.quality_report["analysis_complete"])
        self.assertIn(
            "missing_run",
            {issue["code"] for issue in result.quality_report["issues"]},
        )

    def test_unpaired_seeds_and_mixed_model_are_reported(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            for seed in (1, 2):
                write_pilot(
                    root / f"baseline-{seed}.json",
                    task="igt",
                    condition="baseline",
                    seed=seed,
                    metrics=igt_metrics(),
                    model="gpt-a",
                )
            for seed in (1, 3):
                write_pilot(
                    root / f"detailed-{seed}.json",
                    task="igt",
                    condition="detailed",
                    seed=seed,
                    metrics=igt_metrics(),
                    model="gpt-b",
                )

            result = aggregate_experiment_results(
                [root],
                expected_runs_per_cell=2,
                duplicate_policy="error",
                allow_incomplete=True,
                config=minimal_config(),
                include_horizon_model=False,
            )

        codes = {issue["code"] for issue in result.quality_report["issues"]}
        self.assertIn("unpaired_seed", codes)
        self.assertIn("mixed_model", codes)

    def test_mixed_prompt_hash_inside_cell_and_failed_run_are_audited(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_pilot(
                root / "baseline-1.json",
                task="igt",
                condition="baseline",
                seed=1,
                metrics=igt_metrics(),
                prompt_hash="a" * 64,
            )
            write_pilot(
                root / "baseline-2.json",
                task="igt",
                condition="baseline",
                seed=2,
                metrics=igt_metrics(),
                prompt_hash="b" * 64,
            )
            write_pilot(
                root / "failed.json",
                task="igt",
                condition="detailed",
                seed=1,
                metrics=igt_metrics(),
                done=False,
            )

            result = aggregate_experiment_results(
                [root],
                expected_runs_per_cell=2,
                duplicate_policy="error",
                allow_incomplete=True,
                config=minimal_config(),
                include_horizon_model=False,
            )

        codes = {issue["code"] for issue in result.quality_report["issues"]}
        self.assertIn("mixed_prompt_hash", codes)
        self.assertIn("failed_run", codes)
        self.assertEqual(len(result.rows), 2)

    def test_apply_horizon_estimates_matches_source_runs(self):
        a = Path("a.json").resolve()
        b = Path("b.json").resolve()
        rows = [
            {
                "task": "horizon",
                "prompt_condition": "baseline",
                "seed": 1,
                "source_path": str(a),
            },
            {
                "task": "horizon",
                "prompt_condition": "baseline",
                "seed": 2,
                "source_path": str(b),
            },
        ]
        estimates = {
            llm_run_id(a, 1): 1.5,
            llm_run_id(b, 2): 2.5,
        }

        apply_horizon_run_estimates(rows, estimates)

        self.assertEqual(rows[0]["random_exploration_effect"], 1.5)
        self.assertEqual(rows[1]["random_exploration_effect"], 2.5)

    def test_horizon_single_runs_are_reported_as_insufficient(self):
        record = {
            "first_free_choice": True,
            "horizon_type": "horizon_1",
            "choice": "A",
            "observed_mean_A": 55.0,
            "observed_mean_B": 50.0,
            "n_observed_A": 2,
            "n_observed_B": 2,
        }
        record_h6 = {**record, "horizon_type": "horizon_6"}
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            for condition in ("baseline", "detailed"):
                write_pilot(
                    root / f"{condition}.json",
                    task="horizon",
                    condition=condition,
                    seed=1,
                    metrics={
                        "n_trials": 2,
                        "directed_exploration": 0.5,
                        "horizon_effect": 0.1,
                    },
                    trial_records=[record, record_h6],
                )

            result = aggregate_experiment_results(
                [root],
                expected_runs_per_cell=1,
                duplicate_policy="error",
                allow_incomplete=True,
                config=minimal_config(("horizon",)),
            )

        self.assertIn(
            "random_exploration_insufficient_runs",
            {issue["code"] for issue in result.quality_report["issues"]},
        )
        self.assertNotIn("random_exploration_effect", result.rows[0])

    def test_write_aggregation_outputs_creates_stable_csv_and_report(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            result = AggregationResult(
                rows=[
                    {
                        "run_id": "igt:baseline:1",
                        "task": "igt",
                        "prompt_condition": "baseline",
                        "model": "gpt-test",
                        "seed": 1,
                        "config_name": "test_config",
                        "config_version": "1",
                        "prompt_path": "prompts/igt/baseline.md",
                        "prompt_sha256": "a" * 64,
                        "done": True,
                        "n_trials": 100,
                        "parse_success_rate": 1.0,
                        "invalid_response_count": 0,
                        "source_path": str(Path("run.json").resolve()),
                        "advantageous_choice_rate": 0.7,
                    }
                ],
                quality_report={
                    "analysis_complete": True,
                    "issues": [],
                },
            )

            csv_path, report_path = write_aggregation_outputs(
                result,
                output_dir,
            )

            self.assertTrue(report_path.exists())
            self.assertIsNotNone(csv_path)
            with csv_path.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(rows[0]["run_id"], "igt:baseline:1")

    def test_strict_cli_path_writes_quality_report_before_raising(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "input"
            output = Path(tmpdir) / "output"
            write_pilot(
                root / "baseline.json",
                task="igt",
                condition="baseline",
                seed=1,
                metrics=igt_metrics(),
            )
            config_path = Path(tmpdir) / "config.json"
            config_path.write_text(
                json.dumps(minimal_config()),
                encoding="utf-8",
            )

            with self.assertRaises(AggregationValidationError):
                run_aggregation(
                    [root],
                    output_dir=output,
                    expected_runs_per_cell=1,
                    duplicate_policy="error",
                    allow_incomplete=False,
                    config_path=config_path,
                )

            report = json.loads(
                (output / "aggregation_quality_report.json").read_text(
                    encoding="utf-8"
                )
            )

        self.assertIn(
            "missing_run",
            {issue["code"] for issue in report["issues"]},
        )
        self.assertEqual(report["valid_run_count"], 1)


if __name__ == "__main__":
    unittest.main()
