from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from pathlib import Path
from typing import Any

from src.prompt_loader import load_config


SUMMARY_FIELDS = (
    "task",
    "prompt_condition",
    "metric",
    "n",
    "mean",
    "sd",
    "median",
    "minimum",
    "maximum",
)
EFFECT_FIELDS = (
    "task",
    "prompt_condition",
    "metric",
    "baseline_n",
    "condition_n",
    "baseline_mean",
    "condition_mean",
    "raw_mean_difference",
    "baseline_sd",
    "condition_sd",
    "denominator",
    "sd_source",
    "signed_standardised_effect",
    "absolute_standardised_effect",
    "warning_flags",
)
PSI_FIELDS = (
    "task",
    "prompt_condition",
    "psi",
    "expected_metric_count",
    "valid_metric_count",
    "excluded_metrics",
    "status",
)


class PromptSensitivityValidationError(ValueError):
    def __init__(self, issues: list[dict[str, Any]]) -> None:
        self.issues = issues
        self.issue_codes = tuple(issue["code"] for issue in issues)
        super().__init__(
            "Prompt sensitivity validation failed: "
            + ", ".join(self.issue_codes)
        )


def parse_optional_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        number = float(text)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def summarise_values(
    values: list[float],
) -> dict[str, float | int | None]:
    if not values:
        return {
            "n": 0,
            "mean": None,
            "sd": None,
            "median": None,
            "minimum": None,
            "maximum": None,
        }
    return {
        "n": len(values),
        "mean": statistics.mean(values),
        "sd": statistics.stdev(values) if len(values) >= 2 else None,
        "median": statistics.median(values),
        "minimum": min(values),
        "maximum": max(values),
    }


def pooled_sd(baseline_sd: float, condition_sd: float) -> float:
    return math.sqrt((baseline_sd**2 + condition_sd**2) / 2.0)


def _validation_issue(
    code: str,
    message: str,
    **details: Any,
) -> dict[str, Any]:
    return {
        "code": code,
        "severity": "error",
        "message": message,
        "details": details,
    }


def compute_standardised_effect(
    *,
    baseline_values: list[float],
    condition_values: list[float],
    metric: str,
    policy: dict[str, Any],
    allow_incomplete: bool,
) -> dict[str, Any]:
    if len(baseline_values) < 2 or len(condition_values) < 2:
        issue = _validation_issue(
            "missing_metric",
            "At least two run-level values are required per group.",
            metric=metric,
            baseline_n=len(baseline_values),
            condition_n=len(condition_values),
        )
        raise PromptSensitivityValidationError([issue])

    baseline = summarise_values(baseline_values)
    condition = summarise_values(condition_values)
    baseline_mean = float(baseline["mean"])
    condition_mean = float(condition["mean"])
    baseline_sd = float(baseline["sd"])
    condition_sd = float(condition["sd"])
    difference = condition_mean - baseline_mean
    tolerance = float(policy["zero_tolerance"])
    warning_flags: list[str] = []

    if baseline_sd > tolerance:
        denominator = baseline_sd
        sd_source = "baseline"
        if metric in set(policy.get("bounded_metrics", [])):
            low_variance = (
                baseline_sd
                <= float(policy["low_variance_absolute_threshold"])
            )
        else:
            scale = max(abs(baseline_mean), abs(condition_mean), 1.0)
            low_variance = (
                baseline_sd / scale
                <= float(policy["low_variance_relative_threshold"])
            )
        if low_variance:
            warning_flags.append("low_baseline_variance")
    else:
        fallback = pooled_sd(baseline_sd, condition_sd)
        if fallback > tolerance:
            denominator = fallback
            sd_source = "pooled_fallback"
        elif abs(difference) <= tolerance:
            denominator = 0.0
            sd_source = "constant_equal"
        else:
            issue = _validation_issue(
                "zero_variance_undefined_effect",
                "Both groups are constant but their means differ.",
                metric=metric,
                baseline_mean=baseline_mean,
                condition_mean=condition_mean,
            )
            if allow_incomplete:
                return {
                    "baseline_n": len(baseline_values),
                    "condition_n": len(condition_values),
                    "baseline_mean": baseline_mean,
                    "condition_mean": condition_mean,
                    "raw_mean_difference": difference,
                    "baseline_sd": baseline_sd,
                    "condition_sd": condition_sd,
                    "denominator": None,
                    "sd_source": "undefined",
                    "signed_standardised_effect": None,
                    "absolute_standardised_effect": None,
                    "warning_flags": "zero_variance_undefined_effect",
                }
            raise PromptSensitivityValidationError([issue])

    effect = 0.0 if sd_source == "constant_equal" else difference / denominator
    return {
        "baseline_n": len(baseline_values),
        "condition_n": len(condition_values),
        "baseline_mean": baseline_mean,
        "condition_mean": condition_mean,
        "raw_mean_difference": difference,
        "baseline_sd": baseline_sd,
        "condition_sd": condition_sd,
        "denominator": denominator,
        "sd_source": sd_source,
        "signed_standardised_effect": effect,
        "absolute_standardised_effect": abs(effect),
        "warning_flags": "|".join(warning_flags),
    }


