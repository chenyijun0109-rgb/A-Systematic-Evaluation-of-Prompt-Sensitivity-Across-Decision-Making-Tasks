from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CONFIG_PATH = Path("configs/experiment_config_stage01.json")


@dataclass(frozen=True)
class ResponseFormat:
    prefix: str
    valid_actions: tuple[str, ...]
    valid_outputs: tuple[str, ...]


def load_config(config_path: Path = CONFIG_PATH) -> dict[str, Any]:
    return json.loads(config_path.read_text(encoding="utf-8"))


def load_prompt_template(
    task: str,
    condition: str = "baseline",
    *,
    config: dict[str, Any] | None = None,
) -> str:
    config = config or load_config()
    task_key = task.lower()
    prompt_paths = config["tasks"][task_key]["prompt_paths"]
    if condition not in prompt_paths:
        available = ", ".join(sorted(prompt_paths))
        raise ValueError(
            f"Prompt condition {condition!r} is not currently available for task "
            f"{task_key!r}. Available conditions: {available}."
        )

    prompt_path = Path(prompt_paths[condition])
    if not prompt_path.is_file():
        raise ValueError(
            f"Prompt condition {condition!r} is not currently available for task "
            f"{task_key!r}: missing file {prompt_path}."
        )
    return prompt_path.read_text(encoding="utf-8")


def render_prompt(template: str, observation: str) -> str:
    return template.replace("{observation}", observation)


def extract_response_format(
    task: str,
    *,
    config: dict[str, Any] | None = None,
) -> ResponseFormat:
    config = config or load_config()
    task_key = task.lower()
    valid_outputs = tuple(config["tasks"][task_key]["response_format"]["valid_outputs"])
    prefixes: set[str] = set()
    actions: list[str] = []

    for output in valid_outputs:
        prefix, action = output.split(":", maxsplit=1)
        prefixes.add(prefix.strip().upper())
        actions.append(action.strip().upper())

    if len(prefixes) != 1:
        raise ValueError(f"Task {task!r} has inconsistent response prefixes: {valid_outputs!r}.")

    return ResponseFormat(
        prefix=prefixes.pop(),
        valid_actions=tuple(actions),
        valid_outputs=valid_outputs,
    )
