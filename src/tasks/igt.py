from __future__ import annotations

from collections import Counter
from typing import Any

from src.tasks.base import BaseTaskEnvironment, StepResult
from src.observation_renderer import render_igt_observation


class IGTTaskEnvironment(BaseTaskEnvironment):
    DEFAULT_PAYOFF_SCHEDULE = {
        "A": {
            "gain": 100,
            "losses": (0, -150, 0, -200, 0, -250, 0, -300, 0, -350),
        },
        "B": {
            "gain": 100,
            "losses": (0, 0, 0, 0, 0, 0, 0, 0, 0, -1250),
        },
        "C": {
            "gain": 50,
            "losses": (0, -25, 0, -50, 0, -50, 0, -50, 0, -75),
        },
        "D": {
            "gain": 50,
            "losses": (0, 0, 0, 0, 0, 0, 0, 0, 0, -250),
        },
    }

    def __init__(
        self,
        n_trials: int = 100,
        initial_score: int = 2000,
        block_size: int = 20,
        payoff_schedule: dict[str, dict[str, Any]] | None = None,
    ) -> None:
        self.n_trials = n_trials
        self.initial_score = initial_score
        self.block_size = block_size
        self.payoff_schedule = payoff_schedule or self.DEFAULT_PAYOFF_SCHEDULE
        self.decks = tuple(self.payoff_schedule.keys())
        self.advantageous_decks = ("C", "D")
        self.disadvantageous_decks = ("A", "B")
        self.current_trial = 1
        self.cumulative_score = initial_score
        self.deck_selection_counts: Counter[str] = Counter()
        self.records: list[dict[str, Any]] = []
        self.done = False

    def reset(self, seed: int | None = None) -> None:
        del seed
        self.current_trial = 1
        self.cumulative_score = self.initial_score
        self.deck_selection_counts = Counter()
        self.records = []
        self.done = self.n_trials == 0

    def get_observation(self, language: str = "en") -> str:
        return render_igt_observation(
            language=language,
            done=self.is_done(),
            current_trial=self.current_trial,
            n_trials=self.n_trials,
            cumulative_score=self.cumulative_score,
            records=self.records,
            decks=self.decks,
        )

    def get_valid_actions(self) -> tuple[str, ...]:
        return () if self.is_done() else self.decks

    def step(self, action: str) -> StepResult:
        if self.is_done():
            raise RuntimeError("Cannot step a completed IGT run.")

        deck = action.strip().upper()
        if deck not in self.decks:
            raise ValueError(f"Invalid deck {action!r}; valid decks are {self.decks}.")

        previous_record = self.records[-1] if self.records else None
        previous_deck = previous_record["deck"] if previous_record else None
        previous_loss = previous_record["loss"] if previous_record else None
        post_loss_trial = bool(previous_record and previous_record["loss"] < 0)
        switched_after_loss = (deck != previous_deck) if post_loss_trial else None

        self.deck_selection_counts[deck] += 1
        deck_selection_count = self.deck_selection_counts[deck]
        cycle_index = (deck_selection_count - 1) % 10
        schedule = self.payoff_schedule[deck]
        reward = int(schedule["gain"])
        loss = int(schedule["losses"][cycle_index])
        net_outcome = reward + loss
        self.cumulative_score += net_outcome

        record = {
            "task": "igt",
            "trial_number": self.current_trial,
            "deck": deck,
            "deck_selection_count": deck_selection_count,
            "reward": reward,
            "loss": loss,
            "net_outcome": net_outcome,
            "cumulative_score": self.cumulative_score,
            "block_number": ((self.current_trial - 1) // self.block_size) + 1,
            "advantageous_choice": deck in self.advantageous_decks,
            "previous_deck": previous_deck,
            "previous_loss": previous_loss,
            "post_loss_trial": post_loss_trial,
            "switched_after_loss": switched_after_loss,
        }
        self.records.append(record)

        self.current_trial += 1
        if self.current_trial > self.n_trials:
            self.done = True

        feedback = (
            f"Choice: {deck}. Reward: {reward}. Loss: {loss}. "
            f"Net outcome: {net_outcome}. Cumulative score: {self.cumulative_score}."
        )
        return StepResult(
            observation=self.get_observation(),
            feedback=feedback,
            reward=net_outcome,
            done=self.is_done(),
            info={"record": record},
        )

    def is_done(self) -> bool:
        return self.done

    def get_trial_records(self) -> list[dict[str, Any]]:
        return list(self.records)

    def get_run_metrics(self) -> dict[str, Any]:
        n_trials = len(self.records)
        deck_counts = Counter(record["deck"] for record in self.records)
        advantageous_count = sum(1 for record in self.records if record["advantageous_choice"])
        disadvantageous_count = n_trials - advantageous_count
        post_loss_records = [record for record in self.records if record["post_loss_trial"]]
        switched_after_loss_count = sum(
            1 for record in post_loss_records if record["switched_after_loss"]
        )

        metrics = {
            "n_trials": n_trials,
            "net_score": advantageous_count - disadvantageous_count,
            "advantageous_choice_rate": advantageous_count / n_trials if n_trials else 0.0,
            "deck_A_rate": deck_counts["A"] / n_trials if n_trials else 0.0,
            "deck_B_rate": deck_counts["B"] / n_trials if n_trials else 0.0,
            "deck_C_rate": deck_counts["C"] / n_trials if n_trials else 0.0,
            "deck_D_rate": deck_counts["D"] / n_trials if n_trials else 0.0,
            "average_net_outcome": (
                (self.cumulative_score - self.initial_score) / n_trials if n_trials else 0.0
            ),
            "post_loss_switching_rate": (
                switched_after_loss_count / len(post_loss_records)
                if post_loss_records
                else 0.0
            ),
        }
        metrics["block_wise_learning_curve"] = self._block_wise_net_scores()
        return metrics

    def _block_wise_net_scores(self) -> dict[int, int]:
        scores: dict[int, int] = {}
        for record in self.records:
            block = record["block_number"]
            scores.setdefault(block, 0)
            scores[block] += 1 if record["advantageous_choice"] else -1
        return scores

    def _history_observation_lines(self) -> list[str]:
        previous = self.records[-1]
        lines = [
            "",
            "Previous trial:",
            f"Choice: {previous['deck']}",
            f"Reward: {previous['reward']}",
            f"Loss: {previous['loss']}",
            f"Net outcome: {previous['net_outcome']}",
            "",
            "Deck history summary:",
        ]

        for deck in self.decks:
            deck_records = [record for record in self.records if record["deck"] == deck]
            total_net = sum(record["net_outcome"] for record in deck_records)
            average_net = total_net / len(deck_records) if deck_records else 0.0
            lines.append(
                f"Deck {deck}: selected {len(deck_records)} times, "
                f"total net outcome {total_net}, average net outcome {average_net:.2f}"
            )

        lines.extend(["", "Recent choices and outcomes:"])
        for record in self.records[-5:]:
            lines.append(
                f"Trial {record['trial_number']}: {record['deck']}, "
                f"reward {record['reward']}, loss {record['loss']}, "
                f"net {record['net_outcome']}"
            )
        return lines