def compute_psi_row(
    *,
    task: str,
    condition: str,
    expected_metrics: list[str],
    effect_rows: list[dict[str, Any]],
    minimum_partial_metrics: int,
    allow_incomplete: bool,
) -> dict[str, Any]:
    by_metric = {str(row["metric"]): row for row in effect_rows}
    valid = [
        by_metric[metric]
        for metric in expected_metrics
        if metric in by_metric
        and by_metric[metric].get("absolute_standardised_effect") is not None
    ]
    missing = [
        metric
        for metric in expected_metrics
        if metric not in by_metric
        or by_metric[metric].get("absolute_standardised_effect") is None
    ]
    if missing and not allow_incomplete:
        raise PromptSensitivityValidationError(
            [
                _validation_issue(
                    "missing_metric",
                    "A complete PSI requires all configured metrics.",
                    task=task,
                    prompt_condition=condition,
                    metrics=missing,
                )
            ]
        )

    psi = None
    if len(valid) >= minimum_partial_metrics:
        psi = statistics.mean(
            float(row["absolute_standardised_effect"]) for row in valid
        )
    return {
        "task": task,
        "prompt_condition": condition,
        "psi": psi,
        "expected_metric_count": len(expected_metrics),
        "valid_metric_count": len(valid),
        "excluded_metrics": "|".join(missing),
        "status": (
            "complete"
            if len(valid) == len(expected_metrics)
            else "partial"
            if psi is not None
            else "insufficient"
        ),
    }


