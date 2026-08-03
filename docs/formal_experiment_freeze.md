# Formal Experiment Freeze

Initial method freeze: 2026-06-15

Multilingual scope freeze: 2026-07-29

Status: English complete; matched Chinese and Spanish collection in progress

The machine-readable records are:

```text
configs/formal_experiment_freeze.json
configs/multilingual_experiment_freeze_v01.json
```

The first freezes the model, task parameters, metrics, statistical settings,
and exclusion rules. The second freezes the language factor, all 36 prompt
hashes, matched seeds, output boundary, and multilingual analysis.

## Formal Scope

The project contains one formal experiment with language as an experimental
factor:

```text
3 languages x 3 tasks x 4 prompt conditions x 20 matched seeds
= 720 task runs
```

The completed English `formal_v01` batch supplies 240 task runs. Simplified
Chinese and Spanish use the same base seeds, task offsets, model, sampling
settings, task parameters, conditions, and response tokens for 480 additional
task runs.

Only one open human reference dataset is used per task: Horizon 60
participants, IGT 504 participants, and BART 141 adults. The design does not
include an independent second LLM batch, test-retest ICC, a second set of human
datasets, or cross-dataset robustness analysis.

## Languages and Seeds

```text
languages: en, zh-CN, es
base seeds: 20260708 through 20260727
Horizon task seed: base + 0
IGT task seed: base + 1
BART task seed: base + 2
```

English raw runs remain in `outputs/formal_v01/`. New Chinese and Spanish runs
must be written to `outputs/formal_multilingual_v01/`. Earlier files under
`outputs/multilingual_v01/` are pilot/debug artifacts and are excluded.

Static instructions and dynamic observations use the selected language.
Parser action tokens remain invariant ASCII:

```text
CHOICE: A/B/C/D
ACTION: PUMP/CASH_OUT
```

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

API access credentials are supplied or managed through the University of
Edinburgh. The current client submits inference requests to the OpenAI
Responses API. All three languages must use the same endpoint, fixed model
snapshot, and sampling settings.

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

Within each language, every manipulated condition is compared only with the
baseline in the same language. Language effects use a paired-seed Friedman
omnibus test, Kendall's W, and a within-seed permutation p-value. A second
omnibus analysis compares within-language `condition - baseline` effects
across all three languages. Pairwise language comparisons are not primary.

## Horizon Random Exploration

```text
random_exploration_effect = decision_noise_h6 - decision_noise_h1
```

The model is a project-specific hierarchical logistic MAP adaptation of the
choice-model logic in Wilson et al. (2014). The central estimate uses
`run_effect_sd=0.5`, with sensitivity checks at `0.25`, `0.5`, and `1.0`.

Bootstrap resampling uses whole runs as clusters. Fewer than 15 valid runs is
labelled diagnostic only; 20 valid runs per condition is the target.

Run-specific random-exploration values are partially pooled model-derived
estimates. Every downstream bootstrap replicate used for the random-
exploration prompt effect, model-by-prompt interaction, or PSI must resample
whole run clusters and refit the hierarchical model before recomputing the
reported estimand.

BART `post_explosion_adjustment` is defined only for explosions followed by a
subsequent balloon. If a run or participant has no eligible transition, the
metric is missing and must not be replaced with zero.

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
