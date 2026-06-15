import unittest

from src.tasks.igt import IGTTaskEnvironment


class IGTTaskEnvironmentTests(unittest.TestCase):
    def test_reset_initialises_100_trial_task(self):
        env = IGTTaskEnvironment()
        env.reset(seed=1)

        self.assertFalse(env.is_done())
        self.assertEqual(env.current_trial, 1)
        self.assertEqual(env.cumulative_score, 2000)
        self.assertEqual(env.get_valid_actions(), ("A", "B", "C", "D"))
        self.assertIn("Trial 1 of 100", env.get_observation())

    def test_rejects_invalid_deck(self):
        env = IGTTaskEnvironment()
        env.reset(seed=1)

        with self.assertRaises(ValueError):
            env.step("E")

    def test_payoff_cycles_match_classic_long_term_returns(self):
        expected_net = {"A": -250, "B": -250, "C": 250, "D": 250}

        for deck, net in expected_net.items():
            with self.subTest(deck=deck):
                env = IGTTaskEnvironment(n_trials=10, initial_score=0)
                env.reset(seed=1)
                for _ in range(10):
                    env.step(deck)

                self.assertTrue(env.is_done())
                self.assertEqual(env.cumulative_score, net)
                self.assertEqual(env.get_run_metrics()["average_net_outcome"], net / 10)

    def test_run_completes_and_records_all_trials(self):
        env = IGTTaskEnvironment()
        env.reset(seed=7)
        policy = ("A", "B", "C", "D")

        while not env.is_done():
            env.step(policy[(env.current_trial - 1) % len(policy)])

        records = env.get_trial_records()
        metrics = env.get_run_metrics()

        self.assertEqual(len(records), 100)
        self.assertEqual(metrics["n_trials"], 100)
        self.assertEqual(metrics["net_score"], 0)
        self.assertEqual(metrics["advantageous_choice_rate"], 0.5)
        self.assertEqual(metrics["deck_A_rate"], 0.25)
        self.assertEqual(metrics["deck_B_rate"], 0.25)
        self.assertEqual(metrics["deck_C_rate"], 0.25)
        self.assertEqual(metrics["deck_D_rate"], 0.25)
        self.assertIn("post_loss_switching_rate", metrics)

    def test_records_post_loss_switching(self):
        env = IGTTaskEnvironment(n_trials=3)
        env.reset(seed=1)

        env.step("A")
        env.step("A")
        env.step("B")

        records = env.get_trial_records()
        self.assertFalse(records[1]["post_loss_trial"])
        self.assertTrue(records[2]["post_loss_trial"])
        self.assertTrue(records[2]["switched_after_loss"])

    def test_observation_includes_history_summary_after_feedback(self):
        env = IGTTaskEnvironment(n_trials=5)
        env.reset(seed=1)

        env.step("A")
        env.step("B")

        observation = env.get_observation()

        self.assertIn("Previous trial:", observation)
        self.assertIn("Choice: B", observation)
        self.assertIn("Deck history summary:", observation)
        self.assertIn("Deck A: selected 1 times", observation)
        self.assertIn("Deck B: selected 1 times", observation)
        self.assertIn("Recent choices and outcomes:", observation)
        self.assertIn("Trial 1: A", observation)
        self.assertIn("Trial 2: B", observation)


if __name__ == "__main__":
    unittest.main()
