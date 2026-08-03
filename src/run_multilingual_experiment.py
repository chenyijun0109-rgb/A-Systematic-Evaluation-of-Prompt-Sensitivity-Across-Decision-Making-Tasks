from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from src.llm_client import OpenAIResponsesClient, get_env_value
from src.prompt_loader import CONFIG_PATH, load_config
from src.run_llm_pilot import (
    DEFAULT_MAX_OUTPUT_TOKENS,
    pilot_output_path,
    run_llm_pilot,
    task_seed,
)


DEFAULT_OUTPUT_DIR = Path("outputs/multilingual_pilot_v01")


@dataclass(frozen=True)
class PlannedRun:
    language: str
    task: str
    prompt_condition: str
    base_seed: int
    task_seed: int
    output_path: str


def parse_csv_values(value: str) -> tuple[str, ...]:
    values = tuple(item.strip() for item in value.split(",") if item.strip())
    if not values:
        raise ValueError("At least one comma-separated value is required.")
    return values


def parse_seeds(value: str) -> tuple[int, ...]:
    seeds = tuple(int(item) for item in parse_csv_values(value))
    if len(set(seeds)) != len(seeds):
        raise ValueError("Seeds must be unique.")
    return seeds


def build_experiment_plan(
    *,
    config: dict[str, Any],
    languages: tuple[str, ...],
    seeds: tuple[int, ...],
    output_dir: Path,
) -> list[PlannedRun]:
    configured_languages = set(config.get("prompt_languages", ["en"]))
    unknown = sorted(set(languages).difference(configured_languages))
    if unknown:
        raise ValueError(f"Unknown prompt languages: {unknown}.")
    plan: list[PlannedRun] = []
    for base_seed in seeds:
        for language in languages:
            for task, task_config in config["tasks"].items():
                for condition in task_config["prompt_conditions"]:
                    current_seed = task_seed(base_seed, task)
                    path = pilot_output_path(
                        output_dir / language,
                        task=task,
                        prompt_condition=condition,
                        seed=current_seed,
                        language=language,
                    )
                    plan.append(
                        PlannedRun(
                            language=language,
                            task=task,
                            prompt_condition=condition,
                            base_seed=base_seed,
                            task_seed=current_seed,
                            output_path=str(path),
                        )
                    )
    return plan


def successful_existing_run(path: Path, planned: PlannedRun) -> bool:
    if not path.is_file():
        return False
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return bool(
        payload.get("done")
        and payload.get("prompt_language", "en") == planned.language
        and payload.get("task") == planned.task
        and payload.get("prompt_condition") == planned.prompt_condition
        and int(payload.get("seed", -1)) == planned.task_seed
    )


def request_bounds(plan: list[PlannedRun], config: dict[str, Any]) -> dict[str, int]:
    by_task = {"horizon": 0, "igt": 0, "bart": 0}
    for item in plan:
        by_task[item.task] += 1
    horizon = config["tasks"]["horizon"]["parameters"]
    horizon_per_run = (
        horizon["n_games_per_run"] // 2
        * (
            horizon["horizon_conditions"]["horizon_1"]["total_trials_per_game"]
            + horizon["horizon_conditions"]["horizon_6"]["total_trials_per_game"]
        )
    )
    igt_per_run = int(config["tasks"]["igt"]["parameters"]["n_trials"])
    bart = config["tasks"]["bart"]["parameters"]
    bart_minimum = int(bart["n_balloons"])
    bart_maximum = bart_minimum * int(
        bart["explosion_rule"]["certain_explosion_pump"]
    )
    fixed = by_task["horizon"] * horizon_per_run + by_task["igt"] * igt_per_run
    return {
        "planned_task_runs": len(plan),
        "horizon_requests": by_task["horizon"] * horizon_per_run,
        "igt_requests": by_task["igt"] * igt_per_run,
        "bart_minimum_requests": by_task["bart"] * bart_minimum,
        "bart_maximum_requests": by_task["bart"] * bart_maximum,
        "total_minimum_requests": fixed + by_task["bart"] * bart_minimum,
        "total_maximum_requests": fixed + by_task["bart"] * bart_maximum,
    }


