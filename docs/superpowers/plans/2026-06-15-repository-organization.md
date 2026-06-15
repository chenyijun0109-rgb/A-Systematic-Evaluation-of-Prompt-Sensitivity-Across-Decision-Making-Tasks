# Repository Organization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prepare a concise, reproducible, and privacy-conscious GitHub repository.

**Architecture:** Keep code, prompts, configuration, and current research documentation in Git. Keep secrets, licensed datasets, generated run outputs, and local tool state outside Git while documenting how those local assets are restored and regenerated.

**Tech Stack:** Git, Markdown, Python, PowerShell

---

### Task 1: Define the Git boundary

**Files:**
- Modify: `.gitignore`

- [ ] Add Python, environment, editor, OS, dataset, output, local-tool, and private-document ignore rules.
- [ ] Verify ignored local assets with `git check-ignore -v`.
- [ ] Verify source, tests, prompts, configs, `.env.example`, and current docs are not ignored.

### Task 2: Remove superseded documentation

**Files:**
- Delete: `docs/pilot_results_only.md`
- Delete: `docs/supervisor_meeting_simulation.md`
- Delete: `docs/superpowers/plans/2026-06-07-feedback-driven-progress-presentation.md`
- Delete: `docs/superpowers/specs/2026-06-07-feedback-driven-progress-presentation-design.md`

- [ ] Delete only the approved duplicate and temporary documents.
- [ ] Search the repository for references to the deleted paths.
- [ ] Preserve substantive history in `docs/research_log.md`.

### Task 3: Repair current documentation

**Files:**
- Modify: `README.md`
- Modify: `docs/citation_map.md`
- Modify: `docs/next_steps_plan.md`
- Modify: `docs/research_log.md`

- [ ] Remove stale document references and update the repository tree.
- [ ] Add the local data and generated-output policy to the README.
- [ ] Replace links to missing historical files with current sources or clear historical notes.
- [ ] Record the repository cleanup in the research log.

### Task 4: Validate the GitHub-ready repository

**Files:**
- Verify only

- [ ] Run `git check-ignore` against local-only and trackable paths.
- [ ] Search trackable text for likely API keys and private-key markers.
- [ ] Run a repository-local Markdown path check.
- [ ] Run `git diff --check`.
- [ ] Run `python -m unittest discover`.
- [ ] Review `git status --short` and the final file-size distribution.
