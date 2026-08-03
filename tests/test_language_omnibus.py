import unittest

from src.compute_language_omnibus import (
    build_language_omnibus,
    build_language_prompt_omnibus,
    friedman_statistic,
)


def config():
    return {
        "prompt_languages": ["en", "zh-CN", "es"],
        "tasks": {"igt": {"prompt_conditions": ["baseline", "detailed"]}},
        "analysis": {
            "baseline_condition": "baseline",
            "prompt_sensitivity": {
                "primary_metrics": {"igt": ["advantageous_choice_rate"]},
                "bootstrap_seed": 123,
            },
            "language_sensitivity": {"permutation_replicates": 99},
        },
    }


class LanguageOmnibusTests(unittest.TestCase):
    def test_friedman_statistic_detects_consistent_language_order(self):
        q, w = friedman_statistic(
            [
                [0.1, 0.2, 0.3],
                [0.2, 0.3, 0.4],
                [0.3, 0.4, 0.5],
            ]
        )

        self.assertGreater(q, 0.0)
        self.assertAlmostEqual(w, 1.0)

    def test_all_three_languages_are_analyzed_together(self):
        rows = []
        for language_index, language in enumerate(("en", "zh-CN", "es")):
            for condition_index, condition in enumerate(("baseline", "detailed")):
                for seed in (1, 2, 3):
                    rows.append(
                        {
                            "prompt_language": language,
                            "task": "igt",
                            "prompt_condition": condition,
                            "seed": str(seed),
                            "advantageous_choice_rate": str(
                                0.2
                                + 0.1 * language_index
                                + 0.05 * condition_index * language_index
                                + 0.01 * seed
                            ),
                        }
                    )

        omnibus = build_language_omnibus(rows, config=config())
        interactions = build_language_prompt_omnibus(rows, config=config())

        self.assertEqual(len(omnibus), 2)
        self.assertEqual(len(interactions), 1)
        self.assertTrue(all(row["language_count"] == 3 for row in omnibus))
        self.assertTrue(all(row["languages"] == "en|zh-CN|es" for row in omnibus))
        self.assertEqual(interactions[0]["language_count"], 3)


if __name__ == "__main__":
    unittest.main()
