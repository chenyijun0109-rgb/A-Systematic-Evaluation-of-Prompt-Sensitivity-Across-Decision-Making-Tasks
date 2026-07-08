from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
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
    "hedges_correction",
    "baseline_sd_standardised_effect",
    "signed_standardised_effect",
    "absolute_standardised_effect",
    "confidence_level",
    "bootstrap_replicates",
    "standardised_valid_replicates",
    "raw_difference_ci_lower",
    "raw_difference_ci_upper",
    "standardised_effect_ci_lower",
    "standardised_effect_ci_upper",
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
    "confidence_level",
    "bootstrap_replicates",
    "psi_valid_replicates",
    "psi_ci_lower",
    "psi_ci_upper",
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


def pooled_sample_sd(
    baseline_sd: float,
    condition_sd: float,
    baseline_n: int,
    condition_n: int,
) -> float:
    degrees_of_freedom = baseline_n + condition_n - 2
    if degrees_of_freedom <= 0:
        raise ValueError("Pooled SD requires at least two total degrees of freedom.")
    variance = (
        (baseline_n - 1) * baseline_sd**2
        + (condition_n - 1) * condition_sd**2
    ) / degrees_of_freedom
    return math.sqrt(variance)


def hedges_correction(baseline_n: int, condition_n: int) -> float:
    degrees_of_freedom = baseline_n + condition_n - 2
    if degrees_of_freedom <= 1:
        raise ValueError("Hedges' correction requires more than one degree of freedom.")
    return 1.0 - 3.0 / (4.0 * degrees_of_freedom - 1.0)


def percentile(values: list[float], probability: float) -> float | None:
    if not values:
        return None
    if not 0.0 <= probability <= 1.0:
        raise ValueError("Percentile probability must be between zero and one.")
    ordered = sorted(values)
    position = probability * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] + fraction * (ordered[upper] - ordered[lower])


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
    correction = hedges_correction(
        len(baseline_values),
        len(condition_values),
    )

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

    denominator = pooled_sample_sd(
        baseline_sd,
        condition_sd,
        len(baseline_values),
        len(condition_values),
    )
    if denominator > tolerance:
        sd_source = "pooled"
        effect = correction * difference / denominator
    elif abs(difference) <= tolerance:
        denominator = 0.0
        sd_source = "constant_equal"
        effect = 0.0
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
                "hedges_correction": correction,
                "baseline_sd_standardised_effect": None,
                "signed_standardised_effect": None,
                "absolute_standardised_effect": None,
                "warning_flags": "zero_variance_undefined_effect",
            }
        raise PromptSensitivityValidationError([issue])

    baseline_effect = (
        difference / baseline_sd
        if baseline_sd > tolerance
        else 0.0
        if abs(difference) <= tolerance
        else None
    )
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
        "hedges_correction": correction,
        "baseline_sd_standardised_effect": baseline_effect,
        "signed_standardised_effect": effect,
        "absolute_standardised_effect": abs(effect),
        "warning_flags": "|".join(warning_flags),
    }


def bootstrap_paired_effect(
    *,
    baseline_by_seed: dict[int, float],
    condition_by_seed: dict[int, float],
    metric: str,
    policy: dict[str, Any],
    replicates: int,
    bootstrap_seed: int,
    confidence_level: float,
) -> dict[str, Any]:
    if replicates < 1:
        raise ValueError("Bootstrap replicates must be positive.")
    if not 0.0 < confidence_level < 1.0:
        raise ValueError("Confidence level must be between zero and one.")
    seeds = sorted(set(baseline_by_seed).intersection(condition_by_seed))
    if len(seeds) < 2:
        raise ValueError("Paired bootstrap requires at least two complete seed pairs.")
    if set(baseline_by_seed) != set(condition_by_seed):
        raise ValueError("Paired bootstrap requires identical seed sets.")

    rng = random.Random(bootstrap_seed)
    raw_differences: list[float] = []
    standardised_effects: list[float] = []
    for _ in range(replicates):
        sampled = [rng.choice(seeds) for _ in seeds]
        baseline_values = [baseline_by_seed[seed] for seed in sampled]
        condition_values = [condition_by_seed[seed] for seed in sampled]
        raw_differences.append(
            statistics.mean(condition_values)
            - statistics.mean(baseline_values)
        )
        result = compute_standardised_effect(
            baseline_values=baseline_values,
            condition_values=condition_values,
            metric=metric,
            policy=policy,
            allow_incomplete=True,
        )
        effect = result["signed_standardised_effect"]
        if effect is not None:
            standardised_effects.append(float(effect))

    alpha = (1.0 - confidence_level) / 2.0
    return {
        "confidence_level": confidence_level,
        "bootstrap_replicates": replicates,
        "standardised_valid_replicates": len(standardised_effects),
        "raw_difference_ci_lower": percentile(raw_differences, alpha),
        "raw_difference_ci_upper": percentile(raw_differences, 1.0 - alpha),
        "standardised_effect_ci_lower": percentile(
            standardised_effects,
            alpha,
        ),
        "standardised_effect_ci_upper": percentile(
            standardised_effects,
            1.0 - alpha,
        ),
    }


