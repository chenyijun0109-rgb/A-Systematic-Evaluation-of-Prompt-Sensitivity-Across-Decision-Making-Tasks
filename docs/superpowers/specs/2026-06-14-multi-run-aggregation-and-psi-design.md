# Multi-Run Aggregation and PSI Design

## Goal

Build a reproducible analysis pipeline that can read a completed multi-run LLM
experiment, validate its completeness, produce one row per run, and calculate
prompt-condition summaries, signed standardised effects, and the
project-defined Prompt Sensitivity Index (PSI).

The immediate target is the 36-run mini pilot:

```text
3 tasks x 4 prompt conditions x 3 paired environment seeds = 36 runs
```

The same pipeline must support the later formal experiment by changing the
expected run count rather than changing analysis code.

## Scope

This change includes:

- seed-specific pilot filenames so repeated runs do not overwrite each other;
- recursive discovery of completed and failed pilot JSON files;
- duplicate, missing-cell, failed-run, provenance, and metric validation;
- a flat run-level CSV;
- Horizon random-exploration estimation and run-level integration;
- condition-level descriptive summaries;
- signed standardised prompt effects;
- task-and-condition-level PSI;
- machine-readable quality and analysis reports;
- strict and explicitly enabled incomplete-analysis modes;
- tests and current-state documentation.

This change does not include:

- running the 36 API experiments;
- bootstrap confidence intervals;
- human-versus-LLM comparison;
- inferential hypothesis tests.

These remain later analysis stages. The mini pilot pipeline will preserve the
run and seed fields needed for them.

## Architecture

The pipeline has two stages.

### Stage 1: Aggregate Experiment Results

`src/aggregate_experiment_results.py` reads raw pilot JSON files and writes:

```text
outputs/processed/llm_run_metrics.csv
outputs/processed/aggregation_quality_report.json
```

The CSV contains one row per valid `task x prompt_condition x seed` run. The
quality report records all discovered files, exclusions, duplicates, missing
cells, failed runs, provenance inconsistencies, and warnings.

### Stage 2: Compute Prompt Sensitivity

`src/compute_prompt_sensitivity.py` reads `llm_run_metrics.csv` and writes:

```text
outputs/processed/metric_summary.csv
outputs/processed/prompt_effects.csv
outputs/processed/prompt_sensitivity.csv
outputs/processed/analysis_summary.json
```

This separation allows PSI to be recalculated without repeatedly parsing the
large raw response logs.

## Pilot Output Identity and Provenance

New successful and failed pilot filenames include the actual task seed:

```text
horizon_baseline_seed-20260601.json
horizon_baseline_seed-20260601_failed.json
```

The logical run key is:

```text
task + prompt_condition + seed
```

Each new pilot JSON also records:

- configuration name and version;
- prompt path;
- SHA-256 hash of the prompt template;
- model;
- task seed;
- prompt condition;
- completion status;
- parse-success information;
- run metrics.

Legacy pilot files without the seed suffix remain readable because identity is
derived from JSON content, not from the filename. Missing provenance fields are
reported as warnings for legacy files and as validation failures when strict
analysis requires provenance consistency.

## Discovery and Eligibility

The aggregation CLI accepts one or more files or directories and recursively
discovers JSON files.

A successful run is eligible when:

- `task` is one of `horizon`, `igt`, or `bart`;
- `prompt_condition` belongs to that task's configured condition list;
- `seed` is present;
- `done` is `true`;
- `run_metrics` is present;
- all required run-level metrics can be extracted;
- the run is not superseded by an explicitly selected duplicate policy.

Files that are unrelated JSON outputs are ignored and listed by reason. Failed
pilot files are detected and included in the quality report but never treated
as valid runs.

## Duplicate Policy

Duplicate runs have the same logical run key.

Default behavior:

```text
error
```

The aggregation stops and lists all conflicting files.

Optional behavior:

```text
--duplicate-policy latest
```

The newest successfully completed file by modification time is selected. The
quality report records every candidate and the selected file. Failed files
never replace a successful file under this policy.

## Completeness Modes

The expected number of valid runs per task-condition cell is supplied
explicitly:

