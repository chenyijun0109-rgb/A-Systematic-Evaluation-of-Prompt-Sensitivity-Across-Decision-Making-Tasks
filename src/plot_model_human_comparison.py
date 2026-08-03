from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.plot_english_model_comparison import (
    COLORS, CONDITION_LABELS, CONDITION_ORDER, METRIC_LABELS, PRIMARY_METRICS, TASKS, TASK_LABELS,
    read_csv, save_figure, style_axis,
)


def plot_human_distance(rows: list[dict[str, str]], output_dir: Path) -> list[str]:
    fig, axes = plt.subplots(3, 3, figsize=(15, 10), constrained_layout=True)
    models = list(COLORS)
    for task_index, task in enumerate(TASKS):
        for metric_index in range(3):
            ax = axes[task_index, metric_index]
            if metric_index >= len(PRIMARY_METRICS[task]):
                ax.axis("off")
                continue
            metric = PRIMARY_METRICS[task][metric_index]
            subset = [row for row in rows if row["task"] == task and row["metric"] == metric]
            conditions = sorted(
                {row["prompt_condition"] for row in subset},
                key=lambda condition: CONDITION_ORDER[condition],
            )
            reference = subset[0]
            human_mean = float(reference["human_mean"])
            human_sd = float(reference["human_sd"])
            reference_low = (float(reference["human_reference_lower"]) - human_mean) / human_sd
            reference_high = (float(reference["human_reference_upper"]) - human_mean) / human_sd
            ax.axhspan(reference_low, reference_high, color="#BDBDBD", alpha=0.22, label="Human 95% reference interval")
            ax.axhline(0, color="#333333", linewidth=0.9)
            for model_index, model in enumerate(models):
                by_condition = {
                    row["prompt_condition"]: row for row in subset if row["model"] == model
                }
                x = [index + (-0.11 if model_index == 0 else 0.11) for index in range(len(conditions))]
                y = [float(by_condition[condition]["signed_human_sd_distance"]) for condition in conditions]
                ax.scatter(x, y, color=COLORS[model], s=28, label=model, zorder=3)
                ax.plot(x, y, color=COLORS[model], linewidth=0.8, alpha=0.55)
            ax.set_xticks(range(len(conditions)), [CONDITION_LABELS[c] for c in conditions], rotation=23, ha="right")
            ax.set_title(METRIC_LABELS[metric], fontsize=10, weight="bold")
            if metric_index == 0:
                ax.set_ylabel(f"{TASK_LABELS[task]}\nHuman-SD distance")
            style_axis(ax)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    axes[1, 2].legend(handles, labels, loc="center", frameon=False, fontsize=10)
    fig.suptitle("Figure 6. Model distance from task-specific human reference distributions", fontsize=15, weight="bold")
    return save_figure(fig, output_dir, "figure_06_human_reference_distance")


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot the frozen two-model human-reference comparison.")
    parser.add_argument("comparison_csv", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    generated = plot_human_distance(read_csv(args.comparison_csv), args.output_dir)
    manifest = {
        "figure": "english_two_model_figure_06_human_reference_distance",
        "source": args.comparison_csv.as_posix(),
        "generated_files": generated,
        "interpretation_boundary": "Distributional proximity does not establish a shared cognitive mechanism.",
    }
    (args.output_dir / "figure_06_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
