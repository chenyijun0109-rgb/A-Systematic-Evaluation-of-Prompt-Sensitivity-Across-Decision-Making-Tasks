from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any


KEY_FIELDS = ("task", "prompt_condition", "seed")
PROVENANCE_FIELDS = (
    "requested_model",
    "resolved_model",
    "temperature",
    "top_p",
    "max_output_tokens",
    "config_name",
    "config_version",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def unique_value(rows: list[dict[str, str]], field: str, label: str) -> str:
    values = {row.get(field, "") for row in rows}
    if len(values) != 1:
        raise ValueError(f"{label} has multiple {field} values: {sorted(values)}")
    return next(iter(values))


def task_structure_complete(row: dict[str, str]) -> bool:
    if row["task"] == "horizon":
        return int(row["n_trials"]) == 300 and int(row["n_games"]) == 40
    if row["task"] == "igt":
        return int(row["n_trials"]) == 100
    if row["task"] == "bart":
        return int(row["n_balloons"]) == 40 and int(row["n_trials"]) >= 40
    return False


def audit_inputs(
    model_a_rows: list[dict[str, str]],
    model_b_rows: list[dict[str, str]],
    *,
    model_a_label: str,
    model_b_label: str,
    expected_runs_per_cell: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    issues: list[str] = []
    keyed: list[dict[tuple[str, str, str], dict[str, str]]] = []
    for label, rows in ((model_a_label, model_a_rows), (model_b_label, model_b_rows)):
        keys = [tuple(row[field] for field in KEY_FIELDS) for row in rows]
        duplicates = sorted(key for key, count in Counter(keys).items() if count > 1)
        if duplicates:
            issues.append(f"{label}: duplicate task-condition-seed keys: {duplicates}")
        keyed.append(dict(zip(keys, rows)))
        for row in rows:
            if row.get("done", "").lower() != "true":
                issues.append(f"{label}: incomplete run {tuple(row[field] for field in KEY_FIELDS)}")
            if float(row.get("parse_success_rate", "0")) != 1.0:
                issues.append(f"{label}: parse failure {tuple(row[field] for field in KEY_FIELDS)}")
            if int(row.get("invalid_response_count", "0")) != 0:
                issues.append(f"{label}: invalid response {tuple(row[field] for field in KEY_FIELDS)}")

    if set(keyed[0]) != set(keyed[1]):
        missing_a = sorted(set(keyed[1]) - set(keyed[0]))
        missing_b = sorted(set(keyed[0]) - set(keyed[1]))
        issues.append(f"matched keys differ; missing from {model_a_label}: {missing_a}; missing from {model_b_label}: {missing_b}")

    cell_rows: list[dict[str, Any]] = []
    cells: dict[tuple[str, str], dict[str, list[dict[str, str]]]] = defaultdict(
        lambda: {model_a_label: [], model_b_label: []}
    )
    for label, rows in ((model_a_label, model_a_rows), (model_b_label, model_b_rows)):
        for row in rows:
            cells[(row["task"], row["prompt_condition"])][label].append(row)

    for (task, condition), groups in sorted(cells.items()):
        a_rows, b_rows = groups[model_a_label], groups[model_b_label]
        a_seeds = sorted(int(row["seed"]) for row in a_rows)
        b_seeds = sorted(int(row["seed"]) for row in b_rows)
        hashes = sorted({row["prompt_sha256"] for row in a_rows + b_rows})
        cell_issues: list[str] = []
        if len(a_rows) != expected_runs_per_cell or len(b_rows) != expected_runs_per_cell:
            cell_issues.append("unexpected_run_count")
        if a_seeds != b_seeds:
            cell_issues.append("unmatched_seeds")
        if len(hashes) != 1:
            cell_issues.append("prompt_hash_mismatch")
        for row in a_rows + b_rows:
            if not task_structure_complete(row):
                cell_issues.append("unexpected_trial_count")
                break
        if cell_issues:
            issues.append(f"{task}/{condition}: {','.join(cell_issues)}")
        cell_rows.append(
            {
                "task": task,
                "prompt_condition": condition,
                "model_a_runs": len(a_rows),
                "model_b_runs": len(b_rows),
                "matched_seed_count": len(set(a_seeds) & set(b_seeds)),
                "prompt_sha256": hashes[0] if len(hashes) == 1 else "|".join(hashes),
                "status": "pass" if not cell_issues else "fail",
            }
        )

    provenance: dict[str, dict[str, str]] = {}
    for label, rows in ((model_a_label, model_a_rows), (model_b_label, model_b_rows)):
        try:
            provenance[label] = {field: unique_value(rows, field, label) for field in PROVENANCE_FIELDS}
        except ValueError as error:
            issues.append(str(error))

    report = {
        "analysis": "english_two_model_input_audit",
        "analysis_complete": not issues,
        "model_a": model_a_label,
        "model_b": model_b_label,
        "model_a_run_count": len(model_a_rows),
        "model_b_run_count": len(model_b_rows),
        "cell_count": len(cell_rows),
        "expected_runs_per_cell": expected_runs_per_cell,
        "matched_key_count": len(set(keyed[0]) & set(keyed[1])),
        "provenance": provenance,
        "excluded_inputs": ["Chinese and Spanish runs"],
        "issues": issues,
    }
    return report, cell_rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Freeze and audit English two-model analysis inputs.")
    parser.add_argument("--model-a-dir", type=Path, required=True)
    parser.add_argument("--model-a-label", required=True)
    parser.add_argument("--model-b-dir", type=Path, required=True)
    parser.add_argument("--model-b-label", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--expected-runs-per-cell", type=int, default=20)
    args = parser.parse_args()

    sources = {
        args.model_a_label: args.model_a_dir / "llm_run_metrics.csv",
        args.model_b_label: args.model_b_dir / "llm_run_metrics.csv",
    }
    report, cells = audit_inputs(
        read_csv(sources[args.model_a_label]),
        read_csv(sources[args.model_b_label]),
        model_a_label=args.model_a_label,
        model_b_label=args.model_b_label,
        expected_runs_per_cell=args.expected_runs_per_cell,
    )
    if not report["analysis_complete"]:
        raise ValueError("Input audit failed: " + "; ".join(report["issues"]))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "manifest": "english_two_model_analysis_inputs_v01",
        "frozen_on": date.today().isoformat(),
        "status": "frozen",
        "scope": "English GPT-4.1 versus GPT-5.4 formal analysis",
        "input_files": {
            label: {"path": path.as_posix(), "sha256": sha256(path)}
            for label, path in sources.items()
        },
        "audit_report": "input_audit_report.json",
        "cell_audit": "input_cell_audit.csv",
        "exclusions": report["excluded_inputs"],
    }
    (args.output_dir / "input_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (args.output_dir / "input_audit_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    write_csv(args.output_dir / "input_cell_audit.csv", cells)


if __name__ == "__main__":
    main()
