from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class StepResult:
    observation: str
    feedback: str
    reward: float | int | None
    done: bool
    info: dict[str, Any] = field(default_factory=dict)


class BaseTaskEnvironment(ABC):
    @abstractmethod
    def reset(self, seed: int | None = None) -> Any:
        """Reset the environment and optionally set a seed."""

    @abstractmethod
    def get_observation(self) -> str:
        """Return the current observation text for a prompt."""

    @abstractmethod
    def get_valid_actions(self) -> tuple[str, ...]:
        """Return the currently valid action labels."""

    @abstractmethod
    def step(self, action: str) -> StepResult:
        """Apply one action and return the resulting transition."""

    @abstractmethod
    def is_done(self) -> bool:
        """Return whether the current run is complete."""

    @abstractmethod
    def get_trial_records(self) -> list[dict[str, Any]]:
        """Return trial-level or action-level records."""

    @abstractmethod
    def get_run_metrics(self) -> dict[str, Any]:
        """Return run-level behavioural metrics."""
