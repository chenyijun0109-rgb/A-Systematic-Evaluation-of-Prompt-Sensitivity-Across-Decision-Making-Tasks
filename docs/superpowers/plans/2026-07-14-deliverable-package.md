# Deliverable Package Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prepare a supervisor-review deliverable that keeps the repository reproducible while exposing only concise formal results.

**Architecture:** The main repository remains the source of code, prompts, configs, tests, and method documentation. A new `deliverable/` directory contains a small manifest and copied processed results from the completed formal experiment; raw runs, local datasets, credentials, and caches remain outside the deliverable view.

**Tech Stack:** PowerShell file operations, Python/uv validation commands, Markdown documentation, existing CSV/JSON analysis outputs.

---

### Task 1: Build Deliverable View

**Files:**
- Create: `deliverable/README_DELIVERABLE.md`
- Create: `deliverable/results/README.md`
- Copy: `outputs/processed/formal_v01/*` to `deliverable/results/formal_v01/`

- [ ] **Step 1: Create result directories**

Run:

```powershell
New-Item -ItemType Directory -Force deliverable\results\formal_v01
```

Expected: directory exists and no raw run JSON files are copied.

- [ ] **Step 2: Copy processed formal results**

Run:

```powershell
Copy-Item outputs\processed\formal_v01\aggregation_quality_report.json deliverable\results\formal_v01\ -Force
Copy-Item outputs\processed\formal_v01\analysis_summary.json deliverable\results\formal_v01\ -Force
Copy-Item outputs\processed\formal_v01\llm_run_metrics.csv deliverable\results\formal_v01\ -Force
Copy-Item outputs\processed\formal_v01\metric_summary.csv deliverable\results\formal_v01\ -Force
Copy-Item outputs\processed\formal_v01\prompt_effects.csv deliverable\results\formal_v01\ -Force
Copy-Item outputs\processed\formal_v01\prompt_sensitivity.csv deliverable\results\formal_v01\ -Force
```

Expected: six processed result files in `deliverable/results/formal_v01/`.

- [ ] **Step 3: Document included and excluded files**

Create `deliverable/README_DELIVERABLE.md` with the supervisor-facing package summary and `deliverable/results/README.md` with result-file meanings.

### Task 2: Update Current-State Documentation

**Files:**
- Modify: `README.md`
- Modify: `docs/research_log.md`
- Modify: `docs/next_steps_plan.md`

- [ ] **Step 1: Add README deliverable section**

Add a current-state section naming `deliverable/` as the supervisor-review entry point, with formal v01 completeness.

- [ ] **Step 2: Add research-log entry**

Append a dated entry describing the packaging decision and what was intentionally excluded.

- [ ] **Step 3: Update next steps**

Add the remaining handoff tasks and avoid shipping local process artifacts.

### Task 3: Verify Package

**Files:**
- Read: `deliverable/results/formal_v01/analysis_summary.json`
- Read: `deliverable/results/formal_v01/aggregation_quality_report.json`

- [ ] **Step 1: Check file count**

Run:

```powershell
Get-ChildItem deliverable\results\formal_v01 -File | Select-Object Name,Length
```

Expected: exactly six files.

- [ ] **Step 2: Check formal quality summaries**

Run:

```powershell
Get-Content -Raw deliverable\results\formal_v01\aggregation_quality_report.json
Get-Content -Raw deliverable\results\formal_v01\analysis_summary.json
```

Expected: `valid_run_count=240`, `analysis_complete=true`, and `issues=[]`.

- [ ] **Step 3: Run repository tests when time permits**

Run:

```powershell
uv run python -m unittest discover -s tests
```

Expected: all tests pass. If the local environment makes this impractical, report that the deliverable-file checks were run instead.
