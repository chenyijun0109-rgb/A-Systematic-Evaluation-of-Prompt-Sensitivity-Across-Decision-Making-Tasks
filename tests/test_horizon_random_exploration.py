import math
import random
import tempfile
import unittest
from pathlib import Path

from src.horizon_random_exploration import (
    ChoiceObservation,
    analyze_choice_observations,
    bootstrap_hierarchical_random_exploration,
    build_choice_observation,
    fit_hierarchical_random_exploration,
    llm_run_id,
    load_human_choice_observations,
    resample_run_clusters,
    run_shrinkage_sensitivity,
)


class HorizonRandomExplorationTests(unittest.TestCase):
    def test_llm_run_id_uses_resolved_source_path_and_seed(self):
        path = Path("outputs/example.json")
        expected = f"{path.resolve().as_posix()}:seed=42"

        self.assertEqual(llm_run_id(path, 42), expected)

    def test_build_choice_observation_uses_information_value_direction(self):
        observation = build_choice_observation(
            {
                "first_free_choice": True,
                "horizon_type": "horizon_6",
                "choice": "A",
                "observed_mean_A": 55.0,
                "observed_mean_B": 50.0,
                "n_observed_A": 1,
                "n_observed_B": 3,
            },
            run_id="run-1",
            prompt_condition="baseline",
        )

        self.assertEqual(observation.delta_reward, 5.0)
        self.assertEqual(observation.delta_information_value, 1.0)
        self.assertEqual(observation.choice_a, 1)

    def test_build_choice_observation_rejects_non_first_free_choice(self):
        with self.assertRaises(ValueError):
            build_choice_observation(
                {
                    "first_free_choice": False,
                    "horizon_type": "horizon_1",
                    "choice": "B",
                    "observed_mean_A": 50.0,
                    "observed_mean_B": 50.0,
                    "n_observed_A": 2,
                    "n_observed_B": 2,
                },
                run_id="run-1",
                prompt_condition="baseline",
            )

    def test_hierarchical_fit_recovers_positive_random_exploration_effect(self):
        observations = self._synthetic_observations()

        result = fit_hierarchical_random_exploration(
            observations,
            run_effect_sd=0.35,
        )

        self.assertTrue(result["converged"])
        condition = result["condition_estimate"]
        self.assertGreater(
            condition["decision_noise_h6"],
            condition["decision_noise_h1"],
        )
        self.assertGreater(condition["random_exploration_effect"], 0.0)
        self.assertEqual(len(result["run_estimates"]), 8)

    def test_single_run_is_reported_as_insufficient(self):
        observations = [
            ChoiceObservation(
                run_id="run-1",
                prompt_condition="baseline",
                horizon_type=horizon,
                choice_a=1,
                delta_reward=5.0,
                delta_information_value=0.0,
            )
            for horizon in ("horizon_1", "horizon_6")
        ]

        result = analyze_choice_observations(observations)

        self.assertEqual(result["baseline"]["status"], "insufficient_runs")

    def test_resample_run_clusters_preserves_whole_runs_and_relabels_duplicates(self):
        observations = self._synthetic_observations()

        sampled = resample_run_clusters(
            observations,
            sampled_run_ids=["run-1", "run-1", "run-3"],
        )

        sampled_ids = {observation.run_id for observation in sampled}
        self.assertEqual(
            sampled_ids,
            {
                "bootstrap_cluster_1:run-1",
                "bootstrap_cluster_2:run-1",
                "bootstrap_cluster_3:run-3",
            },
        )
        original_count = sum(
            observation.run_id == "run-1" for observation in observations
        )
        first_copy_count = sum(
            observation.run_id == "bootstrap_cluster_1:run-1"
            for observation in sampled
        )
        self.assertEqual(first_copy_count, original_count)

    def test_cluster_bootstrap_returns_reproducible_intervals(self):
        observations = self._synthetic_observations()

        first = bootstrap_hierarchical_random_exploration(
            observations,
            run_effect_sd=0.35,
            replicates=8,
            bootstrap_seed=123,
            confidence_level=0.95,
        )
        second = bootstrap_hierarchical_random_exploration(
            observations,
            run_effect_sd=0.35,
            replicates=8,
            bootstrap_seed=123,
            confidence_level=0.95,
        )

        self.assertEqual(first, second)
        self.assertEqual(first["bootstrap_replicates"], 8)
        self.assertGreater(first["successful_fits"], 0)
        self.assertIn("random_exploration_effect_ci_lower", first)
        self.assertTrue(first["diagnostic_only"])

    def test_shrinkage_sensitivity_reports_each_requested_setting(self):
        observations = self._synthetic_observations()

        result = run_shrinkage_sensitivity(
            observations,
            run_effect_sds=(0.25, 0.5, 1.0),
        )

        self.assertEqual(
            [row["run_effect_sd"] for row in result],
            [0.25, 0.5, 1.0],
        )
        self.assertTrue(all(row["converged"] for row in result))

    def test_load_human_observations_uses_first_free_choice(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "human.csv"
            path.write_text(
                "subjectNumber,gameLength,c1,c2,c3,c4,c5,r1,r2,r3,r4,r5\n"
                "1,5,1,2,2,2,1,60,50,52,48,61\n",
                encoding="utf-8",
            )

            observations = load_human_choice_observations(path)

        self.assertEqual(len(observations), 1)
        self.assertEqual(observations[0].run_id, "human:1")
        self.assertEqual(observations[0].delta_information_value, 1.0)
        self.assertAlmostEqual(observations[0].delta_reward, 10.0)

    @staticmethod
    def _synthetic_observations() -> list[ChoiceObservation]:
        rng = random.Random(20260613)
        observations: list[ChoiceObservation] = []
        reward_differences = (-20, -12, -8, -4, 4, 8, 12, 20)

        for run_index in range(8):
            run_shift = (run_index - 3.5) * 0.025
            for horizon, decision_noise in (("horizon_1", 4.0), ("horizon_6", 10.0)):
                for repeat in range(8):
                    for delta_reward in reward_differences:
                        delta_information = (-1.0, 0.0, 1.0)[
                            (repeat + delta_reward + run_index) % 3
                        ]
                        information_bonus = 2.0 if horizon == "horizon_1" else 3.0
                        linear_predictor = (
                            delta_reward
                            + information_bonus * delta_information
                        ) / decision_noise + run_shift
                        probability_a = 1.0 / (1.0 + math.exp(-linear_predictor))
                        observations.append(
                            ChoiceObservation(
                                run_id=f"run-{run_index + 1}",
                                prompt_condition="baseline",
                                horizon_type=horizon,
                                choice_a=1 if rng.random() < probability_a else 0,
                                delta_reward=float(delta_reward),
                                delta_information_value=delta_information,
                            )
                        )

        return observations


if __name__ == "__main__":
    unittest.main()
