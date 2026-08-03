from __future__ import annotations

import random
from statistics import mean
from typing import Any

from src.tasks.base import BaseTaskEnvironment, StepResult
from src.observation_renderer import render_bart_observation


class BARTTaskEnvironment(BaseTaskEnvironment):
    def __init__(
        self,
        n_balloons: int = 40,
        balloons_per_block: int = 20,
        pump_reward: float = 0.05,
        certain_explosion_pump: int = 32,
    ) -> None:
        self.n_balloons = n_balloons
        self.balloons_per_block = balloons_per_block
        self.pump_reward = pump_reward
        self.certain_explosion_pump = certain_explosion_pump
        self.rng = random.Random()
        self.explosion_points: list[int] = []
        self.current_balloon = 1
        self.current_pump_count = 0
        self.temporary_earning = 0.0
        self.total_earning = 0.0
        self.action_records: list[dict[str, Any]] = []
        self.balloon_records: list[dict[str, Any]] = []
        self.done = False

    def reset(self, seed: int | None = None) -> None:
        self.rng = random.Random(seed)
        self.explosion_points = [
            self._sample_explosion_point() for _ in range(self.n_balloons)
        ]
        self.current_balloon = 1
        self.current_pump_count = 0
        self.temporary_earning = 0.0
        self.total_earning = 0.0
        self.action_records = []
        self.balloon_records = []
        self.done = self.n_balloons == 0

    def get_observation(self, language: str = "en") -> str:
        return render_bart_observation(
            language=language,
            done=self.is_done(),
            current_balloon=self.current_balloon,
            n_balloons=self.n_balloons,
            block_number=(
                self._current_block()
                if not self.is_done()
                else None
            ),
            current_pump_count=self.current_pump_count,
            temporary_earning=self.temporary_earning,
            total_earning=self.total_earning,
            balloon_records=self.balloon_records,
        )

    def get_valid_actions(self) -> tuple[str, ...]:
        return () if self.is_done() else ("PUMP", "CASH_OUT")

    def step(self, action: str) -> StepResult:
        if self.is_done():
            raise RuntimeError("Cannot step a completed BART run.")

        normalized_action = action.strip().upper()
        if normalized_action not in self.get_valid_actions():
            raise ValueError("Invalid action {!r}; valid actions are PUMP and CASH_OUT.".format(action))

        before_pumps = self.current_pump_count
        before_temporary = self.temporary_earning
        before_total = self.total_earning
        exploded = False
        cashed_out = False
        balloon_ended = False
        reward = 0.0

        if normalized_action == "PUMP":
            self.current_pump_count += 1
            if self.current_pump_count >= self._current_explosion_point():
                exploded = True
                balloon_ended = True
                self.temporary_earning = 0.0
                reward = 0.0
            else:
                self.temporary_earning += self.pump_reward
                reward = self.pump_reward
        else:
            cashed_out = True
            balloon_ended = True
            self.total_earning += self.temporary_earning
            reward = self.temporary_earning

        action_record = {
            "task": "bart",
            "trial_number": len(self.action_records) + 1,
            "balloon_id": self.current_balloon,
            "block_number": self._current_block(),
            "balloon_action_number": before_pumps + 1,
            "action": normalized_action,
            "pump_count_before_action": before_pumps,
            "pump_count_after_action": self.current_pump_count,
            "temporary_earning_before_action": before_temporary,
            "temporary_earning_after_action": self.temporary_earning,
            "total_earning_before_action": before_total,
            "total_earning_after_action": self.total_earning,
            "exploded": exploded,
            "cashed_out": cashed_out,
            "balloon_ended": balloon_ended,
            "explosion_point": self._current_explosion_point(),
        }
        self.action_records.append(action_record)

        feedback = self._feedback(normalized_action, reward, exploded, cashed_out)
        if balloon_ended:
            self._record_balloon(exploded=exploded, cashed_out=cashed_out)
            self._advance_balloon()

        return StepResult(
            observation=self.get_observation(),
            feedback=feedback,
            reward=reward,
            done=self.is_done(),
            info={"record": action_record},
        )

    def is_done(self) -> bool:
        return self.done

    def get_trial_records(self) -> list[dict[str, Any]]:
        return list(self.action_records)

    def get_balloon_records(self) -> list[dict[str, Any]]:
        return list(self.balloon_records)

    def get_run_metrics(self) -> dict[str, Any]:
        n_balloons = len(self.balloon_records)
        pump_counts = [record["final_pump_count"] for record in self.balloon_records]
        unexploded = [record for record in self.balloon_records if not record["exploded"]]
        exploded_count = sum(1 for record in self.balloon_records if record["exploded"])

        return {
            "n_balloons": n_balloons,
            "average_pumps": mean(pump_counts) if pump_counts else 0.0,
            "adjusted_average_pumps": (
                mean(record["final_pump_count"] for record in unexploded)
                if unexploded
                else 0.0
            ),
            "explosion_rate": exploded_count / n_balloons if n_balloons else 0.0,
            "average_earning_per_balloon": self.total_earning / n_balloons if n_balloons else 0.0,
            "post_explosion_adjustment": self._post_explosion_adjustment(),
        }

    def _sample_explosion_point(self) -> int:
        for pump_number in range(1, self.certain_explosion_pump + 1):
            probability = 1 / (self.certain_explosion_pump + 1 - pump_number)
            if self.rng.random() < probability:
                return pump_number
        return self.certain_explosion_pump

    def _current_explosion_point(self) -> int:
        return self.explosion_points[self.current_balloon - 1]

    def _current_block(self) -> int:
        return ((self.current_balloon - 1) // self.balloons_per_block) + 1

    def _record_balloon(self, *, exploded: bool, cashed_out: bool) -> None:
        previous = self.balloon_records[-1] if self.balloon_records else None
        previous_exploded = previous["exploded"] if previous else None
        pump_change = None
        if previous_exploded:
            pump_change = self.current_pump_count - previous["final_pump_count"]

        earning_from_balloon = self.temporary_earning if cashed_out else 0.0
        self.balloon_records.append(
            {
                "task": "bart",
                "balloon_id": self.current_balloon,
                "block_number": self._current_block(),
                "final_pump_count": self.current_pump_count,
                "exploded": exploded,
                "cashed_out": cashed_out,
                "earning_from_balloon": earning_from_balloon,
                "explosion_point": self._current_explosion_point(),
                "previous_balloon_exploded": previous_exploded,
                "pump_change_after_explosion": pump_change,
            }
        )

    def _advance_balloon(self) -> None:
        self.current_balloon += 1
        self.current_pump_count = 0
        self.temporary_earning = 0.0
        if self.current_balloon > self.n_balloons:
            self.done = True

    def _post_explosion_adjustment(self) -> float | None:
        changes = [
            record["pump_change_after_explosion"]
            for record in self.balloon_records
            if record["pump_change_after_explosion"] is not None
        ]
        return mean(changes) if changes else None

    @staticmethod
    def _feedback(action: str, reward: float, exploded: bool, cashed_out: bool) -> str:
        if exploded:
            return "Action: PUMP. The balloon exploded. Temporary earning lost."
        if cashed_out:
            return f"Action: CASH_OUT. Banked earning: {reward:.2f}."
        return f"Action: PUMP. Successful pump reward: {reward:.2f}."

    def _history_observation_lines(self) -> list[str]:
        previous = self.balloon_records[-1]
        outcome = "exploded" if previous["exploded"] else "cashed out"
        exploded_count = sum(1 for record in self.balloon_records if record["exploded"])
        pump_counts = [record["final_pump_count"] for record in self.balloon_records]
        average_pumps = mean(pump_counts) if pump_counts else 0.0

        lines = [
            "",
            "Previous balloon:",
            f"Final pump count: {previous['final_pump_count']}",
            f"Outcome: {outcome}",
            f"Earning: {previous['earning_from_balloon']:.2f}",
            "",
            "Recent balloon outcomes:",
        ]
        for record in self.balloon_records[-5:]:
            record_outcome = "exploded" if record["exploded"] else "cashed out"
            lines.append(
                f"Balloon {record['balloon_id']}: "
                f"{record['final_pump_count']} pumps, {record_outcome}, "
                f"earning {record['earning_from_balloon']:.2f}"
            )

        lines.extend(
            [
                "",
                "Overall so far:",
                f"Balloons completed: {len(self.balloon_records)}",
                f"Explosions: {exploded_count}",
                f"Average pumps: {average_pumps:.2f}",
            ]
        )
        return lines
