import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.prompt_loader import load_config
from src.run_multilingual_experiment import (
    PlannedRun,
    build_experiment_plan,
    parse_seeds,
    request_bounds,
    run_multilingual_experiment,
    successful_existing_run,
)


class MultilingualExperimentRunnerTests(unittest.TestCase):
    def test_two_seed_full_plan_has_seventy_two_runs(self):
        config = load_config()
        plan = build_experiment_plan(
            config=config,
            languages=("en", "zh-CN", "es"),
            seeds=(20260528, 20260531),
            output_dir=Path("outputs/test"),
        )

        self.assertEqual(len(plan), 72)
        self.assertEqual(
            {
                (item.language, item.task, item.prompt_condition)
                for item in plan
            }.__len__(),
            36,
        )
        estimate = request_bounds(plan, config)
        self.assertEqual(estimate["horizon_requests"], 7200)
        self.assertEqual(estimate["igt_requests"], 2400)
        self.assertEqual(estimate["total_minimum_requests"], 10560)
        self.assertEqual(estimate["total_maximum_requests"], 40320)

    def test_parse_seeds_rejects_duplicates(self):
        with self.assertRaisesRegex(ValueError, "unique"):
            parse_seeds("1,1")

    def test_successful_existing_run_checks_full_identity(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "run.json"
            planned = PlannedRun(
                language="es",
                task="igt",
                prompt_condition="baseline",
                base_seed=100,
                task_seed=101,
                output_path=str(path),
            )
            path.write_text(
                json.dumps(
                    {
                        "done": True,
                        "prompt_language": "es",
                        "task": "igt",
                        "prompt_condition": "baseline",
                        "seed": 101,
                    }
                ),
                encoding="utf-8",
            )

            self.assertTrue(successful_existing_run(path, planned))

    def test_resume_skips_existing_success_and_writes_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            planned = PlannedRun(
                language="en",
                task="igt",
                prompt_condition="baseline",
                base_seed=100,
                task_seed=101,
                output_path=str(output_dir / "en" / "igt_baseline_seed-101.json"),
            )
            path = Path(planned.output_path)
            path.parent.mkdir(parents=True)
            path.write_text(
                json.dumps(
                    {
                        "done": True,
                        "prompt_language": "en",
                        "task": "igt",
                        "prompt_condition": "baseline",
                        "seed": 101,
                    }
                ),
                encoding="utf-8",
            )
            with patch(
                "src.run_multilingual_experiment.build_experiment_plan",
                return_value=[planned],
            ), patch(
                "src.run_multilingual_experiment.run_llm_pilot"
            ) as pilot:
                result = run_multilingual_experiment(
                    client=object(),
                    model="test",
                    languages=("en",),
                    seeds=(100,),
                    output_dir=output_dir,
                )

            pilot.assert_not_called()
            self.assertEqual(result["skipped_count"], 1)
            self.assertTrue(
                (output_dir / "multilingual_run_status.json").exists()
            )

    def test_skip_recorded_failures_defers_prior_failure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            planned = PlannedRun(
                language="en",
                task="horizon",
                prompt_condition="baseline",
                base_seed=100,
                task_seed=100,
                output_path=str(
                    output_dir / "en" / "horizon_baseline_seed-100.json"
                ),
            )
            status_path = output_dir / "multilingual_run_status.json"
            status_path.write_text(
                json.dumps(
                    {
                        "failed": [
                            {
                                **planned.__dict__,
                                "error_type": "IncompleteRead",
                                "error": "truncated response",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            with patch(
                "src.run_multilingual_experiment.build_experiment_plan",
                return_value=[planned],
            ), patch(
                "src.run_multilingual_experiment.run_llm_pilot"
            ) as pilot:
                result = run_multilingual_experiment(
                    client=object(),
                    model="test",
                    languages=("en",),
                    seeds=(100,),
                    output_dir=output_dir,
                    skip_recorded_failures=True,
                )

            pilot.assert_not_called()
            self.assertEqual(result["skipped_count"], 1)
            self.assertEqual(result["failed_count"], 1)
            status = json.loads(status_path.read_text(encoding="utf-8"))
            self.assertEqual(
                status["skipped"][0]["reason"],
                "recorded_failure_deferred",
            )


if __name__ == "__main__":
    unittest.main()