def stable_bootstrap_seed(base_seed: int, *labels: str) -> int:
    digest = hashlib.sha256(":".join(labels).encode("utf-8")).digest()
    return base_seed + int.from_bytes(digest[:4], byteorder="big")


def add_effect_bootstrap_intervals(
    effect_rows: list[dict[str, Any]],
    *,
    rows: list[dict[str, Any]],
    config: dict[str, Any],
) -> None:
    policy = config["analysis"]["prompt_sensitivity"]
    baseline_condition = config["analysis"]["baseline_condition"]
    replicates = int(policy["bootstrap_replicates"])
    base_seed = int(policy["bootstrap_seed"])
    confidence_level = float(policy["confidence_level"])
    for effect in effect_rows:
        task = str(effect["task"])
        condition = str(effect["prompt_condition"])
        metric = str(effect["metric"])
        baseline_by_seed = {
            int(row["seed"]): value
            for row in rows
            if row.get("task") == task
            and row.get("prompt_condition") == baseline_condition
            and (value := parse_optional_float(row.get(metric))) is not None
        }
        condition_by_seed = {
            int(row["seed"]): value
            for row in rows
            if row.get("task") == task
            and row.get("prompt_condition") == condition
            and (value := parse_optional_float(row.get(metric))) is not None
        }
        effect.update(
            bootstrap_paired_effect(
                baseline_by_seed=baseline_by_seed,
                condition_by_seed=condition_by_seed,
                metric=metric,
                policy=policy,
                replicates=replicates,
                bootstrap_seed=stable_bootstrap_seed(
                    base_seed,
                    task,
                    condition,
                    metric,
                ),
                confidence_level=confidence_level,
            )
        )


def bootstrap_paired_psi(
    *,
    rows: list[dict[str, Any]],
    task: str,
    condition: str,
    metrics: list[str],
    config: dict[str, Any],
) -> dict[str, Any]:
    policy = config["analysis"]["prompt_sensitivity"]
    baseline_condition = config["analysis"]["baseline_condition"]
    replicates = int(policy["bootstrap_replicates"])
    confidence_level = float(policy["confidence_level"])
    baseline_rows = {
        int(row["seed"]): row
        for row in rows
        if row.get("task") == task
        and row.get("prompt_condition") == baseline_condition
    }
    condition_rows = {
        int(row["seed"]): row
        for row in rows
        if row.get("task") == task
        and row.get("prompt_condition") == condition
    }
    seeds = sorted(set(baseline_rows).intersection(condition_rows))
    if len(seeds) < 2 or set(baseline_rows) != set(condition_rows):
        raise ValueError("PSI bootstrap requires matching complete seed pairs.")

    rng = random.Random(
        stable_bootstrap_seed(
            int(policy["bootstrap_seed"]),
            task,
            condition,
            "psi",
        )
    )
    psi_values: list[float] = []
    for _ in range(replicates):
        sampled = [rng.choice(seeds) for _ in seeds]
        effects: list[float] = []
        for metric in metrics:
            baseline_values = [
                parse_optional_float(baseline_rows[seed].get(metric))
                for seed in sampled
            ]
            condition_values = [
                parse_optional_float(condition_rows[seed].get(metric))
                for seed in sampled
            ]
            if any(value is None for value in baseline_values + condition_values):
                effects = []
                break
            result = compute_standardised_effect(
                baseline_values=[
                    float(value) for value in baseline_values if value is not None
                ],
                condition_values=[
                    float(value) for value in condition_values if value is not None
                ],
                metric=metric,
                policy=policy,
                allow_incomplete=True,
            )
            effect = result["absolute_standardised_effect"]
            if effect is None:
                effects = []
                break
            effects.append(float(effect))
        if len(effects) == len(metrics):
            psi_values.append(statistics.mean(effects))

    alpha = (1.0 - confidence_level) / 2.0
    return {
        "confidence_level": confidence_level,
        "bootstrap_replicates": replicates,
        "psi_valid_replicates": len(psi_values),
        "psi_ci_lower": percentile(psi_values, alpha),
        "psi_ci_upper": percentile(psi_values, 1.0 - alpha),
    }


def add_psi_bootstrap_intervals(
    psi_rows: list[dict[str, Any]],
    *,
    rows: list[dict[str, Any]],
    config: dict[str, Any],
) -> None:
    primary_metrics = config["analysis"]["prompt_sensitivity"]["primary_metrics"]
    for psi_row in psi_rows:
        psi_row.update(
            bootstrap_paired_psi(
                rows=rows,
                task=str(psi_row["task"]),
                condition=str(psi_row["prompt_condition"]),
                metrics=list(primary_metrics[str(psi_row["task"])]),
                config=config,
            )
        )


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
        "requested_model",
        "resolved_model",
        "temperature",
        "top_p",
        "max_output_tokens",
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
    add_effect_bootstrap_intervals(
        effect_rows,
        rows=rows,
        config=config,
    )
    psi_rows, psi_issues = build_psi_rows(
        effect_rows,
        config=config,
        allow_incomplete=allow_incomplete,
    )
    issues.extend(psi_issues)
    add_psi_bootstrap_intervals(
        psi_rows,
        rows=rows,
        config=config,
    )

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