def load_run_metrics(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def validate_run_table(
    rows: list[dict[str, Any]],
    *,
    config: dict[str, Any],
    expected_runs_per_cell: int,
    allow_incomplete: bool,
) -> list[dict[str, Any]]:
    if expected_runs_per_cell < 1:
        raise ValueError("expected_runs_per_cell must be at least 1.")
    issues: list[dict[str, Any]] = []
    for task, task_config in config["tasks"].items():
        condition_seeds: dict[str, set[int]] = {}
        for condition in task_config["prompt_conditions"]:
            cell_rows = [
                row
                for row in rows
                if row.get("task") == task
                and row.get("prompt_condition") == condition
            ]
            seeds = {int(row["seed"]) for row in cell_rows}
            condition_seeds[condition] = seeds
            if len(cell_rows) != expected_runs_per_cell:
                code = (
                    "missing_run"
                    if len(cell_rows) < expected_runs_per_cell
                    else "unexpected_run"
                )
                issues.append(
                    _validation_issue(
                        code,
                        "Run count does not match the expected cell size.",
                        task=task,
                        prompt_condition=condition,
                        observed=len(cell_rows),
                        expected=expected_runs_per_cell,
                    )
                )
        seed_sets = list(condition_seeds.values())
        if seed_sets and any(
            seed_set != seed_sets[0] for seed_set in seed_sets[1:]
        ):
            issues.append(
                _validation_issue(
                    "unpaired_seed",
                    "Prompt conditions within a task do not share seeds.",
                    task=task,
                    condition_seeds={
                        condition: sorted(seeds)
                        for condition, seeds in condition_seeds.items()
                    },
                )
            )
    if issues and not allow_incomplete:
        raise PromptSensitivityValidationError(issues)
    return issues


def _metric_columns(
    rows: list[dict[str, Any]],
    config: dict[str, Any],
) -> list[str]:
    metadata = {
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
        "source_path",
    }
    available = {
        key
        for row in rows
        for key, value in row.items()
        if key not in metadata and parse_optional_float(value) is not None
    }
    primary = [
        metric
        for task in config["tasks"]
        for metric in config["analysis"]["prompt_sensitivity"][
            "primary_metrics"
        ].get(task, [])
        if metric in available
    ]
    supplemental = sorted(available.difference(primary))
    return [*dict.fromkeys(primary), *supplemental]


def build_metric_summaries(
    rows: list[dict[str, Any]],
    *,
    metric_columns: list[str],
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for task, task_config in config["tasks"].items():
        for condition in task_config["prompt_conditions"]:
            cell_rows = [
                row
                for row in rows
                if row.get("task") == task
                and row.get("prompt_condition") == condition
            ]
            for metric in metric_columns:
                values = [
                    value
                    for row in cell_rows
                    if (
                        value := parse_optional_float(row.get(metric))
                    )
                    is not None
                ]
                if values:
                    summaries.append(
                        {
                            "task": task,
                            "prompt_condition": condition,
                            "metric": metric,
                            **summarise_values(values),
                        }
                    )
    return summaries


def build_prompt_effects(
    rows: list[dict[str, Any]],
    *,
    config: dict[str, Any],
    allow_incomplete: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    analysis = config["analysis"]
    baseline = analysis["baseline_condition"]
    policy = analysis["prompt_sensitivity"]
    effects: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    for task, metrics in policy["primary_metrics"].items():
        for condition in config["tasks"][task]["prompt_conditions"]:
            if condition == baseline:
                continue
            for metric in metrics:
                baseline_values = [
                    value
                    for row in rows
                    if row.get("task") == task
                    and row.get("prompt_condition") == baseline
                    and (
                        value := parse_optional_float(row.get(metric))
                    )
                    is not None
                ]
                condition_values = [
                    value
                    for row in rows
                    if row.get("task") == task
                    and row.get("prompt_condition") == condition
                    and (
                        value := parse_optional_float(row.get(metric))
                    )
                    is not None
                ]
                try:
                    effect = compute_standardised_effect(
                        baseline_values=baseline_values,
                        condition_values=condition_values,
                        metric=metric,
                        policy=policy,
                        allow_incomplete=allow_incomplete,
                    )
                except PromptSensitivityValidationError as exc:
                    issues.extend(exc.issues)
                    if not allow_incomplete:
                        raise
                    continue
                if effect["signed_standardised_effect"] is None:
                    issues.append(
                        _validation_issue(
                            "zero_variance_undefined_effect",
                            "A standardised effect could not be computed.",
                            task=task,
                            prompt_condition=condition,
                            metric=metric,
                        )
                    )
                effects.append(
                    {
                        "task": task,
                        "prompt_condition": condition,
                        "metric": metric,
                        **effect,
                    }
                )
    return effects, issues


def build_psi_rows(
    effect_rows: list[dict[str, Any]],
    *,
    config: dict[str, Any],
    allow_incomplete: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    policy = config["analysis"]["prompt_sensitivity"]
    baseline = config["analysis"]["baseline_condition"]
    rows: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    for task, expected_metrics in policy["primary_metrics"].items():
        for condition in config["tasks"][task]["prompt_conditions"]:
            if condition == baseline:
                continue
            condition_effects = [
                row
                for row in effect_rows
                if row["task"] == task
                and row["prompt_condition"] == condition
            ]
            psi_row = compute_psi_row(
                task=task,
                condition=condition,
                expected_metrics=expected_metrics,
                effect_rows=condition_effects,
                minimum_partial_metrics=int(
                    policy["minimum_partial_metrics"]
                ),
                allow_incomplete=allow_incomplete,
            )
            rows.append(psi_row)
            if psi_row["status"] != "complete":
                issues.append(
                    {
                        "code": "partial_psi",
                        "severity": "warning",
                        "message": "PSI does not contain all configured metrics.",
                        "details": {
                            "task": task,
                            "prompt_condition": condition,
                            "status": psi_row["status"],
                            "excluded_metrics": psi_row["excluded_metrics"],
                        },
                    }
                )
    return rows, issues


def _write_csv(
    path: Path,
    rows: list[dict[str, Any]],
    fieldnames: tuple[str, ...],
) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def run_prompt_sensitivity_analysis(
    run_metrics_csv: Path,
    *,
    output_dir: Path,
    expected_runs_per_cell: int,
    allow_incomplete: bool,
    config_path: Path,
) -> dict[str, Any]:
    config = load_config(config_path)
    rows = load_run_metrics(run_metrics_csv)
    issues = validate_run_table(
        rows,
        config=config,
        expected_runs_per_cell=expected_runs_per_cell,
        allow_incomplete=allow_incomplete,
    )
    metric_columns = _metric_columns(rows, config)
    summary_rows = build_metric_summaries(
        rows,
        metric_columns=metric_columns,
        config=config,
    )
    effect_rows, effect_issues = build_prompt_effects(
        rows,
        config=config,
        allow_incomplete=allow_incomplete,
    )
    issues.extend(effect_issues)
    psi_rows, psi_issues = build_psi_rows(
        effect_rows,
        config=config,
        allow_incomplete=allow_incomplete,
    )
    issues.extend(psi_issues)

    output_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(output_dir / "metric_summary.csv", summary_rows, SUMMARY_FIELDS)
    _write_csv(output_dir / "prompt_effects.csv", effect_rows, EFFECT_FIELDS)
    _write_csv(output_dir / "prompt_sensitivity.csv", psi_rows, PSI_FIELDS)
    analysis_complete = (
        not any(issue["severity"] == "error" for issue in issues)
        and all(row["status"] == "complete" for row in psi_rows)
    )
    report = {
        "analysis": "prompt_sensitivity",
        "source_run_metrics": str(run_metrics_csv.resolve()),
        "baseline_condition": config["analysis"]["baseline_condition"],
        "expected_runs_per_cell": expected_runs_per_cell,
        "allow_incomplete": allow_incomplete,
        "analysis_complete": analysis_complete,
        "metric_summary_rows": len(summary_rows),
        "prompt_effect_rows": len(effect_rows),
        "psi_rows": len(psi_rows),
        "issues": issues,
        "psi_definition": (
            "Project-defined descriptive mean of absolute standardised "
            "effects; not a validated psychological scale."
        ),
    }
    (output_dir / "analysis_summary.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return {
        "summary_rows": summary_rows,
        "effect_rows": effect_rows,
        "psi_rows": psi_rows,
        "analysis_summary": report,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute standardised prompt effects and PSI."
    )
    parser.add_argument("run_metrics_csv", type=Path)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/processed"),
    )
    parser.add_argument("--expected-runs-per-cell", type=int, required=True)
    parser.add_argument("--allow-incomplete", action="store_true")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/experiment_config_stage01.json"),
    )
    args = parser.parse_args()

    try:
        result = run_prompt_sensitivity_analysis(
            args.run_metrics_csv,
            output_dir=args.output_dir,
            expected_runs_per_cell=args.expected_runs_per_cell,
            allow_incomplete=args.allow_incomplete,
            config_path=args.config,
        )
    except PromptSensitivityValidationError as exc:
        raise SystemExit(str(exc)) from exc
    print(json.dumps(result["analysis_summary"], indent=2))


if __name__ == "__main__":
    main()
