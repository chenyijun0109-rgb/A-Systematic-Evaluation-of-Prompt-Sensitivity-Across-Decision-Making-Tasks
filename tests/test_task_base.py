import unittest

from src.tasks.base import BaseTaskEnvironment, StepResult


class IncompleteTask(BaseTaskEnvironment):
    pass


class DummyTask(BaseTaskEnvironment):
    def reset(self, seed=None):
        self.seed = seed
        return None

    def get_observation(self):
        return "dummy observation"

    def get_valid_actions(self):
        return ("A", "B")

    def step(self, action):
        return StepResult(
            observation="next observation",
            feedback="feedback",
            reward=1,
            done=True,
            info={"action": action},
        )

    def is_done(self):
        return True

    def get_trial_records(self):
        return []

    def get_run_metrics(self):
        return {"metric": 1}


class BaseTaskEnvironmentTests(unittest.TestCase):
    def test_incomplete_task_cannot_be_instantiated(self):
        with self.assertRaises(TypeError):
            IncompleteTask()

    def test_complete_task_exposes_standard_interface(self):
        task = DummyTask()

        task.reset(seed=123)
        result = task.step("A")

        self.assertEqual(task.seed, 123)
        self.assertEqual(task.get_observation(), "dummy observation")
        self.assertEqual(task.get_valid_actions(), ("A", "B"))
        self.assertTrue(task.is_done())
        self.assertEqual(task.get_trial_records(), [])
        self.assertEqual(task.get_run_metrics(), {"metric": 1})
        self.assertEqual(result.observation, "next observation")
        self.assertEqual(result.feedback, "feedback")
        self.assertEqual(result.reward, 1)
        self.assertTrue(result.done)
        self.assertEqual(result.info, {"action": "A"})


if __name__ == "__main__":
    unittest.main()
