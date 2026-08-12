from __future__ import annotations

import argparse
import csv
import json
import random
import statistics
from pathlib import Path
from typing import Any

from src.compute_language_interactions import _by_seed, _hedges_g, _sample, _values, read_rows
from src.compute_prompt_sensitivity import stable_bootstrap_seed, validated_percentile_interval
from src.prompt_loader import load_config


LANGUAGES = ("en", "zh-CN", "es")
BASELINE_FIELDS = (
    "task", "metric", "language", "n", "language_mean", "three_language_mean",
    "centered_baseline_deviation", "standardised_centered_baseline_deviation",
    "bootstrap_unit", "confidence_level", "bootstrap_replicates", "raw_valid_replicates",
    "raw_valid_proportion", "raw_interval_status", "standardised_valid_replicates",
    "standardised_valid_proportion", "standardised_interval_status", "raw_ci_lower",
    "raw_ci_upper", "standardised_ci_lower", "standardised_ci_upper",
)
PROMPT_FIELDS = (
    "task", "prompt_condition", "metric", "language", "baseline_n", "condition_n",
    "language_prompt_effect", "three_language_mean_prompt_effect", "centered_prompt_effect",
    "language_hedges_g", "three_language_mean_hedges_g", "standardised_centered_prompt_effect",
    "bootstrap_unit", "confidence_level", "bootstrap_replicates", "raw_valid_replicates",
    "raw_valid_proportion", "raw_interval_status", "standardised_valid_replicates",
    "standardised_valid_proportion", "standardised_interval_status", "raw_ci_lower",
    "raw_ci_upper", "standardised_ci_lower", "standardised_ci_upper",
)


def _interval(values: list[float], *, requested: int, confidence: float, config: dict[str, Any]) -> dict[str, Any]:
    return validated_percentile_interval(
        values, requested_replicates=requested, confidence_level=confidence,
        policy=config["analysis"]["prompt_sensitivity"],
    )


