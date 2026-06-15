# Canonical Baseline Prompts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and verify three literature-grounded canonical baselines and remove Horizon analysis-label leakage from participant-facing observations.

**Architecture:** The prompt files contain only stable participant instructions and one `{observation}` placeholder. Task environments provide changing state. Automated tests enforce that Horizon state is participant-facing and that every baseline remains parser-compatible.

**Tech Stack:** Python 3, `unittest`, Markdown prompts, JSON configuration

---

### Task 1: Protect the Horizon participant interface

**Files:**
- Modify: `tests/test_horizon.py`
- Modify: `src/tasks/horizon.py`

- [ ] Add a test asserting that the initial observation contains the correct
  remaining-choice count and does not expose `horizon_1`, `horizon_6`,
  `equal_information`, or `unequal_information`.
- [ ] Run `uv run python -m unittest tests.test_horizon` and confirm the new
  assertion fails because the existing observation exposes analysis labels.
- [ ] Replace the two analysis-label lines in `get_observation()` with
  `Choices remaining in this game: {remaining}`.
- [ ] Run `uv run python -m unittest tests.test_horizon` and confirm it passes.

### Task 2: Create the three canonical baselines

**Files:**
- Create: `prompts/bandit/baseline.md`
- Create: `prompts/igt/baseline.md`
- Create: `prompts/bart/baseline.md`
- Create: `docs/baseline_prompt_source_map.md`

- [ ] Write the Horizon baseline with 40 games, four forced choices, one or
  six free choices, unknown option patterns, neutral total-reward objective,
  `{observation}`, and exact `CHOICE` outputs.
- [ ] Write the IGT baseline with 100 trials, starting score 2000, unknown deck
  gain/loss patterns, feedback, `{observation}`, and exact `CHOICE` outputs.
- [ ] Write the BART baseline with 40 balloons, 0.05 per successful pump,
  pump/explosion/cash-out rules, `{observation}`, and exact `ACTION` outputs.
- [ ] Record literature basis, dataset confirmation, implementation
  adaptation, participant-visible facts, and hidden facts in the source map.

### Task 3: Verify baseline content and parser compatibility

**Files:**
- Modify: `tests/test_prompt_dry_run.py`

- [ ] Add assertions that each baseline contains exactly one `{observation}`.
- [ ] Add assertions that all three contain the neutral total-reward objective.
- [ ] Add task-specific assertions for `40 games`, `100 choices`, starting
  score `2000`, `40 balloons`, and `0.05`.
- [ ] Add forbidden-content assertions for canonical task names, behavioural
  metrics, IGT deck-value disclosure, and BART hidden explosion parameters.
- [ ] Run `uv run python -m unittest tests.test_prompt_dry_run` and confirm all
  checks pass against the new prompt files.
- [ ] Run
  `uv run python -m src.run_prompt_dry_run --seed 20260528 --output-path outputs/debug/prompt_dry_run/canonical_baselines.json`
  and confirm all placeholders are replaced and all legal outputs parse.

### Task 4: Freeze provenance and update current-state documentation

**Files:**
- Modify: `configs/experiment_config_stage01.json`
- Modify: `prompts/generation/current_prompt_provenance.md`
- Modify: `README.md`
- Modify: `docs/research_log.md`

- [ ] Update configuration status to state that canonical baselines are
  restored while nine generated variants remain pending.
- [ ] Mark the three baseline inventory rows as manually constructed
  canonical baselines and leave the nine variant rows pending generation.
- [ ] Update README prompt status, project tree, and next steps.
- [ ] Record the baseline reconstruction and Horizon interface change in the
  research log.

### Task 5: Full verification

**Files:**
- Verify all modified files

- [ ] Run `uv run python -m unittest discover -s tests`.
- [ ] Run `git diff --check`.
- [ ] Confirm no newly created baseline uses a canonical task name, analysis
  label, behavioural metric, or hidden task parameter.

