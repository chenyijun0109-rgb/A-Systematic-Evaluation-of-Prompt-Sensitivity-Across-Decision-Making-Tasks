from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Protocol

from src.llm_client import OpenAIResponsesClient, get_env_value
from src.parser import parse_response
from src.prompt_loader import extract_response_format, load_config, load_prompt_template, render_prompt
from src.run_random_baseline import build_environment
from src.tasks.bart import BARTTaskEnvironment


DEFAULT_OUTPUT_DIR = Path("outputs/pilot/baseline")
DEFAULT_MAX_OUTPUT_TOKENS = 16
ALL_TASKS = ("horizon", "igt", "bart")
TASK_SEED_OFFSETS = {task: index for index, task in enumerate(ALL_TASKS)}


class PilotClient(Protocol):
    def create_response(
        self,
        *,
        prompt: str,
        model: str,
        max_output_tokens: int,
        temperature: float,
        top_p: float,
    ) -> dict[str, Any]:
        ...


def parse_task_names(value: str) -> tuple[str, ...]:
    if value.strip().lower() == "all":
        return ALL_TASKS

    tasks = tuple(task.strip().lower() for task in value.split(",") if task.strip())
    valid_tasks = set(ALL_TASKS)
    invalid = [task for task in tasks if task not in valid_tasks]
    if invalid:
        raise ValueError(f"Unknown task names: {invalid}. Valid tasks are {ALL_TASKS}.")
    if not tasks:
        raise ValueError("At least one task name is required.")
    return tasks


def task_seed(base_seed: int, task: str) -> int:
    try:
        return base_seed + TASK_SEED_OFFSETS[task]
    except KeyError as exc:
        raise ValueError(f"Unknown task name: {task!r}") from exc


def pilot_output_path(
    output_dir: Path,
    *,
    task: str,
    prompt_condition: str,
    seed: int,
    failed: bool = False,
) -> Path:
    suffix = "_failed" if failed else ""
    return output_dir / f"{task}_{prompt_condition}_seed-{seed}{suffix}.json"


def prompt_sha256(template: str) -> str:
    return hashlib.sha256(template.encode("utf-8")).hexdigest()


def run_baseline_llm_pilot(
    *,
    client: PilotClient,
    model: str | None,
    seed: int,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    task_names: tuple[str, ...] = ALL_TASKS,
    max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
    temperature: float | None = None,
    top_p: float | None = None,
    config_path: Path = Path("configs/experiment_config_stage01.json"),
) -> dict[str, dict[str, Any]]:
    return run_llm_pilot(
        client=client,
        model=model,
        seed=seed,
        output_dir=output_dir,
        prompt_condition="baseline",
        task_names=task_names,
        max_output_tokens=max_output_tokens,
        temperature=temperature,
        top_p=top_p,
        config_path=config_path,
    )


def run_llm_pilot(
    *,
    client: PilotClient,
    model: str | None,
    seed: int,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    prompt_condition: str = "baseline",
    task_names: tuple[str, ...] = ALL_TASKS,
    max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
    temperature: float | None = None,
    top_p: float | None = None,
    config_path: Path = Path("configs/experiment_config_stage01.json"),
) -> dict[str, dict[str, Any]]:
    config = load_config(config_path)
    settings = config["global_settings"]
    resolved_model = str(settings["model_name"]) if model is None else model
    resolved_temperature = (
        float(settings["temperature"]) if temperature is None else temperature
    )
    resolved_top_p = float(settings["top_p"]) if top_p is None else top_p
    output_dir.mkdir(parents=True, exist_ok=True)
    summaries: dict[str, dict[str, Any]] = {}

    for task in task_names:
        current_seed = task_seed(seed, task)
        output_path = pilot_output_path(
            output_dir,
            task=task,
            prompt_condition=prompt_condition,
            seed=current_seed,
        )
        result = _run_single_task(
            task=task,
            client=client,
            model=resolved_model,
            seed=current_seed,
            max_output_tokens=max_output_tokens,
            temperature=resolved_temperature,
            top_p=resolved_top_p,
            config=config,
            prompt_condition=prompt_condition,
            failure_output_path=pilot_output_path(
                output_dir,
                task=task,
                prompt_condition=prompt_condition,
                seed=current_seed,
                failed=True,
            ),
        )
        summaries[task] = {
            "task": task,
            "seed": current_seed,
            "done": result["done"],
            "n_trials": len(result["trial_records"]),
            "invalid_response_count": len(result["invalid_responses"]),
            "parse_success_rate": result["parse_success_rate"],
            "output_path": str(output_path),
        }
        output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    return summaries


