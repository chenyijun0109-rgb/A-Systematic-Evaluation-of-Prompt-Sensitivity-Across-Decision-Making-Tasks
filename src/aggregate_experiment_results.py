from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

from src.horizon_random_exploration import (
    analyze_choice_observations,
    llm_run_id,
    load_llm_choice_observations,
)
from src.prompt_loader import load_config


TASK_ORDER = ("horizon", "igt", "bart")
RUN_METADATA_COLUMNS = (
    "run_id",
    "task",
    "prompt_condition",
    "model",
    "seed",
    "config_name",
    "config_version",
    "prompt_path",
    "prompt_sha256",
    "done",
    "n_trials",
    "parse_success_rate",
    "invalid_response_count",
    "source_path",
)


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    severity: str
    message: str
    details: dict[str, Any]


@dataclass
class AggregationResult:
    rows: list[dict[str, Any]]
    quality_report: dict[str, Any]


class AggregationValidationError(ValueError):
    def __init__(self, issues: list[ValidationIssue]) -> None:
        self.issues = issues
        self.issue_codes = tuple(issue.code for issue in issues)
        super().__init__(
            "Aggregation validation failed: " + ", ".join(self.issue_codes)
        )


@dataclass(frozen=True)
class Candidate:
    path: Path
    payload: dict[str, Any]

    @property
    def key(self) -> tuple[str, str, int]:
        return (
            str(self.payload["task"]),
            str(self.payload["prompt_condition"]),
            int(self.payload["seed"]),
        )


def discover_json_paths(inputs: Iterable[Path]) -> list[Path]:
    paths: set[Path] = set()
    for input_path in inputs:
        if input_path.is_dir():
            paths.update(input_path.rglob("*.json"))
        elif input_path.suffix.lower() == ".json":
            paths.add(input_path)
    return sorted(path.resolve() for path in paths)


