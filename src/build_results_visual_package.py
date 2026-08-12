from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.lines import Line2D


ROOT = Path("outputs/processed/final_analysis_v03")
FIGURE_DIR = Path("outputs/figures/final_results_v01")
LATEX_DIR = Path("docs/results_visuals")

TASKS = ("horizon", "igt", "bart")
TASK_LABELS = {"horizon": "Horizon Task", "igt": "Iowa Gambling Task", "bart": "BART"}
METRICS = {
    "horizon": ("directed_exploration", "horizon_effect", "random_exploration_effect"),
    "igt": ("advantageous_choice_rate", "post_loss_switching_rate"),
    "bart": ("adjusted_average_pumps", "explosion_rate", "post_explosion_adjustment"),
}
METRIC_LABELS = {
    "directed_exploration": "Information-seeking choice rate",
    "horizon_effect": "Horizon-related exploration change",
    "random_exploration_effect": "Random-exploration effect",
    "advantageous_choice_rate": "Advantageous-choice rate",
    "post_loss_switching_rate": "Post-loss switching rate",
    "adjusted_average_pumps": "Adjusted average pumps",
    "explosion_rate": "Explosion rate",
    "post_explosion_adjustment": "Post-explosion adjustment",
}
CONDITIONS = {
    "horizon": ("detailed", "role_human", "uncertainty_emphasis"),
    "igt": ("detailed", "role_human", "reward_loss_emphasis"),
    "bart": ("detailed", "role_human", "risk_emphasis"),
}
CONDITION_LABELS = {
    "detailed": "Instruction specificity",
    "role_human": "Role framing",
    "uncertainty_emphasis": "Uncertainty emphasis",
    "reward_loss_emphasis": "Reward/loss emphasis",
    "risk_emphasis": "Risk emphasis",
}
CONDITION_SHORT = {
    "detailed": "Instruction\nspecificity",
    "role_human": "Role\nframing",
    "uncertainty_emphasis": "Uncertainty\nemphasis",
    "reward_loss_emphasis": "Reward/loss\nemphasis",
    "risk_emphasis": "Risk\nemphasis",
}
COLORS = {"detailed": "#0072B2", "role_human": "#D55E00", "task": "#009E73"}
LANGUAGE_COLORS = {"en": "#332288", "zh-CN": "#D55E00", "es": "#009E73"}
LANGUAGE_MARKERS = {"en": "o", "zh-CN": "^", "es": "s"}
LANGUAGE_LABELS = {"en": "English", "zh-CN": "Simplified Chinese", "es": "Spanish"}
MODEL_INPUTS = {
    "GPT-4.1": ROOT / "gpt-4.1-en" / "prompt_effects.csv",
    "GPT-5.4": ROOT / "gpt-5.4-en" / "prompt_effects.csv",
    "GPT-5.4 Mini": ROOT / "gpt-5.4-mini-en" / "prompt_effects.csv",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def f(row: dict[str, str], field: str) -> float:
    return float(row[field])


def condition_color(condition: str) -> str:
    if condition == "detailed":
        return COLORS["detailed"]
    if condition == "role_human":
        return COLORS["role_human"]
    return COLORS["task"]


def set_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.titlesize": 10.5,
            "axes.labelsize": 9.5,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8.5,
            "figure.dpi": 150,
            "savefig.dpi": 600,
            "savefig.bbox": "tight",
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def save_figure(fig: plt.Figure, stem: str) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURE_DIR / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(FIGURE_DIR / f"{stem}.png", dpi=600, bbox_inches="tight")
    plt.close(fig)


def lookup(rows: list[dict[str, str]], **criteria: str) -> dict[str, str]:
    matches = [row for row in rows if all(row[key] == value for key, value in criteria.items())]
    if len(matches) != 1:
        raise ValueError(f"Expected one row for {criteria}, found {len(matches)}")
    return matches[0]


def plot_grouped_forest(
    ax: plt.Axes,
    rows: list[dict[str, str]],
    *,
    task: str,
    estimate: str,
    lower: str,
    upper: str,
) -> None:
    metrics = METRICS[task]
    conditions = CONDITIONS[task]
    offsets = (-0.22, 0.0, 0.22)
    for c_index, condition in enumerate(conditions):
        for m_index, metric in enumerate(metrics):
            row = lookup(rows, task=task, prompt_condition=condition, metric=metric)
            y = len(metrics) - 1 - m_index + offsets[c_index]
            value, lo, hi = f(row, estimate), f(row, lower), f(row, upper)
            ax.errorbar(
                value,
                y,
                xerr=[[value - lo], [hi - value]],
                fmt="o",
                color=condition_color(condition),
                ecolor=condition_color(condition),
                elinewidth=1.4,
                capsize=2.5,
                markersize=4.5,
            )
    ax.axvline(0, color="#555555", linewidth=0.9, linestyle="--", zorder=0)
    ax.set_yticks(range(len(metrics)))
    ax.set_yticklabels([METRIC_LABELS[metric] for metric in reversed(metrics)])
    ax.grid(axis="x", color="#dddddd", linewidth=0.6)
    ax.set_xlabel("Raw contrast (95% bootstrap CI)")


def figure_rq1() -> None:
    fig, axes = plt.subplots(3, 3, figsize=(16.5, 13.5), constrained_layout=True)
    for column, (model, path) in enumerate(MODEL_INPUTS.items()):
        rows = read_csv(path)
        for row_index, task in enumerate(TASKS):
            ax = axes[row_index, column]
            plot_grouped_forest(
                ax,
                rows,
                task=task,
                estimate="raw_mean_difference",
                lower="raw_difference_ci_lower",
                upper="raw_difference_ci_upper",
            )
            ax.set_title(f"{model} — {TASK_LABELS[task]}")
    legend = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLORS["detailed"], markeredgecolor=COLORS["detailed"], label="Instruction specificity"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLORS["role_human"], markeredgecolor=COLORS["role_human"], label="Role framing"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLORS["task"], markeredgecolor=COLORS["task"], label="Task-specific emphasis"),
    ]
    fig.legend(handles=legend, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.025))
    fig.suptitle("RQ1: Within-model prompt effects relative to Neutral", fontsize=14, y=1.045)
    save_figure(fig, "figure_rq1_prompt_effects")


def figure_rq2() -> None:
    comparisons = {
        "GPT-4.1 minus GPT-5.4": ROOT / "gpt-4.1-minus-gpt-5.4" / "model_prompt_interaction_contrasts.csv",
        "GPT-5.4 Mini minus GPT-5.4": ROOT / "gpt-5.4-mini-minus-gpt-5.4" / "model_prompt_interaction_contrasts.csv",
    }
    fig, axes = plt.subplots(3, 2, figsize=(13.5, 13), constrained_layout=True)
    for column, (label, path) in enumerate(comparisons.items()):
        rows = read_csv(path)
        for row_index, task in enumerate(TASKS):
            ax = axes[row_index, column]
            plot_grouped_forest(
                ax,
                rows,
                task=task,
                estimate="model_by_prompt_interaction",
                lower="interaction_ci_lower",
                upper="interaction_ci_upper",
            )
            ax.set_title(f"{label} — {TASK_LABELS[task]}")
    legend = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLORS["detailed"], markeredgecolor=COLORS["detailed"], label="Instruction specificity"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLORS["role_human"], markeredgecolor=COLORS["role_human"], label="Role framing"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLORS["task"], markeredgecolor=COLORS["task"], label="Task-specific emphasis"),
    ]
    fig.legend(handles=legend, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.02))
    fig.suptitle("RQ2: Model-by-prompt interaction contrasts", fontsize=14, y=1.04)
    save_figure(fig, "figure_rq2_model_interactions")


def figure_rq3_baselines() -> None:
    rows = read_csv(ROOT / "gpt-4.1-multilingual" / "language_baseline_contrasts.csv")
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 5.2), constrained_layout=True)
    offsets = {"zh-CN": -0.12, "es": 0.12}
    for ax, task in zip(axes, TASKS):
        metrics = METRICS[task]
        for language in ("zh-CN", "es"):
            for index, metric in enumerate(metrics):
                row = lookup(rows, task=task, target_language=language, metric=metric)
                y = len(metrics) - 1 - index + offsets[language]
                value, lo, hi = f(row, "raw_language_difference"), f(row, "raw_ci_lower"), f(row, "raw_ci_upper")
                ax.errorbar(value, y, xerr=[[value - lo], [hi - value]], fmt="o", color=LANGUAGE_COLORS[language], capsize=3, elinewidth=1.5)
        ax.axvline(0, color="#555555", linewidth=0.9, linestyle="--")
        ax.set_yticks(range(len(metrics)))
        ax.set_yticklabels([METRIC_LABELS[m] for m in reversed(metrics)])
        ax.set_title(TASK_LABELS[task])
        ax.set_xlabel("Target language minus English\n(95% bootstrap CI)")
        ax.grid(axis="x", color="#dddddd", linewidth=0.6)
    legend = [
        Line2D([0], [0], marker="o", color=LANGUAGE_COLORS["zh-CN"], linestyle="none", label="Simplified Chinese"),
        Line2D([0], [0], marker="o", color=LANGUAGE_COLORS["es"], linestyle="none", label="Spanish"),
    ]
    fig.legend(handles=legend, loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 1.05))
    fig.suptitle("RQ3a: Neutral-baseline language contrasts", fontsize=14, y=1.12)
    save_figure(fig, "figure_rq3_baseline_language_contrasts")


