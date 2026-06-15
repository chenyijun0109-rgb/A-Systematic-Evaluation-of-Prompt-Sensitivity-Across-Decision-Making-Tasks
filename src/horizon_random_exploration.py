from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from scipy.optimize import minimize
from scipy.special import expit


HORIZON_INDEX = {"horizon_1": 0, "horizon_6": 1}
DEFAULT_RUN_EFFECT_SD = 0.5


@dataclass(frozen=True)
class ChoiceObservation:
    run_id: str
    prompt_condition: str
    horizon_type: str
    choice_a: int
    delta_reward: float
    delta_information_value: float


def llm_run_id(path: Path, seed: Any) -> str:
    return f"{path.resolve().as_posix()}:seed={seed}"


def build_choice_observation(
    record: dict[str, Any],
    *,
    run_id: str,
    prompt_condition: str,
) -> ChoiceObservation:
    if not record.get("first_free_choice"):
        raise ValueError("Random-exploration analysis requires first free choices only.")

    horizon_type = str(record["horizon_type"])
    if horizon_type not in HORIZON_INDEX:
        raise ValueError(f"Unknown horizon type: {horizon_type!r}")

    observed_mean_a = record.get("observed_mean_A")
    observed_mean_b = record.get("observed_mean_B")
    if observed_mean_a is None or observed_mean_b is None:
        raise ValueError("Both observed option means are required.")

    n_observed_a = int(record["n_observed_A"])
    n_observed_b = int(record["n_observed_B"])
    if n_observed_a < n_observed_b:
        delta_information_value = 1.0
    elif n_observed_b < n_observed_a:
        delta_information_value = -1.0
    else:
        delta_information_value = 0.0

    choice = str(record["choice"]).upper()
    if choice not in {"A", "B"}:
        raise ValueError(f"Unknown choice: {choice!r}")

    return ChoiceObservation(
        run_id=run_id,
        prompt_condition=prompt_condition,
        horizon_type=horizon_type,
        choice_a=1 if choice == "A" else 0,
        delta_reward=float(observed_mean_a) - float(observed_mean_b),
        delta_information_value=delta_information_value,
    )


def load_llm_choice_observations(paths: Iterable[Path]) -> list[ChoiceObservation]:
    observations: list[ChoiceObservation] = []
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("task") != "horizon":
            continue
        if not data.get("done", False):
            continue

        prompt_condition = str(data["prompt_condition"])
        run_id = llm_run_id(path, data.get("seed", "unknown"))
        for record in data.get("trial_records", []):
            if record.get("first_free_choice"):
                observations.append(
                    build_choice_observation(
                        record,
                        run_id=run_id,
                        prompt_condition=prompt_condition,
                    )
                )
    return observations


def load_human_choice_observations(
    path: Path,
    *,
    prompt_condition: str = "human",
) -> list[ChoiceObservation]:
    observations: list[ChoiceObservation] = []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        for game in reader:
            subject = str(game["subjectNumber"])
            game_length = int(game["gameLength"])
            horizon_type = "horizon_1" if game_length == 5 else "horizon_6"
            histories: dict[int, list[float]] = {1: [], 2: []}

            for trial_index in range(1, 6):
                choice_text = str(game.get(f"c{trial_index}", "")).strip()
                reward_text = str(game.get(f"r{trial_index}", "")).strip()
                if not choice_text:
                    continue
                choice = int(float(choice_text))

                if trial_index == 5:
                    record = {
                        "first_free_choice": True,
                        "horizon_type": horizon_type,
                        "choice": "A" if choice == 1 else "B",
                        "observed_mean_A": _safe_mean(histories[1]),
                        "observed_mean_B": _safe_mean(histories[2]),
                        "n_observed_A": len(histories[1]),
                        "n_observed_B": len(histories[2]),
                    }
                    observations.append(
                        build_choice_observation(
                            record,
                            run_id=f"human:{subject}",
                            prompt_condition=prompt_condition,
                        )
                    )

                if reward_text:
                    histories[choice].append(float(reward_text))
    return observations


