# Validation Mini-Pilot v02 Summary

Run date: 2026-06-15

Raw outputs:

```text
outputs/validation_mini_pilot_v02
```

Processed outputs:

```text
outputs/processed/validation_mini_pilot_v02
```

This is the first 36-run validation mini-pilot run under the frozen settings:

```text
requested/resolved model: gpt-4.1-2025-04-14
temperature: 0.7
top_p: 1.0
max_output_tokens: 16
config version: 0.5
```

## Completion

The strict aggregation check passed:

| Check | Result |
|---|---:|
| Raw JSON files | 36 |
| Valid runs | 36 |
| Expected runs per task-condition cell | 3 |
| Invalid responses | 0 |
| Aggregation issues | 0 |
| PSI issues | 0 |
| Analysis complete | true |

All prompt hashes, config versions, API-resolved models, temperature, top-p,
and token limits were consistent across the batch.

## PSI Results

PSI uses mean absolute pooled-SD Hedges' g across primary metrics.

| Task | Condition | PSI | Diagnostic 95% CI |
|---|---|---:|---|
| Horizon | `detailed` | 0.126 | [0.126, 0.775] |
| Horizon | `role_human` | 1.274 | [0.914, 2.355] |
| Horizon | `uncertainty_emphasis` | 1.280 | [1.280, 5.704] |
| IGT | `detailed` | 5.965 | [5.846, 6.794] |
| IGT | `role_human` | 1.356 | [1.264, 1.483] |
| IGT | `reward_loss_emphasis` | 1.318 | [0.939, 6.117] |
| BART | `detailed` | 0.969 | [0.969, 3.492] |
| BART | `role_human` | 0.403 | [0.263, 0.426] |
| BART | `risk_emphasis` | 0.783 | [0.747, 1.612] |

These intervals are diagnostic only because there are three paired runs per
cell.

## IGT Notes

The large `detailed` IGT PSI is mainly driven by
`post_loss_switching_rate`, not by advantageous choice:

| Condition | Metric | Raw difference | Hedges' g |
|---|---|---:|---:|
| `detailed` | `advantageous_choice_rate` | -0.060 | -1.283 |
| `detailed` | `post_loss_switching_rate` | 0.118 | 10.648 |
| `role_human` | `advantageous_choice_rate` | -0.033 | -0.696 |
| `role_human` | `post_loss_switching_rate` | 0.100 | 2.016 |
| `reward_loss_emphasis` | `advantageous_choice_rate` | 0.080 | 1.710 |
| `reward_loss_emphasis` | `post_loss_switching_rate` | -0.049 | -0.925 |

This means the 36-run validation still exposes a small-sample instability:
IGT post-loss switching can produce very large standardized effects when
run-level variance is low. This should be checked again in the 15-20 run
formal batch.

Supplementary learning-trajectory metrics remain excluded from PSI. In this
batch, reward/loss runs all reached `advantageous_choice_rate = 1.0` and
`learning_slope = 0.0`, showing the same ceiling issue identified in v01.

## Horizon Random Exploration

The Horizon diagnostic model converged in all 200 run-cluster bootstrap
replicates for all four conditions. With only three runs, all intervals are
diagnostic.

| Condition | Point estimate | Diagnostic 95% CI | Shrinkage estimates |
|---|---:|---|---|
| `baseline` | -0.955 | [-2.343, 0.857] | -1.120, -0.955, -0.736 |
| `detailed` | -0.763 | [-1.429, 0.543] | -0.860, -0.763, -0.395 |
| `role_human` | 0.468 | [-0.305, 0.857] | 0.455, 0.468, 0.452 |
| `uncertainty_emphasis` | 1.160 | [-6.330, 4.735] | 0.486, 1.160, 1.986 |

The model can produce intervals and the shrinkage diagnostics are available,
but the estimates are not yet stable enough for formal interpretation.

## Decision

The frozen runner and analysis pipeline work under the intended sampling
settings. The batch is suitable as a validation mini-pilot, but not as the
formal experiment. The next step is to run 15-20 valid paired runs per
task-condition cell and re-check IGT post-loss switching variance and Horizon
random-exploration interval width.
