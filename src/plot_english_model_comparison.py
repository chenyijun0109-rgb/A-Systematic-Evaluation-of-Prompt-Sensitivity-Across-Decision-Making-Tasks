from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.reporting_names import (
    METRIC_LABELS,
    PRIMARY_METRICS,
    PROMPT_CONDITION_LABELS,
    PROMPT_CONDITION_ORDER,
    TASK_LABELS,
)

TASKS = ("horizon", "igt", "bart")
# Backward-compatible aliases for scripts that imported the former local names.
CONDITION_LABELS = PROMPT_CONDITION_LABELS
COLORS = {"gpt-4.1": "#2878B5", "gpt-5.4": "#D95F02"}
CONDITION_ORDER = PROMPT_CONDITION_ORDER


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def save_figure(fig: plt.Figure, output_dir: Path, stem: str) -> list[str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for suffix in ("png", "pdf"):
        path = output_dir / f"{stem}.{suffix}"
        fig.savefig(path, dpi=300 if suffix == "png" else None, bbox_inches="tight")
        paths.append(path.as_posix())
    plt.close(fig)
    return paths


def style_axis(ax: plt.Axes) -> None:
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.6, alpha=0.7)
    ax.set_axisbelow(True)


def plot_behavior_distributions(
    model_rows: dict[str, list[dict[str, str]]], output_dir: Path
) -> list[str]:
    fig, axes = plt.subplots(3, 3, figsize=(15, 11), constrained_layout=True)
    rng = random.Random(20260731)
    for task_index, task in enumerate(TASKS):
        conditions = [
            condition for condition in CONDITION_LABELS
            if any(row["task"] == task and row["prompt_condition"] == condition for rows in model_rows.values() for row in rows)
        ]
        for metric_index in range(3):
            ax = axes[task_index, metric_index]
            if metric_index >= len(PRIMARY_METRICS[task]):
                ax.axis("off")
                continue
            metric = PRIMARY_METRICS[task][metric_index]
            for model_index, (model, rows) in enumerate(model_rows.items()):
                offset = -0.18 if model_index == 0 else 0.18
                for condition_index, condition in enumerate(conditions):
                    values = [
                        float(row[metric]) for row in rows
                        if row["task"] == task and row["prompt_condition"] == condition and row.get(metric, "")
                    ]
                    position = condition_index + offset
                    ax.boxplot(
                        values, positions=[position], widths=0.28, patch_artist=True,
                        showfliers=False, medianprops={"color": "black", "linewidth": 1.1},
                        boxprops={"facecolor": COLORS[model], "alpha": 0.35, "edgecolor": COLORS[model]},
                        whiskerprops={"color": COLORS[model]}, capprops={"color": COLORS[model]},
                    )
                    jitter = [position + rng.uniform(-0.055, 0.055) for _ in values]
                    ax.scatter(jitter, values, s=10, alpha=0.48, color=COLORS[model], edgecolors="none")
            ax.set_xticks(range(len(conditions)), [CONDITION_LABELS[c] for c in conditions], rotation=24, ha="right")
            ax.set_title(METRIC_LABELS[metric], fontsize=10, weight="bold")
            if metric_index == 0:
                ax.set_ylabel(TASK_LABELS[task])
            style_axis(ax)
    handles = [plt.Line2D([0], [0], marker="o", linestyle="", color=color, label=model) for model, color in COLORS.items()]
    axes[1, 2].legend(handles=handles, loc="center", ncol=1, frameon=False, fontsize=11)
    fig.suptitle("Figure 2. Run-level behavioural distributions by model and prompt", fontsize=15, weight="bold")
    return save_figure(fig, output_dir, "figure_02_behavioral_distributions")


