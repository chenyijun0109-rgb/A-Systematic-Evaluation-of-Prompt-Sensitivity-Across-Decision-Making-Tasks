from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
import random
from pathlib import Path
from typing import Any

from src.compute_prompt_sensitivity import parse_optional_float, stable_bootstrap_seed
from src.prompt_loader import load_config


OMNIBUS_FIELDS = (
    "task",
    "prompt_condition",
    "metric",
    "languages",
    "language_count",
    "paired_seed_count",
    "friedman_q",
    "kendalls_w",
    "permutation_replicates",
    "permutation_p_value",
    "language_means",
)
INTERACTION_FIELDS = (
    "task",
    "prompt_condition",
    "metric",
    "languages",
    "language_count",
    "paired_seed_count",
    "friedman_q",
    "kendalls_w",
    "permutation_replicates",
    "permutation_p_value",
    "mean_prompt_effect_by_language",
)


def read_rows(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _by_seed(
    rows: list[dict[str, Any]],
    *,
    language: str,
    task: str,
    condition: str,
    metric: str,
) -> dict[int, float]:
    return {
        int(row["seed"]): value
        for row in rows
        if row.get("prompt_language", "en") == language
        and row.get("task") == task
        and row.get("prompt_condition") == condition
        and (value := parse_optional_float(row.get(metric))) is not None
    }


def _average_ranks(values: list[float]) -> list[float]:
    ordered = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    index = 0
    while index < len(ordered):
        end = index + 1
        while end < len(ordered) and ordered[end][1] == ordered[index][1]:
            end += 1
        average_rank = ((index + 1) + end) / 2.0
        for original_index, _value in ordered[index:end]:
            ranks[original_index] = average_rank
        index = end
    return ranks


def friedman_statistic(matrix: list[list[float]]) -> tuple[float, float]:
    """Return tie-tolerant Friedman Q and Kendall's W for paired language rows."""
    if len(matrix) < 2:
        raise ValueError("Friedman analysis requires at least two paired seeds.")
    language_count = len(matrix[0])
    if language_count < 3 or any(len(row) != language_count for row in matrix):
        raise ValueError("Omnibus language analysis requires at least three languages.")
    ranked = [_average_ranks(row) for row in matrix]
    rank_sums = [
        sum(row[column] for row in ranked)
        for column in range(language_count)
    ]
    seed_count = len(matrix)
    q_uncorrected = (
        12.0
        / (seed_count * language_count * (language_count + 1))
        * sum(rank_sum**2 for rank_sum in rank_sums)
        - 3.0 * seed_count * (language_count + 1)
    )
    tie_sum = 0
    for row in matrix:
        counts: dict[float, int] = {}
        for value in row:
            counts[value] = counts.get(value, 0) + 1
        tie_sum += sum(count**3 - count for count in counts.values())
    correction = 1.0 - tie_sum / (
        seed_count * (language_count**3 - language_count)
    )
    q = q_uncorrected / correction if correction > 0 else 0.0
    w = q / (seed_count * (language_count - 1))
    return q, min(max(w, 0.0), 1.0)


def permutation_p_value(
    matrix: list[list[float]],
    *,
    replicates: int,
    seed: int,
) -> float:
    observed, _w = friedman_statistic(matrix)
    rng = random.Random(seed)
    exceedances = 0
    for _ in range(replicates):
        permuted = []
        for row in matrix:
            shuffled = list(row)
            rng.shuffle(shuffled)
            permuted.append(shuffled)
        statistic, _ = friedman_statistic(permuted)
        if statistic >= observed - 1e-12:
            exceedances += 1
    return (exceedances + 1) / (replicates + 1)


def _complete_matrix(
    mappings: list[dict[int, float]],
) -> tuple[list[int], list[list[float]]]:
    if not mappings:
        return [], []
    common = set(mappings[0])
    for mapping in mappings[1:]:
        common.intersection_update(mapping)
    seeds = sorted(common)
    return seeds, [[mapping[seed] for mapping in mappings] for seed in seeds]


def build_language_omnibus(
    rows: list[dict[str, Any]],
    *,
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    languages = [str(value) for value in config["prompt_languages"]]
    policy = config["analysis"]["prompt_sensitivity"]
    replicates = int(
        config["analysis"]["language_sensitivity"]["permutation_replicates"]
    )
    base_seed = int(policy["bootstrap_seed"])
    output: list[dict[str, Any]] = []
    for task, metrics in policy["primary_metrics"].items():
        for condition in config["tasks"][task]["prompt_conditions"]:
            for metric in metrics:
                mappings = [
                    _by_seed(
                        rows,
                        language=language,
                        task=task,
                        condition=condition,
                        metric=metric,
                    )
                    for language in languages
                ]
                seeds, matrix = _complete_matrix(mappings)
                if len(seeds) < 2:
                    continue
                q, w = friedman_statistic(matrix)
                output.append(
                    {
                        "task": task,
                        "prompt_condition": condition,
                        "metric": metric,
                        "languages": "|".join(languages),
                        "language_count": len(languages),
                        "paired_seed_count": len(seeds),
                        "friedman_q": q,
                        "kendalls_w": w,
                        "permutation_replicates": replicates,
                        "permutation_p_value": permutation_p_value(
                            matrix,
                            replicates=replicates,
                            seed=stable_bootstrap_seed(
                                base_seed,
                                "language_omnibus",
                                task,
                                condition,
                                metric,
                            ),
                        ),
                        "language_means": json.dumps(
                            {
                                language: sum(mapping[seed] for seed in seeds)
                                / len(seeds)
                                for language, mapping in zip(languages, mappings)
                            },
                            ensure_ascii=False,
                            sort_keys=True,
                        ),
                    }
                )
    return output


def build_language_prompt_omnibus(
    rows: list[dict[str, Any]],
    *,
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    languages = [str(value) for value in config["prompt_languages"]]
    baseline = config["analysis"]["baseline_condition"]
    policy = config["analysis"]["prompt_sensitivity"]
    replicates = int(
        config["analysis"]["language_sensitivity"]["permutation_replicates"]
    )
    base_seed = int(policy["bootstrap_seed"])
    output: list[dict[str, Any]] = []
    for task, metrics in policy["primary_metrics"].items():
        for condition in config["tasks"][task]["prompt_conditions"]:
            if condition == baseline:
                continue
            for metric in metrics:
                baseline_maps = [
                    _by_seed(
                        rows,
                        language=language,
                        task=task,
                        condition=baseline,
                        metric=metric,
                    )
                    for language in languages
                ]
                condition_maps = [
                    _by_seed(
                        rows,
                        language=language,
                        task=task,
                        condition=condition,
                        metric=metric,
                    )
                    for language in languages
                ]
                all_maps = list(itertools.chain(baseline_maps, condition_maps))
                common = set(all_maps[0]) if all_maps else set()
                for mapping in all_maps[1:]:
                    common.intersection_update(mapping)
                seeds = sorted(common)
                if len(seeds) < 2:
                    continue
                delta_matrix = [
                    [
                        condition_map[seed] - baseline_map[seed]
                        for baseline_map, condition_map in zip(
                            baseline_maps,
                            condition_maps,
                        )
                    ]
                    for seed in seeds
                ]
                q, w = friedman_statistic(delta_matrix)
                output.append(
                    {
                        "task": task,
                        "prompt_condition": condition,
                        "metric": metric,
                        "languages": "|".join(languages),
                        "language_count": len(languages),
                        "paired_seed_count": len(seeds),
                        "friedman_q": q,
                        "kendalls_w": w,
                        "permutation_replicates": replicates,
                        "permutation_p_value": permutation_p_value(
                            delta_matrix,
                            replicates=replicates,
                            seed=stable_bootstrap_seed(
                                base_seed,
                                "language_prompt_omnibus",
                                task,
                                condition,
                                metric,
                            ),
                        ),
                        "mean_prompt_effect_by_language": json.dumps(
                            {
                                language: sum(
                                    condition_map[seed] - baseline_map[seed]
                                    for seed in seeds
                                )
                                / len(seeds)
                                for language, baseline_map, condition_map in zip(
                                    languages,
                                    baseline_maps,
                                    condition_maps,
                                )
                            },
                            ensure_ascii=False,
                            sort_keys=True,
                        ),
                    }
                )
    return output


def _write_csv(
    path: Path,
    rows: list[dict[str, Any]],
    fieldnames: tuple[str, ...],
) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run_language_omnibus_analysis(
    run_metrics_csv: Path,
    *,
    output_dir: Path,
    config_path: Path,
) -> dict[str, Any]:
    config = load_config(config_path)
    rows = read_rows(run_metrics_csv)
    omnibus = build_language_omnibus(rows, config=config)
    interactions = build_language_prompt_omnibus(rows, config=config)
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(output_dir / "language_omnibus.csv", omnibus, OMNIBUS_FIELDS)
    _write_csv(
        output_dir / "language_prompt_omnibus.csv",
        interactions,
        INTERACTION_FIELDS,
    )
    summary = {
        "analysis": "language_omnibus",
        "languages": config["prompt_languages"],
        "language_omnibus_rows": len(omnibus),
        "language_prompt_omnibus_rows": len(interactions),
        "test": "Friedman repeated-measures omnibus with within-seed permutation p-value",
        "effect_size": "Kendall's W",
        "pairwise_comparisons": "not_computed",
    }
    (output_dir / "language_omnibus_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return {"omnibus": omnibus, "interactions": interactions, "summary": summary}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare all configured prompt languages in one omnibus analysis."
    )
    parser.add_argument("run_metrics_csv", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/experiment_config_stage01.json"),
    )
    args = parser.parse_args()
    result = run_language_omnibus_analysis(
        args.run_metrics_csv,
        output_dir=args.output_dir,
        config_path=args.config,
    )
    print(json.dumps(result["summary"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
