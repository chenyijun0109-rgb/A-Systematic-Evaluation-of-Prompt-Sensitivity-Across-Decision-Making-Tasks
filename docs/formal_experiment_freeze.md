# Formal Experiment Freeze

Freeze date: 2026-06-15

Status: frozen for validation rerun

The machine-readable record is
`configs/formal_experiment_freeze.json`. It is the authoritative snapshot of
the prompt hashes, model settings, task parameters, metrics, statistical
settings, and exclusion rules.

## Experiment Model

```text
requested model: gpt-4.1-2025-04-14
temperature: 0.7
top_p: 1.0
max_output_tokens: 16
max retries per trial: 1
```

The API-resolved model and sampling settings are recorded in every new raw
JSON. A batch containing mixed resolved models or mixed sampling parameters
must not be combined in the primary analysis.

The old mini-pilot requested `gpt-4.1`, which resolved to
`gpt-4.1-2025-04-14`, but the API response shows `temperature=1.0`. It is
therefore retained as a methodological pilot rather than treated as the
frozen validation dataset.

## Metrics

Primary PSI metrics:

| Task | Metrics |
|---|---|
| Horizon | `directed_exploration`, `horizon_effect`, `random_exploration_effect` |
| IGT | `advantageous_choice_rate`, `post_loss_switching_rate` |
| BART | `adjusted_average_pumps`, `explosion_rate`, `post_explosion_adjustment` |

IGT trajectory outputs are supplementary:

```text
learning_slope
learning_curve_change
block_wise_learning_curve
```

`learning_slope` is the ordinary least-squares slope through block net scores
1 to 5. It describes temporal change, not learning ability. A zero slope can
mean either no improvement or performance already at ceiling.

## Prompt Sensitivity

The primary standardized effect is:

```text
Hedges' g = J * (condition mean - baseline mean) / pooled sample SD
```

The baseline-SD standardized difference is retained only as a sensitivity
analysis. If both groups are constant and have different means, the
standardized effect is undefined; the raw difference remains reportable.

Conditions share task seeds. Confidence intervals therefore resample complete
baseline-condition seed pairs. Formal analysis uses 2,000 bootstrap
replicates and 95% percentile intervals.

## Horizon Random Exploration

```text
random_exploration_effect = decision_noise_h6 - decision_noise_h1
```

The model is a project-specific hierarchical logistic MAP adaptation of the
choice-model logic in Wilson et al. (2014). The central estimate uses
`run_effect_sd=0.5`, with sensitivity checks at `0.25`, `0.5`, and `1.0`.

Bootstrap resampling uses whole runs as clusters. Fewer than 15 valid runs is
labelled diagnostic only; 20 valid runs per condition is the target.

## Exclusions

LLM runs may be excluded for technical reasons:

- The task did not complete.
- The response remained unparseable after the configured retry.
- Prompt hash, config, model, or sampling settings do not match the batch.
- A duplicate logical run cannot be resolved by the declared policy.

Runs must not be excluded because their behavior is extreme, their metrics
have zero variance, or their cognitive-model estimate has an unexpected
direction. Model-fit failures must be reported and investigated rather than
used to silently delete the underlying behavioral run.

Human-data rules remain:

- Horizon: complete records supported by the local open dataset.
- IGT: the 504 participants in the local 100-trial subset.
- BART: age at least 18; exclude IDs `4, 5, 7, 13, 79, 86`, retaining 141
  adults.
