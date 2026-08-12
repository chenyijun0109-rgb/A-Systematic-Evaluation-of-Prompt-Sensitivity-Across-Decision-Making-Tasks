"""Render the two study-design diagrams used by final.tex as vector PDFs."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "figures" / "design"


def box(ax, xy, wh, text, *, face="#F3F5F7", edge="#46515C", size=10):
    x, y = xy
    w, h = wh
    patch = FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.018",
        linewidth=1.2, facecolor=face, edgecolor=edge,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size)
    return patch


def arrow(ax, start, end, *, dashed=False):
    ax.annotate("", xy=end, xytext=start,
                arrowprops={"arrowstyle": "-|>", "lw": 1.2, "color": "#65717C",
                            "linestyle": "--" if dashed else "-"})


def study_design():
    fig, ax = plt.subplots(figsize=(10.5, 7.0))
    ax.set(xlim=(0, 1), ylim=(0, 1)); ax.axis("off")
    box(ax, (0.12, 0.78), (0.76, 0.15),
        "COMMON DESIGN\n3 tasks × 4 prompt conditions × 20 valid runs per cell\n"
        "Horizon | IGT | BART\nNeutral + Instruction specificity + Role framing + Construct emphasis",
        size=11)
    box(ax, (0.06, 0.47), (0.40, 0.20),
        "ENGLISH: 3 MODELS\nGPT-4.1 | GPT-5.4 | GPT-5.4 Mini\n\n720 valid task runs",
        face="#E8F0F8", edge="#3B6C96", size=11)
    box(ax, (0.54, 0.47), (0.40, 0.20),
        "GPT-4.1: 3 LANGUAGES\nEnglish | Simplified Chinese | Spanish\n\n720 valid task runs",
        face="#E8F5F2", edge="#397B70", size=11)
    box(ax, (0.25, 0.23), (0.50, 0.13),
        "SHARED SAMPLE: ENGLISH GPT-4.1\n240 runs used in both comparisons; counted once",
        face="#FFF2DE", edge="#B67825", size=11)
    box(ax, (0.27, 0.05), (0.46, 0.10),
        "DEDUPLICATED FORMAL DATASET\n1,200 UNIQUE RUNS",
        face="#34404B", edge="#34404B", size=12)
    ax.text(0.5, 0.085, "DEDUPLICATED FORMAL DATASET\n1,200 UNIQUE RUNS",
            color="white", ha="center", va="center", fontsize=12, fontweight="bold")
    arrow(ax, (0.5, 0.78), (0.26, 0.67)); arrow(ax, (0.5, 0.78), (0.74, 0.67))
    arrow(ax, (0.26, 0.47), (0.39, 0.36), dashed=True)
    arrow(ax, (0.74, 0.47), (0.61, 0.36), dashed=True)
    arrow(ax, (0.5, 0.23), (0.5, 0.15))
    fig.savefig(OUT / "study_design_scope.pdf", bbox_inches="tight")
    plt.close(fig)


def workflow():
    fig, ax = plt.subplots(figsize=(9.0, 10.5))
    ax.set(xlim=(0, 1), ylim=(0, 1)); ax.axis("off")
    ys = [0.86, 0.71, 0.52, 0.32, 0.16, 0.02]
    texts = [
        "1. FREEZE THE EXPERIMENTAL SPECIFICATION\nPrompt version and hash | model and generation settings | task implementation",
        "2. DEFINE ONE LOGICAL RUN\nModel × language × task × prompt condition × nominal seed\nIndependent run ID and context",
        "3. REPEATED TASK INTERACTION\nObservation → frozen prompt → API response → strict parser → state update\nRetry once after a parse failure without advancing task state",
        "TECHNICAL VALIDATION\nComplete task record and provenance checks",
        "4. CONSTRUCT TASK-SPECIFIC RUN-LEVEL METRICS\nTrials, choices, games, and balloons remain nested within the run",
        "5. CELL SUMMARIES AND PLANNED COMPARISONS\nPrompt effects | model/language contrasts | human-reference summaries",
    ]
    heights = [0.10, 0.11, 0.13, 0.10, 0.10, 0.10]
    colours = ["#F3F5F7", "#F3F5F7", "#E8F0F8", "#FFF2DE", "#E8F0F8", "#34404B"]
    edges = ["#46515C", "#46515C", "#3B6C96", "#B67825", "#3B6C96", "#34404B"]
    for i, (y, text, h) in enumerate(zip(ys, texts, heights)):
        box(ax, (0.13, y), (0.74, h), text, face=colours[i], edge=edges[i], size=10)
        if i == 5:
            ax.text(0.5, y + h / 2, text, color="white", ha="center", va="center", fontsize=10, fontweight="bold")
        if i:
            arrow(ax, (0.5, ys[i - 1]), (0.5, y + h))
    ax.text(0.91, 0.37, "Fail: exclude and retain audit record;\nreplace under the same technical rules",
            ha="center", va="center", fontsize=8.5, color="#A34A40")
    arrow(ax, (0.87, 0.37), (0.79, 0.37), dashed=True)
    fig.savefig(OUT / "experimental_workflow.pdf", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    study_design()
    workflow()
