import unittest

from src.tasks.bart import BARTTaskEnvironment
from src.tasks.horizon import HorizonTaskEnvironment
from src.tasks.igt import IGTTaskEnvironment


class MultilingualObservationTests(unittest.TestCase):
    def test_horizon_observation_is_rendered_in_all_languages(self):
        env = HorizonTaskEnvironment(n_games_per_run=1)
        env.reset(seed=7)

        self.assertIn("Game 1 of 1", env.get_observation("en"))
        self.assertIn("第 1 个游戏，共 1 个", env.get_observation("zh-CN"))
        self.assertIn("Juego 1 de 1", env.get_observation("es"))
        self.assertIn("CHOICE", "CHOICE")

    def test_igt_history_is_rendered_in_all_languages(self):
        env = IGTTaskEnvironment(n_trials=3)
        env.reset(seed=1)
        env.step("A")

        self.assertIn("Previous trial:", env.get_observation("en"))
        self.assertIn("上一回合：", env.get_observation("zh-CN"))
        self.assertIn("Turno anterior:", env.get_observation("es"))
        self.assertIn("A, B, C, D", env.get_observation("zh-CN"))

    def test_bart_history_is_rendered_in_all_languages(self):
        env = BARTTaskEnvironment(n_balloons=2)
        env.reset(seed=1)
        env.explosion_points = [32, 32]
        env.step("PUMP")
        env.step("CASH_OUT")

        self.assertIn("Previous balloon:", env.get_observation("en"))
        self.assertIn("上一个气球：", env.get_observation("zh-CN"))
        self.assertIn("Globo anterior:", env.get_observation("es"))
        self.assertIn("PUMP, CASH_OUT", env.get_observation("es"))

    def test_language_rendering_does_not_change_hidden_task_state(self):
        for environment in (
            HorizonTaskEnvironment(n_games_per_run=4),
            BARTTaskEnvironment(n_balloons=4),
        ):
            environment.reset(seed=123)
            before = repr(environment.__dict__)
            for language in ("en", "zh-CN", "es"):
                environment.get_observation(language)
            self.assertEqual(repr(environment.__dict__), before)

    def test_unknown_observation_language_is_rejected(self):
        env = IGTTaskEnvironment(n_trials=1)
        env.reset(seed=1)

        with self.assertRaisesRegex(ValueError, "Unsupported observation language"):
            env.get_observation("fr")


if __name__ == "__main__":
    unittest.main()