def heatmap(
    ax: plt.Axes,
    matrix: np.ndarray,
    annotations: list[list[str]],
    *,
    xlabels: list[str],
    ylabels: list[str],
    title: str,
    norm: TwoSlopeNorm,
    cmap: str = "RdBu_r",
) -> Any:
    image = ax.imshow(matrix, cmap=cmap, norm=norm, aspect="auto")
    ax.set_xticks(range(len(xlabels)), labels=xlabels)
    ax.set_yticks(range(len(ylabels)), labels=ylabels)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            value = matrix[i, j]
            rgba = image.cmap(image.norm(value))
            luminance = 0.2126 * rgba[0] + 0.7152 * rgba[1] + 0.0722 * rgba[2]
            ax.text(j, i, annotations[i][j], ha="center", va="center", fontsize=7.3, color="black" if luminance > 0.52 else "white")
    ax.set_title(title)
    ax.tick_params(axis="x", rotation=0)
    ax.set_xticks(np.arange(-0.5, len(xlabels), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(ylabels), 1), minor=True)
    ax.grid(which="minor", color="white", linestyle="-", linewidth=1.2)
    ax.tick_params(which="minor", bottom=False, left=False)
    return image


def figure_rq3_interactions() -> None:
    rows = read_csv(ROOT / "gpt-4.1-multilingual" / "language_prompt_interactions.csv")
    max_abs = max(abs(f(row, "raw_interaction_contrast")) for row in rows)
    norm = TwoSlopeNorm(vmin=-max_abs, vcenter=0, vmax=max_abs)
    fig, axes = plt.subplots(2, 3, figsize=(16.5, 9.5), constrained_layout=True)
    last_image = None
    for r_index, language in enumerate(("zh-CN", "es")):
        for c_index, task in enumerate(TASKS):
            conditions = CONDITIONS[task]
            metrics = METRICS[task]
            matrix = np.zeros((len(metrics), len(conditions)))
            annotations: list[list[str]] = []
            for i, metric in enumerate(metrics):
                annotation_row = []
                for j, condition in enumerate(conditions):
                    row = lookup(rows, task=task, target_language=language, prompt_condition=condition, metric=metric)
                    value = f(row, "raw_interaction_contrast")
                    matrix[i, j] = value
                    excludes_zero = f(row, "raw_ci_lower") > 0 or f(row, "raw_ci_upper") < 0
                    annotation_row.append(f"{value:.2f}{'†' if excludes_zero else ''}")
                annotations.append(annotation_row)
            last_image = heatmap(
                axes[r_index, c_index], matrix, annotations,
                xlabels=[CONDITION_SHORT[c] for c in conditions],
                ylabels=[METRIC_LABELS[m] for m in metrics],
                title=f"{'Simplified Chinese' if language == 'zh-CN' else 'Spanish'} — {TASK_LABELS[task]}",
                norm=norm,
            )
    assert last_image is not None
    fig.colorbar(last_image, ax=axes, shrink=0.72, label="Raw language-by-prompt interaction")
    fig.suptitle("RQ3b: Language-by-prompt interaction contrasts", fontsize=14)
    fig.text(0.5, -0.01, "† Percentile interval does not include zero; marker is descriptive and not multiplicity-adjusted.", ha="center", fontsize=8.5)
    save_figure(fig, "figure_rq3_language_prompt_heatmap")


def figure_rq3_parallel_languages() -> None:
    """Present the three languages as parallel conditions in the main RQ3 display."""
    summary_rows = read_csv(ROOT / "gpt-4.1-multilingual" / "metric_summary.csv")
    effect_rows = read_csv(ROOT / "gpt-4.1-multilingual" / "prompt_effects.csv")
    languages = ("en", "zh-CN", "es")
    offsets = {"en": -0.20, "zh-CN": 0.0, "es": 0.20}
    fig, axes = plt.subplots(2, 3, figsize=(17.5, 10.5), constrained_layout=True)

    for column, task in enumerate(TASKS):
        metrics = METRICS[task]
        baseline_ax = axes[0, column]
        effect_ax = axes[1, column]

        for language in languages:
            for index, metric in enumerate(metrics):
                row = lookup(
                    summary_rows,
                    prompt_language=language,
                    task=task,
                    prompt_condition="baseline",
                    metric=metric,
                )
                y = len(metrics) - 1 - index + offsets[language]
                baseline_ax.errorbar(
                    f(row, "mean"), y, xerr=f(row, "sd"),
                    fmt=LANGUAGE_MARKERS[language], color=LANGUAGE_COLORS[language],
                    capsize=3, elinewidth=1.25, markersize=5,
                )

        baseline_ax.set_yticks(range(len(metrics)))
        baseline_ax.set_yticklabels([METRIC_LABELS[m] for m in reversed(metrics)])
        baseline_ax.set_title(TASK_LABELS[task])
        baseline_ax.set_xlabel("Neutral mean (error bars: run SD)")
        baseline_ax.grid(axis="x", color="#dddddd", linewidth=0.6)

        conditions = CONDITIONS[task]
        grouped = [(metric, condition) for metric in metrics for condition in conditions]
        for language in languages:
            for index, (metric, condition) in enumerate(grouped):
                row = lookup(
                    effect_rows,
                    prompt_language=language,
                    task=task,
                    prompt_condition=condition,
                    metric=metric,
                )
                y = len(grouped) - 1 - index + offsets[language]
                value = f(row, "raw_mean_difference")
                lo, hi = f(row, "raw_difference_ci_lower"), f(row, "raw_difference_ci_upper")
                effect_ax.errorbar(
                    value, y, xerr=[[value - lo], [hi - value]],
                    fmt=LANGUAGE_MARKERS[language], color=LANGUAGE_COLORS[language],
                    capsize=2.5, elinewidth=1.15, markersize=4.5,
                )
        effect_ax.axvline(0, color="#555555", linewidth=0.9, linestyle="--")
        effect_ax.set_yticks(range(len(grouped)))
        effect_ax.set_yticklabels([
            f"{METRIC_LABELS[metric]} | {CONDITION_LABELS[condition]}"
            for metric, condition in reversed(grouped)
        ], fontsize=7.5)
        effect_ax.set_xlabel("Condition minus same-language Neutral\n(95% bootstrap CI)")
        effect_ax.grid(axis="x", color="#dddddd", linewidth=0.6)

    legend = [
        Line2D([0], [0], marker=LANGUAGE_MARKERS[language], color=LANGUAGE_COLORS[language],
               linestyle="none", label=LANGUAGE_LABELS[language])
        for language in languages
    ]
    fig.legend(handles=legend, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.015))
    axes[0, 0].text(0.0, 1.055, "A  Neutral baseline", transform=axes[0, 0].transAxes,
                    ha="left", va="bottom", fontsize=11.5, weight="bold")
    axes[1, 0].text(0.0, 1.035, "B  Within-language prompt effects", transform=axes[1, 0].transAxes,
                    ha="left", va="bottom", fontsize=11.5, weight="bold")
    fig.suptitle("RQ3: Parallel comparison of English, Simplified Chinese, and Spanish", fontsize=14, y=1.04)
    save_figure(fig, "figure_rq3_parallel_languages")


def figure_rq4() -> None:
    rows = read_csv(ROOT / "human_reference_results" / "model_human_distance_changes.csv")
    groups = (
        ("GPT-4.1", "en", "GPT-4.1 EN"),
        ("GPT-4.1", "zh-CN", "GPT-4.1 ZH"),
        ("GPT-4.1", "es", "GPT-4.1 ES"),
        ("GPT-5.4", "en", "GPT-5.4 EN"),
        ("GPT-5.4 Mini", "en", "Mini EN"),
    )
    abs_max = max(abs(f(row, "absolute_deviation_change_from_baseline")) for row in rows)
    norms = {
        "absolute_deviation_change_from_baseline": TwoSlopeNorm(vmin=-abs_max, vcenter=0, vmax=abs_max),
        "reference_coverage_change_from_baseline": TwoSlopeNorm(vmin=-1, vcenter=0, vmax=1),
    }
    fig, axes = plt.subplots(2, 3, figsize=(17.5, 17), constrained_layout=True)
    images: list[Any] = []
    for r_index, field in enumerate(("absolute_deviation_change_from_baseline", "reference_coverage_change_from_baseline")):
        for c_index, task in enumerate(TASKS):
            conditions = CONDITIONS[task]
            y_keys = [(model, language, label, metric) for model, language, label in groups for metric in METRICS[task]]
            matrix = np.zeros((len(y_keys), len(conditions)))
            annotations: list[list[str]] = []
            for i, (model, language, _, metric) in enumerate(y_keys):
                annotation_row = []
                for j, condition in enumerate(conditions):
                    row = lookup(rows, model=model, prompt_language=language, task=task, prompt_condition=condition, metric=metric)
                    value = f(row, field)
                    matrix[i, j] = value
                    annotation_row.append(f"{value:.2f}")
                annotations.append(annotation_row)
            ylabels = [f"{label} · {METRIC_LABELS[metric]}" for _, _, label, metric in y_keys]
            title_prefix = "Change in absolute human-SD-scaled deviation" if r_index == 0 else "Change in empirical coverage"
            image = heatmap(
                axes[r_index, c_index], matrix, annotations,
                xlabels=[CONDITION_SHORT[c] for c in conditions],
                ylabels=ylabels,
                title=f"{title_prefix}\n{TASK_LABELS[task]}",
                norm=norms[field],
            )
            images.append(image)
    fig.colorbar(images[0], ax=axes[0, :], shrink=0.7, label="Δ absolute deviation (negative = closer mean)")
    fig.colorbar(images[3], ax=axes[1, :], shrink=0.7, label="Δ coverage (positive = more runs within range)")
    fig.suptitle("RQ4: Descriptive human-reference sensitivity relative to Neutral", fontsize=14)
    save_figure(fig, "figure_rq4_human_reference_heatmap")


ALL_METRICS = tuple(metric for task in TASKS for metric in METRICS[task])
METRIC_TASK = {metric: task for task in TASKS for metric in METRICS[task]}


def _symmetric_limits(values: list[float]) -> tuple[float, float]:
    extent = max((abs(value) for value in values if math.isfinite(value)), default=1.0)
    extent = max(extent * 1.12, 0.01)
    return -extent, extent


