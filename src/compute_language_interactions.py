from __future__ import annotations

import argparse
import csv
import json
import random
import statistics
from pathlib import Path
from typing import Any

from src.compute_prompt_sensitivity import (
    hedges_correction,
    parse_optional_float,
    pooled_sample_sd,
    stable_bootstrap_seed,
    validated_percentile_interval,
)
from src.prompt_loader import load_config


BASELINE_FIELDS = (
    "task", "metric", "reference_language", "target_language",
    "reference_n", "target_n", "reference_mean", "target_mean",
    "raw_language_difference", "standardised_language_difference",
    "bootstrap_unit", "confidence_level", "bootstrap_replicates",
    "raw_valid_replicates", "raw_valid_proportion", "raw_interval_status",
    "standardised_valid_replicates", "standardised_valid_proportion",
    "standardised_interval_status",
    "raw_ci_lower", "raw_ci_upper", "standardised_ci_lower",
    "standardised_ci_upper",
)
INTERACTION_FIELDS = (
    "task", "prompt_condition", "metric", "reference_language",
    "target_language", "reference_baseline_n", "reference_condition_n",
    "target_baseline_n", "target_condition_n", "reference_prompt_effect",
    "target_prompt_effect", "raw_interaction_contrast",
    "reference_hedges_g", "target_hedges_g",
    "standardised_interaction_contrast", "bootstrap_unit",
    "confidence_level", "bootstrap_replicates", "raw_ci_lower",
    "raw_valid_replicates", "raw_valid_proportion", "raw_interval_status",
    "standardised_valid_replicates", "standardised_valid_proportion",
    "standardised_interval_status",
    "raw_ci_upper", "standardised_ci_lower", "standardised_ci_upper",
)


