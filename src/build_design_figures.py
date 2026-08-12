"""Build concise, high-resolution dissertation design figures."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


OUT = Path(__file__).resolve().parents[1] / "outputs" / "figures" / "design"
NAVY = "#304A60"
BLUE = "#597A91"
TEAL = "#5F8F88"
ORANGE = "#B78355"
INK = "#25313A"
MUTED = "#64727D"
PALE = "#F2F5F6"
WHITE = "#FFFFFF"


def box(ax, xy, width, height, face, edge=NAVY, radius=0.025, lw=1.4):
    patch = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle=f"round,pad=0.012,rounding_size={radius}",
        facecolor=face,
        edgecolor=edge,
        linewidth=lw,
    )
    ax.add_patch(patch)
    return patch


def arrow(ax, start, end, color=MUTED, lw=1.8, style="-|>"):
    ax.annotate(
        "",
        xy=end,
        xytext=start,
        arrowprops=dict(arrowstyle=style, color=color, lw=lw, shrinkA=3, shrinkB=3),
    )


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / name, dpi=600, bbox_inches="tight", facecolor=WHITE)
    plt.close(fig)


def study_design_scope():
    fig, ax = plt.subplots(figsize=(12.0, 5.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(0.5, 0.94, "COMMON PROTOCOL", ha="center", va="center",
            fontsize=18, fontweight="bold", color=INK)
    labels = ["3 tasks", "4 prompt conditions", "20 runs per cell"]
    for x, label in zip([0.25, 0.50, 0.75], labels):
        box(ax, (x - 0.105, 0.80), 0.21, 0.085, PALE, edge=BLUE, radius=0.018)
        ax.text(x, 0.842, label, ha="center", va="center", fontsize=14,
                fontweight="semibold", color=INK)

    box(ax, (0.08, 0.43), 0.37, 0.25, "#EAF0F4", edge=BLUE)
    ax.text(0.265, 0.625, "CROSS-MODEL", ha="center", va="center",
            fontsize=17, fontweight="bold", color=NAVY)
    ax.text(0.265, 0.555, "English", ha="center", va="center",
            fontsize=14, color=INK)
    ax.text(0.265, 0.495, "GPT-4.1  ·  GPT-5.4  ·  Mini", ha="center", va="center",
            fontsize=13, color=MUTED)
    ax.text(0.265, 0.445, "720 runs", ha="center", va="center",
            fontsize=16, fontweight="bold", color=NAVY)

    box(ax, (0.55, 0.43), 0.37, 0.25, "#E9F2F0", edge=TEAL)
    ax.text(0.735, 0.625, "CROSS-LANGUAGE", ha="center", va="center",
            fontsize=17, fontweight="bold", color="#416F69")
    ax.text(0.735, 0.555, "GPT-4.1", ha="center", va="center",
            fontsize=14, color=INK)
    ax.text(0.735, 0.495, "English  ·  Chinese  ·  Spanish", ha="center", va="center",
            fontsize=13, color=MUTED)
    ax.text(0.735, 0.445, "720 runs", ha="center", va="center",
            fontsize=16, fontweight="bold", color="#416F69")

    arrow(ax, (0.5, 0.79), (0.265, 0.69))
    arrow(ax, (0.5, 0.79), (0.735, 0.69))

    box(ax, (0.32, 0.275), 0.36, 0.075, "#F6EEE7", edge=ORANGE, radius=0.016)
    ax.text(0.5, 0.312, "Shared English GPT-4.1: 240 runs",
            ha="center", va="center", fontsize=13, color=INK, fontweight="semibold")
    arrow(ax, (0.265, 0.42), (0.42, 0.35), color=ORANGE, lw=1.4)
    arrow(ax, (0.735, 0.42), (0.58, 0.35), color=ORANGE, lw=1.4)

    box(ax, (0.30, 0.075), 0.40, 0.115, NAVY, edge=NAVY, radius=0.02)
    ax.text(0.5, 0.132, "1,200 UNIQUE VALID RUNS", ha="center", va="center",
            fontsize=19, fontweight="bold", color=WHITE)
    arrow(ax, (0.5, 0.27), (0.5, 0.195), color=NAVY)

    save(fig, "study_design_scope.png")


def experimental_workflow():
    fig, ax = plt.subplots(figsize=(12.0, 4.5))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    steps = [
        ("1", "CELL", "Model · language\nprompt condition"),
        ("2", "TASK", "Horizon · IGT\nBART"),
        ("3", "PROMPT", "Task × condition\nfrozen template"),
        ("4", "RESPONSE", "Observation →\nmodel action"),
        ("5", "PARSE", "Validate action\nupdate state"),
        ("6", "COMPLETE", "Validate run →\nderive metrics"),
    ]
    xs = [0.09, 0.254, 0.418, 0.582, 0.746, 0.91]
    faces = ["#EAF0F4", "#EAF0F4", "#EDF3F5", "#EDF3F5", "#E9F2F0", "#E9F2F0"]
    edges = [BLUE, BLUE, BLUE, BLUE, TEAL, TEAL]

    for i, ((number, heading, detail), x, face, edge) in enumerate(zip(steps, xs, faces, edges)):
        box(ax, (x - 0.0675, 0.43), 0.135, 0.31, face, edge=edge, radius=0.022)
        ax.text(x, 0.685, number, ha="center", va="center", fontsize=14,
                fontweight="bold", color=WHITE,
                bbox=dict(boxstyle="circle,pad=0.35", facecolor=edge, edgecolor=edge))
        ax.text(x, 0.595, heading, ha="center", va="center", fontsize=12.5,
                fontweight="bold", color=INK)
        ax.text(x, 0.495, detail, ha="center", va="center", fontsize=10.8,
                color=MUTED, linespacing=1.25)
        if i < len(xs) - 1:
            arrow(ax, (x + 0.069, 0.585), (xs[i + 1] - 0.069, 0.585), color=MUTED)

    box(ax, (0.585, 0.16), 0.22, 0.095, "#F6EEE7", edge=ORANGE, radius=0.016)
    ax.text(0.695, 0.208, "Technical failure → log and replace",
            ha="center", va="center", fontsize=12, color=INK)
    ax.annotate("", xy=(0.695, 0.425), xytext=(0.695, 0.26),
                arrowprops=dict(arrowstyle="<->", color=ORANGE, lw=1.5))

    ax.text(0.5, 0.88, "FROM FROZEN MATERIALS TO FORMAL ANALYSIS",
            ha="center", va="center", fontsize=18, fontweight="bold", color=INK)
    ax.text(0.5, 0.055, "Inclusion follows prespecified technical criteria, not behavioural outcomes.",
            ha="center", va="center", fontsize=12.5, color=MUTED, style="italic")

    save(fig, "experimental_workflow.png")


def experimental_workflow_compact():
    """Draw a readable two-row overview of one experimental run."""
    fig, ax = plt.subplots(figsize=(10.5, 5.4))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    steps = [
        ("1", "IDENTIFY CELL", "Model, language,\nprompt condition"),
        ("2", "SELECT TASK", "Horizon, IGT,\nor BART"),
        ("3", "LOAD PROMPT", "Frozen task-condition\ntemplate"),
        ("4", "RESPOND", "Observation to\nmodel action"),
        ("5", "PARSE & UPDATE", "Validate action;\nupdate task state"),
        ("6", "COMPLETE", "Validate run;\nderive metrics"),
    ]
    positions = [(0.18, 0.61), (0.50, 0.61), (0.82, 0.61),
                 (0.82, 0.27), (0.50, 0.27), (0.18, 0.27)]
    faces = ["#EAF0F4", "#EAF0F4", "#EDF3F5", "#EDF3F5", "#E9F2F0", "#E9F2F0"]
    edges = [BLUE, BLUE, BLUE, BLUE, TEAL, TEAL]
    for (number, heading, detail), (x, y), face, edge in zip(steps, positions, faces, edges):
        box(ax, (x - 0.125, y - 0.105), 0.25, 0.21, face, edge=edge, radius=0.022)
        ax.text(x - 0.098, y + 0.083, number, ha="center", va="center", fontsize=12,
                fontweight="bold", color=WHITE,
                bbox=dict(boxstyle="circle,pad=0.28", facecolor=edge, edgecolor=edge))
        ax.text(x, y + 0.025, heading, ha="center", va="center", fontsize=12.2,
                fontweight="bold", color=INK)
        ax.text(x, y - 0.052, detail, ha="center", va="center", fontsize=10.7,
                color=MUTED, linespacing=1.25)
    arrow(ax, (0.31, 0.61), (0.37, 0.61), color=MUTED)
    arrow(ax, (0.63, 0.61), (0.69, 0.61), color=MUTED)
    arrow(ax, (0.82, 0.50), (0.82, 0.38), color=MUTED)
    arrow(ax, (0.69, 0.27), (0.63, 0.27), color=MUTED)
    arrow(ax, (0.37, 0.27), (0.31, 0.27), color=MUTED)
    ax.annotate("next decision", xy=(0.82, 0.38), xytext=(0.62, 0.10),
                ha="center", va="center", fontsize=10.3, color=MUTED,
                arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.2,
                                connectionstyle="arc3,rad=-0.30"))
    ax.text(0.5, 0.91, "EXPERIMENTAL RUN WORKFLOW", ha="center", va="center",
            fontsize=18, fontweight="bold", color=INK)
    ax.text(0.22, 0.09, "Parse failure: retry once; otherwise log and replace.",
            ha="center", va="center", fontsize=9.8, color=ORANGE)
    save(fig, "experimental_workflow.png")


def experimental_workflow_v2():
    fig, ax = plt.subplots(figsize=(12.0, 4.5))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    steps = [
        ("1", "IDENTIFY CELL", "Model · language\nprompt condition"),
        ("2", "SELECT TASK", "Horizon · IGT\nBART"),
        ("3", "LOAD PROMPT", "Frozen task–condition\ntemplate"),
        ("4", "RESPOND", "Observation →\nmodel action"),
        ("5", "PARSE & UPDATE", "Task-specific parser\nnext state"),
        ("6", "COMPLETE", "Validate run →\nderive metrics"),
    ]
    xs = [0.09, 0.254, 0.418, 0.582, 0.746, 0.91]
    faces = ["#EAF0F4", "#EAF0F4", "#EDF3F5", "#EDF3F5", "#E9F2F0", "#E9F2F0"]
    edges = [BLUE, BLUE, BLUE, BLUE, TEAL, TEAL]
    for i, ((number, heading, detail), x, face, edge) in enumerate(zip(steps, xs, faces, edges)):
        box(ax, (x - 0.0675, 0.43), 0.135, 0.31, face, edge=edge, radius=0.022)
        ax.text(x, 0.685, number, ha="center", va="center", fontsize=13,
                fontweight="bold", color=WHITE,
                bbox=dict(boxstyle="circle,pad=0.33", facecolor=edge, edgecolor=edge))
        ax.text(x, 0.595, heading, ha="center", va="center", fontsize=12.5,
                fontweight="bold", color=INK)
        ax.text(x, 0.495, detail, ha="center", va="center", fontsize=10.8,
                color=MUTED, linespacing=1.25)
        if i < len(xs) - 1:
            arrow(ax, (x + 0.069, 0.585), (xs[i + 1] - 0.069, 0.585), color=MUTED)
    box(ax, (0.615, 0.15), 0.262, 0.095, "#F6EEE7", edge=ORANGE, radius=0.016)
    ax.text(0.746, 0.198, "Parse failure → retry once; then log/replace",
            ha="center", va="center", fontsize=10.8, color=INK)
    ax.annotate("", xy=(0.746, 0.425), xytext=(0.746, 0.25),
                arrowprops=dict(arrowstyle="<->", color=ORANGE, lw=1.5))
    ax.annotate("next decision", xy=(0.582, 0.42), xytext=(0.70, 0.31),
                ha="center", va="center", fontsize=10.3, color=MUTED,
                arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.2,
                                connectionstyle="arc3,rad=-0.20"))
    ax.text(0.5, 0.88, "EXPERIMENTAL RUN WORKFLOW", ha="center", va="center",
            fontsize=18, fontweight="bold", color=INK)
    ax.text(0.5, 0.055, "Inclusion follows prespecified technical criteria, not behavioural outcomes.",
            ha="center", va="center", fontsize=12.2, color=MUTED, style="italic")
    save(fig, "experimental_workflow.png")


if __name__ == "__main__":
    study_design_scope()
    experimental_workflow_compact()
