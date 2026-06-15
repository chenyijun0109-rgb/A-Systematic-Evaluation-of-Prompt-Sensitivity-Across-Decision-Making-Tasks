import json
import tempfile
import unittest
from pathlib import Path

from src.run_random_baseline import (
    build_environment,
    run_all_random_baselines,
    run_random_baseline,
)
from src.tasks.bart import BARTTaskEnvironment
from src.tasks.horizon import HorizonTaskEnvironment
from src.tasks.igt import IGTTaskEnvironment


class RandomBaselineRunnerTests(unittest.TestCase):
    def test_build_environment_creates_task_instances_from_config(self):
        self.assertIsInstance(build_environment("horizon"), HorizonTaskEnvironment)
        self.assertIsInstance(build_environment("igt"), IGTTaskEnvironment)
        self.assertIsInstance(build_environment("bart"), BARTTaskEnvironment)

    def test_run_random_baseline_completes_each_task(self):
        for task in ("horizon", "igt", "bart"):
            with self.subTest(task=task):
                result = run_random_baseline(task, seed=123)

                self.assertEqual(result["task"], task)
                self.assertTrue(result["done"])
                self.assertGreater(result["n_records"], 0)
                self.assertIsInstance(result["metrics"], dict)

    def test_run_all_random_baselines_writes_debug_json_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            summaries = run_all_random_baselines(seed=123, output_dir=output_dir)

            self.assertEqual(set(summaries), {"horizon", "igt", "bart"})
            for task in summaries:
                path = output_dir / f"{task}_random_baseline.json"
                self.assertTrue(path.exists())
                data = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(data["task"], task)
                self.assertTrue(data["done"])
                self.assertIn("metrics", data)
                self.assertIn("records", data)


if __name__ == "__main__":
    unittest.main()
