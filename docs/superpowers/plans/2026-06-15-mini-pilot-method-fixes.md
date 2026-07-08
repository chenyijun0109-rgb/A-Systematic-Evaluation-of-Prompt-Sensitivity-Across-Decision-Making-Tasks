# Mini-Pilot Method Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Correct the methodological issues exposed by the 36-run mini-pilot and produce a reproducible, frozen configuration for the validation rerun and formal experiment.

**Architecture:** Keep raw task execution, run aggregation, and prompt-sensitivity analysis as separate stages. Add requested and resolved sampling provenance to raw outputs, derive IGT trajectory metrics during aggregation, calculate descriptive Hedges' g and paired-seed bootstrap intervals in the PSI stage, and add run-cluster bootstrap plus shrinkage sensitivity to the Horizon model. Record the final prompts, parameters, metrics, and exclusion rules in a machine-readable freeze manifest.

**Tech Stack:** Python standard library, NumPy, SciPy, unittest, JSON/CSV, Markdown.

---

### Task 1: Freeze Sampling Parameters in Raw Outputs

**Files:**
- Modify: `src/run_llm_pilot.py`
- Modify: `tests/test_llm_pilot.py`
- Modify: `configs/experiment_config_stage01.json`

- [ ] **Step 1: Write failing tests**

Add tests asserting that `run_llm_pilot` passes `temperature=0.7` and
`top_p=1.0` to the client and writes the requested settings plus the resolved
API model and sampling settings into each completed or failed JSON result.

- [ ] **Step 2: Verify the tests fail**

Run:

```powershell
uv run python -m unittest tests.test_llm_pilot -v
```

Expected: failures because `PilotClient` and raw result provenance currently
omit sampling parameters.

- [ ] **Step 3: Implement the sampling provenance**

Extend `PilotClient.create_response`, `run_llm_pilot`, and `_run_single_task`
with explicit `temperature` and `top_p`. Use config values by default, send
them on every API call, and record:

```text
requested_model
resolved_model
temperature
top_p
max_output_tokens
```

The resolved values must be read from the first raw API response rather than
inferred from the request.

- [ ] **Step 4: Verify the tests pass**

Run the same unittest command and expect all tests to pass.

### Task 2: Replace IGT Primary Learning Metric with Supplementary Trajectory Metrics

**Files:**
- Modify: `src/aggregate_experiment_results.py`
- Modify: `tests/test_aggregate_experiment_results.py`
- Modify: `tests/test_prompt_sensitivity.py`
- Modify: `configs/experiment_config_stage01.json`

- [ ] **Step 1: Write failing tests**

Add tests asserting that aggregation derives `learning_slope` from all five
block net scores by ordinary least squares, retains
`learning_curve_change`, and that the configured IGT primary PSI metrics are:

```text
advantageous_choice_rate
post_loss_switching_rate
```

- [ ] **Step 2: Verify the tests fail**

Run:

```powershell
uv run python -m unittest tests.test_aggregate_experiment_results tests.test_prompt_sensitivity -v
```

Expected: failures because `learning_slope` is absent and
`learning_curve_change` is still primary.

- [ ] **Step 3: Implement the derived metric and configuration**

Calculate the slope for block indices `1..5`. Keep `learning_slope`,
`learning_curve_change`, and the full curve as supplementary trajectory
outputs. Do not interpret a zero slope as poor performance.

- [ ] **Step 4: Verify the tests pass**

Run the same unittest command and expect all tests to pass.

### Task 3: Add Hedges' g and Paired-Seed Bootstrap Intervals

**Files:**
- Modify: `src/compute_prompt_sensitivity.py`
- Modify: `tests/test_prompt_sensitivity.py`

- [ ] **Step 1: Write failing tests**

Add tests for:

```text
pooled sample SD with unequal group sizes
Hedges small-sample correction
undefined effect when both groups are constant but unequal
paired bootstrap resampling of complete seed pairs
reproducible percentile confidence intervals with a fixed bootstrap seed
```

- [ ] **Step 2: Verify the tests fail**

Run:

```powershell
uv run python -m unittest tests.test_prompt_sensitivity -v
```

Expected: failures because the analysis currently reports only a Glass-like
baseline-SD effect and has no bootstrap output.

- [ ] **Step 3: Implement descriptive effect outputs**