```text
--expected-runs-per-cell 3
```

For the formal experiment this becomes `20`.

### Strict Mode

Strict mode is the default. Aggregation or PSI calculation stops when:

- a task-condition cell has fewer or more than the expected number of runs;
- paired seed sets differ across prompt conditions within a task;
- duplicate runs remain unresolved;
- a required PSI metric is missing;
- completed runs mix models, configuration versions, or prompt hashes within
  an analysis batch;
- a standardised effect is mathematically undefined.

### Incomplete Mode

`--allow-incomplete` excludes unusable runs or metrics, continues where the
remaining data are sufficient, and records every exclusion and warning.

Incomplete mode never silently fills data. Its outputs carry:

```text
analysis_complete = false
```

This prevents exploratory partial results from being mistaken for a complete
mini-pilot analysis.

## Run-Level Metric Table

Common columns:

```text
run_id
task
prompt_condition
model
seed
config_name
config_version
prompt_path
prompt_sha256
done
n_trials
parse_success_rate
invalid_response_count
source_path
```

The table also contains the union of numeric behavioral metrics. Metrics not
applicable to a task are blank.

Derived metrics include:

- Horizon `random_exploration_effect`;
- IGT `learning_curve_change`, defined as block 5 net score minus block 1 net
  score.

Nested structures such as the complete IGT block-wise learning curve are not
stored as PSI inputs. The source JSON remains the canonical detailed record.

## Horizon Random Exploration Integration

`random_exploration_effect` is not taken from the old behavioral proxy. It is
estimated from first-free-choice data using the existing hierarchical logistic
choice model.

For each Horizon prompt condition:

1. collect all eligible runs;
2. fit the condition jointly with run-level shrinkage;
3. require optimizer convergence;
4. match each model `run_id` back to its source run;
5. add each run's
   `decision_noise_h6 - decision_noise_h1` estimate to the run-level table.

With only one eligible run, the model cannot produce the required hierarchical
estimate. Strict mode fails; incomplete mode records the condition as
insufficient and leaves the metric missing.

## PSI Metric Set

The primary PSI metrics are fixed before the mini pilot:

| Task | Metrics |
|---|---|
| Horizon | `directed_exploration`, `horizon_effect`, `random_exploration_effect` |
| IGT | `advantageous_choice_rate`, `learning_curve_change`, `post_loss_switching_rate` |
| BART | `adjusted_average_pumps`, `explosion_rate`, `post_explosion_adjustment` |

Each task contributes three metrics so tasks are not implicitly weighted by the
number of available measures. Outcome metrics and strongly redundant metrics
remain available in the run table and summary table but do not enter primary
PSI.

The metric lists are stored in the experiment configuration and read by the
analysis code rather than duplicated as hidden constants.

## Descriptive Aggregation

For every `task x prompt_condition x metric`, calculate:

- valid run count;
- mean;
- sample standard deviation using `n - 1`;
- median;
- minimum;
- maximum.

The summary preserves the seed count and expected run count. A condition with
fewer than two valid values cannot provide a sample standard deviation.

## Standardised Prompt Effects

For task \(t\), non-baseline condition \(c\), and primary metric \(m\):

\[
E_{tcm} =
\frac{\bar{x}_{tcm}-\bar{x}_{t,\mathrm{baseline},m}}
{s_{t,\mathrm{baseline},m}}
\]

Each effect row reports:

- condition mean;
- baseline mean;
- raw mean difference;
- condition SD;
- baseline SD;
- denominator value;
- denominator source;
- signed standardised effect;
- absolute standardised effect;
- warning flags.

Baseline rows are not assigned PSI effects against themselves.

## Zero and Low Variance Rules

Use a numerical zero tolerance of `1e-12`.

1. If baseline SD is greater than the tolerance, use baseline SD.
2. If baseline SD is zero and pooled SD is nonzero, use:

\[
s_{\mathrm{pooled}} =
\sqrt{\frac{s^2_{\mathrm{baseline}}+s^2_{\mathrm{condition}}}{2}}
\]

   and mark `sd_source=pooled_fallback`.
3. If both SDs are zero and the means are equal, set the effect to zero and
   mark `sd_source=constant_equal`.