def fit_hierarchical_random_exploration(
    observations: list[ChoiceObservation],
    *,
    run_effect_sd: float = DEFAULT_RUN_EFFECT_SD,
) -> dict[str, Any]:
    if run_effect_sd <= 0:
        raise ValueError("run_effect_sd must be positive.")
    if not observations:
        raise ValueError("At least one observation is required.")

    conditions = {observation.prompt_condition for observation in observations}
    if len(conditions) != 1:
        raise ValueError("Fit one prompt condition at a time.")
    condition = next(iter(conditions))

    run_ids = sorted({observation.run_id for observation in observations})
    if len(run_ids) < 2:
        raise ValueError("Hierarchical estimation requires at least two runs.")

    run_index = {run_id: index for index, run_id in enumerate(run_ids)}
    horizon = np.asarray(
        [HORIZON_INDEX[observation.horizon_type] for observation in observations],
        dtype=int,
    )
    choices = np.asarray([observation.choice_a for observation in observations], dtype=float)
    delta_reward = np.asarray(
        [observation.delta_reward for observation in observations],
        dtype=float,
    )
    delta_information = np.asarray(
        [observation.delta_information_value for observation in observations],
        dtype=float,
    )
    runs = np.asarray([run_index[observation.run_id] for observation in observations], dtype=int)

    for horizon_name, horizon_value in HORIZON_INDEX.items():
        if not np.any(horizon == horizon_value):
            raise ValueError(f"No observations found for {horizon_name}.")

    n_runs = len(run_ids)
    initial = np.zeros(6 + 2 * n_runs, dtype=float)
    initial[0:2] = math.log(1.0 / 8.0)

    def objective_and_gradient(parameters: np.ndarray) -> tuple[float, np.ndarray]:
        log_reward_sensitivity = parameters[0:2]
        information_bonus = parameters[2:4]
        label_bias = parameters[4:6]
        run_deviation = parameters[6:].reshape(n_runs, 2)

        selected_log_sensitivity = (
            log_reward_sensitivity[horizon] + run_deviation[runs, horizon]
        )
        reward_sensitivity = np.exp(np.clip(selected_log_sensitivity, -8.0, 4.0))
        subjective_difference = (
            delta_reward
            + information_bonus[horizon] * delta_information
            + label_bias[horizon]
        )
        linear_predictor = reward_sensitivity * subjective_difference

        negative_log_likelihood = np.sum(
            np.logaddexp(0.0, linear_predictor) - choices * linear_predictor
        )
        residual = expit(linear_predictor) - choices

        gradient = np.zeros_like(parameters)
        for horizon_value in (0, 1):
            mask = horizon == horizon_value
            gradient[horizon_value] = np.sum(
                residual[mask] * linear_predictor[mask]
            )
            gradient[2 + horizon_value] = np.sum(
                residual[mask]
                * reward_sensitivity[mask]
                * delta_information[mask]
            )
            gradient[4 + horizon_value] = np.sum(
                residual[mask] * reward_sensitivity[mask]
            )

        run_gradient = np.zeros((n_runs, 2), dtype=float)
        np.add.at(
            run_gradient,
            (runs, horizon),
            residual * linear_predictor,
        )

        prior_mean = math.log(1.0 / 8.0)
        log_sensitivity_sd = 1.5
        information_bonus_sd = 20.0
        label_bias_sd = 20.0

        negative_log_prior = 0.5 * np.sum(
            ((log_reward_sensitivity - prior_mean) / log_sensitivity_sd) ** 2
        )
        negative_log_prior += 0.5 * np.sum(
            (information_bonus / information_bonus_sd) ** 2
        )
        negative_log_prior += 0.5 * np.sum((label_bias / label_bias_sd) ** 2)
        negative_log_prior += 0.5 * np.sum((run_deviation / run_effect_sd) ** 2)

        gradient[0:2] += (
            log_reward_sensitivity - prior_mean
        ) / log_sensitivity_sd**2
        gradient[2:4] += information_bonus / information_bonus_sd**2
        gradient[4:6] += label_bias / label_bias_sd**2
        run_gradient += run_deviation / run_effect_sd**2
        gradient[6:] = run_gradient.ravel()

        return float(negative_log_likelihood + negative_log_prior), gradient

    fit = minimize(
        objective_and_gradient,
        initial,
        method="L-BFGS-B",
        jac=True,
        options={"maxiter": 2000, "ftol": 1e-10, "gtol": 1e-7},
    )

    parameters = fit.x
    condition_log_sensitivity = parameters[0:2]
    information_bonus = parameters[2:4]
    label_bias = parameters[4:6]
    run_deviation = parameters[6:].reshape(n_runs, 2)

    condition_noise = np.exp(-condition_log_sensitivity)
    condition_estimate = _estimate_record(
        decision_noise_h1=float(condition_noise[0]),
        decision_noise_h6=float(condition_noise[1]),
        information_bonus_h1=float(information_bonus[0]),
        information_bonus_h6=float(information_bonus[1]),
        label_bias_h1=float(label_bias[0]),
        label_bias_h6=float(label_bias[1]),
    )

    run_estimates = []
    for index, run_id in enumerate(run_ids):
        run_noise = np.exp(-(condition_log_sensitivity + run_deviation[index]))
        run_estimates.append(
            {
                "run_id": run_id,
                **_estimate_record(
                    decision_noise_h1=float(run_noise[0]),
                    decision_noise_h6=float(run_noise[1]),
                    information_bonus_h1=float(information_bonus[0]),
                    information_bonus_h6=float(information_bonus[1]),
                    label_bias_h1=float(label_bias[0]),
                    label_bias_h6=float(label_bias[1]),
                ),
            }
        )

    return {
        "prompt_condition": condition,
        "model": "hierarchical_logistic_map_fixed_gaussian_shrinkage",
        "definition": "decision_noise_h6 - decision_noise_h1",
        "first_free_choices_only": True,
        "run_effect_sd": run_effect_sd,
        "n_runs": n_runs,
        "n_choices": len(observations),
        "converged": bool(fit.success),
        "optimizer_message": str(fit.message),
        "objective": float(fit.fun),
        "condition_estimate": condition_estimate,
        "run_estimates": run_estimates,
    }


