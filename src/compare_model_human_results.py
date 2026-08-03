from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


KEY_FIELDS = ("prompt_language", "task", "prompt_condition", "metric")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"No rows to write: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def combine_model_human_results(
    model_rows: dict[str, list[dict[str, str]]], *, baseline_condition: str = "baseline"
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    combined: list[dict[str, Any]] = []
    reference_by_metric: dict[tuple[str, str], tuple[str, ...]] = {}
    for model, rows in model_rows.items():
        for row in rows:
            task_metric = (row["task"], row["metric"])
            reference = tuple(
                row[field]
                for field in (
                    "human_n", "human_mean", "human_sd",
                    "human_reference_lower", "human_reference_upper",
                )
            )
            if task_metric in reference_by_metric and reference_by_metric[task_metric] != reference:
                raise ValueError(f"Human reference mismatch for {task_metric}.")
            reference_by_metric[task_metric] = reference
            distance = float(row["human_sd_standardised_distance"])
            combined.append(
                {
                    "model": model,
                    **{field: row.get(field, "en") for field in KEY_FIELDS},
                    "llm_n": int(row["llm_n"]),
                    "human_n": int(row["human_n"]),
                    "llm_mean": float(row["llm_mean"]),
                    "human_mean": float(row["human_mean"]),
                    "human_sd": float(row["human_sd"]),
                    "signed_human_sd_distance": distance,
                    "absolute_human_sd_distance": abs(distance),
                    "human_reference_lower": float(row["human_reference_lower"]),
                    "human_reference_upper": float(row["human_reference_upper"]),
                    "llm_mean_reference_position": row["llm_mean_reference_position"],
                    "llm_runs_within_human_reference_proportion": float(row["llm_runs_within_human_reference_proportion"]),
                }
            )
    combined.sort(key=lambda row: (row["task"], row["metric"], row["prompt_condition"], row["model"]))

    changes: list[dict[str, Any]] = []
    for row in combined:
        if row["prompt_condition"] == baseline_condition:
            continue
        baseline = next(
            candidate for candidate in combined
            if candidate["model"] == row["model"]
            and candidate["prompt_language"] == row["prompt_language"]
            and candidate["task"] == row["task"]
            and candidate["metric"] == row["metric"]
            and candidate["prompt_condition"] == baseline_condition
        )
        changes.append(
            {
                "model": row["model"],
                "prompt_language": row["prompt_language"],
                "task": row["task"],
                "prompt_condition": row["prompt_condition"],
                "metric": row["metric"],
                "baseline_signed_human_sd_distance": baseline["signed_human_sd_distance"],
                "condition_signed_human_sd_distance": row["signed_human_sd_distance"],
                "signed_distance_change_from_baseline": row["signed_human_sd_distance"] - baseline["signed_human_sd_distance"],
                "baseline_absolute_human_sd_distance": baseline["absolute_human_sd_distance"],
                "condition_absolute_human_sd_distance": row["absolute_human_sd_distance"],
                "absolute_distance_change_from_baseline": row["absolute_human_sd_distance"] - baseline["absolute_human_sd_distance"],
                "baseline_reference_coverage": baseline["llm_runs_within_human_reference_proportion"],
                "condition_reference_coverage": row["llm_runs_within_human_reference_proportion"],
                "reference_coverage_change_from_baseline": row["llm_runs_within_human_reference_proportion"] - baseline["llm_runs_within_human_reference_proportion"],
            }
        )
    return combined, changes


def main() -> None:
    parser = argparse.ArgumentParser(description="Combine two models' frozen human-reference comparisons.")
    parser.add_argument("--model-a-dir", type=Path, required=True)
    parser.add_argument("--model-a-label", required=True)
    parser.add_argument("--model-b-dir", type=Path, required=True)
    parser.add_argument("--model-b-label", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows, changes = combine_model_human_results(
        {
            args.model_a_label: read_csv(args.model_a_dir / "llm_human_comparison.csv"),
            args.model_b_label: read_csv(args.model_b_dir / "llm_human_comparison.csv"),
        }
    )
    write_csv(args.output_dir / "model_human_comparison.csv", rows)
    write_csv(args.output_dir / "model_human_distance_changes.csv", changes)
    summary = {
        "analysis": "english_two_model_human_reference_comparison",
        "models": [args.model_a_label, args.model_b_label],
        "comparison_rows": len(rows),
        "baseline_change_rows": len(changes),
        "human_reference_metric_count": len({(row["task"], row["metric"]) for row in rows}),
        "interpretation_boundary": "Closer distributional location does not establish a shared cognitive mechanism.",
    }
    (args.output_dir / "model_human_comparison_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
