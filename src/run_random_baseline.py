from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any

from src.tasks.base import BaseTaskEnvironment
from src.tasks.bart import BARTTaskEnvironment
from src.tasks.horizon import HorizonTaskEnvironment
from src.tasks.igt import IGTTaskEnvironment


CONFIG_PATH = Path("configs/experiment_config_stage01.json")
DEFAULT_OUTPUT_DIR = Path("outputs/debug/random_baseline")


def load_config(config_path: Path = CONFIG_PATH) -> dict[str, Any]:
    return json.loads(config_path.read_text(encoding="utf-8"))


def build_environment(task: str, config: dict[str, Any] | None = None) -> BaseTaskEnvironment:
    config = config or load_config()
    task_key = task.lower()
    parameters = config["tasks"][task_key]["parameters"]

    if task_key == "horizon":
        reward_distribution = parameters["reward_distribution"]
        return HorizonTaskEnvironment(
            n_games_per_run=parameters["n_games_per_run"],
            reward_sd=reward_distribution["sd"],
            base_means=tuple(reward_distribution["base_means"]),
            mean_differences=tuple(reward_distribution["mean_differences"]),
            display_bounds=tuple(reward_distribution["display_bounds"]),
        )

    if task_key == "igt":
        return IGTTaskEnvironment(
            n_trials=parameters["n_trials"],
            initial_score=parameters["initial_score"],
            block_size=parameters["block_size"],
        )

    if task_key == "bart":
        block_structure = parameters["block_structure"]
        return BARTTaskEnvironment(
            n_balloons=parameters["n_balloons"],
            balloons_per_block=block_structure["balloons_per_block"],
            pump_reward=parameters["pump_reward"],
            certain_explosion_pump=parameters["explosion_rule"]["certain_explosion_pump"],
        )

    raise ValueError(f"Unknown task {task!r}.")


def run_random_baseline(
    task: str,
    *,
    seed: int,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    config = config or load_config()
    environment = build_environment(task, config)
    environment.reset(seed=seed)
    rng = random.Random(seed)

    while not environment.is_done():
        valid_actions = environment.get_valid_actions()
        if not valid_actions:
            break
        environment.step(rng.choice(valid_actions))

    records = environment.get_trial_records()
    result = {
        "task": task,
        "seed": seed,
        "done": environment.is_done(),
        "n_records": len(records),
        "records": records,
        "metrics": environment.get_run_metrics(),
    }
    if isinstance(environment, BARTTaskEnvironment):
        result["balloon_records"] = environment.get_balloon_records()
    return result


def run_all_random_baselines(
    *,
    seed: int,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    config_path: Path = CONFIG_PATH,
) -> dict[str, dict[str, Any]]:
    config = load_config(config_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    summaries = {}
    for offset, task in enumerate(("horizon", "igt", "bart")):
        result = run_random_baseline(task, seed=seed + offset, config=config)
        summaries[task] = result
        output_path = output_dir / f"{task}_random_baseline.json"
        output_path.write_text(
            json.dumps(result, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    return summaries


def main() -> None:
    parser = argparse.ArgumentParser(description="Run random baselines for all task environments.")
    parser.add_argument("--seed", type=int, default=20260528)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    summaries = run_all_random_baselines(seed=args.seed, output_dir=args.output_dir)
    compact = {
        task: {
            "done": result["done"],
            "n_records": result["n_records"],
            "metrics": result["metrics"],
        }
        for task, result in summaries.items()
    }
    print(json.dumps(compact, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
