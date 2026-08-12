"""Canonical manuscript-facing names for frozen experiment identifiers.

Machine identifiers remain unchanged in raw and processed data.  Figures,
manuscript tables, and prose-facing outputs should use the labels defined here.
"""

from __future__ import annotations


TASK_LABELS = {
    "horizon": "Horizon Task",
    "igt": "Iowa Gambling Task",
    "bart": "Balloon Analogue Risk Task",
}

PROMPT_CONDITION_LABELS = {
    "baseline": "Neutral baseline",
    "detailed": "Instruction specificity",
    "role_human": "Role framing",
    "uncertainty_emphasis": "Uncertainty and information emphasis",
    "reward_loss_emphasis": "Reward and loss emphasis",
    "risk_emphasis": "Risk-taking and risk-management emphasis",
}

METRIC_LABELS = {
    "directed_exploration": "Information-seeking choice rate",
    "horizon_effect": "Horizon-related exploration change",
    "random_exploration_effect": "Random exploration effect",
    "advantageous_choice_rate": "Advantageous choice rate",
    "post_loss_switching_rate": "Post-loss switching rate",
    "adjusted_average_pumps": "Adjusted average pumps",
    "explosion_rate": "Explosion rate",
    "post_explosion_adjustment": "Post-explosion adjustment",
}

PRIMARY_METRICS = {
    "horizon": (
        "directed_exploration",
        "horizon_effect",
        "random_exploration_effect",
    ),
    "igt": ("advantageous_choice_rate", "post_loss_switching_rate"),
    "bart": (
        "adjusted_average_pumps",
        "explosion_rate",
        "post_explosion_adjustment",
    ),
}

PROMPT_CONDITION_ORDER = {
    condition: index for index, condition in enumerate(PROMPT_CONDITION_LABELS)
}


def task_label(task: str) -> str:
    return TASK_LABELS.get(task, task)


def prompt_condition_label(condition: str) -> str:
    return PROMPT_CONDITION_LABELS.get(condition, condition)


def metric_label(metric: str) -> str:
    return METRIC_LABELS.get(metric, metric)