def load_candidate(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def logical_run_id(task: str, condition: str, seed: int) -> str:
    return f"{task}:{condition}:{seed}"


def extract_run_row(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    metrics = payload["run_metrics"]
    task = str(payload["task"])
    condition = str(payload["prompt_condition"])
    seed = int(payload["seed"])
    row: dict[str, Any] = {
        "run_id": logical_run_id(task, condition, seed),
        "task": task,
        "prompt_condition": condition,
        "model": str(payload["model"]),
        "seed": seed,
        "config_name": str(payload.get("config_name", "")),
        "config_version": str(payload.get("config_version", "")),
        "prompt_path": str(payload.get("prompt_path", "")),
        "prompt_sha256": str(payload.get("prompt_sha256", "")),
        "done": bool(payload["done"]),
        "n_trials": int(
            metrics.get("n_trials", len(payload.get("trial_records", [])))
        ),
        "parse_success_rate": float(payload.get("parse_success_rate", 0.0)),
        "invalid_response_count": len(payload.get("invalid_responses", [])),
        "source_path": str(path.resolve()),
    }
    for name, value in metrics.items():
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            row[name] = value

    curve = metrics.get("block_wise_learning_curve")
    if task == "igt" and isinstance(curve, dict):
        first = curve.get("1", curve.get(1))
        last = curve.get("5", curve.get(5))
        if first is not None and last is not None:
            row["learning_curve_change"] = float(last) - float(first)
    return row


def apply_horizon_run_estimates(
    rows: list[dict[str, Any]],
    estimates: dict[str, float],
) -> None:
    for row in rows:
        if row["task"] != "horizon":
            continue
        key = llm_run_id(Path(row["source_path"]), row["seed"])
        if key in estimates:
            row["random_exploration_effect"] = estimates[key]


def estimate_horizon_random_exploration(
    selected_paths: list[Path],
) -> tuple[dict[str, float], list[ValidationIssue]]:
    horizon_paths = []
    for path in selected_paths:
        payload = load_candidate(path)
        if payload and payload.get("task") == "horizon" and payload.get("done"):
            horizon_paths.append(path)
    if not horizon_paths:
        return {}, []

    observations = load_llm_choice_observations(horizon_paths)
    results = analyze_choice_observations(observations)
    estimates: dict[str, float] = {}
    issues: list[ValidationIssue] = []
    for condition, result in sorted(results.items()):
        if result["status"] != "ok":
            issues.append(
                ValidationIssue(
                    code="random_exploration_insufficient_runs",
                    severity="error",
                    message=f"{condition} has too few Horizon runs.",
                    details={
                        "condition": condition,
                        "n_runs": result["n_runs"],
                        "minimum_runs": result["minimum_runs"],
                    },
                )
            )
            continue
        if not result["converged"]:
            issues.append(
                ValidationIssue(
                    code="random_exploration_not_converged",
                    severity="error",
                    message=f"{condition} Horizon fit did not converge.",
                    details={
                        "condition": condition,
                        "optimizer_message": result["optimizer_message"],
                    },
                )
            )
            continue
        for run_estimate in result["run_estimates"]:
            estimates[str(run_estimate["run_id"])] = float(
                run_estimate["random_exploration_effect"]
            )
    return estimates, issues


def _issue(
    issues: list[ValidationIssue],
    code: str,
    severity: str,
    message: str,
    **details: Any,
) -> None:
    issues.append(
        ValidationIssue(
            code=code,
            severity=severity,
            message=message,
            details=details,
        )
    )


def _collect_candidates(
    paths: list[Path],
    config: dict[str, Any],
    issues: list[ValidationIssue],
) -> tuple[list[Candidate], list[dict[str, str]]]:
    candidates: list[Candidate] = []
    ignored: list[dict[str, str]] = []
    configured_tasks = config["tasks"]
    for path in paths:
        payload = load_candidate(path)
        if payload is None:
            ignored.append({"path": str(path), "reason": "invalid_json"})
            continue
        task = payload.get("task")
        condition = payload.get("prompt_condition")
        if task not in configured_tasks:
            ignored.append({"path": str(path), "reason": "unrelated_task"})
            continue
        if condition not in configured_tasks[task]["prompt_conditions"]:
            ignored.append({"path": str(path), "reason": "unknown_condition"})
            continue
        if payload.get("seed") is None or not isinstance(payload.get("run_metrics"), dict):
            ignored.append({"path": str(path), "reason": "missing_run_identity_or_metrics"})
            continue
        candidate = Candidate(path=path, payload=payload)
        candidates.append(candidate)
        if not payload.get("done", False):
            _issue(
                issues,
                "failed_run",
                "error",
                "A discovered run did not complete.",
                path=str(path),
                task=task,
                prompt_condition=condition,
                seed=payload.get("seed"),
            )
    return candidates, ignored


def _select_candidates(
    candidates: list[Candidate],
    duplicate_policy: str,
    issues: list[ValidationIssue],
) -> list[Candidate]:
    if duplicate_policy not in {"error", "latest"}:
        raise ValueError("duplicate_policy must be 'error' or 'latest'.")

    grouped: dict[tuple[str, str, int], list[Candidate]] = {}
    for candidate in candidates:
        grouped.setdefault(candidate.key, []).append(candidate)

    selected: list[Candidate] = []
    for key, group in sorted(grouped.items()):
        successful = [
            candidate for candidate in group
            if candidate.payload.get("done", False)
        ]
        if len(group) > 1:
            severity = "error" if duplicate_policy == "error" else "warning"
            chosen = (
                max(successful, key=lambda item: item.path.stat().st_mtime_ns)
                if duplicate_policy == "latest" and successful
                else None
            )
            _issue(
                issues,
                "duplicate_run",
                severity,
                "Multiple files share one logical run key.",
                task=key[0],
                prompt_condition=key[1],
                seed=key[2],
                candidates=[str(item.path) for item in group],
                selected=str(chosen.path) if chosen else None,
            )
            if chosen is not None:
                selected.append(chosen)
            elif duplicate_policy == "error":
                continue
        elif successful:
            selected.append(successful[0])
    return selected


def _validate_completeness(
    rows: list[dict[str, Any]],
    config: dict[str, Any],
    expected_runs_per_cell: int,
    issues: list[ValidationIssue],
) -> None:
    for task, task_config in config["tasks"].items():
        seed_sets: dict[str, set[int]] = {}
        for condition in task_config["prompt_conditions"]:
            cell = [
                row for row in rows
                if row["task"] == task
                and row["prompt_condition"] == condition
            ]
            seeds = {int(row["seed"]) for row in cell}
            seed_sets[condition] = seeds
            if len(cell) < expected_runs_per_cell:
                _issue(
                    issues,
                    "missing_run",
                    "error",
                    "A task-condition cell has too few valid runs.",
                    task=task,
                    prompt_condition=condition,
                    expected=expected_runs_per_cell,
                    observed=len(cell),
                    seeds=sorted(seeds),
                )
            elif len(cell) > expected_runs_per_cell:
                _issue(
                    issues,
                    "unexpected_run",
                    "error",
                    "A task-condition cell has too many valid runs.",
                    task=task,
                    prompt_condition=condition,
                    expected=expected_runs_per_cell,
                    observed=len(cell),
                    seeds=sorted(seeds),
                )
        values = list(seed_sets.values())
        if values and any(value != values[0] for value in values[1:]):
            _issue(
                issues,
                "unpaired_seed",
                "error",
                "Prompt conditions within a task do not share the same seeds.",
                task=task,
                condition_seeds={
                    condition: sorted(seeds)
                    for condition, seeds in seed_sets.items()
                },
            )


def _validate_provenance(
    rows: list[dict[str, Any]],
    issues: list[ValidationIssue],
) -> None:
    models = {row["model"] for row in rows if row["model"]}
    if len(models) > 1:
        _issue(
            issues,
            "mixed_model",
            "error",
            "Valid runs contain multiple model IDs.",
            models=sorted(models),
        )

    configs = {
        (row["config_name"], row["config_version"])
        for row in rows
        if row["config_name"] and row["config_version"]
    }
    if len(configs) > 1:
        _issue(
            issues,
            "mixed_config_version",
            "error",
            "Valid runs contain multiple configuration versions.",
            configurations=[list(item) for item in sorted(configs)],
        )

    missing = [
        row["run_id"] for row in rows
        if not row["config_name"]
        or not row["config_version"]
        or not row["prompt_path"]
        or not row["prompt_sha256"]
    ]
    if missing:
        _issue(
            issues,
            "missing_provenance",
            "error",
            "Some valid runs lack reproducibility metadata.",
            run_ids=missing,
        )

    cells: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        cells.setdefault(
            (row["task"], row["prompt_condition"]),
            [],
        ).append(row)
    for (task, condition), cell_rows in sorted(cells.items()):
        hashes = {row["prompt_sha256"] for row in cell_rows if row["prompt_sha256"]}
        paths = {row["prompt_path"] for row in cell_rows if row["prompt_path"]}
        if len(hashes) > 1 or len(paths) > 1:
            _issue(
                issues,
                "mixed_prompt_hash",
                "error",
                "A task-condition cell contains multiple prompt versions.",
                task=task,
                prompt_condition=condition,
                prompt_hashes=sorted(hashes),
                prompt_paths=sorted(paths),
            )


def _sort_rows(
    rows: list[dict[str, Any]],
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    task_rank = {
        task: index for index, task in enumerate(config["tasks"])
    }
    condition_rank = {
        (task, condition): index
        for task, task_config in config["tasks"].items()
        for index, condition in enumerate(task_config["prompt_conditions"])
    }
    return sorted(
        rows,
        key=lambda row: (
            task_rank.get(row["task"], len(task_rank)),
            condition_rank.get(
                (row["task"], row["prompt_condition"]),
                999,
            ),
            int(row["seed"]),
        ),
    )


def aggregate_experiment_results(
    inputs: Iterable[Path],
    *,
    expected_runs_per_cell: int,
    duplicate_policy: str,
    allow_incomplete: bool,
    config: dict[str, Any],
    include_horizon_model: bool = True,
) -> AggregationResult:
    if expected_runs_per_cell < 1:
        raise ValueError("expected_runs_per_cell must be at least 1.")

    paths = discover_json_paths(inputs)
    issues: list[ValidationIssue] = []
    candidates, ignored = _collect_candidates(paths, config, issues)
    selected = _select_candidates(candidates, duplicate_policy, issues)
    rows = [extract_run_row(item.path, item.payload) for item in selected]

    if include_horizon_model and any(row["task"] == "horizon" for row in rows):
        estimates, horizon_issues = estimate_horizon_random_exploration(
            [item.path for item in selected]
        )
        issues.extend(horizon_issues)
        apply_horizon_run_estimates(rows, estimates)

    _validate_completeness(rows, config, expected_runs_per_cell, issues)
    _validate_provenance(rows, issues)
    rows = _sort_rows(rows, config)
    error_issues = [issue for issue in issues if issue.severity == "error"]
    report = {
        "analysis_complete": not error_issues,
        "allow_incomplete": allow_incomplete,
        "duplicate_policy": duplicate_policy,
        "expected_runs_per_cell": expected_runs_per_cell,
        "discovered_file_count": len(paths),
        "candidate_file_count": len(candidates),
        "valid_run_count": len(rows),
        "ignored_files": ignored,
        "issues": [asdict(issue) for issue in issues],
    }
    result = AggregationResult(rows=rows, quality_report=report)
    if error_issues and not allow_incomplete:
        raise AggregationValidationError(error_issues)
    return result


def write_aggregation_outputs(
    result: AggregationResult,
    output_dir: Path,
) -> tuple[Path | None, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "aggregation_quality_report.json"
    report_path.write_text(
        json.dumps(result.quality_report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    csv_path: Path | None = None
    if result.rows:
        csv_path = output_dir / "llm_run_metrics.csv"
        metric_columns = sorted(
            {
                key
                for row in result.rows
                for key in row
                if key not in RUN_METADATA_COLUMNS
            }
        )
        fieldnames = [*RUN_METADATA_COLUMNS, *metric_columns]
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=fieldnames,
                extrasaction="ignore",
            )
            writer.writeheader()
            for row in result.rows:
                serialized = {
                    key: (
                        str(value).lower()
                        if isinstance(value, bool)
                        else value
                    )
                    for key, value in row.items()
                }
                writer.writerow(serialized)
    return csv_path, report_path


def run_aggregation(
    inputs: list[Path],
    *,
    output_dir: Path,
    expected_runs_per_cell: int,
    duplicate_policy: str,
    allow_incomplete: bool,
    config_path: Path,
) -> AggregationResult:
    config = load_config(config_path)
    result = aggregate_experiment_results(
        inputs,
        expected_runs_per_cell=expected_runs_per_cell,
        duplicate_policy=duplicate_policy,
        allow_incomplete=True,
        config=config,
    )
    result.quality_report["allow_incomplete"] = allow_incomplete
    write_aggregation_outputs(result, output_dir)
    error_issues = [
        ValidationIssue(**issue)
        for issue in result.quality_report["issues"]
        if issue["severity"] == "error"
    ]
    if error_issues and not allow_incomplete:
        raise AggregationValidationError(error_issues)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Aggregate multi-run LLM experiment JSON files."
    )
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/processed"),
    )
    parser.add_argument("--expected-runs-per-cell", type=int, required=True)
    parser.add_argument(
        "--duplicate-policy",
        choices=("error", "latest"),
        default="error",
    )
    parser.add_argument("--allow-incomplete", action="store_true")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/experiment_config_stage01.json"),
    )
    args = parser.parse_args()

    try:
        result = run_aggregation(
            args.inputs,
            output_dir=args.output_dir,
            expected_runs_per_cell=args.expected_runs_per_cell,
            duplicate_policy=args.duplicate_policy,
            allow_incomplete=args.allow_incomplete,
            config_path=args.config,
        )
    except AggregationValidationError as exc:
        raise SystemExit(str(exc)) from exc

    print(
        json.dumps(
            {
                "valid_run_count": len(result.rows),
                "analysis_complete": result.quality_report["analysis_complete"],
                "output_dir": str(args.output_dir),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
