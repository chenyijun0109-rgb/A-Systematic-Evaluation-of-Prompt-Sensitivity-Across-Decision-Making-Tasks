# Mini-Pilot Method Diagnostics

Analysis date: 2026-06-15

Source:

```text
outputs/mini_pilot_v01
outputs/processed/mini_pilot_v01
```

The 36 historical runs were reprocessed without new API calls. All 36 runs
remain valid and all task-condition cells contain three paired seeds.

## IGT PSI Inflation

The reward/loss prompt changed `advantageous_choice_rate` by `0.0867`.
Baseline SD was only `0.0115`, producing the old baseline-SD effect of
`7.506`. Pooled-SD Hedges' g is `1.396`.

After removing the ceiling-sensitive learning metric from primary PSI:

| Condition | PSI |
|---|---:|
| `detailed` | 0.353 |
| `role_human` | 0.892 |
| `reward_loss_emphasis` | 0.880 |

The reward/loss PSI was previously `3.333`. The reduction confirms that the
old value was strongly inflated by the tiny baseline SD and by including the
ceiling-sensitive learning-change metric.

The paired bootstrap intervals remain very wide with three seeds. For
example, reward/loss `advantageous_choice_rate` Hedges' g is `1.396`, with a
diagnostic interval from `0.000` to `13.064`. These intervals are not formal
evidence.

## IGT Ceiling Effect

All three baseline runs began with block-1 net score `-4` and reached block-5
net score `20`. Two reward/loss runs started and remained at `20`.

Therefore:

- `learning_curve_change` gives `24` to baseline but `0` to immediate
  ceiling performance.
- `learning_slope` uses all five blocks but remains sensitive to the same
  ceiling structure.
- Both metrics are retained as supplementary descriptions and are not used in
  primary PSI.

## Horizon Stability

The Horizon model generated run-cluster intervals successfully. All 200
diagnostic bootstrap fits converged for every prompt condition.

| Condition | Point estimate | Diagnostic 95% interval | Shrinkage estimates |
|---|---:|---:|---|
| `baseline` | -1.863 | [-4.873, 0.368] | -2.193, -1.863, -1.365 |
| `detailed` | 0.647 | [-2.861, 3.679] | 0.493, 0.647, 0.343 |
| `role_human` | 0.184 | [-1.996, 1.539] | 0.147, 0.184, 0.283 |
| `uncertainty_emphasis` | 0.848 | [-3.657, 3.032] | 1.079, 0.848, 0.677 |

The condition-level direction is consistent across the three shrinkage
settings, but every bootstrap interval crosses zero and individual runs can
change direction. The implementation can produce intervals; the estimates
cannot yet be called stable with only three runs.

## Sampling Provenance

Raw API responses show:

```text
resolved model: gpt-4.1-2025-04-14
temperature: 1.0
top_p: 1.0
max_output_tokens: 16
```

The old runner omitted `temperature` and `top_p`, so the configured
`temperature=0.7` was not applied. The runner has now been corrected. A new
validation mini-pilot must use the frozen settings before formal runs begin.