def _forest_cell(
    ax: plt.Axes,
    rows: list[dict[str, str]],
    metric: str,
    estimate: str,
    lower: str,
    upper: str,
    *,
    show_ylabels: bool,
) -> list[float]:
    task = METRIC_TASK[metric]
    conditions = CONDITIONS[task]
    values: list[float] = []
    for index, condition in enumerate(conditions):
        row = lookup(rows, task=task, prompt_condition=condition, metric=metric)
        value, lo, hi = f(row, estimate), f(row, lower), f(row, upper)
        values.extend((lo, hi))
        y = len(conditions) - 1 - index
        ax.errorbar(value, y, xerr=[[value - lo], [hi - value]], fmt="o",
                    color=condition_color(condition), ecolor=condition_color(condition),
                    elinewidth=1.35, capsize=2.2, markersize=4.4)
    ax.axvline(0, color="#666666", linewidth=0.8, linestyle="--", zorder=0)
    ax.set_yticks(range(len(conditions)))
    if show_ylabels:
        ax.set_yticklabels([CONDITION_LABELS[c] for c in reversed(conditions)], fontsize=7.2)
    else:
        ax.set_yticklabels([])
    ax.grid(axis="x", color="#e1e1e1", linewidth=0.55)
    return values


def figure_rq1_v2() -> None:
    model_rows = {model: read_csv(path) for model, path in MODEL_INPUTS.items()}
    fig, axes = plt.subplots(len(ALL_METRICS), len(model_rows), figsize=(14.8, 19.5), constrained_layout=True)
    for row_index, metric in enumerate(ALL_METRICS):
        bounds: list[float] = []
        for column, (model, rows) in enumerate(model_rows.items()):
            ax = axes[row_index, column]
            bounds.extend(_forest_cell(ax, rows, metric, "raw_mean_difference",
                                       "raw_difference_ci_lower", "raw_difference_ci_upper",
                                       show_ylabels=column == 0))
            if row_index == 0:
                ax.set_title(model, weight="bold")
            if column == 0:
                ax.set_ylabel(METRIC_LABELS[metric], fontsize=8.3, weight="bold", labelpad=8)
            if row_index == len(ALL_METRICS) - 1:
                ax.set_xlabel("Manipulated minus Neutral\n(95% bootstrap CI)")
        limits = _symmetric_limits(bounds)
        for column in range(len(model_rows)):
            axes[row_index, column].set_xlim(*limits)
    fig.suptitle("RQ1: Within-model prompt effects relative to Neutral", fontsize=14, y=1.01)
    save_figure(fig, "figure_rq1_prompt_effects")


def figure_rq2_v2() -> None:
    comparisons = {
        "GPT-4.1 vs GPT-5.4": ROOT / "gpt-4.1-minus-gpt-5.4" / "model_prompt_interaction_contrasts.csv",
        "GPT-5.4 Mini vs GPT-5.4": ROOT / "gpt-5.4-mini-minus-gpt-5.4" / "model_prompt_interaction_contrasts.csv",
    }
    comparison_rows = {label: read_csv(path) for label, path in comparisons.items()}
    fig, axes = plt.subplots(len(ALL_METRICS), 2, figsize=(12.8, 19.5), constrained_layout=True)
    for row_index, metric in enumerate(ALL_METRICS):
        bounds: list[float] = []
        for column, (label, rows) in enumerate(comparison_rows.items()):
            ax = axes[row_index, column]
            bounds.extend(_forest_cell(ax, rows, metric, "model_by_prompt_interaction",
                                       "interaction_ci_lower", "interaction_ci_upper",
                                       show_ylabels=column == 0))
            if row_index == 0:
                ax.set_title(label, weight="bold")
            if column == 0:
                ax.set_ylabel(METRIC_LABELS[metric], fontsize=8.3, weight="bold", labelpad=8)
            if row_index == len(ALL_METRICS) - 1:
                ax.set_xlabel("Model-by-prompt interaction estimate\n(95% bootstrap CI)")
        limits = _symmetric_limits(bounds)
        for column in range(2):
            axes[row_index, column].set_xlim(*limits)
    fig.suptitle("RQ2: Model-by-prompt interaction contrasts", fontsize=14, y=1.01)
    save_figure(fig, "figure_rq2_model_interactions")


def figure_rq3_v2() -> None:
    summary = read_csv(ROOT / "gpt-4.1-multilingual" / "metric_summary.csv")
    effects = read_csv(ROOT / "gpt-4.1-multilingual" / "prompt_effects.csv")
    interactions = read_csv(ROOT / "gpt-4.1-multilingual" / "language_prompt_interactions.csv")
    languages = ("en", "zh-CN", "es")
    target_languages = ("zh-CN", "es")
    language_offsets = {"en": -0.18, "zh-CN": 0.0, "es": 0.18}
    interaction_offsets = {"zh-CN": -0.11, "es": 0.11}
    fig, axes = plt.subplots(len(ALL_METRICS), 3, figsize=(16.8, 21), constrained_layout=True)
    for row_index, metric in enumerate(ALL_METRICS):
        task, conditions = METRIC_TASK[metric], CONDITIONS[METRIC_TASK[metric]]
        ax_a, ax_b, ax_c = axes[row_index]
        # A: all three languages are parallel experimental conditions.
        for y, language in enumerate(reversed(languages)):
            row = lookup(summary, prompt_language=language, task=task,
                         prompt_condition="baseline", metric=metric)
            ax_a.errorbar(f(row, "mean"), y, xerr=f(row, "sd"), fmt=LANGUAGE_MARKERS[language],
                          color=LANGUAGE_COLORS[language], capsize=2.5, markersize=4.6)
        ax_a.set_yticks(range(3))
        ax_a.set_yticklabels([LANGUAGE_LABELS[l] for l in reversed(languages)], fontsize=7.2)
        ax_a.set_ylabel(METRIC_LABELS[metric], fontsize=8.3, weight="bold", labelpad=8)
        ax_a.grid(axis="x", color="#e1e1e1", linewidth=0.55)
        # B: condition-minus-own-Neutral effects, preserving equal language status.
        b_bounds: list[float] = []
        for condition_index, condition in enumerate(conditions):
            base_y = len(conditions) - 1 - condition_index
            for language in languages:
                row = lookup(effects, prompt_language=language, task=task,
                             prompt_condition=condition, metric=metric)
                value, lo, hi = f(row, "raw_mean_difference"), f(row, "raw_difference_ci_lower"), f(row, "raw_difference_ci_upper")
                b_bounds.extend((lo, hi))
                ax_b.errorbar(value, base_y + language_offsets[language], xerr=[[value-lo], [hi-value]],
                              fmt=LANGUAGE_MARKERS[language], color=LANGUAGE_COLORS[language],
                              capsize=2, elinewidth=1.1, markersize=4)
        ax_b.axvline(0, color="#666666", linewidth=0.8, linestyle="--")
        ax_b.set_yticks(range(3)); ax_b.set_yticklabels([CONDITION_LABELS[c] for c in reversed(conditions)], fontsize=7.2)
        ax_b.set_xlim(*_symmetric_limits(b_bounds)); ax_b.grid(axis="x", color="#e1e1e1", linewidth=0.55)
        # C: the formal language-by-prompt interaction contrasts.
        c_bounds: list[float] = []
        for condition_index, condition in enumerate(conditions):
            base_y = len(conditions) - 1 - condition_index
            for language in target_languages:
                row = lookup(interactions, target_language=language, task=task,
                             prompt_condition=condition, metric=metric)
                value, lo, hi = f(row, "raw_interaction_contrast"), f(row, "raw_ci_lower"), f(row, "raw_ci_upper")
                c_bounds.extend((lo, hi))
                ax_c.errorbar(value, base_y + interaction_offsets[language], xerr=[[value-lo], [hi-value]],
                              fmt=LANGUAGE_MARKERS[language], color=LANGUAGE_COLORS[language],
                              capsize=2, elinewidth=1.1, markersize=4)
        ax_c.axvline(0, color="#666666", linewidth=0.8, linestyle="--")
        ax_c.set_yticks(range(3)); ax_c.set_yticklabels([CONDITION_LABELS[c] for c in reversed(conditions)], fontsize=7.2)
        ax_c.set_xlim(*_symmetric_limits(c_bounds)); ax_c.grid(axis="x", color="#e1e1e1", linewidth=0.55)
        if row_index == 0:
            ax_a.set_title("A  Neutral means ± run SD", weight="bold")
            ax_b.set_title("B  Within-language prompt effects", weight="bold")
            ax_c.set_title("C  Language-by-prompt interactions", weight="bold")
        if row_index == len(ALL_METRICS) - 1:
            ax_a.set_xlabel("Neutral mean (error bars: run SD)")
            ax_b.set_xlabel("Condition − same-language Neutral\n(95% bootstrap CI)")
            ax_c.set_xlabel("Target-language effect − English effect\n(95% bootstrap CI)")
    legend = [Line2D([0], [0], marker=LANGUAGE_MARKERS[l], color=LANGUAGE_COLORS[l],
                     linestyle="none", label=LANGUAGE_LABELS[l]) for l in languages]
    fig.legend(handles=legend, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.012))
    fig.suptitle("RQ3: Baseline and prompt-associated variation across languages", fontsize=14, y=1.025)
    save_figure(fig, "figure_rq3_parallel_languages")


