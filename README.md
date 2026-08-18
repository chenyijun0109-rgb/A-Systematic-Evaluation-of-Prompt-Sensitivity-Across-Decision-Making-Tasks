# How Reliable Are LLMs as Cognitive Models?

*A Systematic Evaluation of Prompt Sensitivity Across Decision-Making Tasks*

MSc Informatics dissertation project, School of Informatics, University of
Edinburgh (2026). This repository contains the reproducible research package
for a systematic evaluation of prompt sensitivity in large language models
(LLMs) on three sequential decision-making tasks: the Horizon Task
(exploration–exploitation), the Iowa Gambling Task (IGT; feedback-based
learning), and the Balloon Analogue Risk Task (BART; sequential risk-taking).

## Overview

The study compares four frozen prompt formulations — Neutral baseline,
Instruction specificity, Role framing, and Task-specific construct emphasis —
while holding task rules, actions, feedback, and hidden-information boundaries
constant:

- English three-model comparison: GPT-4.1, GPT-5.4, and GPT-5.4 Mini.
- Fixed-model multilingual comparison: GPT-4.1 in English, Simplified Chinese,
  and Spanish.
- 20 complete runs per model–language–task–prompt cell, 1,200 unique valid
  task runs in total.
- Uncertainty is represented by 2,000 task-appropriate bootstrap replicates;
  human-reference proximity is reported descriptively (human-SD-scaled mean
  deviation and empirical-interval coverage).

Headline findings (all numbers verifiable in
`outputs/processed/final_analysis_v03/`):

- RQ1: 29/72 within-model prompt-effect intervals excluded zero; no formulation
  ranked consistently across models, tasks, or metrics.
- RQ2: 19/48 model-by-prompt interaction intervals excluded zero; cross-model
  differences were localised rather than pervasive.
- RQ3: 15/24 centred three-language baselines and 31/72 centred prompt effects
  excluded zero.
- RQ4 (descriptive): absolute mean deviation and empirical coverage moved in
  opposite directions in 49/120 cells.

Behavioural similarity to human data is treated as a diagnostic coordinate, not
as evidence of shared cognitive mechanisms.

## Manuscript

- `skeleton_repaired.tex` (with `mybibfile.bib`) is the authoritative manuscript
  source. The 2026-08-12 `dissertation.pdf` was compiled from it inside the
  University's official `infthesis`/`msccheck` Overleaf template. The template
  class files are not included in this repository.
- `docs/final_overleaf_figure_manifest.md` lists the figure files that must be
  uploaded for compilation.
- The appendix of `skeleton_repaired.tex` reproduces all 36 frozen prompts
  verbatim (English, Simplified Chinese, Spanish) and includes a terminology
  mapping table (thesis terms, code identifiers, and three-language glosses).
  Compiling it requires the `CJKutf8` package (already declared in the
  preamble).

## Repository layout

```text
configs/    frozen experiment configurations and prompt-hash manifests
prompts/    frozen prompt files (English, Simplified Chinese, Spanish) and
            generation/audit records
src/        task environments, runners, parsers, and analysis modules
scripts/    collection and packaging launchers
tests/      unit tests (task environments, parsing, metrics, prompts)
outputs/    processed results and figures (see "Results package")
docs/       methodology, schema notes, research log, and writing records
PROJECT/    submission-archive README (kept out of version control)
```

## Tasks and parameters

The three tasks and their frozen parameters are specified in
`configs/experiment_config_stage01.json` and
`configs/formal_experiment_freeze.json`:

| Task | Implementation used here |
| --- | --- |
| Horizon Task | 40 two-option games per run; 4 forced choices then 1 or 6 free choices (H1/H6); latent means anchored at 40/60 with reward SD 8, integer-rounded and clipped to [1, 100]; 10 mean-difference levels; equal (2v2) and unequal (1v3) information conditions in balanced order. |
| Iowa Gambling Task | 100 choices from an initial 2,000 points; classic repeating 10-selection payoff schedule (A/B net −250 and C/D +250 per cycle); A/C frequent losses, B/D rarer larger losses. |
| BART | 40 balloons in two blocks; +0.05 per successful pump; explosion probability 1/(33−k) at pump k, certain at pump 32. |

## Models and configuration

Models were accessed through the University of Edinburgh ELM platform's
OpenAI-compatible Responses API. Generation settings were `temperature=0.7`,
`top_p=1.0`, and `max_output_tokens=16`. GPT-5.4 and GPT-5.4 Mini used
`reasoning_effort=none`; GPT-4.1 used its standard non-reasoning
configuration. Formal collection dates (Asia/Shanghai, from run records):

