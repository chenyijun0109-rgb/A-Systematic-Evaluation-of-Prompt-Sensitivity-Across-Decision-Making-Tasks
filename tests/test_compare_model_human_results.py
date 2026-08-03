import unittest

from src.compare_model_human_results import combine_model_human_results


def row(condition: str, distance: float, coverage: float = 0.5) -> dict[str, str]:
    return {
        "prompt_language": "en", "task": "igt", "prompt_condition": condition,
        "metric": "advantageous_choice_rate", "llm_n": "20", "human_n": "100",
        "llm_mean": str(0.5 + distance * 0.1), "human_mean": "0.5", "human_sd": "0.1",
        "human_sd_standardised_distance": str(distance), "human_reference_lower": "0.3",
        "human_reference_upper": "0.7", "llm_mean_reference_position": "within",
        "llm_runs_within_human_reference_proportion": str(coverage),
    }


class CompareModelHumanResultsTests(unittest.TestCase):
    def test_combines_models_and_computes_absolute_distance_change(self):
        combined, changes = combine_model_human_results(
            {"A": [row("baseline", -2.0), row("detailed", -1.0, 0.7)],
             "B": [row("baseline", 0.5), row("detailed", 1.0, 0.4)]}
        )
        self.assertEqual(len(combined), 4)
        self.assertEqual(len(changes), 2)
        a_change = next(item for item in changes if item["model"] == "A")
        self.assertEqual(a_change["absolute_distance_change_from_baseline"], -1.0)
        self.assertAlmostEqual(a_change["reference_coverage_change_from_baseline"], 0.2)

    def test_rejects_mismatched_human_references(self):
        mismatch = row("baseline", 0.0)
        mismatch["human_mean"] = "0.6"
        with self.assertRaisesRegex(ValueError, "Human reference mismatch"):
            combine_model_human_results({"A": [row("baseline", 0.0)], "B": [mismatch]})


if __name__ == "__main__":
    unittest.main()
