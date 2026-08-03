"""Compare formal LLM run metrics against human participant reference data."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Iterable

from src.prompt_loader import load_config


def read_csv_rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def parse_float(value: object) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def quantile(sorted_values: list[float], probability: float) -> float:
    if not sorted_values:
        raise ValueError("quantile requires at least one value")
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = probability * (len(sorted_values) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_values[lower]
    fraction = position - lower
    return sorted_values[lower] * (1 - fraction) + sorted_values[upper] * fraction


def summarise(values: list[float]) -> dict:
    if not values:
        raise ValueError("cannot summarise an empty value list")
    ordered = sorted(values)
    center = sum(values) / len(values)
    sd = None
    if len(values) > 1:
        sd = math.sqrt(sum((value - center) ** 2 for value in values) / (len(values) - 1))
    return {
        "n": len(values),
        "mean": center,
        "sd": sd,
        "median": quantile(ordered, 0.5),
        "minimum": ordered[0],
        "maximum": ordered[-1],
        "reference_lower": quantile(ordered, 0.025),
        "reference_upper": quantile(ordered, 0.975),
    }


def reference_position(value: float, lower: float, upper: float) -> str:
    if value < lower:
        return "below"
    if value > upper:
        return "above"
    return "within"


def empirical_quantile(value: float, reference_values: list[float]) -> float | None:
    if not reference_values:
        return None
    return sum(1 for item in reference_values if item <= value) / len(reference_values)


def mean(values: Iterable[float]) -> float | None:
    values = list(values)
    return sum(values) / len(values) if values else None


def collect_numeric(rows: list[dict], metric: str) -> list[float]:
    values = []
    for row in rows:
        value = parse_float(row.get(metric))
        if value is not None:
            values.append(value)
    return values


def compare_llm_to_human(
    *,
    task: str,
    prompt_condition: str,
    metric: str,
    llm_values: list[float],
    human_values: list[float],
) -> dict:
    llm_summary = summarise(llm_values)
    human_summary = summarise(human_values)
    raw_difference = llm_summary["mean"] - human_summary["mean"]
    human_sd = human_summary["sd"]
    standardised_distance = None
    if human_sd is not None and human_sd > 0:
        standardised_distance = raw_difference / human_sd
    lower = human_summary["reference_lower"]
    upper = human_summary["reference_upper"]
    within_count = sum(1 for value in llm_values if lower <= value <= upper)
    return {
        "task": task,
        "prompt_condition": prompt_condition,
        "metric": metric,
        "llm_n": llm_summary["n"],
        "human_n": human_summary["n"],
        "llm_mean": llm_summary["mean"],
        "human_mean": human_summary["mean"],
        "raw_mean_difference_llm_minus_human": raw_difference,
        "human_sd_standardised_distance": standardised_distance,
        "llm_sd": llm_summary["sd"],
        "human_sd": human_summary["sd"],
        "llm_median": llm_summary["median"],
        "human_median": human_summary["median"],
        "human_reference_lower": lower,
        "human_reference_upper": upper,
        "llm_mean_reference_position": reference_position(llm_summary["mean"], lower, upper),
        "llm_mean_human_empirical_quantile": empirical_quantile(
            llm_summary["mean"],
            human_values,
        ),
        "llm_runs_within_human_reference_count": within_count,
        "llm_runs_within_human_reference_proportion": within_count / len(llm_values),
    }


def load_human_rows(
    human_metrics_dir: Path,
    horizon_random_exploration_path: Path | None = None,
) -> dict[str, list[dict]]:
    rows_by_task = {}
    for task in ("horizon", "igt", "bart"):
        path = human_metrics_dir / f"{task}_human_metrics.csv"
        if path.exists():
            rows_by_task[task] = read_csv_rows(path)
    if horizon_random_exploration_path and horizon_random_exploration_path.exists():
        payload = json.loads(horizon_random_exploration_path.read_text(encoding="utf-8"))
        human_condition = payload.get("conditions", {}).get("human", {})
        run_estimates = human_condition.get("run_estimates", [])
        if run_estimates:
            for estimate in run_estimates:
                participant_id = str(estimate.get("run_id", "")).split(":")[-1]
                rows_by_task.setdefault("horizon_random_exploration", []).append(
                    {
                        "task": "horizon",
                        "participant_id": participant_id,
                        "random_exploration_effect": estimate.get(
                            "random_exploration_effect"
                        ),
                    }
                )
    return rows_by_task


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def primary_metrics_from_config(config_path: Path) -> dict[str, list[str]]:
    config = load_config(config_path)
    return config["analysis"]["prompt_sensitivity"]["primary_metrics"]


def run_llm_human_comparison(
    *,
    llm_metrics_path: Path,
    human_metrics_dir: Path,
    output_dir: Path,
    metrics_by_task: dict[str, list[str]],
    horizon_random_exploration_path: Path | None = None,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    llm_rows = read_csv_rows(llm_metrics_path)
    human_rows_by_task = load_human_rows(
        human_metrics_dir,
        horizon_random_exploration_path=horizon_random_exploration_path,
    )
    comparison_rows: list[dict] = []
    human_summary_rows: list[dict] = []
    task_participants: dict[str, int] = {}

    languages = sorted({row.get("prompt_language", "en") for row in llm_rows})
    for task, metrics in metrics_by_task.items():
        task_human_rows = human_rows_by_task.get(task, [])
        random_rows = human_rows_by_task.get("horizon_random_exploration", [])
        task_llm_rows = [row for row in llm_rows if row.get("task") == task]
        task_participants[task] = len(task_human_rows)
        if task == "horizon" and random_rows:
            task_participants["horizon_random_exploration"] = len(random_rows)

        for metric in metrics:
            metric_human_rows = (
                random_rows
                if task == "horizon" and metric == "random_exploration_effect" and random_rows
                else task_human_rows
            )
            human_values = collect_numeric(metric_human_rows, metric)
            if not human_values:
                continue
            h_summary = summarise(human_values)
            human_summary_rows.append(
                {
                    "task": task,
                    "metric": metric,
                    "human_n": h_summary["n"],
                    "human_mean": h_summary["mean"],
                    "human_sd": h_summary["sd"],
                    "human_median": h_summary["median"],
                    "human_minimum": h_summary["minimum"],
                    "human_maximum": h_summary["maximum"],
                    "human_reference_lower": h_summary["reference_lower"],
                    "human_reference_upper": h_summary["reference_upper"],
                    "source": (
                        "horizon_random_exploration_model"
                        if task == "horizon" and metric == "random_exploration_effect" and random_rows
                        else "participant_metric_csv"
                    ),
                }
            )
            conditions = sorted({row["prompt_condition"] for row in task_llm_rows})
            for language in languages:
              for condition in conditions:
                condition_rows = [
                    row for row in task_llm_rows
                    if row.get("prompt_language", "en") == language
                    and row.get("prompt_condition") == condition
                ]
                llm_values = collect_numeric(condition_rows, metric)
                if not llm_values:
                    continue
                comparison = compare_llm_to_human(
                        task=task,
                        prompt_condition=condition,
                        metric=metric,
                        llm_values=llm_values,
                        human_values=human_values,
                    )
                comparison["prompt_language"] = language
                comparison_rows.append(comparison)

    closest_rows = []
    for language in languages:
      for task, metrics in metrics_by_task.items():
        for metric in metrics:
            candidates = [
                row for row in comparison_rows
                if row["prompt_language"] == language
                and row["task"] == task and row["metric"] == metric
                and row["human_sd_standardised_distance"] is not None
            ]
            if not candidates:
                continue
            best = min(
                candidates,
                key=lambda row: abs(row["human_sd_standardised_distance"]),
            )
            closest_rows.append(
                {
                    "prompt_language": language,
                    "task": task,
                    "metric": metric,
                    "closest_prompt_condition": best["prompt_condition"],
                    "human_sd_standardised_distance": best[
                        "human_sd_standardised_distance"
                    ],
                    "llm_mean": best["llm_mean"],
                    "human_mean": best["human_mean"],
                    "llm_mean_reference_position": best[
                        "llm_mean_reference_position"
                    ],
                    "llm_runs_within_human_reference_proportion": best[
                        "llm_runs_within_human_reference_proportion"
                    ],
                }
            )

    write_csv(output_dir / "human_metric_summary.csv", human_summary_rows)
    write_csv(output_dir / "llm_human_comparison.csv", comparison_rows)
    write_csv(output_dir / "closest_prompt_by_metric.csv", closest_rows)
    summary = {
        "analysis": "formal_v01_llm_human_comparison",
        "llm_metrics_path": str(llm_metrics_path),
        "human_metrics_dir": str(human_metrics_dir),
        "comparison_rows": len(comparison_rows),
        "human_metric_rows": len(human_summary_rows),
        "closest_prompt_rows": len(closest_rows),
        "task_participants": task_participants,
        "interpretation_boundary": (
            "Each LLM run is compared with participant-level human summaries; "
            "human datasets are task-specific reference distributions, not "
            "population-level definitive benchmarks."
        ),
    }
    (output_dir / "human_comparison_summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("llm_metrics_path", type=Path)
    parser.add_argument("--human-metrics-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/experiment_config_stage01.json"),
    )
    parser.add_argument(
        "--horizon-random-exploration",
        type=Path,
        default=Path("outputs/processed/human_horizon_random_exploration.json"),
    )
    args = parser.parse_args()
    summary = run_llm_human_comparison(
        llm_metrics_path=args.llm_metrics_path,
        human_metrics_dir=args.human_metrics_dir,
        output_dir=args.output_dir,
        metrics_by_task=primary_metrics_from_config(args.config),
        horizon_random_exploration_path=args.horizon_random_exploration,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
