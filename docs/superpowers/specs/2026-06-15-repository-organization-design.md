# Repository Organization Design

**Date:** 2026-06-15
**Status:** Approved
**Scope:** Prepare the project for GitHub while preserving reproducibility and research history

## Goal

Create a clean GitHub repository that stores the reproducible project source
without publishing local secrets, licensed human datasets, or large generated
experiment outputs.

## Repository Boundary

Git tracks:

- source code, tests, configuration, and dependency lock files;
- prompt files and prompt-generation provenance;
- current research specifications and methodological records;
- `README.md`, `AGENTS.md`, and `.env.example`;
- concise analysis documents that are still referenced by the current project.

Git ignores but does not delete locally:

- `.env` and other local secret files;
- `.venv/`, Python caches, test caches, and build artifacts;
- `DATASET/`, because redistribution rights and participant-data constraints
  must be checked separately;
- `outputs/`, because raw runs are large and reproducible from the documented
  commands;
- `.superpowers/`, editor settings, and operating-system metadata;
- local proposal PDFs that may contain personal or assessment information.

## Documentation Organization

The documentation has three roles:

1. `README.md` is the current-state entry point.
2. `docs/research_log.md` preserves detailed methodological history.
3. Focused documents under `docs/` define current methods, schemas, prompts,
   preprocessing, analysis, citations, and next steps.

Delete documents only when they are duplicated, temporary, or superseded and
their useful evidence is already preserved elsewhere. For this cleanup:

- remove `docs/pilot_results_only.md` because
  `docs/pilot_rerun_average_metrics_analysis.md` supersedes the single-run
  summary;
- remove `docs/supervisor_meeting_simulation.md` because it is meeting
  rehearsal material rather than a current project specification;
- remove the completed presentation-only design and plan from
  `docs/superpowers/`.

Keep implementation and methodology plans that explain current experimental
decisions, even when their implementation is complete.

## README Changes

Update the README in the same change to:

- list only current documents;
- explain that datasets and generated outputs are local-only by default;
- document expected local paths and reproduction commands;
- remove references to deleted or missing historical documents;
- reflect the cleaned repository layout.

## Validation

The cleanup is acceptable when:

- `.env`, `.venv/`, `DATASET/`, `outputs/`, `.superpowers/`, and the local
  proposal PDF are ignored;
- `.env.example`, source code, tests, prompts, configs, and current docs remain
  trackable;
- no current README link points to a removed or missing project file;
- no likely API key is present in trackable text files;
- `git diff --check` reports no whitespace errors;
- the existing unit test suite still passes.