def _write_status(
    path: Path,
    *,
    plan: list[PlannedRun],
    completed: list[dict[str, Any]],
    skipped: list[dict[str, Any]],
    failed: list[dict[str, Any]],
    request_estimate: dict[str, int],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "planned_run_count": len(plan),
        "completed_count": len(completed),
        "skipped_count": len(skipped),
        "failed_count": len(failed),
        "request_estimate": request_estimate,
        "completed": completed,
        "skipped": skipped,
        "failed": failed,
        "plan": [asdict(item) for item in plan],
    }
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def run_multilingual_experiment(
    *,
    client: Any,
    model: str | None,
    languages: tuple[str, ...],
    seeds: tuple[int, ...],
    output_dir: Path,
    resume: bool = True,
    skip_recorded_failures: bool = False,
    stop_on_error: bool = False,
    max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
    temperature: float | None = None,
    top_p: float | None = None,
    config_path: Path = CONFIG_PATH,
) -> dict[str, Any]:
    config = load_config(config_path)
    plan = build_experiment_plan(
        config=config,
        languages=languages,
        seeds=seeds,
        output_dir=output_dir,
    )
    request_estimate = request_bounds(plan, config)
    status_path = output_dir / "multilingual_run_status.json"
    completed: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []
    recorded_failure_paths: set[str] = set()
    if skip_recorded_failures and status_path.is_file():
        try:
            prior_status = json.loads(status_path.read_text(encoding="utf-8"))
            failed = list(prior_status.get("failed", []))
            recorded_failure_paths = {
                str(item["output_path"])
                for item in failed
                if item.get("output_path")
            }
        except (OSError, json.JSONDecodeError, TypeError):
            failed = []
            recorded_failure_paths = set()

    for planned in plan:
        path = Path(planned.output_path)
        if resume and successful_existing_run(path, planned):
            skipped.append({**asdict(planned), "reason": "existing_success"})
            _write_status(
                status_path,
                plan=plan,
                completed=completed,
                skipped=skipped,
                failed=failed,
                request_estimate=request_estimate,
            )
            continue
        if skip_recorded_failures and planned.output_path in recorded_failure_paths:
            skipped.append(
                {**asdict(planned), "reason": "recorded_failure_deferred"}
            )
            _write_status(
                status_path,
                plan=plan,
                completed=completed,
                skipped=skipped,
                failed=failed,
                request_estimate=request_estimate,
            )
            continue
        try:
            summary = run_llm_pilot(
                client=client,
                model=model,
                seed=planned.base_seed,
                output_dir=output_dir / planned.language,
                prompt_condition=planned.prompt_condition,
                task_names=(planned.task,),
                max_output_tokens=max_output_tokens,
                temperature=temperature,
                top_p=top_p,
                language=planned.language,
                config_path=config_path,
            )
            completed.append(
                {
                    **asdict(planned),
                    "summary": summary[planned.task],
                }
            )
        except Exception as error:
            failed.append(
                {
                    **asdict(planned),
                    "error_type": type(error).__name__,
                    "error": str(error),
                }
            )
            _write_status(
                status_path,
                plan=plan,
                completed=completed,
                skipped=skipped,
                failed=failed,
                request_estimate=request_estimate,
            )
            if stop_on_error:
                raise
        _write_status(
            status_path,
            plan=plan,
            completed=completed,
            skipped=skipped,
            failed=failed,
            request_estimate=request_estimate,
        )

    _write_status(
        status_path,
        plan=plan,
        completed=completed,
        skipped=skipped,
        failed=failed,
        request_estimate=request_estimate,
    )
    return {
        "planned_run_count": len(plan),
        "completed_count": len(completed),
        "skipped_count": len(skipped),
        "failed_count": len(failed),
        "request_estimate": request_estimate,
        "status_path": str(status_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a resumable multilingual task-condition-seed matrix."
    )
    parser.add_argument("--languages", default="en,zh-CN,es")
    parser.add_argument("--seeds", required=True)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--model")
    parser.add_argument("--max-output-tokens", type=int, default=DEFAULT_MAX_OUTPUT_TOKENS)
    parser.add_argument("--temperature", type=float)
    parser.add_argument("--top-p", type=float)
    parser.add_argument("--no-resume", action="store_true")
    parser.add_argument(
        "--skip-recorded-failures",
        action="store_true",
        help="Defer failures already recorded in this shard's status file.",
    )
    parser.add_argument("--stop-on-error", action="store_true")
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--config", type=Path, default=CONFIG_PATH)
    args = parser.parse_args()

    config = load_config(args.config)
    languages = parse_csv_values(args.languages)
    seeds = parse_seeds(args.seeds)
    plan = build_experiment_plan(
        config=config,
        languages=languages,
        seeds=seeds,
        output_dir=args.output_dir,
    )
    if args.plan_only:
        print(
            json.dumps(
                {
                    "request_estimate": request_bounds(plan, config),
                    "plan": [asdict(item) for item in plan],
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return

    api_key = get_env_value("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is missing.")
    client = OpenAIResponsesClient(api_key=api_key)
    result = run_multilingual_experiment(
        client=client,
        model=args.model,
        languages=languages,
        seeds=seeds,
        output_dir=args.output_dir,
        resume=not args.no_resume,
        skip_recorded_failures=args.skip_recorded_failures,
        stop_on_error=args.stop_on_error,
        max_output_tokens=args.max_output_tokens,
        temperature=args.temperature,
        top_p=args.top_p,
        config_path=args.config,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
