from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np


HUMAN_METRICS_DIR = Path("outputs/processed/human_metrics")
OUTPUT_DIR = Path("outputs/processed/final_analysis_v03/human_reference_results")
SEED = 20260615
BOOTSTRAP_REPLICATES = 2000

PRIMARY_METRICS = {
    "horizon": ("directed_exploration", "horizon_effect"),
    "igt": ("advantageous_choice_rate", "post_loss_switching_rate"),
    "bart": ("adjusted_average_pumps", "explosion_rate", "post_explosion_adjustment"),
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def parse_values(rows: list[dict[str, str]], metric: str) -> np.ndarray:
    values = []
    for row in rows:
        raw = row.get(metric)
        if raw is None or raw == "":
            continue
        values.append(float(raw))
    return np.asarray(values, dtype=float)


def bootstrap_ci(values: np.ndarray, statistic, seed: int, replicates: int) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    estimates = []
    for _ in range(replicates):
        sample = rng.choice(values, size=values.size, replace=True)
        estimates.append(float(statistic(sample)))
    return float(np.percentile(estimates, 2.5)), float(np.percentile(estimates, 97.5))


def main() -> None:
    output_rows: list[dict[str, Any]] = []
    for task, metrics in PRIMARY_METRICS.items():
        rows = read_csv(HUMAN_METRICS_DIR / f"{task}_human_metrics.csv")
        for metric in metrics:
            values = parse_values(rows, metric)
            if values.size == 0:
                continue
            mean = float(values.mean())
            sd = float(values.std(ddof=1))
            mean_lo, mean_hi = bootstrap_ci(values, np.mean, SEED, BOOTSTRAP_REPLICATES)
            sd_lo, sd_hi = bootstrap_ci(
                values, lambda x: float(np.std(x, ddof=1)), SEED, BOOTSTRAP_REPLICATES
            )
            empirical_lo, empirical_hi = (
                float(np.percentile(values, 2.5)),
                float(np.percentile(values, 97.5)),
            )
            output_rows.append(
                {
                    "task": task,
                    "metric": metric,
                    "human_n": int(values.size),
                    "human_mean": round(mean, 10),
                    "human_mean_ci_lower": round(mean_lo, 10),
                    "human_mean_ci_upper": round(mean_hi, 10),
                    "human_sd": round(sd, 10),
                    "human_sd_ci_lower": round(sd_lo, 10),
                    "human_sd_ci_upper": round(sd_hi, 10),
                    "empirical_lower": round(empirical_lo, 10),
                    "empirical_upper": round(empirical_hi, 10),
                }
            )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(OUTPUT_DIR / "human_reference_bootstrap.csv", output_rows)
    summary = {
        "analysis": "human_reference_bootstrap_uncertainty",
        "seed": SEED,
        "bootstrap_replicates": BOOTSTRAP_REPLICATES,
        "metrics": len(output_rows),
        "interpretation": (
            "Percentile bootstrap intervals describe sampling uncertainty in the "
            "participant-level human reference summaries; they are descriptive, not "
            "posterior probability, significance tests, or normative targets."
        ),
    }
    (OUTPUT_DIR / "human_reference_bootstrap_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