def analyze_choice_observations(
    observations: list[ChoiceObservation],
    *,
    run_effect_sd: float = DEFAULT_RUN_EFFECT_SD,
) -> dict[str, Any]:
    by_condition: dict[str, list[ChoiceObservation]] = {}
    for observation in observations:
        by_condition.setdefault(observation.prompt_condition, []).append(observation)

    results: dict[str, Any] = {}
    for condition, condition_observations in sorted(by_condition.items()):
        n_runs = len({observation.run_id for observation in condition_observations})
        if n_runs < 2:
            results[condition] = {
                "status": "insufficient_runs",
                "n_runs": n_runs,
                "minimum_runs": 2,
                "message": "Hierarchical estimation requires at least two runs.",
            }
            continue
        results[condition] = {
            "status": "ok",
            **fit_hierarchical_random_exploration(
                condition_observations,
                run_effect_sd=run_effect_sd,
            ),
        }
    return results


def discover_json_paths(inputs: Iterable[Path]) -> list[Path]:
    paths: set[Path] = set()
    for input_path in inputs:
        if input_path.is_dir():
            paths.update(input_path.rglob("*.json"))
        elif input_path.suffix.lower() == ".json":
            paths.add(input_path)
    return sorted(paths)


def eligible_horizon_json_paths(paths: Iterable[Path]) -> list[Path]:
    eligible = []
    for path in paths:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if data.get("task") == "horizon" and data.get("done", False):
            eligible.append(path)
    return eligible


def _estimate_record(
    *,
    decision_noise_h1: float,
    decision_noise_h6: float,
    information_bonus_h1: float,
    information_bonus_h6: float,
    label_bias_h1: float,
    label_bias_h6: float,
) -> dict[str, float]:
    return {
        "decision_noise_h1": decision_noise_h1,
        "decision_noise_h6": decision_noise_h6,
        "random_exploration_effect": decision_noise_h6 - decision_noise_h1,
        "information_bonus_h1": information_bonus_h1,
        "information_bonus_h6": information_bonus_h6,
        "label_bias_h1": label_bias_h1,
        "label_bias_h6": label_bias_h6,
    }


def _safe_mean(values: list[float]) -> float:
    if not values:
        raise ValueError("Expected at least one observed reward per option.")
    return sum(values) / len(values)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Estimate Horizon random exploration from first free choices."
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        type=Path,
        help="Horizon JSON files or directories containing JSON outputs.",
    )
    parser.add_argument(
        "--human-data",
        type=Path,
        help="Optional raw Horizon human CSV to fit with the same choice model.",
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--run-effect-sd", type=float, default=DEFAULT_RUN_EFFECT_SD)
    args = parser.parse_args()

    paths = eligible_horizon_json_paths(discover_json_paths(args.inputs))
    observations = load_llm_choice_observations(paths)
    if args.human_data:
        observations.extend(load_human_choice_observations(args.human_data))
    if not observations:
        raise SystemExit("No eligible first-free-choice observations were found.")
    result = {
        "analysis": "horizon_random_exploration",
        "source_files": [str(path) for path in paths],
        "n_first_free_choices": len(observations),
        "conditions": analyze_choice_observations(
            observations,
            run_effect_sd=args.run_effect_sd,
        ),
    }
    text = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
