import unittest

from src.process_human_metrics import (
    bart_filter_summary,
    process_bart,
    process_horizon,
    process_igt,
)


class ProcessHumanMetricsTests(unittest.TestCase):
    def test_process_horizon_outputs_comparable_metrics(self):
        rows = process_horizon()

        self.assertEqual(len(rows), 60)
        first = rows[0]
        self.assertEqual(first["task"], "horizon")
        self.assertEqual(first["n_games"], 320)
        self.assertIn("average_reward_per_trial", first)
        self.assertIn("exploration_rate", first)
        self.assertIn("directed_exploration", first)
        self.assertIn("horizon_effect", first)
        self.assertNotIn("random_exploration", first)

    def test_process_igt_outputs_comparable_metrics(self):
        rows = process_igt()

        self.assertEqual(len(rows), 504)
        first = rows[0]
        self.assertEqual(first["task"], "igt")
        self.assertEqual(first["n_trials"], 100)
        self.assertIn("net_score", first)
        self.assertIn("advantageous_choice_rate", first)
        self.assertIn("average_net_outcome", first)
        self.assertIn("block_wise_learning_curve", first)

    def test_process_bart_outputs_comparable_metrics(self):
        rows = process_bart()

        self.assertEqual(len(rows), 141)
        participant_ids = {row["participant_id"] for row in rows}
        self.assertTrue({4, 5, 7, 13, 79, 86}.isdisjoint(participant_ids))
        first = rows[0]
        self.assertEqual(first["task"], "bart")
        self.assertEqual(first["n_balloons"], 40)
        self.assertIn("average_pumps", first)
        self.assertIn("adjusted_average_pumps", first)
        self.assertIn("explosion_rate", first)
        self.assertNotIn("cash_out_threshold", first)
        self.assertIn("average_earning_per_balloon", first)
        self.assertEqual(
            sum(row["post_explosion_adjustment"] is None for row in rows),
            1,
        )

    def test_bart_filter_summary_records_age_exclusions(self):
        summary = bart_filter_summary()

        self.assertEqual(summary["minimum_age"], 18)
        self.assertEqual(summary["source_participants"], 147)
        self.assertEqual(summary["included_participants"], 141)
        self.assertEqual(summary["excluded_participants"], 6)
        self.assertEqual(summary["excluded_participant_ids"], [4, 5, 7, 13, 79, 86])
        self.assertEqual(summary["excluded_ages"], [16, 14, 17, 13, 16, 16])
        self.assertEqual(summary["source_rows"], 5880)
        self.assertEqual(summary["included_rows"], 5640)
        self.assertEqual(summary["excluded_rows"], 240)


if __name__ == "__main__":
    unittest.main()
