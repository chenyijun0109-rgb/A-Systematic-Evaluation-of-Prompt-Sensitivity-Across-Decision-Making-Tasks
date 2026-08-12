"""Build manuscript-facing human-similarity tables for all formal models."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from src.reporting_names import (
    PRIMARY_METRICS,
    PROMPT_CONDITION_ORDER,
    metric_label,
    prompt_condition_label,
    task_label,
)


MODEL_ORDER = {"gpt-4.1": 0, "gpt-5.4": 1, "gpt-5.4-mini": 2}
MODEL_LABEL = {"gpt-4.1": "GPT-4.1", "gpt-5.4": "GPT-5.4", "gpt-5.4-mini": "GPT-5.4 Mini"}
POSITION_SYMBOL = {"within": "○", "above": "↑", "below": "↓"}
LATEX_POSITION_SYMBOL = {"○": r"$\circ$", "↑": r"$\uparrow$", "↓": r"$\downarrow$"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"No rows to write: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def parse_model_input(value: str) -> tuple[str, Path, Path]:
    parts = value.split("=", 2)
    if len(parts) != 3 or not all(parts):
        raise argparse.ArgumentTypeError(
            "--model-input must be MODEL=COMPARISON_CSV=LLM_RUN_METRICS_CSV"
        )
    return parts[0], Path(parts[1]), Path(parts[2])


def classify_runs(
    rows: list[dict[str, str]],
    *,
    task: str,
    condition: str,
    metric: str,
    lower: float,
    upper: float,
) -> tuple[int, int, int]:
    values = [
        float(row[metric])
        for row in rows
        if row.get("task") == task
        and row.get("prompt_condition") == condition
        and row.get(metric, "").strip()
    ]
    below = sum(value < lower for value in values)
    above = sum(value > upper for value in values)
    within = len(values) - below - above
    return below, within, above


def build_tables(
    model_inputs: list[tuple[str, Path, Path]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    detail_rows: list[dict[str, Any]] = []
    human_reference: dict[tuple[str, str], dict[str, Any]] = {}

    for model, comparison_path, metrics_path in model_inputs:
        comparisons = read_csv(comparison_path)
        run_rows = read_csv(metrics_path)
        for row in comparisons:
            task = row["task"]
            metric = row["metric"]
            if metric not in PRIMARY_METRICS[task]:
                continue
            condition = row["prompt_condition"]
            lower = float(row["human_reference_lower"])
            upper = float(row["human_reference_upper"])
            below, within, above = classify_runs(
                run_rows,
                task=task,
                condition=condition,
                metric=metric,
                lower=lower,
                upper=upper,
            )
            llm_n = int(row["llm_n"])
            if below + within + above != llm_n:
                raise ValueError(
                    f"Run classification mismatch for {model}/{task}/{condition}/{metric}: "
                    f"{below}+{within}+{above} != {llm_n}"
                )
            if within != int(row["llm_runs_within_human_reference_count"]):
                raise ValueError(
                    f"Within-count mismatch for {model}/{task}/{condition}/{metric}"
                )
            distance = float(row["human_sd_standardised_distance"])
            position = row["llm_mean_reference_position"]
            coverage = float(row["llm_runs_within_human_reference_proportion"])
            detail_rows.append(
                {
                    "model": model,
                    "task": task,
                    "task_label": task_label(task),
                    "metric": metric,
                    "metric_label": metric_label(metric),
                    "prompt_condition": condition,
                    "prompt_condition_label": prompt_condition_label(condition),
                    "human_n": int(row["human_n"]),
                    "human_mean": float(row["human_mean"]),
                    "human_sd": float(row["human_sd"]),
                    "human_reference_lower": lower,
                    "human_reference_upper": upper,
                    "llm_n": llm_n,
                    "llm_mean": float(row["llm_mean"]),
                    "llm_sd": float(row["llm_sd"]),
                    "raw_mean_difference_llm_minus_human": float(
                        row["raw_mean_difference_llm_minus_human"]
                    ),
                    "signed_human_sd_distance": distance,
                    "absolute_human_sd_distance": abs(distance),
                    "llm_mean_reference_position": position,
                    "llm_mean_human_empirical_quantile": float(
                        row["llm_mean_human_empirical_quantile"]
                    ),
                    "llm_runs_below_human_reference_count": below,
                    "llm_runs_within_human_reference_count": within,
                    "llm_runs_above_human_reference_count": above,
                    "llm_runs_within_human_reference_proportion": coverage,
                    "display_cell": (
                        f"{POSITION_SYMBOL[position]} {distance:+.2f} | {coverage:.0%}"
                    ),
                }
            )
            key = (task, metric)
            candidate = {
                "task": task,
                "task_label": task_label(task),
                "metric": metric,
                "metric_label": metric_label(metric),
                "human_n": int(row["human_n"]),
                "human_mean": float(row["human_mean"]),
                "human_sd": float(row["human_sd"]),
                "human_reference_lower": lower,
                "human_reference_upper": upper,
            }
            if key in human_reference and human_reference[key] != candidate:
                raise ValueError(f"Human reference mismatch across models for {task}/{metric}")
            human_reference[key] = candidate

    detail_rows.sort(
        key=lambda row: (
            MODEL_ORDER.get(row["model"], 99),
            list(PRIMARY_METRICS).index(row["task"]),
            PRIMARY_METRICS[row["task"]].index(row["metric"]),
            PROMPT_CONDITION_ORDER[row["prompt_condition"]],
        )
    )
    references = sorted(
        human_reference.values(),
        key=lambda row: (
            list(PRIMARY_METRICS).index(row["task"]),
            PRIMARY_METRICS[row["task"]].index(row["metric"]),
        ),
    )
    by_key = {
        (row["model"], row["task"], row["metric"], row["prompt_condition"]): row
        for row in detail_rows
    }
    matrix_rows: list[dict[str, Any]] = []
    for model, _, _ in sorted(
        model_inputs, key=lambda item: MODEL_ORDER.get(item[0], 99)
    ):
        for reference in references:
            task = reference["task"]
            metric = reference["metric"]
            conditions = sorted(
                {
                    row["prompt_condition"]
                    for row in detail_rows
                    if row["model"] == model
                    and row["task"] == task
                    and row["metric"] == metric
                },
                key=lambda condition: PROMPT_CONDITION_ORDER[condition],
            )
            cells = {
                condition: by_key[(model, task, metric, condition)]["display_cell"]
                for condition in conditions
            }
            task_specific = next(
                condition
                for condition in conditions
                if condition not in {"baseline", "detailed", "role_human"}
            )
            matrix_rows.append(
                {
                    "model": model,
                    "task": task,
                    "task_label": reference["task_label"],
                    "metric": metric,
                    "metric_label": reference["metric_label"],
                    "neutral_baseline": cells["baseline"],
                    "instruction_specificity": cells["detailed"],
                    "role_framing": cells["role_human"],
                    "task_specific_emphasis": cells[task_specific],
                }
            )
    return references, detail_rows, matrix_rows


def write_markdown(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Formal human-similarity matrix",
        "",
        "Each cell reports `position signed human-SD distance | percentage of LLM runs within the empirical central 95% human reference interval`.",
        "",
        "Symbols: `○` within, `↑` above, and `↓` below the human 2.5th–97.5th percentile interval. The interval describes participant-level variation and is not a confidence interval for the human mean.",
        "",
    ]
    current_model = None
    for index, row in enumerate(rows):
        if row["model"] != current_model:
            current_model = row["model"]
            lines.extend(
                [
                    f"## {current_model}",
                    "",
                    "| Task | Metric | Neutral baseline | Instruction specificity | Role framing | Task-specific emphasis |",
                    "|---|---|---:|---:|---:|---:|",
                ]
            )
        markdown_row = {
            key: (value.replace("|", "\\|") if isinstance(value, str) else value)
            for key, value in row.items()
        }
        lines.append(
            "| {task_label} | {metric_label} | {neutral_baseline} | "
            "{instruction_specificity} | {role_framing} | {task_specific_emphasis} |".format(
                **markdown_row
            )
        )
        next_index = index + 1
        if next_index == len(rows) or rows[next_index]["model"] != current_model:
            lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def latex_escape(value: str) -> str:
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "_": r"\_",
        "#": r"\#",
    }
    return "".join(replacements.get(character, character) for character in value)


def latex_cell(display_cell: str) -> str:
    symbol, distance, separator, coverage = display_cell.split()
    if separator != "|":
        raise ValueError(f"Unexpected display-cell format: {display_cell}")
    return f"{LATEX_POSITION_SYMBOL[symbol]} ${distance}$ / {latex_escape(coverage)}"


def write_latex(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = [
        "% Required packages: \\usepackage{booktabs,graphicx}",
        "% Cell format: position, signed human-SD distance / percentage of LLM runs within the human reference interval.",
        "% Symbols: circle = within, up arrow = above, down arrow = below the empirical human 2.5th--97.5th percentile interval.",
        "% The reference interval describes participant-level variation, not uncertainty around the human mean.",
        "",
    ]
    models = list(dict.fromkeys(row["model"] for row in rows))
    for model in models:
        model_rows = [row for row in rows if row["model"] == model]
        label_model = model.replace(".", "_").replace("-", "_")
        lines.extend(
            [
                r"\begin{table*}[htbp]",
                r"\centering",
                rf"\caption{{Human-reference comparison for {latex_escape(MODEL_LABEL.get(model, model))}.}}",
                rf"\label{{tab:human_similarity_{label_model}}}",
                r"\resizebox{\textwidth}{!}{%",
                r"\begin{tabular}{llcccc}",
                r"\toprule",
                r"Task & Metric & Neutral baseline & Instruction specificity & Role framing & Task-specific emphasis \\ ",
                r"\midrule",
            ]
        )
        previous_task = None
        for row in model_rows:
            if previous_task is not None and row["task"] != previous_task:
                lines.append(r"\addlinespace")
            previous_task = row["task"]
            values = [
                latex_escape(row["task_label"]),
                latex_escape(row["metric_label"]),
                latex_cell(row["neutral_baseline"]),
                latex_cell(row["instruction_specificity"]),
                latex_cell(row["role_framing"]),
                latex_cell(row["task_specific_emphasis"]),
            ]
            lines.append(" & ".join(values) + " \\\\")
        lines.extend(
            [
                r"\bottomrule",
                r"\end{tabular}%",
                r"}",
                r"\begin{minipage}{\textwidth}",
                r"\footnotesize\textit{Note.} Cells report the position of the LLM condition mean relative to the empirical central 95\% human reference interval ($\circ$ within, $\uparrow$ above, $\downarrow$ below), followed by the signed human-SD standardised distance and the percentage of LLM runs within that interval. The interval is based on the human participant-level 2.5th and 97.5th percentiles and is not a confidence interval for the human population mean.",
                r"\end{minipage}",
                r"\end{table*}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build formal three-model human-similarity tables."
    )
    parser.add_argument(
        "--model-input",
        action="append",
        type=parse_model_input,
        required=True,
        help="MODEL=COMPARISON_CSV=LLM_RUN_METRICS_CSV; repeat once per model",
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    references, details, matrix = build_tables(args.model_input)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "table_human_reference.csv", references)
    write_csv(args.output_dir / "table_human_similarity_long.csv", details)
    write_csv(args.output_dir / "table_human_similarity_matrix.csv", matrix)
    write_markdown(args.output_dir / "table_human_similarity_matrix.md", matrix)
    write_latex(args.output_dir / "table_human_similarity_matrix.tex", matrix)
    manifest = {
        "table_set": "formal_three_model_human_similarity_v01",
        "models": [item[0] for item in args.model_input],
        "row_counts": {
            "human_reference": len(references),
            "human_similarity_long": len(details),
            "human_similarity_matrix": len(matrix),
        },
        "cell_format": "position symbol + signed human-SD distance + within-run percentage",
        "interpretation_boundary": (
            "Human empirical reference intervals describe participant-level variation "
            "and are not confidence intervals for the human population mean."
        ),
    }
    (args.output_dir / "table_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