def _write(path: Path, rows: list[dict[str, Any]], fields: tuple[str, ...]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def run(run_metrics: Path, output_dir: Path, config_path: Path) -> None:
    config = load_config(config_path)
    rows = read_rows(run_metrics)
    policy = config["analysis"]["language_sensitivity"]
    prompt_policy = config["analysis"]["prompt_sensitivity"]
    replicates = int(policy.get("bootstrap_replicates", prompt_policy["bootstrap_replicates"]))
    confidence = float(policy.get("confidence_level", prompt_policy["confidence_level"]))
    base_seed = int(policy.get("bootstrap_seed", prompt_policy["bootstrap_seed"]))
    baseline = str(config["analysis"]["baseline_condition"])
    metrics_by_task = prompt_policy["primary_metrics"]
    baseline_rows: list[dict[str, Any]] = []
    prompt_rows: list[dict[str, Any]] = []

    for task, metrics in metrics_by_task.items():
        paired = task in {"horizon", "bart"}
        for metric in metrics:
            if paired:
                maps = {language: _by_seed(rows, language=language, task=task, condition=baseline, metric=metric) for language in LANGUAGES}
                seeds = sorted(set.intersection(*(set(mapping) for mapping in maps.values())))
                cells = {language: [maps[language][seed] for seed in seeds] for language in LANGUAGES}
            else:
                seeds = []
                cells = {language: _values(rows, language=language, task=task, condition=baseline, metric=metric) for language in LANGUAGES}
            means = {language: statistics.mean(values) for language, values in cells.items()}
            grand = statistics.mean(means.values())
            pooled = (sum(statistics.variance(values) for values in cells.values()) / len(LANGUAGES)) ** 0.5
            raw_boot = {language: [] for language in LANGUAGES}
            std_boot = {language: [] for language in LANGUAGES}
            rng = random.Random(stable_bootstrap_seed(base_seed, "joint_language_baseline", task, metric))
            for _ in range(replicates):
                if paired:
                    indices = [rng.randrange(len(seeds)) for _ in seeds]
                    sampled = {language: [values[index] for index in indices] for language, values in cells.items()}
                else:
                    sampled = {language: _sample(values, rng) for language, values in cells.items()}
                sample_means = {language: statistics.mean(values) for language, values in sampled.items()}
                sample_grand = statistics.mean(sample_means.values())
                sample_pooled = (sum(statistics.variance(values) for values in sampled.values()) / len(LANGUAGES)) ** 0.5
                for language in LANGUAGES:
                    deviation = sample_means[language] - sample_grand
                    raw_boot[language].append(deviation)
                    if sample_pooled > 0:
                        std_boot[language].append(deviation / sample_pooled)
            for language in LANGUAGES:
                raw_i = _interval(raw_boot[language], requested=replicates, confidence=confidence, config=config)
                std_i = _interval(std_boot[language], requested=replicates, confidence=confidence, config=config)
                deviation = means[language] - grand
                baseline_rows.append({
                    "task": task, "metric": metric, "language": language, "n": len(cells[language]),
                    "language_mean": means[language], "three_language_mean": grand,
                    "centered_baseline_deviation": deviation,
                    "standardised_centered_baseline_deviation": deviation / pooled if pooled > 0 else None,
                    "bootstrap_unit": "matched_seed_block" if paired else "independent_cell_run",
                    "confidence_level": confidence, "bootstrap_replicates": replicates,
                    "raw_valid_replicates": raw_i["valid_replicates"], "raw_valid_proportion": raw_i["valid_proportion"],
                    "raw_interval_status": raw_i["interval_status"], "standardised_valid_replicates": std_i["valid_replicates"],
                    "standardised_valid_proportion": std_i["valid_proportion"], "standardised_interval_status": std_i["interval_status"],
                    "raw_ci_lower": raw_i["ci_lower"], "raw_ci_upper": raw_i["ci_upper"],
                    "standardised_ci_lower": std_i["ci_lower"], "standardised_ci_upper": std_i["ci_upper"],
                })

        for condition in config["tasks"][task]["prompt_conditions"]:
            if condition == baseline:
                continue
            for metric in metrics:
                keys = [(language, cell) for language in LANGUAGES for cell in (baseline, condition)]
                if paired:
                    maps = {(language, cell): _by_seed(rows, language=language, task=task, condition=cell, metric=metric) for language, cell in keys}
                    seeds = sorted(set.intersection(*(set(mapping) for mapping in maps.values())))
                    cells = {(language, cell): [maps[(language, cell)][seed] for seed in seeds] for language, cell in keys}
                else:
                    seeds = []
                    cells = {(language, cell): _values(rows, language=language, task=task, condition=cell, metric=metric) for language, cell in keys}
                effects = {language: statistics.mean(cells[(language, condition)]) - statistics.mean(cells[(language, baseline)]) for language in LANGUAGES}
                gs = {language: _hedges_g(cells[(language, baseline)], cells[(language, condition)]) for language in LANGUAGES}
                effect_grand = statistics.mean(effects.values())
                g_grand = statistics.mean(value for value in gs.values() if value is not None)
                raw_boot = {language: [] for language in LANGUAGES}
                std_boot = {language: [] for language in LANGUAGES}
                rng = random.Random(stable_bootstrap_seed(base_seed, "joint_language_prompt", task, condition, metric))
                for _ in range(replicates):
                    if paired:
                        indices = [rng.randrange(len(seeds)) for _ in seeds]
                        sampled = {key: [values[index] for index in indices] for key, values in cells.items()}
                    else:
                        sampled = {key: _sample(values, rng) for key, values in cells.items()}
                    sample_effects = {language: statistics.mean(sampled[(language, condition)]) - statistics.mean(sampled[(language, baseline)]) for language in LANGUAGES}
                    sample_gs = {language: _hedges_g(sampled[(language, baseline)], sampled[(language, condition)]) for language in LANGUAGES}
                    sample_effect_grand = statistics.mean(sample_effects.values())
                    valid_gs = [value for value in sample_gs.values() if value is not None]
                    for language in LANGUAGES:
                        raw_boot[language].append(sample_effects[language] - sample_effect_grand)
                        if sample_gs[language] is not None and len(valid_gs) == len(LANGUAGES):
                            std_boot[language].append(sample_gs[language] - statistics.mean(valid_gs))
                for language in LANGUAGES:
                    raw_i = _interval(raw_boot[language], requested=replicates, confidence=confidence, config=config)
                    std_i = _interval(std_boot[language], requested=replicates, confidence=confidence, config=config)
                    prompt_rows.append({
                        "task": task, "prompt_condition": condition, "metric": metric, "language": language,
                        "baseline_n": len(cells[(language, baseline)]), "condition_n": len(cells[(language, condition)]),
                        "language_prompt_effect": effects[language], "three_language_mean_prompt_effect": effect_grand,
                        "centered_prompt_effect": effects[language] - effect_grand, "language_hedges_g": gs[language],
                        "three_language_mean_hedges_g": g_grand,
                        "standardised_centered_prompt_effect": gs[language] - g_grand if gs[language] is not None else None,
                        "bootstrap_unit": "matched_seed_block" if paired else "independent_cell_run",
                        "confidence_level": confidence, "bootstrap_replicates": replicates,
                        "raw_valid_replicates": raw_i["valid_replicates"], "raw_valid_proportion": raw_i["valid_proportion"],
                        "raw_interval_status": raw_i["interval_status"], "standardised_valid_replicates": std_i["valid_replicates"],
                        "standardised_valid_proportion": std_i["valid_proportion"], "standardised_interval_status": std_i["interval_status"],
                        "raw_ci_lower": raw_i["ci_lower"], "raw_ci_upper": raw_i["ci_upper"],
                        "standardised_ci_lower": std_i["ci_lower"], "standardised_ci_upper": std_i["ci_upper"],
                    })

    output_dir.mkdir(parents=True, exist_ok=True)
    _write(output_dir / "language_centered_baselines.csv", baseline_rows, BASELINE_FIELDS)
    _write(output_dir / "language_centered_prompt_effects.csv", prompt_rows, PROMPT_FIELDS)
    (output_dir / "joint_language_summary.json").write_text(json.dumps({
        "analysis": "symmetric_three_language_centered_contrasts", "languages": LANGUAGES,
        "baseline_rows": len(baseline_rows), "prompt_rows": len(prompt_rows),
        "bootstrap_replicates": replicates,
    }, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute symmetric three-language centred contrasts.")
    parser.add_argument("run_metrics_csv", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=Path("configs/experiment_config_stage01.json"))
    args = parser.parse_args()
    run(args.run_metrics_csv, args.output_dir, args.config)


if __name__ == "__main__":
    main()
