import unittest

from src.compare_model_results import build_model_prompt_interactions


def config() -> dict:
    return {
        "tasks": {"igt": {"prompt_conditions": ["baseline", "detailed"]}},
        "analysis": {
            "baseline_condition": "baseline",
            "prompt_sensitivity": {
                "primary_metrics": {"igt": ["advantageous_choice_rate"]},
                "bootstrap_replicates": 200,
                "bootstrap_seed": 123,
                "confidence_level": 0.95,
            },
        },
    }


def rows(baseline: list[float], effects: list[float]) -> list[dict[str, str]]:
    result = []
    for seed, (base, effect) in enumerate(zip(baseline, effects), start=1):
        result.extend(
            [
                {"task": "igt", "prompt_condition": "baseline", "seed": str(seed), "advantageous_choice_rate": str(base)},
                {"task": "igt", "prompt_condition": "detailed", "seed": str(seed), "advantageous_choice_rate": str(base + effect)},
            ]
        )
    return result


class CompareModelResultsTests(unittest.TestCase):
    def test_igt_interaction_uses_independent_cell_bootstrap(self):
        output = build_model_prompt_interactions(
            rows([0.1, 0.8, 0.3], [0.1, 0.2, 0.3]),
            rows([0.9, 0.2, 0.5], [0.4, 0.5, 0.6]),
            model_a_label="A",
            model_b_label="B",
            config=config(),
        )
        self.assertEqual(len(output), 1)
        self.assertAlmostEqual(output[0]["model_a_mean_prompt_effect"], 0.2)
        self.assertAlmostEqual(output[0]["model_b_mean_prompt_effect"], 0.5)
        self.assertAlmostEqual(output[0]["model_by_prompt_interaction"], 0.3)
        self.assertEqual(output[0]["runs_per_cell"], 3)
        self.assertEqual(output[0]["resampling_unit"], "independent_run_within_model_prompt_cell")
        self.assertIsNone(output[0]["interaction_sd"])

    def test_horizon_interaction_resamples_matched_environment_seed_blocks(self):
        test_config = config()
        test_config["tasks"] = {"horizon": {"prompt_conditions": ["baseline", "detailed"]}}
        test_config["analysis"]["prompt_sensitivity"]["primary_metrics"] = {
            "horizon": ["directed_exploration"]
        }
        model_a = [
            {"task": "horizon", "prompt_condition": condition, "seed": str(seed), "directed_exploration": str(value)}
            for seed, base, effect in ((1, 0.1, 0.1), (2, 0.8, 0.2), (3, 0.3, 0.3))
            for condition, value in (("baseline", base), ("detailed", base + effect))
        ]
        model_b = [
            {"task": "horizon", "prompt_condition": condition, "seed": str(seed), "directed_exploration": str(value)}
            for seed, base, effect in ((1, 0.9, 0.4), (2, 0.2, 0.5), (3, 0.5, 0.6))
            for condition, value in (("baseline", base), ("detailed", base + effect))
        ]
        output = build_model_prompt_interactions(
            model_a, model_b, model_a_label="A", model_b_label="B", config=test_config
        )
        self.assertEqual(output[0]["resampling_unit"], "matched_environment_seed_block")
        self.assertAlmostEqual(output[0]["interaction_sd"], 0.0)

    def test_unmatched_model_seeds_are_rejected(self):
        model_b = rows([0.1, 0.2], [0.3, 0.4])
        model_b[-1]["seed"] = "3"
        with self.assertRaisesRegex(ValueError, "unmatched"):
            build_model_prompt_interactions(
                rows([0.1, 0.2], [0.1, 0.2]),
                model_b,
                model_a_label="A",
                model_b_label="B",
                config=config(),
            )


if __name__ == "__main__":
    unittest.main()