| Model | Scope | Resolved identifier | Collection dates |
| --- | --- | --- | --- |
| GPT-4.1 | English | gpt-4.1-2025-04-14 | 2026-07-08 – 07-13 |
| GPT-5.4 | English | gpt-5.4-2026-03-05 | 2026-07-30 – 07-31 |
| GPT-5.4 Mini | English | gpt-5.4-mini-2026-03-17 | 2026-08-01 |
| GPT-4.1 | Chinese (zh-CN) | gpt-4.1-2025-04-14 | 2026-08-03 – 08-05 |
| GPT-4.1 | Spanish (es) | gpt-4.1-2025-04-14 | 2026-08-05 – 08-07 |

## Prompts

36 frozen prompt files (3 tasks × 4 conditions × 3 languages) live under
`prompts/`. Prompt provenance and generation records are under
`prompts/generation/`; multilingual construction and audit records are under
`prompts/multilingual/`. Prompt hashes are pinned in
`configs/formal_experiment_freeze.json` and
`configs/multilingual_experiment_freeze_v01.json`.

## Human reference data

Three existing public datasets provide descriptive, non-normative references.
They are not included in this repository; the processing pipeline and outputs
are:

- Horizon: Feng et al. (2021), *Scientific Reports* 11:3077 — 60 participants,
  320 games each. Local record: `DATASET/BANDIT/` (kept locally).
- IGT: Steingroever et al. (2015), *Journal of Open Psychology Data* 3(1):e5 —
  504 participants with 100 complete trials from the 617-participant pool.
  Local record: `DATASET/IGT/` (kept locally).
- BART: Sebri et al. (2023), *Journal of Cognitive Psychology* 35(3):340–354 —
  141 adults after excluding six minors; 140 contribute the post-explosion
  adjustment metric. Local record: `DATASET/BART/` (kept locally).

Participant-level human summaries are in `outputs/processed/human_metrics/`;
participant-level bootstrap uncertainty is in
`outputs/processed/final_analysis_v03/human_reference_results/`. Run-level
bootstrap intervals for the RQ4 prompt-associated changes (seven directly
computed metrics) are in
`human_reference_results/model_human_distance_changes_bootstrap.csv`.

## Results package

`outputs/processed/final_analysis_v03/` is the authoritative analysis package.
`analysis_manifest.json` records file hashes, expected row counts,
bootstrap-validity checks, aggregation completeness, and Random-exploration
convergence. All publication figures are in the top-level `figures/` directory.

## Reproducibility

Python environment: `uv sync` (see `pyproject.toml` / `uv.lock`).

Run the test suite:

```powershell
python -m unittest discover
```

Key entry points:

```text
python -m src.run_random_baseline --seed 20260528 --output-dir outputs/debug/random_baseline
python -m src.run_prompt_dry_run --all-languages --seed 20260528
python -m src.process_human_metrics --output-dir outputs/processed/human_metrics
python -m src.horizon_random_exploration ...            # hierarchical fit
python -m src.aggregate_experiment_results ...          # run-level metrics
python -m src.compute_prompt_sensitivity ...            # RQ1 effects and PSI
python -m src.compare_model_results ...                 # RQ2 interactions
python -m src.compute_joint_language_contrasts ...      # RQ3 centred contrasts
python -m src.compare_model_human_results ...           # RQ4 human reference
python -m src.build_human_reference_uncertainty ...     # reference bootstrap
python -m src.build_final_analysis_manifest ...         # validates the package
python -m src.build_results_visual_package ...          # Results figures
```

Raw LLM run outputs and the human datasets are kept locally (not committed);
the repository contains prompts, code, configs, tests, processed results, and
figures. Collection launchers are under `scripts/`.

## Ethics

No human participants were recruited or contacted. The study used existing
published datasets only; no Informatics Research Ethics committee approval was
required.

## Submission archive

For the School's electronic submission, a separate `PROJECT/` archive is
prepared with its own README (`PROJECT/README.md`). It contains source, scripts,
configs, prompts, tests, the processed analysis package, and documentation,
and it records where the raw data came from and how outputs are regenerated.

## Links

- Repository: https://github.com/chenyijun0109-rgb/A-Systematic-Evaluation-of-Prompt-Sensitivity-Across-Decision-Making-Tasks
