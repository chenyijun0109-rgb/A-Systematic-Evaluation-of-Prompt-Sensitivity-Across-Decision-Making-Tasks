# Prompt Isolation and Reproducibility Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tighten the nine generated prompt variants into controlled single-factor manipulations and document the complete generation and review chain.

**Architecture:** Keep the three canonical baselines and all raw API outputs unchanged. Treat final prompt files as reviewed derivatives: detailed prompts may reorganise existing facts, role prompts add only one explicit human-participant framing sentence, and task-specific prompts replace only one authorised baseline paragraph.

**Tech Stack:** Markdown prompt files, Python `unittest`, JSON configuration, SHA-256 file hashes.

---

### Task 1: Lock Manipulation Isolation in Tests

**Files:**
- Modify: `tests/test_prompt_dry_run.py`

- [ ] Add tests requiring the baseline objective sentence in all 12 prompts.
- [ ] Add tests proving each role prompt becomes byte-identical to its baseline after removing the one authorised role sentence.
- [ ] Add tests proving each task-specific prompt becomes byte-identical to its baseline after restoring its one authorised paragraph.
- [ ] Run `uv run python -m unittest tests.test_prompt_dry_run` and verify failure against the current prompts.

### Task 2: Optimise the Nine Final Prompts

**Files:**
- Modify: `prompts/bandit/detailed.md`
- Modify: `prompts/bandit/role_human.md`
- Modify: `prompts/bandit/uncertainty_emphasis.md`
- Modify: `prompts/igt/detailed.md`
- Modify: `prompts/igt/role_human.md`
- Modify: `prompts/igt/reward_loss_emphasis.md`
- Modify: `prompts/bart/detailed.md`
- Modify: `prompts/bart/role_human.md`
- Modify: `prompts/bart/risk_emphasis.md`

- [ ] Restore the exact neutral baseline objective in all nine variants.
- [ ] Make each role prompt equal to baseline plus `Take the role of a human participant completing this task.`.
- [ ] Make each emphasis prompt equal to baseline except for one authorised paragraph.
- [ ] Keep detailed prompts explanatory but fact-equivalent.
- [ ] Run the focused tests and verify they pass.

### Task 3: Create the Reproducibility Record

**Files:**
- Create: `docs/prompt_generation_and_review_record.md`
- Modify: `docs/prompt_generation_protocol.md`
- Modify: `prompts/generation/records/2026-06-14_gpt-4o-2024-11-20/final_review.md`

- [ ] Record the exact historical meta-prompt file and explain the per-task substitutions.
- [ ] Record model, API, date, `temperature=0.0`, `top_p=1.0`, token limit, and candidate count.
- [ ] Link the three exact rendered requests and raw responses.
- [ ] Record every first-review and second-review edit without changing raw outputs.
- [ ] Record final prompt paths and updated hashes.

### Task 4: Synchronise Project Status

**Files:**
- Modify: `README.md`
- Modify: `prompts/generation/current_prompt_provenance.md`
- Modify: `docs/research_log.md`
- Modify: `configs/experiment_config_stage01.json`

- [ ] Mark the prompt matrix as reviewed under the stricter isolation audit.
- [ ] Link the new reproducibility record.
- [ ] State that prior pilot outputs cannot be pooled with the revised prompt version.

### Task 5: Verify

**Files:**
- Regenerate: `outputs/debug/prompt_dry_run/prompt_matrix_dry_run.json`

- [ ] Run the 12-prompt matrix dry run.
- [ ] Run `uv run python -m unittest discover -s tests`.
- [ ] Validate configuration and generation-record JSON files.
- [ ] Run `git diff --check`.
- [ ] Recompute and verify all 12 SHA-256 hashes.