def read_rows(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _values(
    rows: list[dict[str, Any]], *, language: str, task: str,
    condition: str, metric: str,
) -> list[float]:
    return [
        value
        for row in rows
        if row.get("prompt_language", "en") == language
        and row.get("task") == task
        and row.get("prompt_condition") == condition
        and (value := parse_optional_float(row.get(metric))) is not None
    ]


def _by_seed(
    rows: list[dict[str, Any]], *, language: str, task: str,
    condition: str, metric: str,
) -> dict[int, float]:
    return {
        int(row["seed"]): value
        for row in rows
        if row.get("prompt_language", "en") == language
        and row.get("task") == task
        and row.get("prompt_condition") == condition
        and (value := parse_optional_float(row.get(metric))) is not None
    }


def _hedges_g(baseline: list[float], condition: list[float]) -> float | None:
    if len(baseline) < 2 or len(condition) < 2:
        return None
    baseline_sd = statistics.stdev(baseline)
    condition_sd = statistics.stdev(condition)
    denominator = pooled_sample_sd(
        baseline_sd, condition_sd, len(baseline), len(condition)
    )
    if denominator == 0:
        return None
    return (
        hedges_correction(len(baseline), len(condition))
        * (statistics.mean(condition) - statistics.mean(baseline))
        / denominator
    )


def _sample(values: list[float], rng: random.Random) -> list[float]:
    return [rng.choice(values) for _ in values]


def _analysis_policy(config: dict[str, Any]) -> tuple[list[tuple[str, str]], int, float, int]:
    policy = config["analysis"]["language_sensitivity"]
    if "comparison_pairs" in policy:
        pairs = [(str(a), str(b)) for a, b in policy["comparison_pairs"]]
    else:
        reference = str(policy.get("reference_language", "en"))
        pairs = [(reference, str(value)) for value in policy["target_languages"]]
    prompt_policy = config["analysis"]["prompt_sensitivity"]
    return (
        pairs,
        int(policy.get("bootstrap_replicates", prompt_policy["bootstrap_replicates"])),
        float(policy.get("confidence_level", prompt_policy["confidence_level"])),
        int(policy.get("bootstrap_seed", prompt_policy["bootstrap_seed"])),
    )


def build_language_baseline_contrasts(
    rows: list[dict[str, Any]], *, config: dict[str, Any]
) -> list[dict[str, Any]]:
    pairs, replicates, confidence, base_seed = _analysis_policy(config)
    baseline = str(config["analysis"]["baseline_condition"])
    metrics_by_task = config["analysis"]["prompt_sensitivity"]["primary_metrics"]
    output: list[dict[str, Any]] = []
    for task, metrics in metrics_by_task.items():
        paired = task in {"horizon", "bart"}
        for metric in metrics:
            for reference, target in pairs:
                if paired:
                    reference_map = _by_seed(rows, language=reference, task=task, condition=baseline, metric=metric)
                    target_map = _by_seed(rows, language=target, task=task, condition=baseline, metric=metric)
                    seeds = sorted(set(reference_map) & set(target_map))
                    reference_values = [reference_map[seed] for seed in seeds]
                    target_values = [target_map[seed] for seed in seeds]
                else:
                    reference_values = _values(rows, language=reference, task=task, condition=baseline, metric=metric)
                    target_values = _values(rows, language=target, task=task, condition=baseline, metric=metric)
                    seeds = []
                if len(reference_values) < 2 or len(target_values) < 2:
                    continue
                rng = random.Random(stable_bootstrap_seed(base_seed, "language_baseline", task, metric, reference, target))
                raw_boot: list[float] = []
                g_boot: list[float] = []
                for _ in range(replicates):
                    if paired:
                        indices = [rng.randrange(len(seeds)) for _ in seeds]
                        ref_sample = [reference_values[index] for index in indices]
                        target_sample = [target_values[index] for index in indices]
                    else:
                        ref_sample = _sample(reference_values, rng)
                        target_sample = _sample(target_values, rng)
                    raw_boot.append(statistics.mean(target_sample) - statistics.mean(ref_sample))
                    if (g := _hedges_g(ref_sample, target_sample)) is not None:
                        g_boot.append(g)
                validity_policy = config["analysis"]["prompt_sensitivity"]
                raw_interval = validated_percentile_interval(
                    raw_boot, requested_replicates=replicates,
                    confidence_level=confidence, policy=validity_policy,
                )
                g_interval = validated_percentile_interval(
                    g_boot, requested_replicates=replicates,
                    confidence_level=confidence, policy=validity_policy,
                )
                output.append({
                    "task": task, "metric": metric,
                    "reference_language": reference, "target_language": target,
                    "reference_n": len(reference_values), "target_n": len(target_values),
                    "reference_mean": statistics.mean(reference_values),
                    "target_mean": statistics.mean(target_values),
                    "raw_language_difference": statistics.mean(target_values) - statistics.mean(reference_values),
                    "standardised_language_difference": _hedges_g(reference_values, target_values),
                    "bootstrap_unit": "matched_seed_block" if paired else "independent_cell_run",
                    "confidence_level": confidence, "bootstrap_replicates": replicates,
                    "raw_valid_replicates": raw_interval["valid_replicates"],
                    "raw_valid_proportion": raw_interval["valid_proportion"],
                    "raw_interval_status": raw_interval["interval_status"],
                    "standardised_valid_replicates": g_interval["valid_replicates"],
                    "standardised_valid_proportion": g_interval["valid_proportion"],
                    "standardised_interval_status": g_interval["interval_status"],
                    "raw_ci_lower": raw_interval["ci_lower"], "raw_ci_upper": raw_interval["ci_upper"],
                    "standardised_ci_lower": g_interval["ci_lower"], "standardised_ci_upper": g_interval["ci_upper"],
                })
    return output


def build_language_prompt_interactions(
    rows: list[dict[str, Any]], *, config: dict[str, Any]
) -> list[dict[str, Any]]:
    pairs, replicates, confidence, base_seed = _analysis_policy(config)
    baseline = str(config["analysis"]["baseline_condition"])
    metrics_by_task = config["analysis"]["prompt_sensitivity"]["primary_metrics"]
    output: list[dict[str, Any]] = []
    for task, metrics in metrics_by_task.items():
        paired = task in {"horizon", "bart"}
        for condition in config["tasks"][task]["prompt_conditions"]:
            if condition == baseline:
                continue
            for metric in metrics:
                for reference, target in pairs:
                    keys = ((reference, baseline), (reference, condition), (target, baseline), (target, condition))
                    if paired:
                        maps = [_by_seed(rows, language=language, task=task, condition=cell, metric=metric) for language, cell in keys]
                        common = set(maps[0])
                        for mapping in maps[1:]:
                            common &= set(mapping)
                        seeds = sorted(common)
                        cells = [[mapping[seed] for seed in seeds] for mapping in maps]
                    else:
                        cells = [_values(rows, language=language, task=task, condition=cell, metric=metric) for language, cell in keys]
                        seeds = []
                    if any(len(cell) < 2 for cell in cells):
                        continue
                    ref_base, ref_cond, target_base, target_cond = cells
                    ref_effect = statistics.mean(ref_cond) - statistics.mean(ref_base)
                    target_effect = statistics.mean(target_cond) - statistics.mean(target_base)
                    ref_g = _hedges_g(ref_base, ref_cond)
                    target_g = _hedges_g(target_base, target_cond)
                    rng = random.Random(stable_bootstrap_seed(base_seed, "language_prompt_interaction", task, condition, metric, reference, target))
                    raw_boot: list[float] = []
                    g_boot: list[float] = []
                    for _ in range(replicates):
                        if paired:
                            indices = [rng.randrange(len(seeds)) for _ in seeds]
                            sampled = [[cell[index] for index in indices] for cell in cells]
                        else:
                            sampled = [_sample(cell, rng) for cell in cells]
                        rb, rc, tb, tc = sampled
                        raw_boot.append((statistics.mean(tc) - statistics.mean(tb)) - (statistics.mean(rc) - statistics.mean(rb)))
                        sampled_ref_g = _hedges_g(rb, rc)
                        sampled_target_g = _hedges_g(tb, tc)
                        if sampled_ref_g is not None and sampled_target_g is not None:
                            g_boot.append(sampled_target_g - sampled_ref_g)
                    validity_policy = config["analysis"]["prompt_sensitivity"]
                    raw_interval = validated_percentile_interval(
                        raw_boot, requested_replicates=replicates,
                        confidence_level=confidence, policy=validity_policy,
                    )
                    g_interval = validated_percentile_interval(
                        g_boot, requested_replicates=replicates,
                        confidence_level=confidence, policy=validity_policy,
                    )
                    output.append({
                        "task": task, "prompt_condition": condition, "metric": metric,
                        "reference_language": reference, "target_language": target,
                        "reference_baseline_n": len(ref_base), "reference_condition_n": len(ref_cond),
                        "target_baseline_n": len(target_base), "target_condition_n": len(target_cond),
                        "reference_prompt_effect": ref_effect, "target_prompt_effect": target_effect,
                        "raw_interaction_contrast": target_effect - ref_effect,
                        "reference_hedges_g": ref_g, "target_hedges_g": target_g,
                        "standardised_interaction_contrast": (target_g - ref_g) if target_g is not None and ref_g is not None else None,
                        "bootstrap_unit": "matched_seed_block" if paired else "independent_cell_run",
                        "confidence_level": confidence, "bootstrap_replicates": replicates,
                        "raw_valid_replicates": raw_interval["valid_replicates"],
                        "raw_valid_proportion": raw_interval["valid_proportion"],
                        "raw_interval_status": raw_interval["interval_status"],
                        "standardised_valid_replicates": g_interval["valid_replicates"],
                        "standardised_valid_proportion": g_interval["valid_proportion"],
                        "standardised_interval_status": g_interval["interval_status"],
                        "raw_ci_lower": raw_interval["ci_lower"], "raw_ci_upper": raw_interval["ci_upper"],
                        "standardised_ci_lower": g_interval["ci_lower"], "standardised_ci_upper": g_interval["ci_upper"],
                    })
    return output


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: tuple[str, ...]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def run_language_interaction_analysis(
    run_metrics_csv: Path, *, output_dir: Path, config_path: Path
) -> dict[str, Any]:
    config = load_config(config_path)
    rows = read_rows(run_metrics_csv)
    baseline_rows = build_language_baseline_contrasts(rows, config=config)
    interaction_rows = build_language_prompt_interactions(rows, config=config)
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(output_dir / "language_baseline_contrasts.csv", baseline_rows, BASELINE_FIELDS)
    _write_csv(output_dir / "language_prompt_interactions.csv", interaction_rows, INTERACTION_FIELDS)
    summary = {
        "analysis": "language_interaction_bootstrap",
        "comparison_pairs": config["analysis"]["language_sensitivity"].get(
            "comparison_pairs",
            [[config["analysis"]["language_sensitivity"]["reference_language"], target]
             for target in config["analysis"]["language_sensitivity"]["target_languages"]],
        ),
        "baseline_contrast_rows": len(baseline_rows),
        "prompt_interaction_rows": len(interaction_rows),
        "interval": "percentile bootstrap",
    }
    (output_dir / "language_interaction_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return {"baseline_contrasts": baseline_rows, "interactions": interaction_rows, "summary": summary}


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute prespecified pairwise language contrasts with bootstrap intervals.")
    parser.add_argument("run_metrics_csv", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=Path("configs/experiment_config_stage01.json"))
    args = parser.parse_args()
    result = run_language_interaction_analysis(args.run_metrics_csv, output_dir=args.output_dir, config_path=args.config)
    print(json.dumps(result["summary"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
