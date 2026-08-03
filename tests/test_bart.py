import unittest

from src.tasks.bart import BARTTaskEnvironment


class BARTTaskEnvironmentTests(unittest.TestCase):
    def test_reset_initialises_40_balloon_task(self):
        env = BARTTaskEnvironment()
        env.reset(seed=1)

        self.assertFalse(env.is_done())
        self.assertEqual(env.current_balloon, 1)
        self.assertEqual(env.n_balloons, 40)
        self.assertEqual(env.get_valid_actions(), ("PUMP", "CASH_OUT"))
        self.assertIn("Balloon 1 of 40", env.get_observation())
        self.assertIn("Temporary earning: 0.00", env.get_observation())

    def test_rejects_invalid_action(self):
        env = BARTTaskEnvironment()
        env.reset(seed=1)

        with self.assertRaises(ValueError):
            env.step("WAIT")

    def test_cash_out_adds_temporary_earning_and_ends_balloon(self):
        env = BARTTaskEnvironment(n_balloons=1)
        env.reset(seed=1)
        env.explosion_points[0] = 32

        pump_result = env.step("PUMP")
        cash_result = env.step("CASH_OUT")

        self.assertEqual(pump_result.reward, 0.05)
        self.assertTrue(cash_result.done)
        self.assertAlmostEqual(env.total_earning, 0.05)
        summary = env.get_balloon_records()[0]
        self.assertEqual(summary["final_pump_count"], 1)
        self.assertFalse(summary["exploded"])
        self.assertTrue(summary["cashed_out"])
        self.assertAlmostEqual(summary["earning_from_balloon"], 0.05)

    def test_32nd_pump_explodes_with_certain_explosion_point(self):
        env = BARTTaskEnvironment(n_balloons=1)
        env.reset(seed=1)
        env.explosion_points[0] = 32

        for _ in range(31):
            result = env.step("PUMP")
            self.assertFalse(result.done)

        result = env.step("PUMP")

        self.assertTrue(result.done)
        self.assertTrue(env.get_balloon_records()[0]["exploded"])
        self.assertEqual(env.get_balloon_records()[0]["final_pump_count"], 32)
        self.assertAlmostEqual(env.total_earning, 0.0)

    def test_run_completes_and_reports_metrics(self):
        env = BARTTaskEnvironment(n_balloons=4)
        env.reset(seed=2)

        while not env.is_done():
            env.step("CASH_OUT")

        action_records = env.get_trial_records()
        balloon_records = env.get_balloon_records()
        metrics = env.get_run_metrics()

        self.assertEqual(len(action_records), 4)
        self.assertEqual(len(balloon_records), 4)
        self.assertEqual(metrics["n_balloons"], 4)
        self.assertEqual(metrics["average_pumps"], 0.0)
        self.assertEqual(metrics["adjusted_average_pumps"], 0.0)
        self.assertEqual(metrics["explosion_rate"], 0.0)
        self.assertNotIn("cash_out_threshold", metrics)
        self.assertEqual(metrics["average_earning_per_balloon"], 0.0)
        self.assertIsNone(metrics["post_explosion_adjustment"])

    def test_post_explosion_adjustment_uses_only_eligible_transitions(self):
        env = BARTTaskEnvironment(n_balloons=3)
        env.reset(seed=1)
        env.explosion_points = [2, 32, 32]

        env.step("PUMP")
        env.step("PUMP")
        env.step("PUMP")
        env.step("CASH_OUT")
        env.step("PUMP")
        env.step("PUMP")
        env.step("PUMP")
        env.step("CASH_OUT")

        self.assertEqual(env.get_run_metrics()["post_explosion_adjustment"], -1.0)

    def test_same_seed_produces_same_explosion_points(self):
        first = BARTTaskEnvironment(n_balloons=5)
        second = BARTTaskEnvironment(n_balloons=5)

        first.reset(seed=123)
        second.reset(seed=123)

        self.assertEqual(first.explosion_points, second.explosion_points)

    def test_observation_includes_balloon_history_after_completed_balloon(self):
        env = BARTTaskEnvironment(n_balloons=3)
        env.reset(seed=1)
        env.explosion_points = [32, 32, 32]

        env.step("PUMP")
        env.step("CASH_OUT")

        observation = env.get_observation()

        self.assertIn("Previous balloon:", observation)
        self.assertIn("Final pump count: 1", observation)
        self.assertIn("Outcome: cashed out", observation)
        self.assertIn("Recent balloon outcomes:", observation)
        self.assertIn("Balloon 1: 1 pumps, cashed out", observation)
        self.assertIn("Overall so far:", observation)
        self.assertIn("Balloons completed: 1", observation)
        self.assertIn("Explosions: 0", observation)


if __name__ == "__main__":
    unittest.main()
