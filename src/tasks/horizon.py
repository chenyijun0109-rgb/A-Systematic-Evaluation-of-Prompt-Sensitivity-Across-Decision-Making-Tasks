from __future__ import annotations

import random
from statistics import mean
from typing import Any

from src.tasks.base import BaseTaskEnvironment, StepResult
from src.observation_renderer import render_horizon_observation


class HorizonTaskEnvironment(BaseTaskEnvironment):
    def __init__(
        self,
        n_games_per_run: int = 40,
        reward_sd: float = 8.0,
        base_means: tuple[int, ...] = (40, 60),
        mean_differences: tuple[int, ...] = (-30, -20, -12, -8, -4, 4, 8, 12, 20, 30),
        display_bounds: tuple[int, int] = (1, 100),
    ) -> None:
        self.n_games_per_run = n_games_per_run
        self.reward_sd = reward_sd
        self.base_means = base_means
        self.mean_differences = mean_differences
        self.display_bounds = display_bounds
        self.rng = random.Random()
        self.games: list[dict[str, Any]] = []
        self.records: list[dict[str, Any]] = []
        self.current_game_index = 0
        self.current_trial_index = 0
        self.done = False

    def reset(self, seed: int | None = None) -> None:
        self.rng = random.Random(seed)
        self.games = [self._create_game(game_id) for game_id in range(1, self.n_games_per_run + 1)]
        self.records = []
        self.current_game_index = 0
        self.current_trial_index = 0
        self.done = self.n_games_per_run == 0

    def get_observation(self, language: str = "en") -> str:
        if self.is_done():
            return render_horizon_observation(language=language, done=True)
        game = self._current_game()
        trial_number = self.current_trial_index + 1
        choices_remaining = game["total_trials"] - self.current_trial_index
        forced_target = self._forced_target(game)
        return render_horizon_observation(
            language=language,
            done=False,
            game_id=game["game_id"],
            n_games=self.n_games_per_run,
            trial_number=trial_number,
            total_trials=game["total_trials"],
            choices_remaining=choices_remaining,
            rewards_a=game["observed_rewards"]["A"],
            rewards_b=game["observed_rewards"]["B"],
            forced_target=forced_target,
        )

    def get_valid_actions(self) -> tuple[str, ...]:
        if self.is_done():
            return ()

        forced_target = self._forced_target(self._current_game())
        if forced_target is not None:
            return (forced_target,)
        return ("A", "B")

    def step(self, action: str) -> StepResult:
        if self.is_done():
            raise RuntimeError("Cannot step a completed Horizon Task run.")

        normalized_action = action.strip().upper()
        valid_actions = self.get_valid_actions()
        if normalized_action not in valid_actions:
            raise ValueError(f"Invalid action {action!r}; valid actions are {valid_actions}.")

        game = self._current_game()
        trial_number = self.current_trial_index + 1
        forced_target = self._forced_target(game)
        histories_before = {
            "A": list(game["observed_rewards"]["A"]),
            "B": list(game["observed_rewards"]["B"]),
        }
        n_observed_a = len(histories_before["A"])
        n_observed_b = len(histories_before["B"])
        observed_mean_a = self._safe_mean(histories_before["A"])
        observed_mean_b = self._safe_mean(histories_before["B"])

        reward = self._sample_reward(game["means"][normalized_action])
        game["observed_rewards"][normalized_action].append(reward)

        record = {
            "task": "horizon",
            "game_id": game["game_id"],
            "trial_number": len(self.records) + 1,
            "game_trial_number": trial_number,
            "horizon_type": game["horizon_type"],
            "information_condition": game["information_condition"],
            "is_forced_choice": forced_target is not None,
            "forced_choice_target": forced_target,
            "choice": normalized_action,
            "reward": reward,
            "mean_A": game["means"]["A"],
            "mean_B": game["means"]["B"],
            "observed_rewards_A": histories_before["A"],
            "observed_rewards_B": histories_before["B"],
            "n_observed_A": n_observed_a,
            "n_observed_B": n_observed_b,
            "observed_mean_A": observed_mean_a,
            "observed_mean_B": observed_mean_b,
            "information_difference": n_observed_a - n_observed_b,
            "observed_mean_difference": self._mean_difference(observed_mean_a, observed_mean_b),
            "first_free_choice": forced_target is None and self.current_trial_index == 4,
        }
        self.records.append(record)

        self._advance()
        feedback = f"Choice: {normalized_action}. Reward: {reward}."
        return StepResult(
            observation=self.get_observation(),
            feedback=feedback,
            reward=reward,
            done=self.is_done(),
            info={"record": record},
        )

    def is_done(self) -> bool:
        return self.done

    def get_trial_records(self) -> list[dict[str, Any]]:
        return list(self.records)

    def get_run_metrics(self) -> dict[str, Any]:
        cumulative_reward = sum(record["reward"] for record in self.records)
        choices = [record["choice"] for record in self.records]
        switches = sum(1 for previous, current in zip(choices, choices[1:]) if previous != current)
        switching_rate = switches / (len(choices) - 1) if len(choices) > 1 else 0.0

        free_records = [record for record in self.records if not record["is_forced_choice"]]
        first_free_records = [record for record in self.records if record["first_free_choice"]]

        exploration_rate = self._exploration_rate(free_records)
        horizon_1_exploration = self._exploration_rate(
            [record for record in first_free_records if record["horizon_type"] == "horizon_1"]
        )
        horizon_6_exploration = self._exploration_rate(
            [record for record in first_free_records if record["horizon_type"] == "horizon_6"]
        )
        directed_exploration = self._directed_exploration(first_free_records)

        return {
            "n_games": len(self.games),
            "n_trials": len(self.records),
            "average_reward_per_trial": cumulative_reward / len(self.records) if self.records else 0.0,
            "switching_rate": switching_rate,
            "exploration_rate": exploration_rate,
            "directed_exploration": directed_exploration,
            "horizon_effect": horizon_6_exploration - horizon_1_exploration,
        }

    def _create_game(self, game_id: int) -> dict[str, Any]:
        horizon_type = "horizon_1" if game_id % 2 else "horizon_6"
        total_trials = 5 if horizon_type == "horizon_1" else 10
        information_condition = "unequal_information" if game_id % 4 in (1, 2) else "equal_information"
        forced_sequence = self._create_forced_sequence(information_condition)
        means = self._create_option_means()

        return {
            "game_id": game_id,
            "horizon_type": horizon_type,
            "information_condition": information_condition,
            "total_trials": total_trials,
            "forced_sequence": forced_sequence,
            "means": means,
            "observed_rewards": {"A": [], "B": []},
        }

    def _create_forced_sequence(self, information_condition: str) -> list[str]:
        if information_condition == "equal_information":
            sequence = ["A", "A", "B", "B"]
        else:
            rare_option = self.rng.choice(("A", "B"))
            common_option = "B" if rare_option == "A" else "A"
            sequence = [rare_option, common_option, common_option, common_option]
        self.rng.shuffle(sequence)
        return sequence

    def _create_option_means(self) -> dict[str, int]:
        first_mean = self.rng.choice(self.base_means)
        second_mean = first_mean + self.rng.choice(self.mean_differences)
        low, high = self.display_bounds
        second_mean = max(low, min(high, second_mean))

        if self.rng.choice((True, False)):
            return {"A": first_mean, "B": second_mean}
        return {"A": second_mean, "B": first_mean}

    def _sample_reward(self, option_mean: float) -> int:
        reward = round(self.rng.gauss(option_mean, self.reward_sd))
        low, high = self.display_bounds
        return max(low, min(high, reward))

    def _advance(self) -> None:
        self.current_trial_index += 1
        if self.current_trial_index >= self._current_game()["total_trials"]:
            self.current_game_index += 1
            self.current_trial_index = 0
            if self.current_game_index >= len(self.games):
                self.done = True

    def _current_game(self) -> dict[str, Any]:
        return self.games[self.current_game_index]

    def _forced_target(self, game: dict[str, Any]) -> str | None:
        if self.current_trial_index < len(game["forced_sequence"]):
            return game["forced_sequence"][self.current_trial_index]
        return None

    @staticmethod
    def _safe_mean(values: list[int]) -> float | None:
        return mean(values) if values else None

    @staticmethod
    def _mean_difference(left: float | None, right: float | None) -> float | None:
        if left is None or right is None:
            return None
        return left - right

    @staticmethod
    def _exploration_rate(records: list[dict[str, Any]]) -> float:
        eligible = [
            record
            for record in records
            if record["observed_mean_A"] is not None and record["observed_mean_B"] is not None
        ]
        if not eligible:
            return 0.0

        exploratory_choices = 0
        for record in eligible:
            if record["observed_mean_A"] == record["observed_mean_B"]:
                continue
            best_option = "A" if record["observed_mean_A"] > record["observed_mean_B"] else "B"
            if record["choice"] != best_option:
                exploratory_choices += 1

        return exploratory_choices / len(eligible)

    @staticmethod
    def _directed_exploration(records: list[dict[str, Any]]) -> float:
        eligible = [
            record
            for record in records
            if record["information_condition"] == "unequal_information"
            and record["n_observed_A"] != record["n_observed_B"]
        ]
        if not eligible:
            return 0.0

        directed_choices = 0
        for record in eligible:
            less_observed_option = "A" if record["n_observed_A"] < record["n_observed_B"] else "B"
            if record["choice"] == less_observed_option:
                directed_choices += 1

        return directed_choices / len(eligible)