def _rq4_heatmap(field: str, stem: str, title: str, cmap: str, colorbar_label: str) -> None:
    rows = read_csv(ROOT / "human_reference_results" / "model_human_distance_changes.csv")
    groups = (
        ("GPT-4.1", "en", "GPT-4.1 English"),
        ("GPT-4.1", "zh-CN", "GPT-4.1 Simplified Chinese"),
        ("GPT-4.1", "es", "GPT-4.1 Spanish"),
        ("GPT-5.4", "en", "GPT-5.4 English"),
        ("GPT-5.4 Mini", "en", "GPT-5.4 Mini English"),
    )
    max_abs = max(abs(f(row, field)) for row in rows)
    norm = TwoSlopeNorm(vmin=-max_abs, vcenter=0, vmax=max_abs)
    fig, axes = plt.subplots(1, 3, figsize=(18.5, 10.5), constrained_layout=True)
    images = []
    for column, task in enumerate(TASKS):
        conditions = CONDITIONS[task]
        keys = [(model, language, label, metric) for model, language, label in groups for metric in METRICS[task]]
        matrix = np.zeros((len(keys), len(conditions)))
        annotations: list[list[str]] = []
        for i, (model, language, _, metric) in enumerate(keys):
            annotation_row = []
            for j, condition in enumerate(conditions):
                row = lookup(rows, model=model, prompt_language=language, task=task,
                             prompt_condition=condition, metric=metric)
                value = f(row, field); matrix[i, j] = value; annotation_row.append(f"{value:.2f}")
            annotations.append(annotation_row)
        images.append(heatmap(axes[column], matrix, annotations,
                              xlabels=[CONDITION_SHORT[c] for c in conditions],
                              ylabels=[f"{label} · {METRIC_LABELS[metric]}" for _, _, label, metric in keys],
                              title=TASK_LABELS[task], norm=norm, cmap=cmap))
    fig.colorbar(images[0], ax=axes, shrink=0.72, label=colorbar_label)
    fig.suptitle(title, fontsize=14)
    save_figure(fig, stem)


def figure_rq4_v2() -> None:
    _rq4_heatmap("absolute_deviation_change_from_baseline",
                 "figure_rq4_absolute_deviation_heatmap",
                 "RQ4a: Prompt-associated changes in absolute human-reference deviation",
                 "PuOr_r", "Δ absolute deviation (− closer; + farther)")
    _rq4_heatmap("reference_coverage_change_from_baseline",
                 "figure_rq4_coverage_heatmap",
                 "RQ4b: Prompt-associated changes in human-reference coverage",
                 "PRGn", "Δ coverage (− less overlap; + greater overlap)")


OVERVIEW_CMAP = LinearSegmentedColormap.from_list(
    "academic_diverging", ("#5E81AC", "#F5F3EE", "#B76E79")
)


def _compact_rows() -> list[tuple[str, str]]:
    return [(metric, condition) for task in TASKS for metric in METRICS[task] for condition in CONDITIONS[task]]


def _compact_labels(rows: list[tuple[str, str]]) -> list[str]:
    return [f"{METRIC_LABELS[metric]} · {CONDITION_LABELS[condition]}" for metric, condition in rows]


def _matrix_overview(
    matrix: np.ndarray,
    annotations: list[list[str]],
    *,
    xlabels: list[str],
    ylabels: list[str],
    title: str,
    stem: str,
    colorbar_label: str,
    panel_boundaries: tuple[int, ...] = (),
    figsize: tuple[float, float] = (10.5, 12.5),
) -> None:
    max_abs = max(float(np.nanmax(np.abs(matrix))), 0.5)
    norm = TwoSlopeNorm(vmin=-max_abs, vcenter=0, vmax=max_abs)
    fig, ax = plt.subplots(figsize=figsize, constrained_layout=True)
    image = ax.imshow(matrix, cmap=OVERVIEW_CMAP, norm=norm, aspect="auto")
    ax.set_xticks(range(len(xlabels)), xlabels, fontsize=9, weight="bold")
    ax.set_yticks(range(len(ylabels)), ylabels, fontsize=7.3)
    ax.tick_params(top=True, labeltop=True, bottom=False, labelbottom=False, length=0)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            rgba = image.cmap(image.norm(matrix[i, j]))
            luminance = 0.2126 * rgba[0] + 0.7152 * rgba[1] + 0.0722 * rgba[2]
            ax.text(j, i, annotations[i][j], ha="center", va="center",
                    fontsize=7.2, color="#202020" if luminance > 0.55 else "white")
    ax.set_xticks(np.arange(-0.5, len(xlabels), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(ylabels), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=0.9)
    for boundary in panel_boundaries:
        ax.axhline(boundary - 0.5, color="#4A4A4A", linewidth=1.4)
    fig.colorbar(image, ax=ax, shrink=0.72, pad=0.025, label=colorbar_label)
    ax.set_title(title, fontsize=13.5, pad=16)
    save_figure(fig, stem)


def figure_rq1_overview() -> None:
    compact_rows = _compact_rows()
    models = list(MODEL_INPUTS)
    model_rows = {model: read_csv(path) for model, path in MODEL_INPUTS.items()}
    matrix = np.zeros((len(compact_rows), len(models)))
    annotations: list[list[str]] = []
    for i, (metric, condition) in enumerate(compact_rows):
        task = METRIC_TASK[metric]
        annotation_row: list[str] = []
        for j, model in enumerate(models):
            row = lookup(model_rows[model], task=task, prompt_condition=condition, metric=metric)
            matrix[i, j] = f(row, "signed_standardised_effect")
            annotation_row.append(f"{f(row, 'raw_mean_difference'):.2f}")
        annotations.append(annotation_row)
    _matrix_overview(matrix, annotations, xlabels=models, ylabels=_compact_labels(compact_rows),
                     title="RQ1: Prompt-associated behavioural changes",
                     stem="figure_rq1_prompt_effects_overview",
                     colorbar_label="Hedges' g (negative ← 0 → positive)",
                     panel_boundaries=(9, 15), figsize=(10.8, 14.2))


def figure_rq2_overview() -> None:
    compact_rows = _compact_rows()
    targets = ("GPT-4.1", "GPT-5.4 Mini")
    effects = {model: read_csv(path) for model, path in MODEL_INPUTS.items()}
    raw_paths = {
        "GPT-4.1": ROOT / "gpt-4.1-minus-gpt-5.4" / "model_prompt_interaction_contrasts.csv",
        "GPT-5.4 Mini": ROOT / "gpt-5.4-mini-minus-gpt-5.4" / "model_prompt_interaction_contrasts.csv",
    }
    raw_rows = {model: read_csv(path) for model, path in raw_paths.items()}
    matrix = np.zeros((len(compact_rows), 2))
    annotations: list[list[str]] = []
    for i, (metric, condition) in enumerate(compact_rows):
        task = METRIC_TASK[metric]
        reference = lookup(effects["GPT-5.4"], task=task, prompt_condition=condition, metric=metric)
        annotation_row: list[str] = []
        for j, target in enumerate(targets):
            target_row = lookup(effects[target], task=task, prompt_condition=condition, metric=metric)
            matrix[i, j] = f(target_row, "signed_standardised_effect") - f(reference, "signed_standardised_effect")
            raw = lookup(raw_rows[target], task=task, prompt_condition=condition, metric=metric)
            annotation_row.append(f"{f(raw, 'model_by_prompt_interaction'):.2f}")
        annotations.append(annotation_row)
    _matrix_overview(matrix, annotations,
                     xlabels=["GPT-4.1 − GPT-5.4", "GPT-5.4 Mini − GPT-5.4"],
                     ylabels=_compact_labels(compact_rows),
                     title="RQ2: Model-by-prompt interaction patterns",
                     stem="figure_rq2_model_interactions_overview",
                     colorbar_label="Difference in Hedges' g (descriptive)",
                     panel_boundaries=(9, 15), figsize=(10.8, 14.2))


def figure_rq3_overview() -> None:
    summary = read_csv(ROOT / "gpt-4.1-multilingual" / "metric_summary.csv")
    interactions = read_csv(ROOT / "gpt-4.1-multilingual" / "language_prompt_interactions.csv")
    languages = ("en", "zh-CN", "es")
    language_names = [LANGUAGE_LABELS[l] for l in languages]
    baseline = np.zeros((len(ALL_METRICS), 3))
    baseline_annotations: list[list[str]] = []
    for i, metric in enumerate(ALL_METRICS):
        task = METRIC_TASK[metric]
        metric_rows = [lookup(summary, prompt_language=language, task=task,
                              prompt_condition="baseline", metric=metric) for language in languages]
        means = np.array([f(row, "mean") for row in metric_rows])
        pooled_sd = math.sqrt(sum(f(row, "sd") ** 2 for row in metric_rows) / len(metric_rows))
        baseline[i, :] = (means - means.mean()) / pooled_sd if pooled_sd > 0 else 0.0
        baseline_annotations.append([f"{value:.2f}" for value in means])
    interaction_rows = _compact_rows()
    interaction = np.zeros((len(interaction_rows), 3))
    interaction_annotations: list[list[str]] = []
    for i, (metric, condition) in enumerate(interaction_rows):
        task = METRIC_TASK[metric]
        annotation_row = ["ref"]
        for j, language in enumerate(("zh-CN", "es"), start=1):
            row = lookup(interactions, target_language=language, task=task,
                         prompt_condition=condition, metric=metric)
            interaction[i, j] = f(row, "standardised_interaction_contrast")
            annotation_row.append(f"{f(row, 'raw_interaction_contrast'):.2f}")
        interaction_annotations.append(annotation_row)
    baseline_max = max(float(np.nanmax(np.abs(baseline))), 0.5)
    interaction_max = max(float(np.nanmax(np.abs(interaction))), 0.5)
    norms = (
        TwoSlopeNorm(vmin=-baseline_max, vcenter=0, vmax=baseline_max),
        TwoSlopeNorm(vmin=-interaction_max, vcenter=0, vmax=interaction_max),
    )
    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(15.8, 14.3),
                                     gridspec_kw={"width_ratios": (0.78, 1.5)}, constrained_layout=True)
    images = []
    for panel_index, (ax, matrix, annotations, ylabels, heading) in enumerate((
        (ax_a, baseline, baseline_annotations, [METRIC_LABELS[m] for m in ALL_METRICS],
         "A  Neutral baselines (languages centred within metric)"),
        (ax_b, interaction, interaction_annotations, _compact_labels(interaction_rows),
         "B  Language-by-prompt interactions (English reference)"),
    )):
        image = ax.imshow(matrix, cmap=OVERVIEW_CMAP, norm=norms[panel_index], aspect="auto")
        images.append(image)
        ax.set_xticks(range(3), language_names, fontsize=8.5, weight="bold")
        ax.set_yticks(range(len(ylabels)), ylabels, fontsize=7.1)
        ax.tick_params(top=True, labeltop=True, bottom=False, labelbottom=False, length=0)
        ax.set_title(heading, fontsize=10.5, pad=14, weight="bold")
        ax.set_xticks(np.arange(-0.5, 3, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, len(ylabels), 1), minor=True)
        ax.grid(which="minor", color="white", linewidth=0.9)
        for i in range(matrix.shape[0]):
            for j in range(3):
                rgba = image.cmap(image.norm(matrix[i, j])); lum = 0.2126*rgba[0]+0.7152*rgba[1]+0.0722*rgba[2]
                ax.text(j, i, annotations[i][j], ha="center", va="center", fontsize=7,
                        color="#202020" if lum > 0.55 else "white")
    for boundary in (3, 5): ax_a.axhline(boundary - 0.5, color="#4A4A4A", linewidth=1.4)
    for boundary in (9, 15): ax_b.axhline(boundary - 0.5, color="#4A4A4A", linewidth=1.4)
    fig.colorbar(images[0], ax=ax_a, shrink=0.62, pad=0.02,
                 label="Centred Neutral mean / pooled run SD")
    fig.colorbar(images[1], ax=ax_b, shrink=0.62, pad=0.02,
                 label="Standardised interaction contrast")
    fig.suptitle("RQ3: Baseline and prompt-associated cross-language variation", fontsize=14)
    save_figure(fig, "figure_rq3_language_overview")


