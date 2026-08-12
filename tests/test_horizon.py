import unittest

from src.tasks.horizon import HorizonTaskEnvironment


class HorizonTaskEnvironmentTests(unittest.TestCase):
    def test_reset_creates_configured_games_and_initial_forced_choice(self):
        env = HorizonTaskEnvironment(n_games_per_run=4)
        env.reset(seed=7)

        self.assertFalse(env.is_done())
        self.assertEqual(len(env.games), 4)
        self.assertEqual(len(env.get_valid_actions()), 1)
        self.assertIn("Forced choice", env.get_observation())
        self.assertIn("Game 1 of 4", env.get_observation())

    def test_forced_choice_rejects_non_required_action(self):
        env = HorizonTaskEnvironment(n_games_per_run=1)
        env.reset(seed=11)

        required = env.get_valid_actions()[0]
        invalid = "B" if required == "A" else "A"

        with self.assertRaises(ValueError):
            env.step(invalid)

    def test_observation_is_participant_facing_and_reports_remaining_choices(self):
        env = HorizonTaskEnvironment(n_games_per_run=2)
        env.reset(seed=7)

        observation = env.get_observation()

        self.assertIn("Choices remaining in this game: 5", observation)
        for analysis_label in (
            "horizon_1",
            "horizon_6",
            "equal_information",
            "unequal_information",
        ):
            with self.subTest(analysis_label=analysis_label):
                self.assertNotIn(analysis_label, observation)

    def test_run_completes_and_records_all_trials(self):
        env = HorizonTaskEnvironment(n_games_per_run=6)
        env.reset(seed=42)

        while not env.is_done():
            env.step(env.get_valid_actions()[0])

        records = env.get_trial_records()
        metrics = env.get_run_metrics()

        self.assertTrue(env.is_done())
        self.assertEqual(len(records), sum(game["total_trials"] for game in env.games))
        self.assertEqual(metrics["n_games"], 6)
        self.assertEqual(metrics["n_trials"], len(records))
        self.assertIn("average_reward_per_trial", metrics)
        self.assertIn("switching_rate", metrics)
        self.assertIn("exploration_rate", metrics)
        self.assertIn("directed_exploration", metrics)
        self.assertNotIn("random_exploration", metrics)

    def test_same_seed_produces_same_rewards_for_same_policy(self):
        first = self._run_choose_first_valid(seed=123)
        second = self._run_choose_first_valid(seed=123)

        self.assertEqual(
            [record["reward"] for record in first.get_trial_records()],
            [record["reward"] for record in second.get_trial_records()],
        )
        self.assertEqual(first.get_run_metrics(), second.get_run_metrics())

    def test_exploration_rate_excludes_equal_observed_means(self):
        records = [
            {
                "observed_mean_A": 50.0,
                "observed_mean_B": 50.0,
                "choice": "A",
            },
            {
                "observed_mean_A": 60.0,
                "observed_mean_B": 40.0,
                "choice": "B",
            },
        ]

        self.assertEqual(HorizonTaskEnvironment._exploration_rate(records), 1.0)

    def test_exploration_rate_is_missing_without_eligible_choices(self):
        records = [
            {
                "observed_mean_A": 50.0,
                "observed_mean_B": 50.0,
                "choice": "A",
            }
        ]

        self.assertIsNone(HorizonTaskEnvironment._exploration_rate(records))

    def _run_choose_first_valid(self, seed):
        env = HorizonTaskEnvironment(n_games_per_run=4)
        env.reset(seed=seed)
        while not env.is_done():
            env.step(env.get_valid_actions()[0])
        return env


if __name__ == "__main__":
    unittest.main()
