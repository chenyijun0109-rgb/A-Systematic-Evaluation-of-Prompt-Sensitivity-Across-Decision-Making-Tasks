from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from src.reporting_names import (
    PRIMARY_METRICS,
    PROMPT_CONDITION_ORDER as CONDITION_ORDER,
    metric_label,
    prompt_condition_label,
    task_label,
)


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


def is_primary(row: dict[str, Any]) -> bool:
    return row["metric"] in PRIMARY_METRICS[row["task"]]


def fmt(value: Any) -> str:
    if value in (None, ""):
        return "NA"
    return f"{float(value):.3f}"


def add_reporting_labels(row: dict[str, Any]) -> dict[str, Any]:
    """Add manuscript labels without replacing stable machine identifiers."""
    labelled = dict(row)
    if "task" in row:
        labelled["task_label"] = task_label(str(row["task"]))
    if "prompt_condition" in row:
        labelled["prompt_condition_label"] = prompt_condition_label(
            str(row["prompt_condition"])
        )
    if "metric" in row:
        labelled["metric_label"] = metric_label(str(row["metric"]))
    return labelled


def build_checklist(
    table2: list[dict[str, Any]],
    table3: list[dict[str, Any]],
    table4: list[dict[str, Any]],
    table5: list[dict[str, Any]],
    table6: list[dict[str, Any]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for index, row in enumerate(table2, 1):
        statement = (
            f"{row['model']} {task_label(row['task'])}, "
            f"{prompt_condition_label(row['prompt_condition'])}, {metric_label(row['metric'])}: "
            f"mean {fmt(row['mean'])}, SD {fmt(row['sd'])}, median {fmt(row['median'])}, "
            f"range [{fmt(row['minimum'])}, {fmt(row['maximum'])}], n={row['n']}."
        )
        rows.append({"result_id": f"D{index:03d}", "family": "primary_metric_descriptive", "verified_statement": statement, "source_file": "table_02_primary_metric_descriptives.csv", "source_key": f"{row['model']}|{row['task']}|{row['prompt_condition']}|{row['metric']}", "status": "verified_from_frozen_table"})
    for index, row in enumerate(table3, 1):
        statement = (
            f"{row['model']} {task_label(row['task'])}, "
            f"{prompt_condition_label(row['prompt_condition'])} versus Neutral baseline, "
            f"{metric_label(row['metric'])}: raw mean difference {fmt(row['raw_mean_difference'])}; "
            f"Hedges' g {fmt(row['signed_standardised_effect'])}, 95% bootstrap CI "
            f"[{fmt(row['standardised_effect_ci_lower'])}, {fmt(row['standardised_effect_ci_upper'])}]."
        )
        rows.append({"result_id": f"W{index:03d}", "family": "within_model_prompt_effect", "verified_statement": statement, "source_file": "table_03_within_model_prompt_effects.csv", "source_key": f"{row['model']}|{row['task']}|{row['prompt_condition']}|{row['metric']}", "status": "verified_from_frozen_table"})
    for index, row in enumerate(table4, 1):
        statement = (
            f"GPT-5.4 minus GPT-4.1 prompt effect for {task_label(row['task'])}, "
            f"{prompt_condition_label(row['prompt_condition'])}, {metric_label(row['metric'])}: interaction contrast "
            f"{fmt(row['model_by_prompt_interaction'])}, 95% bootstrap CI "
            f"[{fmt(row['interaction_ci_lower'])}, {fmt(row['interaction_ci_upper'])}] "
            f"using {row['resampling_unit']}."
        )
        rows.append({"result_id": f"I{index:03d}", "family": "model_by_prompt_interaction", "verified_statement": statement, "source_file": "table_04_model_prompt_interactions.csv", "source_key": f"{row['task']}|{row['prompt_condition']}|{row['metric']}", "status": "verified_from_frozen_table"})
    for index, row in enumerate(table5, 1):
        statement = (
            f"{row['model']} {task_label(row['task'])}, "
            f"{prompt_condition_label(row['prompt_condition'])}: PSI {fmt(row['psi'])}, "
            f"95% bootstrap CI [{fmt(row['psi_ci_lower'])}, {fmt(row['psi_ci_upper'])}]; "
            f"descriptive GPT-5.4 minus GPT-4.1 PSI {fmt(row['gpt54_minus_gpt41_psi'])}."
        )
        rows.append({"result_id": f"P{index:03d}", "family": "prompt_sensitivity_index", "verified_statement": statement, "source_file": "table_05_psi_summary.csv", "source_key": f"{row['model']}|{row['task']}|{row['prompt_condition']}", "status": "verified_from_frozen_table"})
    for index, row in enumerate(table6, 1):
        statement = (
            f"{row['model']} {task_label(row['task'])}, "
            f"{prompt_condition_label(row['prompt_condition'])}, {metric_label(row['metric'])}: "
            f"mean distance from human reference {fmt(row['signed_human_sd_distance'])} human SD; "
            f"run coverage within the human reference interval {fmt(row['llm_runs_within_human_reference_proportion'])}."
        )
        rows.append({"result_id": f"H{index:03d}", "family": "human_reference_comparison", "verified_statement": statement, "source_file": "table_06_human_reference_comparison.csv", "source_key": f"{row['model']}|{row['task']}|{row['prompt_condition']}|{row['metric']}", "status": "verified_from_frozen_table"})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Build frozen English two-model manuscript tables.")
    parser.add_argument("--model-a-dir", type=Path, required=True)
    parser.add_argument("--model-a-label", required=True)
    parser.add_argument("--model-b-dir", type=Path, required=True)
    parser.add_argument("--model-b-label", required=True)
    parser.add_argument("--comparison-dir", type=Path, required=True)
    parser.add_argument("--human-comparison-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    models = {args.model_a_label: args.model_a_dir, args.model_b_label: args.model_b_dir}

    audit = json.loads((args.comparison_dir / "input_audit_report.json").read_text(encoding="utf-8"))
    cell_audit = read_csv(args.comparison_dir / "input_cell_audit.csv")
    task_lengths = {"horizon": "40 games / 300 choices", "igt": "100 trials", "bart": "40 balloons / variable pump actions"}
    table1: list[dict[str, Any]] = []
    for model, provenance in audit["provenance"].items():
        for cell in cell_audit:
            table1.append(add_reporting_labels({
                "model": model, "requested_model": provenance["requested_model"], "resolved_model": provenance["resolved_model"],
                "task": cell["task"], "prompt_condition": cell["prompt_condition"], "prompt_sha256": cell["prompt_sha256"],
                "temperature": provenance["temperature"], "top_p": provenance["top_p"], "max_output_tokens": provenance["max_output_tokens"],
                "runs": cell["model_a_runs"] if model == audit["model_a"] else cell["model_b_runs"],
                "matched_seed_count": cell["matched_seed_count"], "task_length": task_lengths[cell["task"]], "audit_status": cell["status"],
            }))

    table2: list[dict[str, Any]] = []
    table3: list[dict[str, Any]] = []
    table5: list[dict[str, Any]] = []
    psi_comparison = {(row["task"], row["prompt_condition"]): row for row in read_csv(args.comparison_dir / "model_psi_comparison.csv")}
    for model, directory in models.items():
        for row in read_csv(directory / "metric_summary.csv"):
            if is_primary(row):
                table2.append(add_reporting_labels({"model": model, "task": row["task"], "prompt_condition": row["prompt_condition"], "metric": row["metric"], **{field: row[field] for field in ("n", "mean", "sd", "median", "minimum", "maximum")} }))
        for row in read_csv(directory / "prompt_effects.csv"):
            if is_primary(row):
                table3.append(add_reporting_labels({"model": model, **{field: row[field] for field in ("task", "prompt_condition", "metric", "baseline_n", "condition_n", "baseline_mean", "condition_mean", "raw_mean_difference", "raw_difference_ci_lower", "raw_difference_ci_upper", "signed_standardised_effect", "standardised_effect_ci_lower", "standardised_effect_ci_upper", "warning_flags")}}))
        for row in read_csv(directory / "prompt_sensitivity.csv"):
            comparison = psi_comparison[(row["task"], row["prompt_condition"])]
            table5.append(add_reporting_labels({"model": model, "task": row["task"], "prompt_condition": row["prompt_condition"], "psi": row["psi"], "psi_ci_lower": row["psi_ci_lower"], "psi_ci_upper": row["psi_ci_upper"], "valid_metric_count": row["valid_metric_count"], "status": row["status"], "gpt54_minus_gpt41_psi": comparison["model_b_minus_model_a_psi"]}))

    sort_key = lambda row: (row["task"], PRIMARY_METRICS[row["task"]].index(row.get("metric", PRIMARY_METRICS[row["task"]][0])), CONDITION_ORDER[row["prompt_condition"]], row.get("model", ""))
    table2.sort(key=sort_key); table3.sort(key=sort_key); table5.sort(key=lambda row: (row["task"], CONDITION_ORDER[row["prompt_condition"]], row["model"]))
    table4 = [add_reporting_labels(row) for row in read_csv(args.comparison_dir / "model_prompt_interaction_contrasts.csv")]
    table4.sort(key=sort_key)
    human_rows = read_csv(args.human_comparison_dir / "model_human_comparison.csv")
    changes = {(row["model"], row["task"], row["prompt_condition"], row["metric"]): row for row in read_csv(args.human_comparison_dir / "model_human_distance_changes.csv")}
    table6 = []
    for row in human_rows:
        change = changes.get((row["model"], row["task"], row["prompt_condition"], row["metric"]), {})
        table6.append(add_reporting_labels({**row, "absolute_distance_change_from_baseline": change.get("absolute_distance_change_from_baseline", ""), "reference_coverage_change_from_baseline": change.get("reference_coverage_change_from_baseline", "")}))
    table6.sort(key=sort_key)

    expected = {"table1": 24, "table2": 64, "table3": 48, "table4": 24, "table5": 18, "table6": 64}
    actual = {"table1": len(table1), "table2": len(table2), "table3": len(table3), "table4": len(table4), "table5": len(table5), "table6": len(table6)}
    if actual != expected:
        raise ValueError(f"Main table row-count validation failed: expected {expected}, observed {actual}")

    tables = {
        "table_01_design_and_provenance.csv": table1,
        "table_02_primary_metric_descriptives.csv": table2,
        "table_03_within_model_prompt_effects.csv": table3,
        "table_04_model_prompt_interactions.csv": table4,
        "table_05_psi_summary.csv": table5,
        "table_06_human_reference_comparison.csv": table6,
    }
    for filename, rows in tables.items():
        write_csv(args.output_dir / filename, rows)
    checklist = build_checklist(table2, table3, table4, table5, table6)
    if len(checklist) != 218 or len({row["source_key"] + row["family"] for row in checklist}) != 218:
        raise ValueError("Primary-results checklist completeness/uniqueness validation failed.")
    write_csv(args.output_dir / "primary_results_checklist.csv", checklist)
    manifest = {"table_set": "english_two_model_main_tables_v01", "row_counts": actual, "checklist_rows": len(checklist), "checklist_scope": "Every row in Tables 2-6 has one verified statement and source key.", "source_scope": "frozen English GPT-4.1 and GPT-5.4 formal batches", "notes": ["No FDR-adjusted p-values are included because the current frozen outputs contain effect sizes and bootstrap intervals but no p-values.", "PSI differences are descriptive.", "Human proximity does not imply a shared cognitive mechanism."]}
    (args.output_dir / "table_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