def _draw_task_matrix(
    ax: plt.Axes,
    matrix: np.ndarray,
    annotations: list[list[str]],
    *,
    xlabels: list[str],
    ylabels: list[str],
    norm: TwoSlopeNorm,
    title: str,
    show_ylabels: bool = True,
) -> Any:
    image = ax.imshow(matrix, cmap=OVERVIEW_CMAP, norm=norm, aspect="auto")
    ax.set_xticks(range(len(xlabels)), xlabels, fontsize=10, weight="bold")
    ax.set_yticks(range(len(ylabels)), ylabels if show_ylabels else [], fontsize=9)
    ax.tick_params(top=True, labeltop=True, bottom=False, labelbottom=False, length=0, pad=6)
    ax.set_title(title, fontsize=13, weight="bold", pad=14)
    ax.set_xticks(np.arange(-0.5, len(xlabels), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(ylabels), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.1)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            rgba = image.cmap(image.norm(matrix[i, j]))
            luminance = 0.2126 * rgba[0] + 0.7152 * rgba[1] + 0.0722 * rgba[2]
            ax.text(j, i, annotations[i][j], ha="center", va="center", fontsize=9,
                    color="#202020" if luminance > 0.55 else "white")
    return image


def figure_rq1_overview() -> None:
    models = list(MODEL_INPUTS)
    model_rows = {model: read_csv(path) for model, path in MODEL_INPUTS.items()}
    task_payloads = []
    all_standardised: list[float] = []
    for task in TASKS:
        task_rows = [(metric, condition) for metric in METRICS[task] for condition in CONDITIONS[task]]
        matrix = np.zeros((len(task_rows), len(models)))
        annotations: list[list[str]] = []
        for i, (metric, condition) in enumerate(task_rows):
            annotation_row = []
            for j, model in enumerate(models):
                row = lookup(model_rows[model], task=task, prompt_condition=condition, metric=metric)
                matrix[i, j] = f(row, "signed_standardised_effect")
                all_standardised.append(matrix[i, j])
                annotation_row.append(f"{f(row, 'raw_mean_difference'):.2f}")
            annotations.append(annotation_row)
        ylabels = [f"{METRIC_LABELS[m]}\n{CONDITION_LABELS[c]}" for m, c in task_rows]
        task_payloads.append((matrix, annotations, ylabels))
    max_abs = max(max(abs(value) for value in all_standardised), 0.5)
    norm = TwoSlopeNorm(vmin=-max_abs, vcenter=0, vmax=max_abs)
    fig, axes = plt.subplots(1, 3, figsize=(20, 8.2), constrained_layout=True)
    images = []
    for ax, task, (matrix, annotations, ylabels) in zip(axes, TASKS, task_payloads):
        images.append(_draw_task_matrix(ax, matrix, annotations, xlabels=models, ylabels=ylabels,
                                        norm=norm, title=TASK_LABELS[task]))
    cbar = fig.colorbar(images[0], ax=axes, shrink=0.78, pad=0.02)
    cbar.set_label("Signed Hedges' g (negative ← 0 → positive)", fontsize=11)
    cbar.ax.tick_params(labelsize=10)
    fig.suptitle("RQ1: Prompt-associated behavioural changes", fontsize=17, y=1.035)
    save_figure(fig, "figure_rq1_prompt_effects_overview")


def figure_rq2_overview() -> None:
    targets = ("GPT-4.1", "GPT-5.4 Mini")
    effects = {model: read_csv(path) for model, path in MODEL_INPUTS.items()}
    raw_paths = {
        "GPT-4.1": ROOT / "gpt-4.1-minus-gpt-5.4" / "model_prompt_interaction_contrasts.csv",
        "GPT-5.4 Mini": ROOT / "gpt-5.4-mini-minus-gpt-5.4" / "model_prompt_interaction_contrasts.csv",
    }
    raw_rows = {model: read_csv(path) for model, path in raw_paths.items()}
    task_payloads = []
    all_standardised: list[float] = []
    for task in TASKS:
        task_rows = [(metric, condition) for metric in METRICS[task] for condition in CONDITIONS[task]]
        matrix = np.zeros((len(task_rows), 2))
        annotations: list[list[str]] = []
        for i, (metric, condition) in enumerate(task_rows):
            reference = lookup(effects["GPT-5.4"], task=task, prompt_condition=condition, metric=metric)
            annotation_row = []
            for j, target in enumerate(targets):
                target_row = lookup(effects[target], task=task, prompt_condition=condition, metric=metric)
                matrix[i, j] = f(target_row, "signed_standardised_effect") - f(reference, "signed_standardised_effect")
                all_standardised.append(matrix[i, j])
                raw = lookup(raw_rows[target], task=task, prompt_condition=condition, metric=metric)
                annotation_row.append(f"{f(raw, 'model_by_prompt_interaction'):.2f}")
            annotations.append(annotation_row)
        ylabels = [f"{METRIC_LABELS[m]}\n{CONDITION_LABELS[c]}" for m, c in task_rows]
        task_payloads.append((matrix, annotations, ylabels))
    max_abs = max(max(abs(value) for value in all_standardised), 0.5)
    norm = TwoSlopeNorm(vmin=-max_abs, vcenter=0, vmax=max_abs)
    fig, axes = plt.subplots(1, 3, figsize=(20, 8.2), constrained_layout=True)
    images = []
    xlabels = ["GPT-4.1\n− GPT-5.4", "GPT-5.4 Mini\n− GPT-5.4"]
    for ax, task, (matrix, annotations, ylabels) in zip(axes, TASKS, task_payloads):
        images.append(_draw_task_matrix(ax, matrix, annotations, xlabels=xlabels, ylabels=ylabels,
                                        norm=norm, title=TASK_LABELS[task]))
    cbar = fig.colorbar(images[0], ax=axes, shrink=0.78, pad=0.02)
    cbar.set_label("Difference in signed Hedges' g (descriptive)", fontsize=11)
    cbar.ax.tick_params(labelsize=10)
    fig.suptitle("RQ2: Model-by-prompt interaction patterns", fontsize=17, y=1.035)
    save_figure(fig, "figure_rq2_model_interactions_overview")


def figure_rq3_overview() -> None:
    summary = read_csv(ROOT / "gpt-4.1-multilingual" / "metric_summary.csv")
    interactions = read_csv(ROOT / "gpt-4.1-multilingual" / "language_prompt_interactions.csv")
    languages = ("en", "zh-CN", "es")
    language_names = [LANGUAGE_LABELS[language] for language in languages]
    baseline_payloads = []
    interaction_payloads = []
    baseline_values: list[float] = []
    interaction_values: list[float] = []
    for task in TASKS:
        baseline = np.zeros((len(METRICS[task]), 3))
        baseline_annotations: list[list[str]] = []
        for i, metric in enumerate(METRICS[task]):
            rows = [lookup(summary, prompt_language=language, task=task,
                           prompt_condition="baseline", metric=metric) for language in languages]
            means = np.array([f(row, "mean") for row in rows])
            pooled_sd = math.sqrt(sum(f(row, "sd") ** 2 for row in rows) / len(rows))
            baseline[i, :] = (means - means.mean()) / pooled_sd if pooled_sd > 0 else 0.0
            baseline_values.extend(baseline[i, :].tolist())
            baseline_annotations.append([f"{value:.2f}" for value in means])
        baseline_payloads.append((baseline, baseline_annotations, [METRIC_LABELS[m] for m in METRICS[task]]))

        task_rows = [(metric, condition) for metric in METRICS[task] for condition in CONDITIONS[task]]
        interaction = np.zeros((len(task_rows), 3))
        interaction_annotations: list[list[str]] = []
        for i, (metric, condition) in enumerate(task_rows):
            annotation_row = ["ref"]
            for j, language in enumerate(("zh-CN", "es"), start=1):
                row = lookup(interactions, target_language=language, task=task,
                             prompt_condition=condition, metric=metric)
                interaction[i, j] = f(row, "standardised_interaction_contrast")
                interaction_values.append(interaction[i, j])
                annotation_row.append(f"{f(row, 'raw_interaction_contrast'):.2f}")
            interaction_annotations.append(annotation_row)
        ylabels = [f"{METRIC_LABELS[m]}\n{CONDITION_LABELS[c]}" for m, c in task_rows]
        interaction_payloads.append((interaction, interaction_annotations, ylabels))
    baseline_max = max(max(abs(value) for value in baseline_values), 0.5)
    interaction_max = max(max(abs(value) for value in interaction_values), 0.5)
    baseline_norm = TwoSlopeNorm(vmin=-baseline_max, vcenter=0, vmax=baseline_max)
    interaction_norm = TwoSlopeNorm(vmin=-interaction_max, vcenter=0, vmax=interaction_max)
    fig, axes = plt.subplots(2, 3, figsize=(20, 13.2), constrained_layout=True,
                             gridspec_kw={"height_ratios": (0.62, 1.38)})
    baseline_images = []; interaction_images = []
    for column, task in enumerate(TASKS):
        b_matrix, b_annotations, b_labels = baseline_payloads[column]
        i_matrix, i_annotations, i_labels = interaction_payloads[column]
        baseline_images.append(_draw_task_matrix(axes[0, column], b_matrix, b_annotations,
                                                  xlabels=language_names, ylabels=b_labels,
                                                  norm=baseline_norm, title=TASK_LABELS[task]))
        interaction_images.append(_draw_task_matrix(axes[1, column], i_matrix, i_annotations,
                                                     xlabels=language_names, ylabels=i_labels,
                                                     norm=interaction_norm, title=TASK_LABELS[task]))
    axes[0, 0].text(-0.32, 1.18, "A  Neutral baselines", transform=axes[0, 0].transAxes,
                    fontsize=14, weight="bold", ha="left")
    axes[1, 0].text(-0.32, 1.10, "B  Language-by-prompt interactions", transform=axes[1, 0].transAxes,
                    fontsize=14, weight="bold", ha="left")
    cbar_a = fig.colorbar(baseline_images[0], ax=axes[0, :], shrink=0.72, pad=0.02)
    cbar_a.set_label("Centred Neutral mean / pooled run SD", fontsize=11); cbar_a.ax.tick_params(labelsize=10)
    cbar_b = fig.colorbar(interaction_images[0], ax=axes[1, :], shrink=0.72, pad=0.02)
    cbar_b.set_label("Standardised interaction contrast", fontsize=11); cbar_b.ax.tick_params(labelsize=10)
    fig.suptitle("RQ3: Baseline and prompt-associated cross-language variation", fontsize=17, y=1.025)
    save_figure(fig, "figure_rq3_language_overview")


MODEL_STYLE = {
    "GPT-4.1": ("#5E81AC", "o"),
    "GPT-5.4": ("#777777", "s"),
    "GPT-5.4 Mini": ("#B76E79", "^"),
}
LANGUAGE_STYLE = {
    "en": ("#5E81AC", "o"),
    "zh-CN": ("#777777", "s"),
    "es": ("#B76E79", "^"),
}


def figure_rq1_overview() -> None:
    model_rows = {model: read_csv(path) for model, path in MODEL_INPUTS.items()}
    offsets = {"GPT-4.1": -0.18, "GPT-5.4": 0.0, "GPT-5.4 Mini": 0.18}
    fig, axes = plt.subplots(1, 3, figsize=(20, 8.4), constrained_layout=True)
    for ax, task in zip(axes, TASKS):
        task_rows = [(metric, condition) for metric in METRICS[task] for condition in CONDITIONS[task]]
        for model, rows in model_rows.items():
            color, marker = MODEL_STYLE[model]
            for index, (metric, condition) in enumerate(task_rows):
                row = lookup(rows, task=task, prompt_condition=condition, metric=metric)
                value = f(row, "signed_standardised_effect")
                lo, hi = f(row, "standardised_effect_ci_lower"), f(row, "standardised_effect_ci_upper")
                y = len(task_rows) - 1 - index + offsets[model]
                ax.errorbar(value, y, xerr=[[value-lo], [hi-value]], fmt=marker,
                            color=color, ecolor=color, markersize=5.8,
                            elinewidth=1.35, capsize=2.4, zorder=3)
        ax.axvline(0, color="#555555", linewidth=1.0, linestyle="--", zorder=0)
        ax.set_yticks(range(len(task_rows)))
        ax.set_yticklabels([f"{METRIC_LABELS[m]}\n{CONDITION_LABELS[c]}"
                            for m, c in reversed(task_rows)], fontsize=9)
        ax.set_title(TASK_LABELS[task], fontsize=14, weight="bold", pad=12)
        ax.set_xlabel("Signed Hedges' g (95% bootstrap CI)", fontsize=11)
        ax.tick_params(axis="x", labelsize=10)
        ax.grid(axis="x", color="#dedbd5", linewidth=0.7)
    legend = [Line2D([0], [0], marker=MODEL_STYLE[m][1], color=MODEL_STYLE[m][0],
                     linestyle="none", markersize=7, label=m) for m in MODEL_INPUTS]
    fig.legend(handles=legend, loc="upper center", ncol=3, frameon=False,
               bbox_to_anchor=(0.5, 1.035), fontsize=11)
    fig.suptitle("RQ1: Within-model prompt effects", fontsize=17, y=1.075)
    save_figure(fig, "figure_rq1_prompt_effects_overview")


def figure_rq3_overview() -> None:
    baselines = read_csv(ROOT / "gpt-4.1-multilingual" / "language_centered_baselines.csv")
    interactions = read_csv(ROOT / "gpt-4.1-multilingual" / "language_centered_prompt_effects.csv")
    languages = ("en", "zh-CN", "es")
    offsets = {"en": -0.18, "zh-CN": 0.0, "es": 0.18}
    fig, axes = plt.subplots(2, 3, figsize=(20, 13.2), constrained_layout=True,
                             gridspec_kw={"height_ratios": (0.62, 1.38)})
    for column, task in enumerate(TASKS):
        ax_base, ax_interaction = axes[0, column], axes[1, column]
        metrics = METRICS[task]
        # Symmetric deviations of each Neutral mean from the three-language mean.
        for metric_index, metric in enumerate(metrics):
            base_y = len(metrics) - 1 - metric_index
            for language in languages:
                row = lookup(baselines, language=language, task=task, metric=metric)
                value = f(row, "standardised_centered_baseline_deviation")
                lo, hi = f(row, "standardised_ci_lower"), f(row, "standardised_ci_upper")
                color, marker = LANGUAGE_STYLE[language]
                ax_base.errorbar(value, base_y + offsets[language], xerr=[[value-lo], [hi-value]],
                                 fmt=marker, color=color, ecolor=color, markersize=7,
                                 elinewidth=1.25, capsize=2.2)
        ax_base.axvline(0, color="#555555", linewidth=1.0, linestyle="--")
        ax_base.set_yticks(range(len(metrics)))
        ax_base.set_yticklabels([METRIC_LABELS[m] for m in reversed(metrics)], fontsize=9.5)
        ax_base.set_xlabel("Neutral mean deviation from three-language mean\n(pooled-SD units; 95% bootstrap CI)", fontsize=11)
        ax_base.set_title(TASK_LABELS[task], fontsize=14, weight="bold", pad=12)
        ax_base.tick_params(axis="x", labelsize=10)
        ax_base.grid(axis="x", color="#dedbd5", linewidth=0.7)

        # Symmetric deviations of each within-language prompt effect from the three-language mean effect.
        task_rows = [(metric, condition) for metric in metrics for condition in CONDITIONS[task]]
        for language in languages:
            color, marker = LANGUAGE_STYLE[language]
            for index, (metric, condition) in enumerate(task_rows):
                row = lookup(interactions, language=language, task=task,
                             prompt_condition=condition, metric=metric)
                value = f(row, "standardised_centered_prompt_effect")
                lo, hi = f(row, "standardised_ci_lower"), f(row, "standardised_ci_upper")
                y = len(task_rows) - 1 - index + offsets[language]
                ax_interaction.errorbar(value, y, xerr=[[value-lo], [hi-value]], fmt=marker,
                                        color=color, ecolor=color, markersize=5.8,
                                        elinewidth=1.35, capsize=2.4)
        ax_interaction.axvline(0, color="#555555", linewidth=1.0, linestyle="--")
        ax_interaction.set_yticks(range(len(task_rows)))
        ax_interaction.set_yticklabels([f"{METRIC_LABELS[m]}\n{CONDITION_LABELS[c]}"
                                        for m, c in reversed(task_rows)], fontsize=9)
        ax_interaction.set_xlabel("Prompt-effect deviation from three-language mean\n(standardised; 95% bootstrap CI)", fontsize=11)
        ax_interaction.set_title(TASK_LABELS[task], fontsize=14, weight="bold", pad=12)
        ax_interaction.tick_params(axis="x", labelsize=10)
        ax_interaction.grid(axis="x", color="#dedbd5", linewidth=0.7)
    axes[0, 0].text(-0.32, 1.20, "A  Neutral baseline profiles", transform=axes[0, 0].transAxes,
                    fontsize=14, weight="bold", ha="left")
    axes[1, 0].text(-0.32, 1.11, "B  Centred prompt-effect profiles", transform=axes[1, 0].transAxes,
                    fontsize=14, weight="bold", ha="left")
    language_legend = [Line2D([0], [0], marker=LANGUAGE_STYLE[l][1], color=LANGUAGE_STYLE[l][0],
                              linestyle="none", markersize=7, label=LANGUAGE_LABELS[l]) for l in languages]
    fig.legend(handles=language_legend, loc="upper center", ncol=3, frameon=False,
               bbox_to_anchor=(0.5, 1.025), fontsize=11)
    fig.suptitle("RQ3: Joint comparison of English, Simplified Chinese, and Spanish", fontsize=17, y=1.065)
    save_figure(fig, "figure_rq3_language_overview")


CONDITION_MARKERS = {
    "detailed": "o",
    "role_human": "s",
    "uncertainty_emphasis": "^",
    "reward_loss_emphasis": "^",
    "risk_emphasis": "^",
}


def figure_rq1_overview() -> None:
    model_rows = {model: read_csv(path) for model, path in MODEL_INPUTS.items()}
    models = list(MODEL_INPUTS)
    fig, axes = plt.subplots(3, 1, figsize=(8.2, 11.5))
    for ax, task in zip(axes, TASKS):
        metrics = METRICS[task]
        combos = [(m, c) for c in CONDITIONS[task] for m in models]
        offsets = np.linspace(-0.30, 0.30, len(combos))
        for metric_index, metric in enumerate(metrics):
            y0 = len(metrics) - 1 - metric_index
            for offset, (model, condition) in zip(offsets, combos):
                row = lookup(model_rows[model], task=task, prompt_condition=condition, metric=metric)
                value = f(row, "signed_standardised_effect")
                lo, hi = f(row, "standardised_effect_ci_lower"), f(row, "standardised_effect_ci_upper")
                color, _ = MODEL_STYLE[model]
                ax.errorbar(value, y0 + offset, xerr=[[value - lo], [hi - value]],
                            fmt=CONDITION_MARKERS[condition], color=color, ecolor=color,
                            markersize=5.6, elinewidth=1.2, capsize=2.0)
        ax.axvline(0, color="#555555", linewidth=1.0, linestyle="--")
        ax.set_yticks(range(len(metrics)), [METRIC_LABELS[m] for m in reversed(metrics)])
        ax.set_ylim(-0.65, len(metrics) - 0.35)
        ax.set_title(TASK_LABELS[task], fontsize=14, weight="bold")
        ax.set_xlabel("Signed Hedges' g (95% bootstrap CI)", fontsize=11)
        ax.tick_params(labelsize=10)
        ax.grid(axis="x", color="#dedbd5", linewidth=0.7)
    model_legend = [Line2D([0], [0], marker="o", color=MODEL_STYLE[m][0], linestyle="none",
                           markersize=7, label=m) for m in models]
    condition_legend = [
        Line2D([0], [0], marker="o", color="#444444", linestyle="none", markersize=7,
               label="Instruction specificity"),
        Line2D([0], [0], marker="s", color="#444444", linestyle="none", markersize=7,
               label="Role framing"),
        Line2D([0], [0], marker="^", color="#444444", linestyle="none", markersize=7,
               label="Task-specific emphasis"),
    ]
    fig.subplots_adjust(left=0.28, right=0.98, top=0.92, bottom=0.10, hspace=0.48)
    fig.legend(handles=model_legend + condition_legend, loc="lower center", ncol=3,
               frameon=False, bbox_to_anchor=(0.5, 0.01), fontsize=9.5)
    fig.suptitle("RQ1: Within-model prompt effects", fontsize=16, y=0.985)
    save_figure(fig, "figure_rq1_prompt_effects_overview")


def figure_rq2_overview() -> None:
    targets = ("GPT-4.1", "GPT-5.4 Mini")
    effects = {model: read_csv(path) for model, path in MODEL_INPUTS.items()}
    raw_rows = {
        "GPT-4.1": read_csv(ROOT / "gpt-4.1-minus-gpt-5.4" / "model_prompt_interaction_contrasts.csv"),
        "GPT-5.4 Mini": read_csv(ROOT / "gpt-5.4-mini-minus-gpt-5.4" / "model_prompt_interaction_contrasts.csv"),
    }
    payloads = []
    values = []
    for task in TASKS:
        columns = [(target, condition) for target in targets for condition in CONDITIONS[task]]
        matrix = np.zeros((len(METRICS[task]), len(columns)))
        annotations = []
        for i, metric in enumerate(METRICS[task]):
            row_text = []
            for j, (target, condition) in enumerate(columns):
                ref = lookup(effects["GPT-5.4"], task=task, prompt_condition=condition, metric=metric)
                candidate = lookup(effects[target], task=task, prompt_condition=condition, metric=metric)
                matrix[i, j] = f(candidate, "signed_standardised_effect") - f(ref, "signed_standardised_effect")
                values.append(matrix[i, j])
                raw = lookup(raw_rows[target], task=task, prompt_condition=condition, metric=metric)
                row_text.append(f"{f(raw, 'model_by_prompt_interaction'):.2f}")
            annotations.append(row_text)
        labels = []
        for target, condition in columns:
            model = "4.1" if target == "GPT-4.1" else "Mini"
            cond = {"detailed": "Inst.", "role_human": "Role"}.get(condition, "Task")
            labels.append(f"{model}\n{cond}")
        payloads.append((matrix, annotations, labels))
    max_abs = max(max(abs(v) for v in values), 0.5)
    norm = TwoSlopeNorm(vmin=-max_abs, vcenter=0, vmax=max_abs)
    fig, axes = plt.subplots(3, 1, figsize=(8.2, 10.5), constrained_layout=True)
    images = []
    for ax, task, (matrix, annotations, labels) in zip(axes, TASKS, payloads):
        images.append(_draw_task_matrix(ax, matrix, annotations, xlabels=labels,
                                        ylabels=[METRIC_LABELS[m] for m in METRICS[task]],
                                        norm=norm, title=TASK_LABELS[task]))
    cbar = fig.colorbar(images[0], ax=axes, shrink=0.55, pad=0.02)
    cbar.set_label("Difference in signed Hedges' g", fontsize=11)
    fig.suptitle("RQ2: Candidate model minus GPT-5.4 prompt effects", fontsize=16, y=1.02)
    save_figure(fig, "figure_rq2_model_interactions_overview")


def figure_rq3_overview() -> None:
    baselines = read_csv(ROOT / "gpt-4.1-multilingual" / "language_centered_baselines.csv")
    interactions = read_csv(ROOT / "gpt-4.1-multilingual" / "language_centered_prompt_effects.csv")
    languages = ("en", "zh-CN", "es")
    fig, axes = plt.subplots(3, 2, figsize=(8.2, 11.8),
                             gridspec_kw={"width_ratios": (0.92, 1.08)})
    for column, task in enumerate(TASKS):
        metrics = METRICS[task]
        ax_base, ax_prompt = axes[column, 0], axes[column, 1]
        language_offsets = {"en": -0.18, "zh-CN": 0.0, "es": 0.18}
        for i, metric in enumerate(metrics):
            y0 = len(metrics) - 1 - i
            for language in languages:
                row = lookup(baselines, language=language, task=task, metric=metric)
                value = f(row, "standardised_centered_baseline_deviation")
                lo, hi = f(row, "standardised_ci_lower"), f(row, "standardised_ci_upper")
                color, marker = LANGUAGE_STYLE[language]
                ax_base.errorbar(value, y0 + language_offsets[language],
                                 xerr=[[value - lo], [hi - value]], fmt=marker,
                                 color=color, ecolor=color, markersize=6.5,
                                 elinewidth=1.2, capsize=2.0)
        prompt_combos = [(language, condition) for condition in CONDITIONS[task] for language in languages]
        prompt_offsets = np.linspace(-0.30, 0.30, len(prompt_combos))
        for i, metric in enumerate(metrics):
            y0 = len(metrics) - 1 - i
            for offset, (language, condition) in zip(prompt_offsets, prompt_combos):
                row = lookup(interactions, language=language, task=task,
                             prompt_condition=condition, metric=metric)
                value = f(row, "standardised_centered_prompt_effect")
                lo, hi = f(row, "standardised_ci_lower"), f(row, "standardised_ci_upper")
                color, _ = LANGUAGE_STYLE[language]
                ax_prompt.errorbar(value, y0 + offset, xerr=[[value - lo], [hi - value]],
                                   fmt=CONDITION_MARKERS[condition], color=color, ecolor=color,
                                   markersize=5.3, elinewidth=1.15, capsize=1.8)
        for ax in (ax_base, ax_prompt):
            ax.axvline(0, color="#555555", linewidth=1.0, linestyle="--")
            ax.set_yticks(range(len(metrics)), [METRIC_LABELS[m] for m in reversed(metrics)])
            ax.set_ylim(-0.65, len(metrics) - 0.35)
            ax.tick_params(labelsize=9.5)
            ax.grid(axis="x", color="#dedbd5", linewidth=0.7)
        ax_base.set_title(TASK_LABELS[task], fontsize=14, weight="bold")
        ax_base.set_xlabel("Centred Neutral baseline (pooled-SD units)", fontsize=10.5)
        ax_prompt.set_xlabel("Centred prompt effect (standardised)", fontsize=10.5)
    axes[0, 0].set_title("A  Neutral baselines", fontsize=13, weight="bold")
    axes[0, 1].set_title("B  Within-language prompt effects", fontsize=13, weight="bold")
    language_legend = [Line2D([0], [0], marker=LANGUAGE_STYLE[l][1], color=LANGUAGE_STYLE[l][0],
                              linestyle="none", markersize=7, label=LANGUAGE_LABELS[l]) for l in languages]
    prompt_legend = [
        Line2D([0], [0], marker="o", color="#444444", linestyle="none", markersize=7,
               label="Instruction specificity"),
        Line2D([0], [0], marker="s", color="#444444", linestyle="none", markersize=7,
               label="Role framing"),
        Line2D([0], [0], marker="^", color="#444444", linestyle="none", markersize=7,
               label="Task-specific emphasis"),
    ]
    fig.subplots_adjust(left=0.24, right=0.98, top=0.92, bottom=0.11,
                        hspace=0.48, wspace=0.72)
    fig.legend(handles=language_legend + prompt_legend, loc="lower center", ncol=3,
               frameon=False, bbox_to_anchor=(0.5, 0.01), fontsize=9.2)
    fig.suptitle("RQ3: Joint three-language comparison", fontsize=16, y=0.985)
    save_figure(fig, "figure_rq3_language_overview")


def figure_rq4_v2() -> None:
    rows = read_csv(ROOT / "human_reference_results" / "model_human_distance_changes.csv")
    groups = (
        ("GPT-4.1", "en", "4.1 EN"),
        ("GPT-4.1", "zh-CN", "4.1 ZH"),
        ("GPT-4.1", "es", "4.1 ES"),
        ("GPT-5.4", "en", "5.4 EN"),
        ("GPT-5.4 Mini", "en", "Mini EN"),
    )
    fields = (
        ("absolute_deviation_change_from_baseline", "A  Absolute mean deviation", "PuOr_r"),
        ("reference_coverage_change_from_baseline", "B  Empirical coverage", "PRGn"),
    )
    norms = {}
    for field, _, _ in fields:
        maximum = max(abs(f(row, field)) for row in rows)
        norms[field] = TwoSlopeNorm(vmin=-maximum, vcenter=0, vmax=maximum)
    fig, axes = plt.subplots(3, 2, figsize=(8.2, 11.0), constrained_layout=True)
    row_images = [None, None]
    for r_index, (field, row_title, cmap) in enumerate(fields):
        for column, task in enumerate(TASKS):
            columns = [(metric, condition) for metric in METRICS[task] for condition in CONDITIONS[task]]
            matrix = np.zeros((len(groups), len(columns)))
            annotations = []
            for i, (model, language, _) in enumerate(groups):
                text_row = []
                for j, (metric, condition) in enumerate(columns):
                    row = lookup(rows, model=model, prompt_language=language, task=task,
                                 prompt_condition=condition, metric=metric)
                    matrix[i, j] = f(row, field)
                    text_row.append(f"{matrix[i, j]:.2f}")
                annotations.append(text_row)
            short_metric = {
                "directed_exploration": "Info", "horizon_effect": "HΔ", "random_exploration_effect": "RE",
                "advantageous_choice_rate": "Adv", "post_loss_switching_rate": "Switch",
                "adjusted_average_pumps": "Pumps", "explosion_rate": "Expl", "post_explosion_adjustment": "Post",
            }
            short_condition = {"detailed": "I", "role_human": "R",
                               "uncertainty_emphasis": "T", "reward_loss_emphasis": "T", "risk_emphasis": "T"}
            xlabels = [f"{short_metric[m]}\n{short_condition[c]}" for m, c in columns]
            image = heatmap(axes[column, r_index], matrix, annotations, xlabels=xlabels,
                            ylabels=[label for _, _, label in groups], title=TASK_LABELS[task],
                            norm=norms[field], cmap=cmap)
            axes[column, r_index].tick_params(axis="x", labelsize=8.5)
            axes[column, r_index].tick_params(axis="y", labelsize=9.5)
            if row_images[r_index] is None:
                row_images[r_index] = image
        axes[0, r_index].set_title(row_title, fontsize=13, weight="bold")
    cbar_a = fig.colorbar(row_images[0], ax=axes[:, 0], shrink=0.55, pad=0.015)
    cbar_a.set_label("Δ absolute deviation (− closer)", fontsize=10.5)
    cbar_b = fig.colorbar(row_images[1], ax=axes[:, 1], shrink=0.55, pad=0.015)
    cbar_b.set_label("Δ coverage (+ greater overlap)", fontsize=10.5)
    fig.suptitle("RQ4: Prompt-associated changes in human-reference proximity", fontsize=16, y=1.02)
    save_figure(fig, "figure_rq4_human_reference_overview")


def write_latex() -> None:
    LATEX_DIR.mkdir(parents=True, exist_ok=True)
    tables = r"""% Required packages: booktabs, tabularx
\begin{table}[htbp]
\centering
\caption{Analysis sample and quality checks.}
\label{tab:results_quality}
\begin{tabularx}{\textwidth}{lrrrrX}
\toprule
Dataset & Valid runs & Cells & Runs/cell & Parser recoveries & Analysis status \\
\midrule
GPT-4.1 English & 240 & 12 & 20 & 0 & Complete; all reported bootstrap intervals used 2,000/2,000 valid replicates. \\
GPT-5.4 English & 240 & 12 & 20 & 0 & Complete; all reported bootstrap intervals used 2,000/2,000 valid replicates. \\
GPT-5.4 Mini English & 240 & 12 & 20 & 1 & Complete after the prespecified parser retry; all reported intervals passed the reporting gate. \\
GPT-4.1 Simplified Chinese & 240 & 12 & 20 & 0 & Complete; provenance and cell-completeness checks passed. \\
GPT-4.1 Spanish & 240 & 12 & 20 & 0 & Complete; provenance and cell-completeness checks passed. \\
\midrule
Unique total & 1,200 & 60 & 20 & 1 & The 240 English GPT-4.1 runs are shared across the model and language analyses and counted once. \\
\bottomrule
\end{tabularx}
\begin{flushleft}\footnotesize
Random-exploration point estimates and shrinkage-sensitivity fits converged for the human reference and every formal LLM cell. Parser recovery counts successful response-format retries, not API-level network retries.
\end{flushleft}
\end{table}

\begin{table}[htbp]
\centering
\caption{Summary of answers to the research questions.}
\label{tab:rq_summary}
\begin{tabularx}{\textwidth}{p{1.0cm}p{3.2cm}Xp{3.8cm}}
\toprule
RQ & Primary display & Main empirical pattern & Interpretation boundary \\
\midrule
RQ1 & Figure~\ref{fig:rq1} & Prompt effects varied across models, tasks, metrics, and formulations; no condition produced a uniform behavioural shift. & Direction does not automatically indicate improved performance. \\
RQ2 & Figure~\ref{fig:rq2} & Model differences were concentrated in specific task--metric--condition cells, particularly BART and selected Horizon/IGT outcomes. & Interactions compare prompt responses, not general model capability. \\
RQ3 & Figure~\ref{fig:rq3} & Both Neutral-baseline locations and within-language prompt effects varied across English, Simplified Chinese, and Spanish. & Results are language-associated, not pure causal effects of language. \\
RQ4 & Figures~\ref{fig:rq4a}--\ref{fig:rq4b} & Prompt formulations sometimes reduced and sometimes increased human-SD-scaled deviation; mean proximity and empirical coverage could diverge. & Human proximity is descriptive and does not establish shared mechanisms. \\
\bottomrule
\end{tabularx}
\end{table}
"""
    (LATEX_DIR / "results_tables.tex").write_text(tables, encoding="utf-8")

    figures = r"""% Required packages: graphicx, rotating
% Adjust the path prefix if this file is copied outside the project root.
\begin{sidewaysfigure}[p]
\centering
\includegraphics[width=\textheight]{outputs/figures/final_results_v01/figure_rq1_prompt_effects_overview.pdf}
\caption{Task-grouped forest plots of within-model prompt effects relative to Neutral (RQ1). Horizon, IGT, and BART are arranged as three horizontal panels. Points are signed Hedges' $g$ estimates and horizontal lines are percentile-bootstrap 95\% confidence intervals; colour and shape identify model. Raw effects, raw confidence intervals, and PSI are reported in the supplementary tables.}
\label{fig:rq1}
\end{sidewaysfigure}

\begin{sidewaysfigure}[p]
\centering
\includegraphics[width=\textheight]{outputs/figures/final_results_v01/figure_rq2_model_interactions_overview.pdf}
\caption{Task-grouped overview of model-by-prompt interaction contrasts (RQ2). Horizon, IGT, and BART are arranged as three horizontal panels. Cell text is the raw interaction $(\bar{Y}_{\mathrm{target},p}-\bar{Y}_{\mathrm{target},N})-(\bar{Y}_{\mathrm{GPT\text{-}5.4},p}-\bar{Y}_{\mathrm{GPT\text{-}5.4,N})$. Colour is the descriptive difference between the two models' signed Hedges' $g$ values. Raw percentile-bootstrap 95\% confidence intervals are reported in the supplementary table; the complete metric-specific forest display is retained in the appendix package.}
\label{fig:rq2}
\end{sidewaysfigure}

\begin{sidewaysfigure}[p]
\centering
\includegraphics[width=\textheight]{outputs/figures/final_results_v01/figure_rq3_language_overview.pdf}
\caption{Task-grouped forest plots for the joint GPT-4.1 three-language comparison (RQ3). Columns distinguish Horizon, IGT, and BART. The upper row plots each language's Neutral mean deviation from the three-language mean, scaled by the pooled within-language run SD. The lower row plots each language's Hedges' $g$ minus the corresponding three-language mean Hedges' $g$. Both rows include percentile-bootstrap 95\% confidence intervals; the three language-specific deviations sum to zero within each comparison, so no language is designated as a reference. Raw centred estimates and intervals are reported in the supplementary tables.}
\label{fig:rq3}
\end{sidewaysfigure}

\begin{sidewaysfigure}[p]
\centering
\includegraphics[width=\textheight]{outputs/figures/final_results_v01/figure_rq4_absolute_deviation_heatmap.pdf}
\caption{Prompt-associated changes in absolute human-SD-scaled mean deviation (RQ4a). Cells contain descriptive point-estimated manipulated-minus-Neutral changes: negative values indicate movement closer to the human mean and positive values movement farther away. No inferential intervals were constructed for these human-reference proximity measures.}
\label{fig:rq4a}
\end{sidewaysfigure}

\begin{sidewaysfigure}[p]
\centering
\includegraphics[width=\textheight]{outputs/figures/final_results_v01/figure_rq4_coverage_heatmap.pdf}
\caption{Prompt-associated changes in empirical human-reference coverage (RQ4b). Cells contain descriptive point-estimated manipulated-minus-Neutral changes: positive values indicate greater overlap with the empirical human range and negative values less overlap. Coverage is quantised by the valid-run denominator (in increments of 0.05 when all 20 runs are non-missing). No inferential intervals were constructed for these human-reference proximity measures; neither RQ4 display is an equivalence test or evidence of a shared mechanism.}
\label{fig:rq4b}
\end{sidewaysfigure}
"""
    (LATEX_DIR / "results_figures.tex").write_text(figures, encoding="utf-8")
    (LATEX_DIR / "results_visual_package.tex").write_text(
        "% Required in the preamble: \\usepackage{booktabs,tabularx,graphicx,rotating}\n"
        "\\input{docs/results_visuals/results_tables.tex}\n"
        "\\input{docs/results_visuals/results_figures.tex}\n",
        encoding="utf-8",
    )


def main() -> None:
    set_style()
    figure_rq1_overview()
    figure_rq2_overview()
    figure_rq3_overview()
    figure_rq4_v2()
    write_latex()
    manifest = {
        "figure_directory": str(FIGURE_DIR),
        "latex_directory": str(LATEX_DIR),
        "figures": sorted(path.name for path in FIGURE_DIR.glob("*")),
        "latex_files": sorted(path.name for path in LATEX_DIR.glob("*.tex")),
        "source": str(ROOT / "analysis_manifest.json"),
    }
    (LATEX_DIR / "visual_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
