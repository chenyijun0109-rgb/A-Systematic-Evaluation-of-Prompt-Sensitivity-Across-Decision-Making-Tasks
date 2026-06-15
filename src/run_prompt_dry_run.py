from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.parser import parse_response
from src.prompt_loader import (
    CONFIG_PATH,
    extract_response_format,
    load_config,
    load_prompt_template,
    render_prompt,
)
from src.run_random_baseline import build_environment


DEFAULT_OUTPUT_PATH = Path("outputs/debug/prompt_dry_run/baseline_prompt_dry_run.json")
MATRIX_DEFAULT_OUTPUT_PATH = Path(
    "outputs/debug/prompt_dry_run/prompt_matrix_dry_run.json"
)


def run_baseline_prompt_dry_run(
    *,
    seed: int,
    output_path: Path = DEFAULT_OUTPUT_PATH,
    config_path: Path = CONFIG_PATH,
) -> dict[str, dict[str, Any]]:
    config = load_config(config_path)
    results: dict[str, dict[str, Any]] = {}

    for offset, task in enumerate(("horizon", "igt", "bart")):
        environment = build_environment(task, config)
        environment.reset(seed=seed + offset)
        observation = environment.get_observation()
        results[task] = _validate_prompt(
            task=task,
            condition="baseline",
            observation=observation,
            config=config,
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    return results


def run_prompt_matrix_dry_run(
    *,
    seed: int,
    output_path: Path = MATRIX_DEFAULT_OUTPUT_PATH,
    config_path: Path = CONFIG_PATH,
) -> dict[str, dict[str, Any]]:
    config = load_config(config_path)
    results: dict[str, dict[str, Any]] = {}

    for offset, task in enumerate(("horizon", "igt", "bart")):
        environment = build_environment(task, config)
        environment.reset(seed=seed + offset)
        observation = environment.get_observation()
        for condition in config["tasks"][task]["prompt_conditions"]:
            key = f"{task}:{condition}"
            results[key] = _validate_prompt(
                task=task,
                condition=condition,
                observation=observation,
                config=config,
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    return results


def _validate_prompt(
    *,
    task: str,
    condition: str,
    observation: str,
    config: dict[str, Any],
) -> dict[str, Any]:
    template = load_prompt_template(task, condition, config=config)
    rendered_prompt = render_prompt(template, observation)
    response_format = extract_response_format(task, config=config)
    parse_checks = [
        parse_response(
            output,
            prefix=response_format.prefix,
            valid_actions=response_format.valid_actions,
        )
        for output in response_format.valid_outputs
    ]

    return {
        "task": task,
        "prompt_condition": condition,
        "prompt_path": config["tasks"][task]["prompt_paths"][condition],
        "observation": observation,
        "rendered_prompt": rendered_prompt,
        "placeholder_replaced": "{observation}" not in rendered_prompt,
        "parser_prefix": response_format.prefix,
        "valid_actions": list(response_format.valid_actions),
        "config_valid_outputs": list(response_format.valid_outputs),
        "all_config_valid_outputs_parse": all(check.parse_success for check in parse_checks),
        "parse_checks": [
            {
                "raw_response": check.raw_response,
                "parse_success": check.parse_success,
                "parsed_action": check.parsed_action,
                "invalid_reason": check.invalid_reason,
                "normalized_response": check.normalized_response,
            }
            for check in parse_checks
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Dry-run baseline prompts without calling an LLM.")
    parser.add_argument("--seed", type=int, default=20260528)
    parser.add_argument("--output-path", type=Path)
    parser.add_argument(
        "--all-conditions",
        action="store_true",
        help="Validate the complete 3-task by 4-condition prompt matrix.",
    )
    args = parser.parse_args()

    if args.all_conditions:
        results = run_prompt_matrix_dry_run(
            seed=args.seed,
            output_path=args.output_path or MATRIX_DEFAULT_OUTPUT_PATH,
        )
    else:
        results = run_baseline_prompt_dry_run(
            seed=args.seed,
            output_path=args.output_path or DEFAULT_OUTPUT_PATH,
        )
    compact = {
        task: {
            "placeholder_replaced": result["placeholder_replaced"],
            "all_config_valid_outputs_parse": result["all_config_valid_outputs_parse"],
            "parser_prefix": result["parser_prefix"],
            "valid_actions": result["valid_actions"],
        }
        for task, result in results.items()
    }
    print(json.dumps(compact, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