def plot_within_model_effects(
    effect_rows: dict[str, list[dict[str, str]]], output_dir: Path
) -> list[str]:
    fig, axes = plt.subplots(1, 3, figsize=(16, 9), constrained_layout=True)
    for ax, task in zip(axes, TASKS):
        rows_by_model = {
            model: [row for row in rows if row["task"] == task]
            for model, rows in effect_rows.items()
        }
        keys = sorted(
            {(row["metric"], row["prompt_condition"]) for rows in rows_by_model.values() for row in rows},
            key=lambda key: (PRIMARY_METRICS[task].index(key[0]), CONDITION_ORDER[key[1]]),
        )
        labels = [f"{METRIC_LABELS[m]} · {CONDITION_LABELS[c]}" for m, c in keys]
        for model_index, (model, rows) in enumerate(rows_by_model.items()):
            by_key = {(row["metric"], row["prompt_condition"]): row for row in rows}
            y = [index + (-0.14 if model_index == 0 else 0.14) for index in range(len(keys))]
            values = [float(by_key[key]["signed_standardised_effect"]) for key in keys]
            lower = [float(by_key[key]["standardised_effect_ci_lower"]) for key in keys]
            upper = [float(by_key[key]["standardised_effect_ci_upper"]) for key in keys]
            ax.errorbar(values, y, xerr=[[v-l for v, l in zip(values, lower)], [u-v for u, v in zip(upper, values)]], fmt="o", color=COLORS[model], label=model, capsize=2.5, markersize=4)
        ax.axvline(0, color="#333333", linewidth=0.9)
        ax.set_yticks(range(len(keys)), labels, fontsize=8)
        ax.set_title(TASK_LABELS[task], weight="bold")
        ax.set_xlabel("Hedges' g (95% bootstrap CI)")
        ax.invert_yaxis()
        style_axis(ax)
    axes[0].legend(frameon=False, loc="lower left")
    fig.suptitle("Figure 3. Within-model prompt effects", fontsize=15, weight="bold")
    return save_figure(fig, output_dir, "figure_03_within_model_prompt_effects")


def plot_interaction_contrasts(rows: list[dict[str, str]], output_dir: Path) -> list[str]:
    fig, axes = plt.subplots(3, 3, figsize=(15, 10), constrained_layout=True)
    for task_index, task in enumerate(TASKS):
        for metric_index in range(3):
            ax = axes[task_index, metric_index]
            if metric_index >= len(PRIMARY_METRICS[task]):
                ax.axis("off")
                continue
            metric = PRIMARY_METRICS[task][metric_index]
            subset = [row for row in rows if row["task"] == task and row["metric"] == metric]
            subset.sort(key=lambda row: CONDITION_ORDER[row["prompt_condition"]])
            values = [float(row["model_by_prompt_interaction"]) for row in subset]
            lower = [float(row["interaction_ci_lower"]) for row in subset]
            upper = [float(row["interaction_ci_upper"]) for row in subset]
            y = range(len(subset))
            ax.errorbar(values, y, xerr=[[v-l for v, l in zip(values, lower)], [u-v for u, v in zip(upper, values)]], fmt="o", color="#6A3D9A", capsize=3)
            ax.axvline(0, color="#333333", linewidth=0.9)
            ax.set_yticks(list(y), [CONDITION_LABELS[row["prompt_condition"]] for row in subset])
            ax.invert_yaxis()
            ax.set_title(METRIC_LABELS[metric], fontsize=10, weight="bold")
            if metric_index == 0:
                ax.set_ylabel(TASK_LABELS[task])
            ax.set_xlabel("GPT-5.4 effect − GPT-4.1 effect")
            style_axis(ax)
    fig.suptitle("Figure 4. Model-by-prompt interaction contrasts (95% bootstrap CI)", fontsize=15, weight="bold")
    return save_figure(fig, output_dir, "figure_04_model_prompt_interactions")