4. If both SDs are zero and the means differ, the standardised effect is
   undefined. Strict mode stops. In incomplete mode the metric is excluded from
   PSI and reported.
5. A positive but very small baseline SD is not automatically replaced.
   Instead, the result receives a `low_baseline_variance` warning. For
   scale-free metrics bounded to `[0, 1]`, the warning threshold is `1e-6`.
   Other metrics are warned when the denominator is within `1e-6` of the
   larger absolute group mean, after protecting zero with a scale of one.

The warning is diagnostic and does not alter the effect formula.

## PSI Calculation

For task \(t\) and manipulated prompt condition \(c\):

\[
\mathrm{PSI}_{tc}
=
\frac{1}{M_t}
\sum_{m=1}^{M_t}|E_{tcm}|
\]

The output contains one row per task and manipulated condition with:

- the three expected primary metrics;
- number of valid effects;
- arithmetic mean of absolute effects;
- completeness status;
- excluded metric names;
- warning flags.

Strict mode requires all three metrics. In incomplete mode PSI is calculated
only when at least two of the three effects are valid, is marked partial, and
reports the reduced denominator. A one-metric value is not labelled PSI.

PSI is a project-defined descriptive composite, not a validated psychological
scale. Signed effects remain the primary directional result.

## Paired Seeds

The same three environment seeds must appear under all four prompt conditions
within each task. Aggregation validates this pairing and preserves seed in all
outputs.

The current PSI point estimate follows the preregistered group-mean and
baseline-SD formula. Pairing is not substituted into that denominator.
Preserving pairing allows later paired confidence intervals and hypothesis
tests without changing raw aggregation.

## CLI

Aggregation:

```powershell
python -m src.aggregate_experiment_results outputs/mini_pilot `
  --expected-runs-per-cell 3 `
  --output-dir outputs/processed/mini_pilot
```

Explicit incomplete and duplicate handling:

```powershell
python -m src.aggregate_experiment_results outputs/mini_pilot `
  --expected-runs-per-cell 3 `
  --duplicate-policy latest `
  --allow-incomplete `
  --output-dir outputs/processed/mini_pilot
```

PSI:

```powershell
python -m src.compute_prompt_sensitivity `
  outputs/processed/mini_pilot/llm_run_metrics.csv `
  --expected-runs-per-cell 3 `
  --output-dir outputs/processed/mini_pilot
```

The PSI command also supports `--allow-incomplete`.

## Error Reporting

CLI errors are concise and point to the quality report when one has been
written. JSON reports contain stable machine-readable issue codes, including:

```text
duplicate_run
missing_run
unexpected_run
unpaired_seed
failed_run
missing_metric
mixed_model
mixed_config_version
mixed_prompt_hash
random_exploration_not_converged
zero_variance_undefined_effect
low_baseline_variance
partial_psi
```

## Testing

Tests use small synthetic JSON and CSV fixtures and do not call the API.

Aggregation tests cover:

- one row per logical run;
- recursive discovery;
- legacy filename support;
- failed-run exclusion;
- strict missing-cell failure;
- incomplete-mode warnings;
- duplicate default failure;
- latest duplicate selection;
- paired-seed validation;
- model and provenance inconsistency;
- IGT learning-curve derivation;
- Horizon model estimates merged by run.

PSI tests cover:

- known means and sample SDs;
- signed and absolute effect direction;
- equal weighting across three metrics;
- baseline-SD denominator;
- pooled fallback;
- constant equal groups;
- undefined constant unequal groups;
- strict missing-metric failure;
- partial PSI in incomplete mode;
- deterministic output ordering.

Existing full tests remain part of final verification.

## Documentation

The implementation change updates:

- `README.md` with mini-pilot run naming and complete analysis commands;
- `configs/experiment_config_stage01.json` with primary PSI metric lists and
  variance rules;
- `docs/data_schema.md` with the run-level and PSI schemas;
- `docs/research_log.md` with implementation and verification evidence;
- `docs/next_steps_plan.md` with completion status.

This follows the repository rule that method, metric, command, output-schema,
and workflow changes update README in the same change.
