import unittest

from src.freeze_model_comparison_inputs import audit_inputs


def row(model: str, seed: int, prompt_hash: str = "abc") -> dict[str, str]:
    return {
        "task": "igt",
        "prompt_condition": "baseline",
        "seed": str(seed),
        "requested_model": model,
        "resolved_model": model,
        "temperature": "0.7",
        "top_p": "1.0",
        "max_output_tokens": "16",
        "config_name": "experiment_config_stage01",
        "config_version": "0.7",
        "prompt_sha256": prompt_hash,
        "done": "true",
        "n_trials": "100",
        "n_games": "",
        "n_balloons": "",
        "parse_success_rate": "1.0",
        "invalid_response_count": "0",
    }


class FreezeModelComparisonInputsTests(unittest.TestCase):
    def test_complete_matched_inputs_pass(self):
        report, cells = audit_inputs(
            [row("model-a", 1), row("model-a", 2)],
            [row("model-b", 1), row("model-b", 2)],
            model_a_label="A",
            model_b_label="B",
            expected_runs_per_cell=2,
        )
        self.assertTrue(report["analysis_complete"])
        self.assertEqual(report["matched_key_count"], 2)
        self.assertEqual(cells[0]["status"], "pass")

    def test_prompt_hash_or_seed_mismatch_fails(self):
        report, cells = audit_inputs(
            [row("model-a", 1), row("model-a", 2)],
            [row("model-b", 1), row("model-b", 3, "different")],
            model_a_label="A",
            model_b_label="B",
            expected_runs_per_cell=2,
        )
        self.assertFalse(report["analysis_complete"])
        self.assertEqual(cells[0]["status"], "fail")


if __name__ == "__main__":
    unittest.main()