def plot_psi(
    psi_rows: dict[str, list[dict[str, str]]], comparison_rows: list[dict[str, str]], output_dir: Path
) -> list[str]:
    fig, axes = plt.subplots(2, 3, figsize=(15, 8), constrained_layout=True)
    for task_index, task in enumerate(TASKS):
        ax = axes[0, task_index]
        task_conditions = sorted(
            {row["prompt_condition"] for rows in psi_rows.values() for row in rows if row["task"] == task},
            key=lambda condition: CONDITION_ORDER[condition],
        )
        for model_index, (model, rows) in enumerate(psi_rows.items()):
            by_condition = {row["prompt_condition"]: row for row in rows if row["task"] == task}
            x = [index + (-0.1 if model_index == 0 else 0.1) for index in range(len(task_conditions))]
            values = [float(by_condition[c]["psi"]) for c in task_conditions]
            lower = [float(by_condition[c]["psi_ci_lower"]) for c in task_conditions]
            upper = [float(by_condition[c]["psi_ci_upper"]) for c in task_conditions]
            ax.errorbar(x, values, yerr=[[v-l for v, l in zip(values, lower)], [u-v for u, v in zip(upper, values)]], fmt="o", color=COLORS[model], label=model, capsize=3)
        ax.set_xticks(range(len(task_conditions)), [CONDITION_LABELS[c] for c in task_conditions], rotation=20, ha="right")
        ax.set_title(TASK_LABELS[task], weight="bold")
        ax.set_ylabel("PSI" if task_index == 0 else "")
        style_axis(ax)

        diff_ax = axes[1, task_index]
        subset = sorted(
            [row for row in comparison_rows if row["task"] == task],
            key=lambda row: CONDITION_ORDER[row["prompt_condition"]],
        )
        x = range(len(subset))
        values = [float(row["model_b_minus_model_a_psi"]) for row in subset]
        diff_ax.bar(x, values, color=["#6A3D9A" if value >= 0 else "#5AAE61" for value in values], alpha=0.8)
        diff_ax.axhline(0, color="#333333", linewidth=0.9)
        diff_ax.set_xticks(list(x), [CONDITION_LABELS[row["prompt_condition"]] for row in subset], rotation=20, ha="right")
        diff_ax.set_ylabel("GPT-5.4 − GPT-4.1 PSI" if task_index == 0 else "")
        style_axis(diff_ax)
    axes[0, 0].legend(frameon=False)
    fig.suptitle("Figure 5. Prompt Sensitivity Index by model and task", fontsize=15, weight="bold")
    return save_figure(fig, output_dir, "figure_05_prompt_sensitivity_index")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate English two-model comparison Figures 2-5.")
    parser.add_argument("--model-a-dir", type=Path, required=True)
    parser.add_argument("--model-a-label", default="gpt-4.1")
    parser.add_argument("--model-b-dir", type=Path, required=True)
    parser.add_argument("--model-b-label", default="gpt-5.4")
    parser.add_argument("--comparison-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    models = {args.model_a_label: args.model_a_dir, args.model_b_label: args.model_b_dir}
    model_rows = {label: read_csv(path / "llm_run_metrics.csv") for label, path in models.items()}
    effects = {label: read_csv(path / "prompt_effects.csv") for label, path in models.items()}
    psi = {label: read_csv(path / "prompt_sensitivity.csv") for label, path in models.items()}
    generated = []
    generated += plot_behavior_distributions(model_rows, args.output_dir)
    generated += plot_within_model_effects(effects, args.output_dir)
    generated += plot_interaction_contrasts(read_csv(args.comparison_dir / "model_prompt_interaction_contrasts.csv"), args.output_dir)
    generated += plot_psi(psi, read_csv(args.comparison_dir / "model_psi_comparison.csv"), args.output_dir)
    manifest: dict[str, Any] = {
        "figure_set": "english_two_model_figures_02_to_05",
        "models": list(models),
        "generated_files": generated,
        "notes": [
            "Positive metric effects are not inherently beneficial.",
            "PSI is a project-defined descriptive index, not a validated psychological scale.",
            "Interaction contrasts are not causal difference-in-differences estimates.",
        ],
    }
    (args.output_dir / "figure_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
