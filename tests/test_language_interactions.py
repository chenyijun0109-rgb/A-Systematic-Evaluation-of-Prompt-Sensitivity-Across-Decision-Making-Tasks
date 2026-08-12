import unittest

from src.compute_language_interactions import (
    build_language_baseline_contrasts,
    build_language_prompt_interactions,
)


def config():
    return {
        "prompt_languages": ["en", "zh-CN", "es"],
        "tasks": {"igt": {"prompt_conditions": ["baseline", "detailed"]}},
        "analysis": {
            "baseline_condition": "baseline",
            "prompt_sensitivity": {
                "primary_metrics": {"igt": ["advantageous_choice_rate"]},
                "bootstrap_replicates": 199,
                "confidence_level": 0.95,
                "bootstrap_seed": 123,
            },
            "language_sensitivity": {
                "reference_language": "en",
                "target_languages": ["zh-CN", "es"],
                "bootstrap_replicates": 199,
                "confidence_level": 0.95,
                "bootstrap_seed": 123,
            },
        },
    }


def rows():
    output = []
    baseline_shift = {"en": 0.0, "zh-CN": 0.1, "es": 0.2}
    prompt_shift = {"en": 0.0, "zh-CN": 0.05, "es": -0.04}
    for language in ("en", "zh-CN", "es"):
        for condition in ("baseline", "detailed"):
            for seed in range(1, 9):
                value = 0.2 + baseline_shift[language] + 0.01 * seed
                if condition == "detailed":
                    value += 0.03 + prompt_shift[language]
                output.append({
                    "prompt_language": language,
                    "task": "igt",
                    "prompt_condition": condition,
                    "seed": str(seed),
                    "advantageous_choice_rate": str(value),
                })
    return output


class LanguageInteractionTests(unittest.TestCase):
    def test_baseline_contrasts_use_english_reference(self):
        result = build_language_baseline_contrasts(rows(), config=config())
        self.assertEqual(len(result), 2)
        self.assertEqual({row["target_language"] for row in result}, {"zh-CN", "es"})
        self.assertTrue(all(row["reference_language"] == "en" for row in result))
        self.assertAlmostEqual(result[0]["raw_language_difference"], 0.1)

    def test_prompt_interactions_are_target_minus_english(self):
        result = build_language_prompt_interactions(rows(), config=config())
        by_language = {row["target_language"]: row for row in result}
        self.assertAlmostEqual(by_language["zh-CN"]["raw_interaction_contrast"], 0.05)
        self.assertAlmostEqual(by_language["es"]["raw_interaction_contrast"], -0.04)
        self.assertTrue(all(row["bootstrap_unit"] == "independent_cell_run" for row in result))
        self.assertTrue(all(row["raw_ci_lower"] is not None for row in result))

    def test_horizon_interactions_keep_only_complete_matched_seed_blocks(self):
        horizon_config = config()
        horizon_config["tasks"] = {
            "horizon": {"prompt_conditions": ["baseline", "detailed"]}
        }
        horizon_config["analysis"]["prompt_sensitivity"]["primary_metrics"] = {
            "horizon": ["directed_exploration"]
        }
        horizon_rows = []
        for language in ("en", "zh-CN", "es"):
            for condition in ("baseline", "detailed"):
                for seed in (1, 2, 3):
                    if language == "zh-CN" and condition == "detailed" and seed == 3:
                        continue
                    horizon_rows.append({
                        "prompt_language": language,
                        "task": "horizon",
                        "prompt_condition": condition,
                        "seed": str(seed),
                        "directed_exploration": str(
                            seed + (1 if condition == "detailed" else 0)
                        ),
                    })

        result = build_language_prompt_interactions(
            horizon_rows, config=horizon_config
        )
        chinese = next(row for row in result if row["target_language"] == "zh-CN")

        self.assertEqual(chinese["bootstrap_unit"], "matched_seed_block")
        self.assertEqual(chinese["reference_baseline_n"], 2)
        self.assertEqual(chinese["target_condition_n"], 2)


if __name__ == "__main__":
    unittest.main()