def _run_single_task(
    *,
    task: str,
    client: PilotClient,
    model: str,
    seed: int,
    max_output_tokens: int,
    temperature: float,
    top_p: float,
    config: dict[str, Any],
    prompt_condition: str,
    failure_output_path: Path | None = None,
) -> dict[str, Any]:
    environment = build_environment(task, config)
    environment.reset(seed=seed)
    template = load_prompt_template(task, prompt_condition, config=config)
    provenance = {
        "config_name": str(config["config_name"]),
        "config_version": str(config["version"]),
        "prompt_path": str(config["tasks"][task]["prompt_paths"][prompt_condition]),
        "prompt_sha256": prompt_sha256(template),
    }
    response_format = extract_response_format(task, config=config)
    retry_policy = config["global_settings"]["retry_policy"]
    max_retries = int(retry_policy["max_retries_per_trial"])

    raw_llm_outputs: list[dict[str, Any]] = []
    invalid_responses: list[dict[str, Any]] = []
    parse_successes = 0
    parse_attempts = 0

    while not environment.is_done():
        observation = environment.get_observation()
        prompt = render_prompt(template, observation)
        valid_actions = environment.get_valid_actions()
        parsed_action = None
        last_parse = None

        for attempt in range(max_retries + 1):
            llm_response = client.create_response(
                prompt=prompt,
                model=model,
                max_output_tokens=max_output_tokens,
                temperature=temperature,
                top_p=top_p,
            )
            output_text = llm_response["output_text"]
            parse_result = parse_response(
                output_text,
                prefix=response_format.prefix,
                valid_actions=valid_actions,
            )
            last_parse = parse_result
            parse_attempts += 1
            raw_llm_outputs.append(
                {
                    "task": task,
                    "attempt": attempt + 1,
                    "trial_index": len(environment.get_trial_records()) + 1,
                    "observation": observation,
                    "prompt": prompt,
                    "raw_output_text": output_text,
                    "raw_response": llm_response["raw_response"],
                    "parse_success": parse_result.parse_success,
                    "parsed_action": parse_result.parsed_action,
                    "invalid_reason": parse_result.invalid_reason,
                }
            )

            if parse_result.parse_success:
                parse_successes += 1
                parsed_action = parse_result.parsed_action
                break

            invalid_responses.append(
                {
                    "task": task,
                    "attempt": attempt + 1,
                    "trial_index": len(environment.get_trial_records()) + 1,
                    "raw_output_text": output_text,
                    "invalid_reason": parse_result.invalid_reason,
                    "valid_actions": list(valid_actions),
                }
            )

        if parsed_action is None:
            failure_reason = last_parse.invalid_reason if last_parse else "unknown"
            if failure_output_path is not None:
                failed_result = _build_partial_result(
                    task=task,
                    prompt_condition=prompt_condition,
                    model=model,
                    seed=seed,
                    environment=environment,
                    raw_llm_outputs=raw_llm_outputs,
                    invalid_responses=invalid_responses,
                    parse_successes=parse_successes,
                    parse_attempts=parse_attempts,
                    failure_reason=failure_reason,
                    provenance=provenance,
                    temperature=temperature,
                    top_p=top_p,
                    max_output_tokens=max_output_tokens,
                )
                failure_output_path.write_text(
                    json.dumps(failed_result, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
            raise RuntimeError(
                "LLM response could not be parsed after retries: "
                f"{failure_reason}. Debug output: {failure_output_path}"
            )

        environment.step(parsed_action)

    trial_records = environment.get_trial_records()
    result = {
        "task": task,
        "prompt_condition": prompt_condition,
        "model": model,
        **_sampling_provenance(
            requested_model=model,
            temperature=temperature,
            top_p=top_p,
            max_output_tokens=max_output_tokens,
            raw_llm_outputs=raw_llm_outputs,
        ),
        "seed": seed,
        **provenance,
        "done": environment.is_done(),
        "raw_llm_outputs": raw_llm_outputs,
        "invalid_responses": invalid_responses,
        "trial_records": trial_records,
        "run_metrics": environment.get_run_metrics(),
        "parse_success_rate": parse_successes / parse_attempts if parse_attempts else 0.0,
    }
    if isinstance(environment, BARTTaskEnvironment):
        result["balloon_records"] = environment.get_balloon_records()
    return result


def _build_partial_result(
    *,
    task: str,
    prompt_condition: str,
    model: str,
    seed: int,
    environment: Any,
    raw_llm_outputs: list[dict[str, Any]],
    invalid_responses: list[dict[str, Any]],
    parse_successes: int,
    parse_attempts: int,
    failure_reason: str,
    provenance: dict[str, str],
    temperature: float,
    top_p: float,
    max_output_tokens: int,
) -> dict[str, Any]:
    result = {
        "task": task,
        "prompt_condition": prompt_condition,
        "model": model,
        **_sampling_provenance(
            requested_model=model,
            temperature=temperature,
            top_p=top_p,
            max_output_tokens=max_output_tokens,
            raw_llm_outputs=raw_llm_outputs,
        ),
        "seed": seed,
        **provenance,
        "done": environment.is_done(),
        "failure_reason": failure_reason,
        "raw_llm_outputs": raw_llm_outputs,
        "invalid_responses": invalid_responses,
        "trial_records": environment.get_trial_records(),
        "run_metrics": environment.get_run_metrics(),
        "parse_success_rate": parse_successes / parse_attempts if parse_attempts else 0.0,
    }
    if isinstance(environment, BARTTaskEnvironment):
        result["balloon_records"] = environment.get_balloon_records()
    return result


def _sampling_provenance(
    *,
    requested_model: str,
    temperature: float,
    top_p: float,
    max_output_tokens: int,
    raw_llm_outputs: list[dict[str, Any]],
) -> dict[str, Any]:
    raw_response: dict[str, Any] = {}
    if raw_llm_outputs:
        candidate = raw_llm_outputs[0].get("raw_response")
        if isinstance(candidate, dict):
            raw_response = candidate
    return {
        "requested_model": requested_model,
        "resolved_model": str(raw_response.get("model") or requested_model),
        "temperature": float(raw_response.get("temperature", temperature)),
        "top_p": float(raw_response.get("top_p", top_p)),
        "max_output_tokens": int(
            raw_response.get("max_output_tokens", max_output_tokens)
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a small baseline LLM pilot.")
    parser.add_argument(
        "--model",
        help="Explicit override; defaults to global_settings.model_name in the config.",
    )
    parser.add_argument("--seed", type=int, default=20260528)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--condition", default="baseline")
    parser.add_argument("--tasks", default="all", help="Comma-separated task names or 'all'.")
    parser.add_argument("--max-output-tokens", type=int, default=DEFAULT_MAX_OUTPUT_TOKENS)
    parser.add_argument("--temperature", type=float)
    parser.add_argument("--top-p", type=float)
    args = parser.parse_args()

    api_key = get_env_value("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is missing. Set it in PowerShell or in a local .env file.")

    client = OpenAIResponsesClient(api_key=api_key)
    summaries = run_llm_pilot(
        client=client,
        model=args.model,
        seed=args.seed,
        output_dir=args.output_dir,
        prompt_condition=args.condition,
        task_names=parse_task_names(args.tasks),
        max_output_tokens=args.max_output_tokens,
        temperature=args.temperature,
        top_p=args.top_p,
    )
    print(json.dumps(summaries, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
