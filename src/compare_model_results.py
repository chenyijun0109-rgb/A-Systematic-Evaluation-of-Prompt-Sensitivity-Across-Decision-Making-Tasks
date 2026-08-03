from __future__ import annotations

import argparse
import csv
import json
import math
import random
import statistics
from pathlib import Path
from typing import Any

from src.compute_prompt_sensitivity import (
    _horizon_observations_by_seed,
    _refit_horizon_run_values,
    percentile,
    stable_bootstrap_seed,
)
from src.prompt_loader import load_config


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


def hedges_g(
    mean_a: float,
    sd_a: float,
    n_a: int,
    mean_b: float,
    sd_b: float,
    n_b: int,
) -> float | None:
    degrees = n_a + n_b - 2
    if degrees <= 0:
        return None
    pooled_variance = (
        (n_a - 1) * sd_a**2 + (n_b - 1) * sd_b**2
    ) / degrees
    if pooled_variance <= 0:
        return None
    correction = 1 - 3 / (4 * degrees - 1)
    return correction * (mean_b - mean_a) / math.sqrt(pooled_variance)


def keyed(rows: list[dict[str, str]], fields: tuple[str, ...]) -> dict[tuple[str, ...], dict[str, str]]:
    return {tuple(row[field] for field in fields): row for row in rows}