Use Hedges' g as the primary standardized effect:

```text
g = J * (condition_mean - baseline_mean) / pooled_sample_sd
```

Retain the raw mean difference and the previous baseline-SD effect as a named
sensitivity result. Bootstrap complete baseline-condition seed pairs and
write 95% percentile intervals for raw differences, Hedges' g where defined,
and PSI.

- [ ] **Step 4: Verify the tests pass**

Run the same unittest command and expect all tests to pass.

### Task 4: Add Horizon Run-Cluster Bootstrap and Shrinkage Diagnostics

**Files:**
- Modify: `src/horizon_random_exploration.py`
- Modify: `tests/test_horizon_random_exploration.py`
- Modify: `src/aggregate_experiment_results.py`

- [ ] **Step 1: Write failing tests**

Using synthetic observations, add tests that:

```text
resample whole runs rather than individual choices
return percentile intervals for decision_noise_h1, decision_noise_h6,
  and random_exploration_effect
report requested replicates, successful fits, and convergence rate
produce reproducible output with a fixed seed
compare run_effect_sd values 0.25, 0.50, and 1.00
```

- [ ] **Step 2: Verify the tests fail**

Run:

```powershell
uv run python -m unittest tests.test_horizon_random_exploration -v
```

Expected: failures because bootstrap and sensitivity APIs do not exist.

- [ ] **Step 3: Implement diagnostics**

Resample run IDs with replacement while preserving every selected run's
internal choices. Relabel duplicate sampled clusters so the hierarchical
model treats them as separate bootstrap clusters. Report intervals only when
enough fits converge; for the three-run mini-pilot label intervals
`diagnostic_only`.

- [ ] **Step 4: Verify the tests pass**

Run the same unittest command and expect all tests to pass.

### Task 5: Create the Formal Experiment Freeze Manifest

**Files:**
- Create: `configs/formal_experiment_freeze.json`
- Create: `docs/formal_experiment_freeze.md`
- Modify: `docs/research_log.md`
- Modify: `README.md`
- Test: `tests/test_prompt_sensitivity.py`

- [ ] **Step 1: Write a failing manifest test**

Assert that the manifest contains:

```text
12 prompt paths and SHA-256 hashes
requested and resolved model policy
temperature, top_p, and max_output_tokens
task parameters
primary and supplementary metrics
Horizon model and bootstrap settings
technical-only run exclusion rules
human-data exclusion rules
```

- [ ] **Step 2: Verify the test fails**

Run:

```powershell
uv run python -m unittest tests.test_prompt_sensitivity -v
```

Expected: failure because the manifest does not exist.

- [ ] **Step 3: Generate and document the manifest**

Hash the final prompt files, freeze the validated settings, and state that
behavioral extremity, zero variance, or an unexpected cognitive-model
estimate are not exclusion criteria. Update README in the same change with
the current commands, metrics, provenance fields, and validation-rerun
status.

- [ ] **Step 4: Verify JSON and documentation**

Run:

```powershell
uv run python -m json.tool configs/formal_experiment_freeze.json
uv run python -m unittest discover -s tests -v
git diff --check
```

Expected: valid JSON, all tests passing, and no whitespace errors.

### Task 6: Regenerate Mini-Pilot Analysis Without New API Calls

**Files:**
- Regenerate: `outputs/processed/mini_pilot_v01/*`
- Create: `docs/mini_pilot_method_diagnostics.md`
- Modify: `README.md`
- Modify: `docs/research_log.md`

- [ ] **Step 1: Re-run aggregation and analysis**

Use the existing 36 raw JSON files to regenerate run metrics, Hedges' g,
paired intervals, IGT supplementary trajectories, and Horizon diagnostics.

- [ ] **Step 2: Inspect diagnostics**

Confirm that the previous IGT `7.51` baseline-SD effect is retained only as a
sensitivity value, while Hedges' g and its interval are the primary
standardized result. Report Horizon mini-pilot intervals as diagnostic only.

- [ ] **Step 3: Run final verification**

Run:

```powershell
uv run python -m unittest discover -s tests -v
uv run python -m json.tool configs/experiment_config_stage01.json
uv run python -m json.tool configs/formal_experiment_freeze.json
git diff --check
```

Expected: all tests and validation commands pass.