def build_model_prompt_interactions(
    model_a_rows: list[dict[str, str]],
    model_b_rows: list[dict[str, str]],
    *,
    model_a_label: str,
    model_b_label: str,
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    """Estimate model-by-prompt interaction contrasts with task-valid resampling."""
    policy = config["analysis"]["prompt_sensitivity"]
    baseline = config["analysis"]["baseline_condition"]
    replicates = int(policy["bootstrap_replicates"])
    confidence_level = float(policy["confidence_level"])
    base_bootstrap_seed = int(policy["bootstrap_seed"])
    index: dict[str, dict[tuple[str, str, int], dict[str, str]]] = {}
    for label, rows in ((model_a_label, model_a_rows), (model_b_label, model_b_rows)):
        model_index: dict[tuple[str, str, int], dict[str, str]] = {}
        for row in rows:
            key = (row["task"], row["prompt_condition"], int(row["seed"]))
            if key in model_index:
                raise ValueError(f"{label} contains duplicate run key {key}.")
            model_index[key] = row
        index[label] = model_index

    output: list[dict[str, Any]] = []
    for task, metrics in policy["primary_metrics"].items():
        conditions = [
            condition
            for condition in config["tasks"][task]["prompt_conditions"]
            if condition != baseline
        ]
        for condition in conditions:
            seed_sets = []
            for label in (model_a_label, model_b_label):
                baseline_seeds = {
                    seed for row_task, row_condition, seed in index[label]
                    if row_task == task and row_condition == baseline
                }
                condition_seeds = {
                    seed for row_task, row_condition, seed in index[label]
                    if row_task == task and row_condition == condition
                }
                if baseline_seeds != condition_seeds:
                    raise ValueError(f"{label} has unmatched baseline/condition seeds for {task}/{condition}.")
                seed_sets.append(baseline_seeds)
            if seed_sets[0] != seed_sets[1]:
                raise ValueError(f"Models have unmatched seeds for {task}/{condition}.")
            seeds = sorted(seed_sets[0])
            if len(seeds) < 2:
                raise ValueError("Interaction contrasts require at least two runs per cell.")

            for metric in metrics:
                model_a_effects: list[float] = []
                model_b_effects: list[float] = []
                did_values: list[float] = []
                for seed in seeds:
                    a_effect = (
                        float(index[model_a_label][(task, condition, seed)][metric])
                        - float(index[model_a_label][(task, baseline, seed)][metric])
                    )
                    b_effect = (
                        float(index[model_b_label][(task, condition, seed)][metric])
                        - float(index[model_b_label][(task, baseline, seed)][metric])
                    )
                    model_a_effects.append(a_effect)
                    model_b_effects.append(b_effect)
                    did_values.append(b_effect - a_effect)

                rng = random.Random(
                    stable_bootstrap_seed(
                        base_bootstrap_seed,
                        "model_prompt_interaction",
                        task,
                        "shared_horizon_random_baseline"
                        if task == "horizon" and metric == "random_exploration_effect"
                        else condition,
                        metric,
                    )
                )
                if task == "horizon" and metric == "random_exploration_effect":
                    run_effect_sd = float(
                        config["analysis"]["horizon_random_exploration"]["run_effect_sd"]
                    )
                    cells = {
                        (label, prompt): _horizon_observations_by_seed([
                            index[label][(task, prompt, seed)] for seed in seeds
                        ])
                        for label in (model_a_label, model_b_label)
                        for prompt in (baseline, condition)
                    }
                    bootstrap_means = []
                    for _ in range(replicates):
                        sampled = [rng.choice(seeds) for _ in seeds]
                        try:
                            a_base = statistics.mean(_refit_horizon_run_values(
                                cells[(model_a_label, baseline)], sampled,
                                run_effect_sd=run_effect_sd,
                            ))
                            a_condition = statistics.mean(_refit_horizon_run_values(
                                cells[(model_a_label, condition)], sampled,
                                run_effect_sd=run_effect_sd,
                            ))
                            b_base = statistics.mean(_refit_horizon_run_values(
                                cells[(model_b_label, baseline)], sampled,
                                run_effect_sd=run_effect_sd,
                            ))
                            b_condition = statistics.mean(_refit_horizon_run_values(
                                cells[(model_b_label, condition)], sampled,
                                run_effect_sd=run_effect_sd,
                            ))
                        except (ValueError, RuntimeError, FloatingPointError):
                            continue
                        bootstrap_means.append(
                            (b_condition - b_base) - (a_condition - a_base)
                        )
                    resampling_unit = "matched_environment_seed_block_hierarchical_refit"
                    interaction_sd = statistics.stdev(did_values)
                elif task in {"horizon", "bart"}:
                    bootstrap_means = [
                        statistics.mean(rng.choice(did_values) for _ in seeds)
                        for _ in range(replicates)
                    ]
                    resampling_unit = "matched_environment_seed_block"
                    interaction_sd: float | None = statistics.stdev(did_values)
                else:
                    bootstrap_means = []
                    for _ in range(replicates):
                        a_base = statistics.mean(
                            rng.choice(
                                [float(index[model_a_label][(task, baseline, seed)][metric]) for seed in seeds]
                            )
                            for _ in seeds
                        )
                        a_condition = statistics.mean(
                            rng.choice(
                                [float(index[model_a_label][(task, condition, seed)][metric]) for seed in seeds]
                            )
                            for _ in seeds
                        )
                        b_base = statistics.mean(
                            rng.choice(
                                [float(index[model_b_label][(task, baseline, seed)][metric]) for seed in seeds]
                            )
                            for _ in seeds
                        )
                        b_condition = statistics.mean(
                            rng.choice(
                                [float(index[model_b_label][(task, condition, seed)][metric]) for seed in seeds]
                            )
                            for _ in seeds
                        )
                        bootstrap_means.append((b_condition - b_base) - (a_condition - a_base))
                    resampling_unit = "independent_run_within_model_prompt_cell"
                    interaction_sd = None
                alpha = (1.0 - confidence_level) / 2.0
                output.append(
                    {
                        "prompt_language": "en",
                        "task": task,
                        "prompt_condition": condition,
                        "metric": metric,
                        "model_a": model_a_label,
                        "model_b": model_b_label,
                        "runs_per_cell": len(seeds),
                        "model_a_mean_prompt_effect": statistics.mean(model_a_effects),
                        "model_b_mean_prompt_effect": statistics.mean(model_b_effects),
                        "model_by_prompt_interaction": statistics.mean(model_b_effects) - statistics.mean(model_a_effects),
                        "interaction_sd": interaction_sd,
                        "resampling_unit": resampling_unit,
                        "confidence_level": confidence_level,
                        "bootstrap_replicates": replicates,
                        "interaction_ci_lower": percentile(bootstrap_means, alpha),
                        "interaction_ci_upper": percentile(bootstrap_means, 1.0 - alpha),
                    }
                )
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare two processed model batches.")
    parser.add_argument("--model-a-dir", type=Path, required=True)
    parser.add_argument("--model-a-label", required=True)
    parser.add_argument("--model-b-dir", type=Path, required=True)
    parser.add_argument("--model-b-label", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/experiment_config_stage01.json"),
    )
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    metric_fields = ("task", "prompt_condition", "metric")
    a_metrics = keyed(read_csv(args.model_a_dir / "metric_summary.csv"), metric_fields)
    b_metrics = keyed(read_csv(args.model_b_dir / "metric_summary.csv"), metric_fields)
    if set(a_metrics) != set(b_metrics):
        raise ValueError("Model metric-summary keys do not match.")

    metric_rows: list[dict[str, Any]] = []
    for key in sorted(a_metrics):
        a, b = a_metrics[key], b_metrics[key]
        mean_a, mean_b = float(a["mean"]), float(b["mean"])
        sd_a, sd_b = float(a["sd"]), float(b["sd"])
        n_a, n_b = int(a["n"]), int(b["n"])
        metric_rows.append(
            {
                "task": key[0],
                "prompt_condition": key[1],
                "metric": key[2],
                "model_a": args.model_a_label,
                "model_b": args.model_b_label,
                "model_a_n": n_a,
                "model_b_n": n_b,
                "model_a_mean": mean_a,
                "model_b_mean": mean_b,
                "model_b_minus_model_a": mean_b - mean_a,
                "cross_model_hedges_g": hedges_g(mean_a, sd_a, n_a, mean_b, sd_b, n_b),
            }
        )
    write_csv(args.output_dir / "model_metric_comparison.csv", metric_rows)

    psi_fields = ("task", "prompt_condition")
    a_psi = keyed(read_csv(args.model_a_dir / "prompt_sensitivity.csv"), psi_fields)
    b_psi = keyed(read_csv(args.model_b_dir / "prompt_sensitivity.csv"), psi_fields)
    if set(a_psi) != set(b_psi):
        raise ValueError("Model PSI keys do not match.")
    psi_rows: list[dict[str, Any]] = []
    for key in sorted(a_psi):
        value_a, value_b = float(a_psi[key]["psi"]), float(b_psi[key]["psi"])
        psi_rows.append(
            {
                "task": key[0],
                "prompt_condition": key[1],
                "model_a": args.model_a_label,
                "model_b": args.model_b_label,
                "model_a_psi": value_a,
                "model_b_psi": value_b,
                "model_b_minus_model_a_psi": value_b - value_a,
            }
        )
    write_csv(args.output_dir / "model_psi_comparison.csv", psi_rows)

    interaction_rows = build_model_prompt_interactions(
        read_csv(args.model_a_dir / "llm_run_metrics.csv"),
        read_csv(args.model_b_dir / "llm_run_metrics.csv"),
        model_a_label=args.model_a_label,
        model_b_label=args.model_b_label,
        config=load_config(args.config),
    )
    write_csv(args.output_dir / "model_prompt_interaction_contrasts.csv", interaction_rows)

    summary = {
        "analysis": "two_model_english_comparison",
        "model_a": args.model_a_label,
        "model_b": args.model_b_label,
        "metric_comparison_rows": len(metric_rows),
        "psi_comparison_rows": len(psi_rows),
        "model_prompt_interaction_rows": len(interaction_rows),
        "model_prompt_interaction_definition": "[(model_b condition - model_b baseline) - (model_a condition - model_a baseline)]",
        "bootstrap_units": {
            "horizon_and_bart": "matched_environment_seed_block",
            "horizon_random_exploration": "matched_environment_seed_block_hierarchical_refit",
            "igt": "independent_run_within_model_prompt_cell"
        },
        "metric_keys_match": True,
        "psi_keys_match": True,
        "notes": "Positive differences and Hedges g indicate model_b exceeds model_a; direction is metric-specific and is not inherently better.",
    }
    (args.output_dir / "model_comparison_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
