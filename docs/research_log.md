# Research Log

## 2026-08-08: Complete manuscript formula and subscript audit

- Checked all 26 display equations against the implemented task and analysis
  code and verified balanced delimiters and braces.
- Added the participant/run index to the direct Horizon effect and retained the
  H6-minus-H1 direction used by preprocessing.
- Removed nested display-math environments from the Horizon reward and BART
  hazard equations without changing their definitions.
- Aligned the Hedges' g zero-variance text with the frozen operational rule:
  equal constant groups use `g=0`; unequal constant groups are undefined.
- Defined human-reference coverage over non-missing metric values, documented
  linear quantile interpolation, and replaced ambiguous `Delta|D|` notation
  with `Delta^abs`.
- Stated the zero-human-SD boundary for human-standardised distances.

Status: manuscript formulas, notation, edge cases, and code are aligned; 54
targeted tests pass.

## 2026-08-08: Verify IGT signs and Horizon metric parameterisation

- Confirmed that LLM and human IGT loss fields use zero or negative signed
  values and that post-loss switching is triggered by `loss < 0`, independently
  of the sign of net outcome.
- Matched the manuscript `horizon_effect` definition to implementation: first
  free choices only, both information conditions, pre-choice observed means,
  ties excluded, and Horizon 6 minus Horizon 1.
- Clarified that the model variable `reward_sensitivity` is the slope on reward
  difference but multiplies the whole subjective-evidence bracket, making it
  the overall evidence inverse-temperature under this parameterisation.

Status: code, source-data signs, README, and manuscript terminology aligned.

## 2026-08-08: Align Horizon tie handling and finalise metric definitions

- Audited the manuscript definitions against the task and human-preprocessing
  code and the retained source datasets.
- Defined IGT post-loss switching from the recorded negative loss component,
  not net outcome, and excluded trial 100 because it has no subsequent choice.
- Clarified that legacy `directed_exploration` is the unequal-information
  information-seeking choice rate, whereas `horizon_effect` is the Horizon-6
  minus Horizon-1 lower-observed-mean choice rate across both information
  conditions.
- Fixed LLM Horizon preprocessing to exclude observed-mean ties, matching the
  existing human rule. The audit found 160 ties in 16,000 formal English LLM
  games and 151 in 19,200 human games.
- Regenerated all three English model metric sets, prompt-sensitivity analyses,
  model comparisons, human comparisons, and human-similarity tables from the
  retained raw records.
- Corrected manuscript provenance: the 60-person Horizon reference is the Feng
  et al. release (31 `pilot-v1`, 29 `repeater-v1`), and the 504-person IGT
  subset comprises seven documented study labels with complete 100-trial
  choice, reward, and loss records.

Status: definitions, implementation, English derived outputs, and manuscript
wording aligned.

## 2026-08-05: Complete manuscript interaction and uncertainty specification

- Defined GPT-4.1-reference model interactions and English-reference language
  baseline and prompt-interaction contrasts in the thesis Method.
- Specified raw interaction contrasts as primary and cross-language Hedges' g
  differences as supplementary standardised summaries.
- Recorded 2,000 two-sided percentile-bootstrap 95% intervals, bootstrap seed
  20260615, and task-specific resampling units.
- Added an estimation-focused multiplicity policy: no family-wise adjustment,
  no isolated binary decisions from unadjusted intervals, and interpretation
  based on prespecified effect patterns and uncertainty.

Status: manuscript wording aligned with the current interaction/bootstrap plan.

## 2026-08-05: Replace multilingual omnibus tests with interactions

- Replaced the planned Friedman/Kendall's W/permutation analysis with English-
  reference baseline contrasts and language-by-prompt interaction contrasts.
- Added `src/compute_language_interactions.py`, producing raw and Hedges' g
  contrasts with 2,000 percentile-bootstrap confidence intervals.
- Preserved matched-seed block bootstrap for Horizon and BART and independent-
  cell run bootstrap for deterministic-schedule IGT.
- Updated the canonical experiment config, multilingual freeze, tests, output
  schema, command documentation, and compatibility entry point.

Status: implemented; formal three-language data must be complete before the
production interaction outputs can be generated.

## 2026-08-04: Reorder the Statistical Analysis comparison logic

- Reorganised the manuscript analysis in the order required by the controlled
  comparisons: prompt conditions within one model and language; models within
  English; then languages within GPT-4.1.
- Added an explicit language index to prompt-effect, Hedges' g, and PSI
  notation so the formulas match the multilingual design.
- Kept model-by-prompt and language-by-prompt interactions as separate stages.

Status: applied to the external manuscript source and repository method notes.

## 2026-08-04: Revise thesis Method for behavioural metrics and languages

- Audited the Method in `final.pdf` and recorded the required corrections in
  `docs/method_revision_multilingual_metrics_zh.md`.
- Replaced “pre-frozen” as the rationale for metric selection with construct
  coverage, record-based measurability, and human--LLM comparability; freezing
  is retained only as an analysis-timing safeguard.
- Specified the multilingual comparison as English, Simplified Chinese, and
  Spanish under fixed `gpt-4.1-2025-04-14`, semantically matched prompt
  manipulations, matched task settings, and 20 base seeds per cell.
- Kept the three-model English comparison separate from the fixed-model
  language comparison and specified language-by-prompt interactions.
- Flagged the distinction between the project-level information-seeking rate
  named `directed_exploration` and the separate horizon-dependent exploration
  effect.

Status: paste-ready Method revision prepared; the external manuscript source
must apply the wording and replace its model-collection date placeholders.

## 2026-08-03: Propagate Horizon model uncertainty and correct BART missingness

- Classified Horizon `random_exploration_effect` run values as partially
  pooled, model-derived estimates.
- Changed downstream prompt-effect and PSI bootstraps to resample complete
  Horizon run clusters and refit the hierarchical logistic model within every
  replicate before recomputing raw effects, pooled-SD Hedges' g, and PSI.
- Changed cross-model random-exploration interaction intervals to refit all
  four model--prompt cells within each matched-seed bootstrap replicate.
- Changed BART `post_explosion_adjustment` to missing when no explosion has a
  subsequent balloon, rather than assigning an arbitrary zero.
- Audited the formal data: none of the 240 LLM BART runs lacks an eligible
  transition; one of 141 adult human participants does, giving effective
  human n=140 for this metric.
- No LLM API recollection is required; affected processed and statistical
  outputs must be regenerated from retained raw records.

## 2026-08-01: Correct IGT uncertainty resampling

- Changed IGT within-model prompt-effect bootstrap from nominal seed pairing to independent resampling within the baseline and manipulated-condition cells.
- Changed IGT PSI bootstrap to use the same independent-cell scheme while preserving within-run correlations across IGT primary metrics.
- Retained paired environment-seed block bootstrap for Horizon and BART.
- Added `bootstrap_unit` to every prompt-effect and PSI output row.
- Recomputed GPT-4.1, GPT-5.4, and GPT-5.4 Mini prompt effects and PSI using 2,000 bootstrap replicates.
- All three analyses completed with 24 prompt-effect rows, 9 PSI rows, and `issues=[]`.

Status: IGT uncertainty correction complete.

## 2026-08-01: Delete superseded GPT-5.4 Mini failed attempts

- Deleted the three failed-attempt JSON files under
  `outputs/model_comparison_en_v01/gpt-5.4-mini-failed-audit-v01/` after their
  logical runs had been successfully repaired.
- Retained all 240 successful formal runs and all processed analysis outputs.
- Future processing inputs contain successful formal data only.

Status: Superseded failures deleted; successful dataset unchanged.

## 2026-08-01: Remove obsolete two-model manuscript figures and tables

- Removed the generated GPT-4.1-versus-GPT-5.4 Figures 2-6 directory.
- Removed the generated two-model Tables 1-6, table manifest, and primary-results checklist.
- Retained raw data, model-specific processed outputs, two-model comparison CSVs, human-comparison CSVs, generation scripts, captions, and table notes for audit and three-model pipeline development.
- Final manuscript figures and tables must be regenerated with GPT-5.4 Mini included.

Status: Obsolete two-model figure/table outputs removed.

## 2026-08-01: Complete and process GPT-5.4 Mini English formal batch

- Completed the five-wave, two-worker English GPT-5.4 Mini collection with
  240/240 successful logical runs.
- Deferred failures during formal collection and repaired all three failed
  logical runs after wave 5.
- Preserved the superseded failed-attempt JSON files under
  `outputs/model_comparison_en_v01/gpt-5.4-mini-failed-audit-v01/` so they do
  not collide with their successful replacements during strict aggregation.
- Strict aggregation completed with 240 valid runs and `issues=[]`.
- Prompt-sensitivity analysis produced 128 metric-summary rows, 24
  prompt-effect rows, and 9 PSI rows with `analysis_complete=true`.
- The API resolved the requested model to `gpt-5.4-mini-2026-03-17`.
- One Horizon baseline run (`seed=20260726`) contained one invalid intermediate
  response followed by a successful retry; the completed output contains all
  300 valid trials and was retained.

Status: Complete and analysis-ready.

这个文件用于记录项目后续每一步实质性工作。规则是：只要一个步骤会影响实验设计、代码实现、prompt、数据、分析或论文写作，就必须在这里留下记录。

## 2026-06-15: GitHub repository organization

- Expanded `.gitignore` to exclude local secrets, virtual environments,
  caches, human datasets, generated experiment outputs, local agent/editor
  state, and the local proposal PDF.
- Kept `DATASET/` and `outputs/` on disk; the cleanup only prevents accidental
  GitHub publication.
- Removed the superseded `pilot_results_only.md`, temporary supervisor-meeting
  simulation, and completed presentation-only Superpowers documents.
- Removed the unused scaffold `main.py` and replaced the placeholder package
  description in `pyproject.toml`.
- Updated `README.md` as the current-state entry point and documented how local
  data and generated outputs are handled.
- Repaired current documentation references that pointed to files no longer
  present in the repository.

## 记录模板

```text
Date:
Phase:
Step:
Action:
Why this was done:
Evidence / basis:
Related citations:
Files changed or created:
Output / result:
Status:
Next step:
Notes:
```

## Evidence / Basis 标签

如果某一步不是直接来自文献，也必须说明依据类型：

- Literature-based decision
- Dataset-based decision
- Config-based decision
- Pilot-based decision
- Project design decision
- Implementation necessity
- Assumption to verify

## Log Entries

### 2026-07-29 - Unify Current Project Scope and Documentation

Change:

- Rewrote `docs/next_steps_plan.md` as a current-state plan instead of an
  experiment-preparation history.
- Updated the formal freeze document to define one 720-run, three-language
  experiment and its matched seed policy.
- Updated README and deliverable indexes to label `formal_v01` and its current
  human comparison as the completed English stage.
- Fixed the project-wide boundary at one open human reference dataset per task
  and no independent second LLM batch.
- Kept historical pilot and implementation entries in this log as history,
  while current-state documents now use the unified scope.

Verification:

- Current-scope conflict search returned no matches.
- `python -m unittest discover -s tests`: 125 tests passed.
- `git diff --check`: passed.
- The active multilingual smoke process remained running during documentation
  edits.

Status: Done

### 2026-07-29 - Freeze Formal Multilingual Completion

Change:

- Defined English, Simplified Chinese, and Spanish as levels of one formal
  language factor.
- Kept the completed 240-run English `formal_v01` batch and froze 480 matched
  Chinese/Spanish task runs for collection.
- Reused base seeds `20260708` through `20260727`, which reproduce the existing
  task-specific English seed sets through offsets 0, 1, and 2.
- Reserved `outputs/formal_multilingual_v01/` for new formal language runs and
  excluded the earlier `outputs/multilingual_v01/` pilot artifacts.
- Updated README and the active next-step order before paid API collection.

Status: Frozen; one-seed Chinese/Spanish smoke collection is in progress.

### 2026-07-29 - Retry Formal API Disconnects

Change:

- The first formal multilingual smoke cell failed when the remote endpoint
  closed a connection during a 300-trial Horizon run.
- Added retry handling for remote disconnects, connection errors, and TLS
  errors in addition to the existing timeout and URL-error handling.
- Increased transient network retries to five and applied exponential backoff.
- Added a regression test for recovery from `RemoteDisconnected`.
- Stopped the remaining smoke matrix after the first failed cell to avoid
  unnecessary API calls before the retry fix was validated.

Status: Implemented and validated by the completed first formal Chinese cell.

### 2026-07-29 - First Formal Multilingual Cell Completed

Result:

- Language: `zh-CN`
- Task: Horizon
- Condition: `baseline`
- Base/task seed: `20260708`
- Trials: 300
- Parse success rate: 1.0
- Invalid responses: 0
- Requested and resolved model: `gpt-4.1-2025-04-14`
- The resumed 24-cell Chinese/Spanish smoke matrix skipped this valid output
  and continued with the remaining cells.

Status: One formal cell complete; matched one-seed smoke matrix in progress.

### 2026-07-29 - Remove Independent Second-Batch Scope

Change:

- Standardized the project around one formal experiment and removed the
  independent second-batch design.
- Removed out-of-scope comparison artifacts, dedicated source modules, tests,
  claims, and workflow instructions.
- The later multilingual scope freeze treats English, Chinese, and Spanish as
  levels of this same formal experiment rather than separate experiments.

Status: Done

### 2026-07-29 - Keep One Open Human Dataset Set

Change:

- Removed the three supplementary raw human-data sources, their processed
  metrics, the additional LLM-human comparison, and the dataset-comparison
  robustness analysis.
- Removed the dedicated processing/comparison modules and tests.
- Kept one open human reference dataset per task:
  Horizon 60 participants, IGT 504 participants, and BART 141 adults.
- Kept the primary `formal_v01` LLM-human comparison only.

Status: Done

### 2026-05-26 - 建立研究记录与引用规则

Date: 2026-05-26

Phase: Project management / research reproducibility

Step: Establish recording and citation workflow

Action:

- 在 `plan.md` 中加入“研究记录与引用规则”；
- 新建 `docs/research_log.md`；
- 新建 `docs/citation_map.md`；
- 规定后续每一步工作都要记录，并同步记录文献依据和引用位置。

Why this was done:

- 本项目是学术毕业设计，需要保证实验设计、任务实现、prompt manipulation、metrics 和分析都有可追踪依据；
- prompt sensitivity 是项目核心，因此 prompt 的每一次设计和修改都必须可追溯；
- 后期 dissertation 写作需要清楚说明“哪里引用哪篇文献”。

Evidence / basis:

- Project design decision；
- Academic reproducibility requirement；
- Dissertation writing requirement。

Related citations:

- 暂无单一特定文献；这是项目管理和学术写作规范。

Files changed or created:

- `plan.md`
- `docs/research_log.md`
- `docs/citation_map.md`

Output / result:

- 项目建立了后续工作记录与引用登记机制。

Status: Done

### 2026-07-18 - Primary LLM-Human Comparison

Change:

- Added `src/compare_llm_human.py`.
- Added `tests/test_llm_human_comparison.py`.
- Generated primary LLM-human comparison outputs in `deliverable/results/human_comparison_formal_v01/`.
- Updated README and deliverable result index with the human comparison location and headline findings.

Input data:

```text
LLM: deliverable/results/formal_v01/llm_run_metrics.csv
Human Horizon: outputs/processed/human_metrics/horizon_human_metrics.csv, 60 participants
Human IGT: outputs/processed/human_metrics/igt_human_metrics.csv, 504 participants
Human BART: outputs/processed/human_metrics/bart_human_metrics.csv, 141 participants
Horizon random exploration: outputs/processed/human_horizon_random_exploration.json
```

Outputs:

```text
deliverable/results/human_comparison_formal_v01/human_metric_summary.csv
deliverable/results/human_comparison_formal_v01/llm_human_comparison.csv
deliverable/results/human_comparison_formal_v01/closest_prompt_by_metric.csv
deliverable/results/human_comparison_formal_v01/human_comparison_summary.json
deliverable/results/human_comparison_formal_v01/human_comparison_analysis_zh.md
deliverable/results/human_comparison_formal_v01/metric_notes.md
deliverable/results/human_comparison_formal_v01/README.md
```

Headline findings:

- BART metrics are broadly human-compatible across prompt conditions.
- Horizon `directed_exploration` is close to the human reference distribution, especially under baseline.
- Horizon `horizon_effect` and `random_exploration_effect` are weaker than human reference values.
- IGT `post_loss_switching_rate` falls within the human reference distribution.
- IGT `advantageous_choice_rate` is above the human reference interval across all prompt conditions.

Verification:

- `uv run python -m unittest tests.test_llm_human_comparison`: 5 tests passed.

Status: Done

### 2026-07-14 - Supervisor Review Deliverable View

Change:

- Added a compact supervisor-review deliverable directory at `deliverable/`.
- Copied only the completed formal v01 processed outputs into `deliverable/results/formal_v01/`.
- Added `deliverable/README_DELIVERABLE.md` and `deliverable/results/README.md` to explain included result files and excluded local process artifacts.
- Updated `README.md` to identify the deliverable entry point and the current formal v01 status.

Formal v01 quality status:

```text
valid_run_count = 240
expected_runs_per_cell = 20
aggregation analysis_complete = true
PSI analysis_complete = true
issues = []
```

Packaging boundary:

- Included: source code, tests, configs, prompts, method documentation, and compact processed formal v01 result tables.
- Excluded from the deliverable view: `.env`, `.venv/`, `.tmp/`, `.uv-cache/`, `DATASET/`, raw JSON runs, and early debug/pilot outputs.
- Raw runs and datasets were not deleted; they remain local audit/regeneration materials.

Status: Done

### 2026-06-15 - Correct Mini-Pilot Effect Sizes and Freeze Validation Method

Change:

- Updated the LLM runner to send and record `temperature`, `top_p`, and
  `max_output_tokens`, together with requested and API-resolved model IDs.
- Made `configs/experiment_config_stage01.json` the default source for the
  experiment model instead of allowing a stale `.env` model alias to override
  it silently.
- Froze the validation model as `gpt-4.1-2025-04-14`, temperature `0.7`,
  top-p `1.0`, and 16 output tokens.
- Removed `learning_curve_change` from IGT primary PSI metrics.
- Added supplementary IGT `learning_slope` based on all five block net
  scores.
- Changed the primary standardized effect from a baseline-SD difference to
  pooled-SD Hedges' g.
- Retained the baseline-SD effect as a named sensitivity output.
- Added paired-seed bootstrap intervals for raw differences, Hedges' g, and
  PSI.
- Added whole-run cluster bootstrap intervals and shrinkage sensitivity
  diagnostics for the Horizon random-exploration model.
- Created `configs/formal_experiment_freeze.json`.

Diagnostic result:

- The old IGT reward/loss PSI decreased from `3.333` to `0.880`.
- Its advantageous-choice effect decreased from baseline-SD `7.506` to
  Hedges' g `1.396`.
- Horizon bootstrap fitting succeeded for all 200 diagnostic replicates in
  all four conditions, but every random-exploration interval crossed zero.
- The historical 36-run mini-pilot used API-resolved temperature `1.0`, not
  the intended `0.7`, and therefore remains a methodological pilot.

Files:

- `src/run_llm_pilot.py`
- `src/aggregate_experiment_results.py`
- `src/compute_prompt_sensitivity.py`
- `src/horizon_random_exploration.py`
- `configs/experiment_config_stage01.json`
- `configs/formal_experiment_freeze.json`
- `docs/formal_experiment_freeze.md`
- `docs/mini_pilot_method_diagnostics.md`
- `README.md`

Status: Validation rerun required before formal data collection.

### 2026-06-15 - Frozen-Parameter Validation Mini-Pilot v02

Change:

- Ran a new 36-run validation mini-pilot under the frozen configuration:
  `gpt-4.1-2025-04-14`, temperature `0.7`, top-p `1.0`, 16 output tokens,
  config version `0.5`.
- Used paired base seeds `20260620`, `20260621`, and `20260622`.
- Wrote raw outputs to `outputs/validation_mini_pilot_v02`.
- Wrote processed outputs to `outputs/processed/validation_mini_pilot_v02`.
- Added `docs/validation_mini_pilot_v02_summary.md`.

Result:

- 36/36 valid runs.
- 0 invalid responses.
- Strict aggregation passed with no issues.
- Prompt hashes, API-resolved model IDs, temperature, top-p, and token limits
  were consistent across the batch.
- PSI analysis completed with 24 primary prompt-effect rows and 9 PSI rows.
- Horizon random-exploration diagnostic bootstrap produced intervals for all
  four conditions with 100% convergence across 200 diagnostic replicates.

Key diagnostic findings:

- IGT `detailed` PSI was high (`5.965`), mainly because
  `post_loss_switching_rate` had a Hedges' g of `10.648`.
- IGT reward/loss runs all reached `advantageous_choice_rate = 1.0`, again
  showing ceiling effects in supplementary learning-trajectory metrics.
- Horizon random-exploration intervals remained wide and diagnostic only.

Status:

- The frozen runner and analysis pipeline are operational.
- v02 is a validation mini-pilot, not the formal experiment.
- The next stage is the 15-20 valid runs per task-condition cell formal
  batch, with special attention to IGT post-loss switching variance.

### 2026-06-13 - Reconstruct Three Canonical Baselines

Change:

- Reconstructed the neutral Horizon, four-deck, and balloon baselines from
  the original task literature, local human-data structure, and implemented
  task parameters.
- Added `docs/baseline_prompt_source_map.md`.
- Removed Horizon analysis labels from participant-facing observations and
  replaced them with the number of choices remaining in the current game.
- Added content and interface regression tests.
- Made unavailable generated conditions fail with an explicit error.
- Added `meta_prompt_v2.md`, which generates three variants per task while
  treating the canonical baseline as frozen input.

Prompt boundary:

- Baselines include the neutral total-reward objective and explain that
  outcome patterns are initially unknown.
- They do not expose task names, behavioural metrics, advantageous decks,
  true reward distributions, or hidden balloon explosion parameters.

Verification:

- Canonical baseline dry run replaced every observation placeholder and
  parsed every configured legal response.
- `uv run python -m unittest discover -s tests`: 56 tests passed.
- SHA-256 hashes for all three baseline inputs are stored in
  `prompts/generation/records/2026-06-13_canonical_baselines/review.md`.

Status: Done

### 2026-06-14 - Implement Multi-Run Aggregation and PSI Pipeline

Change:

- Added seed-specific successful and failed pilot filenames.
- Fixed task seed offsets at Horizon `+0`, IGT `+1`, and BART `+2`, including
  task-subset runs.
- Added config and prompt SHA-256 provenance to pilot JSON.
- Added `src/aggregate_experiment_results.py`.
- Added `src/compute_prompt_sensitivity.py`.
- Added strict validation and explicit `--allow-incomplete` recovery.
- Added duplicate detection with optional `--duplicate-policy latest`.
- Added paired-seed, failed-run, model, config-version, and prompt-hash audits.
- Integrated run-level Horizon `random_exploration_effect` estimates.
- Added IGT `learning_curve_change`, defined as block 5 minus block 1.
- Froze three primary PSI metrics per task in config version 0.4.

PSI variance rules:

- Use baseline sample SD when nonzero.
- Use pooled SD when baseline SD is zero but condition SD is nonzero.
- Assign zero effect when both groups are constant and equal.
- Treat constant but unequal groups as undefined.
- Warn, without replacing the denominator, when baseline variance is very low.

Outputs:

- `llm_run_metrics.csv`
- `aggregation_quality_report.json`
- `metric_summary.csv`
- `prompt_effects.csv`
- `prompt_sensitivity.csv`
- `analysis_summary.json`

Verification:

- Focused pilot and Horizon tests: 16 passed.
- Focused aggregation and PSI tests: 22 passed.
- Complete synthetic mini pilot: 36 run rows, 27 effect rows, 9 complete PSI
  rows, and 12 finite Horizon random-exploration estimates.
- `uv run python -m unittest discover -s tests`: 92 tests passed.
- Configuration JSON parsed successfully.
- `git diff --check` passed.

Status: Done; the pipeline is ready for the 36-run mini pilot.

### 2026-06-14 - Complete 36-Run Mini Pilot

Run design:

```text
3 tasks x 4 prompt conditions x 3 paired base seeds = 36 runs
```

Base seeds:

- `20260614`
- `20260615`
- `20260616`

Model:

- `gpt-4.1`

Outputs:

- Raw run JSON: `outputs/mini_pilot_v01`
- Aggregated analysis: `outputs/processed/mini_pilot_v01`

Quality result:

- 36 discovered files and 36 valid runs.
- Every task-condition cell contains three paired runs.
- All runs completed with parse success rate 1.0.
- Total invalid responses: 0.
- All 12 Horizon runs received finite `random_exploration_effect` estimates.
- `aggregation_quality_report.json`: zero issues.
- `analysis_summary.json`: `analysis_complete=true`.
- 124 metric-summary rows, 27 prompt-effect rows, and 9 complete PSI rows.

Mini-pilot PSI values:

| Task | Condition | PSI |
|---|---|---:|
| Horizon | `detailed` | 1.094 |
| Horizon | `role_human` | 0.939 |
| Horizon | `uncertainty_emphasis` | 2.676 |
| IGT | `detailed` | 0.305 |
| IGT | `role_human` | 0.526 |
| IGT | `reward_loss_emphasis` | 3.333 |
| BART | `detailed` | 1.338 |
| BART | `role_human` | 1.193 |
| BART | `risk_emphasis` | 0.389 |

Interpretation boundary:

- These estimates are based on only three runs per cell and are diagnostic.
- The large IGT reward/loss PSI is strongly influenced by a standardised
  advantageous-choice effect and must be checked for low baseline variability
  before the formal experiment.

Status: Done; mini-pilot outputs are ready for diagnostic review and method
freeze.

### 2026-06-13 - Add Separate GPT-5.5 Prompt Generator

Change:

- Added `PROMPT_GENERATOR_MODEL=gpt-5.5` while retaining
  `OPENAI_MODEL=gpt-4.1` for cognitive-task runs.
- Added `src/generate_prompt_variants.py`.
- Extended the Responses API client to support `reasoning.effort` and
  `text.verbosity`.
- Configured prompt generation with low reasoning effort, low verbosity, and
  6000 maximum output tokens. Temperature and top-p are not sent.
- Added auditable per-task outputs for the rendered request, raw response,
  raw output text, and generation metadata.
- The generator does not install outputs as final prompts.

Reason:

- Prompt generation and experimental task performance use different models
  and must remain methodologically and operationally separate.
- The API response model identifier and complete raw materials must be
  retained for reproducibility.

Verification:

- The three generation requests render with no unresolved meta-prompt
  placeholders and exactly one `{observation}` placeholder each.
- `uv run python -m unittest discover -s tests`: 59 tests passed.
- The experiment configuration is valid JSON.
- `.env` remains ignored by Git.

Status: Done

### 2026-06-14 - Lock Prompt Generator Sampling Configuration

Change:

- Replaced the planned prompt-generation model with the fixed snapshot
  `gpt-4o-2024-11-20`.
- Kept `OPENAI_MODEL=gpt-4.1` unchanged for cognitive-task runs.
- Extended the shared Responses API client to accept optional `temperature`
  and `top_p` parameters.
- Configured the prompt generator to send `temperature=0.0` and `top_p=1.0`.
- Removed reasoning-effort and text-verbosity arguments from the generator
  while preserving those optional capabilities in the shared client.
- Updated Prompt Generation Protocol 1.2, configuration, provenance,
  environment examples, README, and generation-record template.

Reason:

- A dated model snapshot is more reproducible than the moving `gpt-4o` alias.
- Temperature zero reduces sampling variation, while top-p one is retained as
  a fixed neutral setting.
- The generation metadata must describe the parameters actually sent to the
  API.

Evidence / basis:

- OpenAI's GPT-4o model documentation lists `gpt-4o-2024-11-20` as a snapshot
  and states that snapshots lock a specific model version for more consistent
  behaviour.
- Project reproducibility requirement.

Verification:

- Prompt-generation and HTTP-client tests verify that `temperature=0.0` and
  `top_p=1.0` are included in the request body and audit record.
- `uv run python -m unittest discover -s tests`: 60 tests passed.
- The experiment configuration parses as valid JSON.
- No prompt-generation API call was made during this change.

Status: Implemented; generation API calls remain pending.

### 2026-06-14 - Generate Nine Prompt Candidates

Change:

- Called the university-provided OpenAI Responses API once for each of the
  Horizon, IGT, and BART tasks.
- Generated three candidate variants per task: `detailed`, `role_human`, and
  the task-specific emphasis condition.
- Retained each rendered request, raw API response, extracted output,
  generation record, response ID, returned model identifier, baseline hash,
  and sampling configuration.
- Added `pre_review.md` without modifying the raw outputs.

Generation settings:

```text
model = gpt-4o-2024-11-20
temperature = 0.0
top_p = 1.0
max_output_tokens = 6000
candidate sets per task = 1
```

Result:

- All three calls succeeded.
- The requested and returned model identifiers matched.
- All nine candidates preserved the observation placeholder and legal
  response tokens.
- Initial review identified minor semantic drift: strengthened reward-pattern
  claims in Horizon and IGT, and a changed probability claim in BART.
- Raw candidates remain uninstalled pending documented minimal edits, manual
  review, dry-run checks, and parser tests.

Files:

- `prompts/generation/records/2026-06-14_gpt-4o-2024-11-20/`
- `prompts/generation/records/2026-06-14_gpt-4o-2024-11-20/pre_review.md`

Status: Generation complete; manual review and prompt freezing pending.

### 2026-06-14 - Review and Freeze Twelve-Prompt Matrix

Change:

- Reviewed the three frozen baselines and all nine generated candidates.
- Preserved every raw generation output unchanged.
- Installed nine final variants after only the edits needed to restore task
  equivalence and isolate the intended manipulation.
- Added all nine paths to the experiment configuration.
- Added complete 12-prompt dry-run validation.
- Recorded the exact edit log and SHA-256 hash for every final prompt in
  `final_review.md`.
- Marked all three generation records as `passed_with_edits`.

Main corrections:

- Restored uncertain reward-pattern wording in Horizon and IGT.
- Removed IGT explanations that were absent from the frozen baseline.
- Removed unintended risk emphasis from BART `detailed` and `role_human`.
- Restored BART wording about unknown explosion outcomes instead of making a
  new claim about explosion probabilities.

Verification:

- All 12 prompts contain exactly one observation placeholder.
- All 12 prompts passed rendering and parser checks.
- No experimental prompt exposes canonical task names or configured hidden
  information.
- `uv run python -m unittest discover -s tests`: 63 tests passed.

Files:

- `prompts/bandit/*.md`
- `prompts/igt/*.md`
- `prompts/bart/*.md`
- `prompts/generation/records/2026-06-14_gpt-4o-2024-11-20/final_review.md`
- `outputs/debug/prompt_dry_run/prompt_matrix_dry_run.json`

Status: Done; current 12-prompt experimental matrix frozen.

### 2026-06-14 - Tighten Prompt Manipulation Isolation

Change:

- Reopened the prompt freeze after a second independent review found that the
  first reviewed variants still changed non-target wording.
- Updated Prompt Generation Protocol from 1.2 to 1.3.
- Required every prompt to preserve the exact neutral baseline objective.
- Rebuilt each `role_human` prompt as the baseline plus one explicit
  human-participant role sentence.
- Rebuilt each task-specific emphasis prompt as the baseline with only one
  authorised paragraph changed.
- Retained the detailed variants' explanatory organisation while restoring
  the exact objective.
- Added `docs/prompt_generation_and_review_record.md`, which records the
  generation instruction, task substitutions, model, temperature, top-p,
  raw records, two review rounds, and final hashes.

Reason:

- Broad paraphrasing in role and emphasis conditions could confound the
  intended manipulation with wording length, style, or objective strength.
- Restoring non-target content exactly to baseline provides a stronger
  control-variable design.

Verification boundary:

- Raw API requests and responses were not changed.
- No behavioural pilot result was consulted when choosing final wording.
- Automated tests now enforce the role-sentence and one-paragraph-difference
  invariants.

Final verification:

- All 12 prompt conditions passed observation rendering and parser checks.
- `uv run python -m unittest discover -s tests`: 66 tests passed.
- Experiment configuration and all three generation records parsed as valid
  JSON.
- Final hashes were updated in the generation records, `final_review.md`, and
  `docs/prompt_generation_and_review_record.md`.
- `git diff --check` passed.

Status: Done; Protocol 1.3 prompt matrix frozen.

### 2026-06-14 - Apply Adult Filter to BART Human Data

Change:

- Identified participant age at zero-based Excel column index 8.
- Verified that age is constant across all 40 rows for every participant.
- Added a dynamic `age >= 18` inclusion rule to BART preprocessing.
- Excluded six participants: IDs 4, 5, 7, 13, 79, and 86.
- Regenerated BART human metrics with 141 adult participants.
- Added `bart_exclusions.csv` and filter metadata to `summary.json`.
- Added `docs/bart_human_preprocessing.md`.

Audit result:

- Source: 147 participants, 5,880 rows.
- Excluded: 6 participants, 240 rows.
- Included: 141 participants, 5,640 rows.
- Excluded ages: 16, 14, 17, 13, 16, and 16.
- Every source participant had 40 balloon records.

Reason:

- The planned human comparison uses the adult analysis sample.
- The exclusion must be rule-based and reproducible rather than implemented
  as a hard-coded participant-ID list.

Verification:

- `uv run python -m unittest discover -s tests`: 67 tests passed.
- `bart_human_metrics.csv`: 141 rows; every participant has 40 balloons.
- `bart_exclusions.csv`: 6 rows for IDs 4, 5, 7, 13, 79, and 86.
- `summary.json`: 147 source participants, 6 excluded, 141 included.
- Experiment configuration parsed as valid JSON.
- `git diff --check` passed.

Status: Done; adult BART analysis sample fixed at 141 participants.

### 2026-06-13 - Remove Historical Experimental Prompts

Change:

- Removed the 12 prompt files in the current three-task by four-condition
  experimental matrix.
- Retained the three `baseline_task_named.md` files because they are outside
  the current four-condition matrix and may support a future task-name
  exposure comparison.
- Selected prospective regeneration under Prompt Generation Protocol 1.0.
- Updated README, provenance record, and next-steps plan to pause new LLM
  pilots until replacement prompts are generated, reviewed, tested, and
  frozen.

Reason:

- The exact historical meta-prompt, generator settings, raw outputs, and
  manual edit history were not recorded.
- Regenerating prospectively provides a complete reproducibility chain.

Data boundary:

- Historical pilot outputs remain development records.
- They must not be pooled with results produced using the replacement prompt
  version.

Status: Done

### 2026-06-13 - Add Prompt Generation Protocol

Change:

- Added `docs/prompt_generation_protocol.md`.
- Added the exact reusable meta-prompt at
  `prompts/generation/meta_prompt_v1.md`.
- Added generation-record and manual-review templates.
- Added `prompts/generation/current_prompt_provenance.md` so unavailable
  historical generation metadata is explicitly marked `not recorded`.
- Added prompt provenance and version-freeze requirements to the README and
  next-steps plan.

Method boundary:

- The task literature and local implementation determine task content.
- The prompt-generation LLM is limited to constrained rewriting.
- Existing prompt-generation metadata that was not recorded historically
  must be reported as `not recorded`; it must not be reconstructed or
  invented retrospectively.
- Formal data collection requires retained raw outputs, manual edit records,
  prompt review, and a frozen version identifier.

Status: Done

Next step:

- 后续进行 Phase 1 固定研究设计时，逐项记录 research questions、task parameters、prompt conditions、metrics 和 human datasets 的依据。

Notes:

- 如果某个决定暂时没有文献依据，应在记录中标记为 `Assumption to verify`，不能留空。

### 2026-05-26 - Draft Final Experiment Design Table

Date: 2026-05-26

Phase: Phase 1 / 固定研究设计

Step: Step 1 - Final Experiment Design Table

Action:

- 新建 `docs/project_design.md`；
- 写出三项任务的 draft final experiment design table；
- 为每个 task 整理 prompt conditions、runs per condition、trials / units per run、main metrics、human dataset 和 citation basis；
- 标记了进入 implementation 前需要确认的 open decisions。

Why this was done:

- 用户询问 Step 1 中 “Task, Prompt conditions, Runs per condition, Trials per run, Main metrics, Human dataset” 应该具体做什么；
- 在写代码前，需要先固定实验矩阵，避免 task implementation、prompt writing 和 analysis 指标后续反复变化；
- 这一步是后续 data schema、task environment 和 pilot 的前置条件。

Evidence / basis:

- Project design decision；
- Literature-based decision；
- Dataset-based decision；
- Assumption to verify；
- Config-based decision could not be used directly because `configs/experiment_config_stage01.json` is currently empty on disk.

Related citations:

- BinzSchulz2023PNAS；
- BinzSchulz2023CognitiveModels；
- Shanahan2023RolePlay；
- LoyaSinhaFutrell2023；
- Sclar2023PromptFormatting；
- Razavi2025PromptSensitivity；
- Wilson2014HorizonTask；
- Feng2021ExploreExploit；
- Bechara1994IGT；
- Toplak2010IGTReview；
- Steingroever2015IGTData；
- Lejuez2002BART；
- Lejuez2003BARTAdolescent；
- Canning2022BARTReview；
- Sebri2023BART。

Files changed or created:

- `docs/project_design.md`
- `docs/research_log.md`
- `docs/citation_map.md`

Output / result:

- 生成了 draft final experiment design table；
- 明确了当前可以固定的内容；
- 标记了 Horizon reward schedule、IGT payoff schedule、BART balloon count / explosion rule、response labels 和空 config 文件等待确认事项。

Status: Draft completed

Next step:

- 继续完成 Step 2：确定每个 task 的 exact parameters；
- 在实现代码前恢复或重新生成 `configs/experiment_config_stage01.json`。

Notes:

- 当前 `docs/project_design.md` 是 draft，不是 locked design。
- BART 的 30 vs 40 balloons、Horizon exact game structure、IGT exact payoff table 需要在下一步确认。
### 2026-05-26 - Project Action Plan

Date: 2026-05-26

Phase: Project management / execution planning

Step: Create practical action plan

Action:

- Created `docs/action_plan.md`.
- Summarised what needs to be prepared before implementation.
- Converted the current draft experiment design into an ordered execution plan.
- Listed phases from design locking through task implementation, prompts, pilot, formal experiment, human dataset processing, analysis, and dissertation writing.

Why this was done:

- The project needs a practical plan showing what to prepare and what to do next.
- The current design document identifies open decisions, but a separate action plan makes the next steps easier to follow.

Evidence / basis:

- Project design decision.
- Based on `docs/project_design.md`.

Related citations:

- No new literature citation was introduced in this step.

Files changed or created:

- `docs/action_plan.md`
- `docs/research_log.md`

Output / result:

- A Chinese execution plan was added, including preparation checklist, phase-by-phase tasks, outputs, completion criteria, risks, and final deliverables.

Status: Done

Next step:

- Use the plan to complete task parameter decisions and regenerate `configs/experiment_config_stage01.json`.

Notes:

- The existing `plan.md`, `research_log.md`, and `citation_map.md` appear to contain encoding issues in some Chinese text. They were not rewritten in this step.

### 2026-05-26 - Three Task Details Document

Date: 2026-05-26

Phase: Phase 1 / 固定研究设计

Step: Create detailed task description document

Action:

- 新建 `docs/task_details.md`；
- 详细说明 Horizon Task / two-option bandit、Iowa Gambling Task 和 Balloon Analogue Risk Task；
- 为每个 task 整理概述、任务内容、流程、变量、prompt 条件、主要 metrics、human dataset 对齐和待确认事项；
- 汇总跨任务共同变量、控制变量、记录字段和 dissertation 对应位置。

Why this was done:

- 用户要求“再做一份文档，详细说一下这三个 task，包括概述，任务内容，不同变量等”；
- 后续实现 task environments、编写 prompts、设计 data schema 和写 dissertation methodology 都需要一份更细的 task-level 说明；
- 当前 `docs/project_design.md` 是实验矩阵层面的设计，不足以直接作为 task implementation specification。

Evidence / basis:

- Project design decision；
- Based on `docs/project_design.md`；
- Based on `docs/action_plan.md`；
- Assumption to verify for unresolved exact task parameters.

Related citations:

- Wilson2014HorizonTask；
- Feng2021ExploreExploit；
- Bechara1994IGT；
- Toplak2010IGTReview；
- Steingroever2015IGTData；
- Lejuez2002BART；
- Lejuez2003BARTAdolescent；
- Canning2022BARTReview；
- Sebri2023BART。

Files changed or created:

- `docs/task_details.md`
- `docs/research_log.md`

Output / result:

- 生成了一份中文 task details 文档，覆盖三个任务的概述、流程、变量、prompt 条件、metrics、human data alignment 和 open decisions。

Status: Draft completed

Next step:

- 继续确认 Horizon、IGT 和 BART 的 exact parameters；
- 将确认后的参数写入 `docs/task_parameters.md` 或 `configs/experiment_config_stage01.json`。

Notes:

- 文档中未锁定的参数均标记为 `To verify`，避免把草案误写成最终实验规则。

### 2026-05-26 - Prompt Sensitivity Formula Basis

Date: 2026-05-26

Phase: Phase 1 / 固定研究设计

Step: Clarify prompt sensitivity operationalisation

Action:

- Updated `docs/task_details.md` section 2.4 to explain the literature basis and methodological status of the prompt sensitivity formula；
- Clarified that the formula is an operational definition for this project, not a fixed formula directly copied from one LLM prompt sensitivity paper；
- Added explanation linking the formula to standardised mean difference / effect size logic, Glass-type baseline SD standardisation, and LLM prompt variation comparison；
- Added statistical method citation entries to `docs/citation_map.md`。

Why this was done:

- The project needs to justify why prompt sensitivity can be calculated using standardised differences between manipulated prompt conditions and baseline；
- The PSI should be described as a descriptive composite index constructed for this project, not as a standard psychological scale；
- This clarification will make the proposal and dissertation methodology more rigorous.

Evidence / basis:

- Literature-based decision；
- Statistical method basis；
- Project design decision。

Related citations:

- Cohen1988PowerAnalysis；
- HedgesOlkin1985MetaAnalysis；
- Glass1976Delta；
- Sclar2023PromptFormatting；
- Razavi2025PromptSensitivity。

Files changed or created:

- `docs/task_details.md`
- `docs/citation_map.md`
- `docs/research_log.md`

Output / result:

- Prompt sensitivity is now described as an operationalised standardised mean-difference measure；
- PSI is explicitly described as a project-specific descriptive summary index；
- Citation map now includes effect-size and Glass-type standardisation basis.

Status: Done

Next step:

- Use this operational definition in the proposal / methodology draft and later implement it in the analysis scripts.

Notes:

- If the final analysis uses pooled SD rather than baseline SD, the formula and citation notes should be updated consistently.

### 2026-05-28 - Literature-Based Exact Task Parameters

Date: 2026-05-28

Phase: Phase 2 / Confirm exact task parameters

Step: Fix task parameters using literature and local dataset alignment

Action:

- Created `docs/task_parameters.md`.
- Fixed the working exact parameters for the Horizon Task, Iowa Gambling Task, and Balloon Analogue Risk Task.
- Used literature sources to justify the task structure, reward/payoff schedules, trial counts, and main scoring variables.
- Checked local datasets to align implementation decisions with available human comparison data.

Why this was done:

- The previous design documents still marked several task parameters as `To verify`.
- The project cannot safely move to config generation, prompt writing, or task environment implementation until task rules are fixed.
- The dissertation methodology needs a clear explanation of which task version was implemented and why.

Evidence / basis:

- Literature-based decision.
- Dataset-based decision.
- Implementation necessity.

Related citations:

- Wilson et al. (2014) for the Horizon Task.
- Bechara et al. (1994) and Steingroever et al. (2015) for the Iowa Gambling Task.
- Lejuez et al. (2002) and Sebri et al. (2023) for the Balloon Analogue Risk Task.

Files changed or created:

- `docs/task_parameters.md`
- `docs/research_log.md`

Output / result:

- Horizon Task: Wilson-style 4 forced-choice trials plus Horizon 1 / Horizon 6 free-choice phase.
- IGT: standard 100-trial Bechara payoff scheme.
- BART: 40-balloon probabilistic version aligned with the local human dataset.

Status: Working decision completed

Next step:

- Generate `configs/experiment_config_stage01.json` from the fixed parameters.
- Write the three baseline prompts.
- Create `docs/data_schema.md`.

Notes:

- Horizon uses 40 games per LLM run for cost and runtime reasons, not the full 320 games used in Wilson et al. (2014).
- BART follows the 40-balloon Sebri et al. style because the local dataset contains 147 participants x 40 balloons.

### 2026-05-28 - Stage 01 Experiment Config

Date: 2026-05-28

Phase: Phase 2 / Convert task parameters into executable configuration

Step: Generate `configs/experiment_config_stage01.json`

Action:

- Filled `configs/experiment_config_stage01.json`.
- Added global model/run settings, prompt conditions, task-specific parameters, response formats, metric lists, human dataset paths, output paths, and prompt sensitivity analysis settings.
- Validated the file with `python -m json.tool`.

Why this was done:

- The config file was empty, so later task environments, prompt loaders, parsers, and runners did not yet have a single machine-readable source of truth.
- The project has now moved from literature-based parameter decisions to executable experiment setup.

Evidence / basis:

- Config-based decision.
- Based on `docs/task_parameters.md`.
- Implementation necessity.

Related citations:

- No new literature citation was introduced in this step.

Files changed or created:

- `configs/experiment_config_stage01.json`
- `docs/research_log.md`

Output / result:

- A valid JSON experiment config now exists.
- The config includes Horizon, IGT, and BART task parameters and all four prompt conditions per task.

Status: Done

Next step:

- Create `docs/data_schema.md`.
- Write baseline prompt files for Horizon, IGT, and BART.

Notes:

- `model_name` and `max_tokens` remain marked as `TO_CONFIRM` until API access and pilot testing are complete.

### 2026-05-28 - Data Schema Draft

Date: 2026-05-28

Phase: Phase 3 / Data schema design

Step: Define raw, trial-level, run-level, and invalid-response schemas

Action:

- Created `docs/data_schema.md`.
- Defined common identifiers, raw LLM output fields, trial/action-level fields, task-specific fields for Horizon, IGT, and BART, run-level metrics, invalid response logging, and file naming rules.

Why this was done:

- The project needs a stable data format before task environments, parsers, runners, and analysis scripts are implemented.
- All planned metrics must be computable from saved data.
- Raw model responses and invalid outputs must remain traceable for reproducibility.

Evidence / basis:

- Implementation necessity.
- Based on `configs/experiment_config_stage01.json`.
- Based on `docs/task_parameters.md`.

Related citations:

- No new literature citation was introduced in this step.

Files changed or created:

- `docs/data_schema.md`
- `docs/research_log.md`

Output / result:

- A draft data schema now exists for all three tasks.
- The schema defines raw output, processed trial/action data, run-level metrics, invalid response logs, and naming conventions.

Status: Draft completed

Next step:

- Write baseline prompt files for Horizon, IGT, and BART.
- Then implement task environments with a random agent before connecting to an LLM.

Notes:

- BART uses both action-level and balloon-level records because one balloon may contain multiple model actions.

### 2026-05-28 - Project Detail Overview

Date: 2026-05-28

Phase: Project documentation / design summary

Step: Create overall project detail document

Action:

- Created `docs/detail.md`.
- Summarised the whole project, including research aim, three tasks, prompt conditions, concrete settings, metrics, prompt sensitivity analysis, human dataset comparison, expected outputs, and dissertation argument.

Why this was done:

- The project now has several specialised documents, including task parameters, config, and data schema.
- A single overview document is useful for understanding the whole study design without reading every lower-level file.

Evidence / basis:

- Project design decision.
- Based on `docs/task_parameters.md`.
- Based on `configs/experiment_config_stage01.json`.
- Based on `docs/data_schema.md`.

Related citations:

- No new literature citation was introduced in this step.

Files changed or created:

- `docs/detail.md`
- `docs/research_log.md`

Output / result:

- A project-level detail document now exists.
- It can be used as a high-level explanation of the project design and as a starting point for dissertation methodology writing.

Status: Done

Next step:

- Write the baseline prompt files for Horizon, IGT, and BART.

Notes:

- `docs/detail.md` is an overview document. Exact implementation details should still be taken from `docs/task_parameters.md`, `docs/data_schema.md`, and `configs/experiment_config_stage01.json`.

### 2026-05-28 - Rewrite Detail Document In Chinese

Date: 2026-05-28

Phase: Project documentation / design summary

Step: Improve `docs/detail.md`

Action:

- Rewrote `docs/detail.md` into a clearer Chinese-heavy overview document.
- Reorganised tables for experiment design, prompt conditions, task settings, metrics, human datasets, analysis methods, and final outputs.

Why this was done:

- The previous version was useful but mixed English and Chinese unevenly.
- The user requested a clearer Chinese document with correctly represented tables.

Evidence / basis:

- Project documentation need.
- Based on existing project design documents.

Related citations:

- No new literature citation was introduced in this step.

Files changed or created:

- `docs/detail.md`
- `docs/research_log.md`

Output / result:

- `docs/detail.md` now provides a cleaner Chinese overview of the project.

Status: Done

Next step:

- Continue to baseline prompt drafting.

### 2026-05-28 - Baseline Prompt Drafts

Date: 2026-05-28

Phase: Prompt design

Step: Create baseline prompts for all three tasks

Action:

- Created `prompts/bandit/baseline.md`.
- Created `prompts/igt/baseline.md`.
- Created `prompts/bart/baseline.md`.
- Kept the prompts neutral: they explain the task, current state placeholder, valid outputs, and strict response format without role framing, cognitive emphasis, or strategy advice.

Why this was done:

- Baseline prompts are needed before detailed, role, and task-specific prompts can be written.
- They provide the reference condition for prompt sensitivity analysis.

Evidence / basis:

- Prompt design necessity.
- Based on `configs/experiment_config_stage01.json`.
- Based on `docs/detail.md`.
- Based on `docs/task_parameters.md`.

Related citations:

- No new literature citation was introduced in this step.

Files changed or created:

- `prompts/bandit/baseline.md`
- `prompts/igt/baseline.md`
- `prompts/bart/baseline.md`
- `docs/research_log.md`

Output / result:

- Three baseline prompt files now exist and match the prompt paths in the experiment config.

Status: Done

Next step:

- Implement a simple parser for legal response formats.
- Then implement task environments and run them with a random agent before connecting an LLM.

Notes:

- The prompts use `{observation}` as the placeholder for the current task state.

### 2026-05-28 - Next Implementation Plan

Date: 2026-05-28

Phase: Planning / implementation roadmap

Step: Create next-stage implementation plan

Action:

- Created `docs/next_plan.md`.
- Summarised the current project state and defined the next implementation phases: parser, task environments, random runner, baseline prompt dry run, LLM pilot, prompt expansion, and formal experiment locking.

Why this was done:

- The early design phase is mostly complete.
- The project needs a current plan that starts from the present state, rather than the older broad action plan.

Evidence / basis:

- Project planning need.
- Based on `docs/detail.md`, `docs/data_schema.md`, `configs/experiment_config_stage01.json`, and baseline prompt files.

Related citations:

- No new literature citation was introduced in this step.

Files changed or created:

- `docs/next_plan.md`
- `docs/research_log.md`

Output / result:

- A concrete next-stage plan now exists.

Status: Done

Next step:

- Implement `src/parser.py` and parser tests.

Notes:

- The plan recommends not calling an LLM until the parser, task environments, and random baseline runner are working locally.

### 2026-05-29 - Parser And Base Task Interface

Date: 2026-05-29

Phase: Implementation / parser and task interface

Step: Implement Phase 1 and Phase 2 from `docs/next_plan.md`

Action:

- Added parser tests in `tests/test_parser.py`.
- Added base task interface tests in `tests/test_task_base.py`.
- Implemented `src/parser.py` with `parse_response()` and `ParseResult`.
- Implemented `src/tasks/base.py` with `BaseTaskEnvironment` and `StepResult`.
- Added package initialisers under `src/`.

Why this was done:

- The project needs a stable parser before any LLM runner can be implemented.
- The task environments need a shared interface before Horizon, IGT, and BART are implemented separately.

Evidence / basis:

- Implementation necessity.
- Based on `docs/next_plan.md`.
- Based on `docs/data_schema.md`.
- Based on `configs/experiment_config_stage01.json`.

Related citations:

- No new literature citation was introduced in this step.

Files changed or created:

- `src/__init__.py`
- `src/parser.py`
- `src/tasks/__init__.py`
- `src/tasks/base.py`
- `tests/test_parser.py`
- `tests/test_task_base.py`
- `docs/research_log.md`

Output / result:

- Parser supports strict one-line `CHOICE: ...` and `ACTION: ...` formats.
- Parser returns structured parse results including `parsed_action`, `parse_success`, `invalid_reason`, and `normalized_response`.
- Base task interface defines `reset`, `get_observation`, `get_valid_actions`, `step`, `is_done`, `get_trial_records`, and `get_run_metrics`.

Verification:

- `python -m unittest tests.test_parser tests.test_task_base`
- Result: 8 tests passed.

Status: Done

Next step:

- Implement the concrete task environments, starting with IGT or Horizon.

Notes:

- The parser currently accepts case-insensitive valid actions and normalises them to uppercase.

### 2026-05-29 - Horizon Task Environment

Date: 2026-05-29

Phase: Implementation / task environments

Step: Implement Phase 3 from `docs/next_plan.md`

Action:

- Added Horizon environment tests in `tests/test_horizon.py`.
- Implemented `src/tasks/horizon.py` with `HorizonTaskEnvironment`.
- Added support for game generation, Horizon 1 / Horizon 6 structure, equal and unequal information conditions, forced-choice trials, free-choice trials, Gaussian rewards, trial-level records, and basic run-level metrics.

Why this was done:

- The project needs task environments that can run without LLM calls before any LLM pilot is attempted.
- Horizon is the first concrete task environment required by the next-stage implementation plan.

Evidence / basis:

- Implementation necessity.
- Based on `docs/next_plan.md`.
- Based on `docs/task_parameters.md`.
- Based on `configs/experiment_config_stage01.json`.
- Based on `docs/data_schema.md`.

Related citations:

- No new literature citation was introduced in this step.

Files changed or created:

- `src/tasks/horizon.py`
- `tests/__init__.py`
- `tests/test_horizon.py`
- `docs/research_log.md`

Output / result:

- `HorizonTaskEnvironment` supports `reset`, `get_observation`, `get_valid_actions`, `step`, `is_done`, `get_trial_records`, and `get_run_metrics`.
- Forced-choice trials restrict valid actions to the required option.
- Random-policy execution can complete a full Horizon run.
- Same seed and same policy produce reproducible rewards and metrics.

Verification:

- `python -m unittest tests.test_parser tests.test_task_base tests.test_horizon`
- Result: 12 tests passed.
- `python -m unittest discover`
- Result: 12 tests passed.

Status: Done

Next step:

- Implement IGT environment as Phase 4.

Notes:

- `random_exploration` is currently represented with a simple exploration-rate proxy. It can be refined later when the full analysis script is implemented.

### 2026-05-29 - IGT Task Environment

Date: 2026-05-29

Phase: Implementation / task environments

Step: Implement Phase 4 from `docs/next_plan.md`

Action:

- Added IGT environment tests in `tests/test_igt.py`.
- Implemented `src/tasks/igt.py` with `IGTTaskEnvironment`.
- Added support for 100-trial IGT runs, initial score, A/B/C/D decks, per-deck 10-card payoff cycles, reward/loss/net outcome feedback, cumulative score tracking, trial-level records, and run-level metrics.

Why this was done:

- IGT is the next concrete task environment after Horizon.
- The project needs task environments that can run locally with a random or deterministic policy before connecting to an LLM.

Evidence / basis:

- Implementation necessity.
- Based on `docs/next_plan.md`.
- Based on `docs/task_parameters.md`.
- Based on `configs/experiment_config_stage01.json`.
- Based on `docs/data_schema.md`.

Related citations:

- No new literature citation was introduced in this step.

Files changed or created:

- `src/tasks/igt.py`
- `tests/test_igt.py`
- `docs/research_log.md`

Output / result:

- `IGTTaskEnvironment` supports the shared task interface.
- A/B have net -250 per 10 selections.
- C/D have net +250 per 10 selections.
- Run-level metrics include `net_score`, `advantageous_choice_rate`, deck rates, final cumulative score, post-loss switching rate, and block-wise net scores.

Verification:

- `python -m unittest tests.test_igt`
- Result: 5 tests passed.
- `python -m unittest discover`
- Result: 17 tests passed.

Status: Done

Next step:

- Implement BART environment as Phase 5.

Notes:

- The payoff schedule is indexed by per-deck selection count, not global trial number.

### 2026-05-29 - BART Task Environment

Date: 2026-05-29

Phase: Implementation / task environments

Step: Implement Phase 5 from `docs/next_plan.md`

Action:

- Added BART environment tests in `tests/test_bart.py`.
- Implemented `src/tasks/bart.py` with `BARTTaskEnvironment`.
- Added support for 40-balloon BART runs, 2x20 block numbering, `PUMP` and `CASH_OUT` actions, 0.05 reward per successful pump, increasing explosion probability, certain explosion at pump 32, action-level records, balloon-level records, and run-level metrics.

Why this was done:

- BART is the third concrete task environment required before the random baseline runner can exercise all tasks locally.
- The implementation follows the BART settings described in `docs/detail.md`.

Evidence / basis:

- Implementation necessity.
- Based on `docs/detail.md`.
- Based on `docs/next_plan.md`.
- Based on `docs/task_parameters.md`.
- Based on `configs/experiment_config_stage01.json`.
- Based on `docs/data_schema.md`.

Related citations:

- No new literature citation was introduced in this step.

Files changed or created:

- `src/tasks/bart.py`
- `tests/test_bart.py`
- `docs/research_log.md`

Output / result:

- `BARTTaskEnvironment` supports the shared task interface.
- Each balloon has a pre-sampled hidden explosion point.
- `CASH_OUT` banks temporary earning and ends the balloon.
- Explosion clears current temporary earning and ends the balloon.
- Run-level metrics include average pumps, adjusted average pumps, explosion rate, cash-out threshold, total earnings, and post-explosion adjustment.

Verification:

- `python -m unittest tests.test_bart`
- Result: 6 tests passed.
- `python -m unittest discover`
- Result: 23 tests passed.

Status: Done

Next step:

- Implement random baseline runner as Phase 6.

Notes:

- Explosion probabilities follow `1 / (33 - pump_number)` with pump 32 as certain explosion.

### 2026-05-29 - Random Baseline Runner

Date: 2026-05-29

Phase: Implementation / random baseline runner

Step: Implement Phase 6 from `docs/next_plan.md`

Action:

- Added random baseline runner tests in `tests/test_random_baseline.py`.
- Implemented `src/run_random_baseline.py`.
- Added config-based environment construction for Horizon, IGT, and BART.
- Added a CLI entry point for running all three tasks with a random agent.
- Wrote debug JSON outputs under `outputs/debug/random_baseline/`.

Why this was done:

- Before connecting any LLM, the three task environments need to be runnable locally.
- A random agent is a simple sanity check for task logic, records, metrics, seed reproducibility, and config loading.
- This step reduces the risk that later LLM pilot failures are caused by environment bugs rather than prompt or model behaviour.

Evidence / basis:

- Implementation necessity.
- Based on `docs/next_plan.md`.
- Based on `docs/detail.md`.
- Based on `configs/experiment_config_stage01.json`.
- Based on `docs/data_schema.md`.

Related citations:

- No new literature citation was introduced in this step.

Files changed or created:

- `src/run_random_baseline.py`
- `tests/test_random_baseline.py`
- `outputs/debug/random_baseline/horizon_random_baseline.json`
- `outputs/debug/random_baseline/igt_random_baseline.json`
- `outputs/debug/random_baseline/bart_random_baseline.json`
- `docs/research_log.md`

Output / result:

- The random runner can build and run all three environments from the stage 01 config.
- Horizon random baseline produced 300 trial records across 40 games.
- IGT random baseline produced 100 trial records.
- BART random baseline produced action-level records and balloon-level metrics for 40 balloons.
- Each output file contains task name, seed, completion status, records, and run-level metrics.

Verification:

- `python -m unittest tests.test_random_baseline`
- Result: 3 tests passed.
- `python -m unittest discover`
- Result: 26 tests passed.
- `python -m src.run_random_baseline --seed 20260528 --output-dir outputs/debug/random_baseline`
- Result: all three random baselines completed and wrote JSON debug outputs.

Status: Done

Next step:

- Implement Phase 7: baseline prompt dry run.
- Add a prompt loader that reads baseline prompt files and inserts task observations.
- Check that prompt response formats match the parser.

Notes:

- The random baseline is not intended as a psychological model. It is a debugging and pipeline validation tool.

### 2026-05-29 - README Project Status Update

Date: 2026-05-29

Phase: Project documentation / implementation status

Step: Update project README after Phase 6

Action:

- Updated `README.md`.
- Added the project aim, task overview, current phase status, project structure, test command, random baseline command, output paths, and next-step guidance.

Why this was done:

- The README was empty.
- After Phase 6, the project has a runnable local pipeline for parser, task environments, and random baseline checks.
- A clear README helps keep the implementation state, usage commands, and next phase visible.

Evidence / basis:

- Project documentation need.
- Based on the current implementation state.
- Based on `docs/detail.md`, `docs/next_plan.md`, and the completed random baseline runner.

Related citations:

- No new literature citation was introduced in this step.

Files changed or created:

- `README.md`
- `docs/research_log.md`

Output / result:

- The repository now has a readable entry-point document.
- The README explains how to run tests and random baselines.
- The README identifies Phase 7 baseline prompt dry run as the next step.

Status: Done

Next step:

- Continue with Phase 7: prompt loader and baseline prompt dry run.

Notes:

- README status should be updated again after the LLM pilot or any major pipeline change.

### 2026-05-29 - Baseline Prompt Dry Run

Date: 2026-05-29

Phase: Implementation / baseline prompt dry run

Step: Implement Phase 7 from `docs/next_plan.md`

Action:

- Added prompt dry-run tests in `tests/test_prompt_dry_run.py`.
- Implemented `src/prompt_loader.py`.
- Implemented `src/run_prompt_dry_run.py`.
- Added a CLI command for checking baseline prompt rendering without calling an LLM.
- Generated `outputs/debug/prompt_dry_run/baseline_prompt_dry_run.json`.
- Updated `README.md` to include Phase 7 status and the dry-run command.

Why this was done:

- Before calling an LLM, the project needs to verify that prompt files can be loaded and rendered correctly.
- The prompt response format must match the parser and the config-defined legal outputs.
- This step reduces the chance that the first LLM pilot fails because of prompt loading or parser-format mismatch.

Evidence / basis:

- Implementation necessity.
- Based on `docs/next_plan.md`.
- Based on `configs/experiment_config_stage01.json`.
- Based on baseline prompt files under `prompts/`.
- Based on the existing parser in `src/parser.py`.

Related citations:

- No new literature citation was introduced in this step.

Files changed or created:

- `src/prompt_loader.py`
- `src/run_prompt_dry_run.py`
- `tests/test_prompt_dry_run.py`
- `outputs/debug/prompt_dry_run/baseline_prompt_dry_run.json`
- `README.md`
- `docs/research_log.md`

Output / result:

- Baseline prompt templates for Horizon, IGT, and BART can be loaded from the config.
- `{observation}` is replaced with the current task state for all three tasks.
- Config-defined valid outputs parse successfully for all three tasks.

Verification:

- `python -m unittest tests.test_prompt_dry_run`
- Result: 4 tests passed.
- `python -m src.run_prompt_dry_run --seed 20260528 --output-path outputs/debug/prompt_dry_run/baseline_prompt_dry_run.json`
- Result: all three tasks reported `placeholder_replaced: true` and `all_config_valid_outputs_parse: true`.
- `python -m unittest discover`
- Result: 30 tests passed.

Status: Done

Next step:

- Implement Phase 8: small LLM pilot runner.
- Start with `3 tasks x baseline prompt x 1 run`.

Notes:

- This dry run does not evaluate prompt quality or model behaviour. It only checks local prompt rendering and parser compatibility.

### 2026-05-29 - Clarify Project Title And Research Aim

Date: 2026-05-29

Phase: Project documentation / research framing

Step: Align README research aim with dissertation title

Action:

- Updated the README title to `How Reliable Are LLMs as Cognitive Models?`
- Added the subtitle `A Systematic Evaluation of Prompt Sensitivity Across Decision-Making Tasks`.
- Rewrote the README research aim section to foreground prompt sensitivity quantification and cognitive-model reliability evaluation.
- Clarified that human data are used as an important reference for evaluating reliability, not as the only or primary research target.

Why this was done:

- The previous README framing over-emphasised whether LLM behaviour is close to human data.
- The user's dissertation title and intended focus are about quantifying LLM sensitivity to different prompts and evaluating whether this sensitivity undermines LLM reliability as cognitive models.

Evidence / basis:

- Project design decision.
- User clarification.
- Dissertation framing requirement.

Related citations:

- No new literature citation was introduced in this step.

Files changed or created:

- `README.md`
- `docs/research_log.md`

Output / result:

- The README now states that the project evaluates prompt sensitivity across decision-making tasks and uses that evidence to assess whether LLMs can be reliable cognitive models.

Status: Done

Next step:

- Keep future documentation, prompt design, analysis scripts, and dissertation writing aligned with this framing.

Notes:

- Future analysis should report human-data comparison as part of reliability evaluation, not as the sole success criterion.

### 2026-05-29 - Prepare Small LLM Pilot Runner

Date: 2026-05-29

Phase: Implementation / small LLM pilot preparation

Step: Prepare Phase 8 API-ready pilot runner

Action:

- Added `tests/test_llm_pilot.py` with fake-client tests that do not call the network.
- Implemented `src/llm_client.py` with a standard-library OpenAI Responses API client and local `.env` loading.
- Implemented `src/run_llm_pilot.py` for the baseline small LLM pilot.
- Updated `.gitignore` to exclude `.env`.
- Updated `README.md` with API key setup and pilot run instructions.

Why this was done:

- The user will provide an API key locally later.
- The project needs the Phase 8 pilot runner prepared before the real API run.
- API keys must not be hard-coded or committed.
- Pilot output must preserve raw model responses, parsed actions, invalid responses, task records, and run-level metrics.

Evidence / basis:

- Implementation necessity.
- API preparation requirement.
- Based on the OpenAI Responses API reference.
- Based on `docs/next_plan.md`.
- Based on the existing parser, prompt loader, and task environments.

Related citations:

- No new academic literature citation was introduced in this step.
- API basis: OpenAI Responses API reference, `POST https://api.openai.com/v1/responses`.

Files changed or created:

- `src/llm_client.py`
- `src/run_llm_pilot.py`
- `tests/test_llm_pilot.py`
- `.gitignore`
- `README.md`
- `docs/research_log.md`

Output / result:

- The codebase is ready for the user to set `OPENAI_API_KEY` and run the minimal baseline LLM pilot.
- Tests use a fake client, so no API calls or costs are incurred during test runs.

Verification:

- `python -m unittest tests.test_llm_pilot`
- Result: 3 tests passed.

Status: Prepared, awaiting local API key

Next step:

- User sets `OPENAI_API_KEY` and optionally `OPENAI_MODEL`.
- Run `python -m src.run_llm_pilot --seed 20260528 --output-dir outputs/pilot/baseline`.

Notes:

- The default model is currently `gpt-4.1`, matching the user's local `.env` setting.
- The first real API run should be treated as a pilot and inspected before scaling up.

### 2026-05-29 - Save Failed LLM Pilot Debug Output

Date: 2026-05-29

Phase: Implementation / small LLM pilot debugging

Step: Improve Phase 8 failure handling

Action:

- Added a failing test for unparsable LLM output in `tests/test_llm_pilot.py`.
- Updated `src/run_llm_pilot.py` so parser failure writes a `*_baseline_pilot_failed.json` debug file before raising `RuntimeError`.
- Updated `README.md` to document failed pilot debug outputs.

Why this was done:

- The first real API pilot failed because the model returned text without the required parser prefix, producing `missing_required_prefix`.
- The previous runner raised an error but did not save the raw model output for inspection.
- Failed pilot attempts need to be reproducible and diagnosable without rerunning paid API calls.

Evidence / basis:

- Pilot-based decision.
- Implementation necessity.
- User-provided traceback from the first Phase 8 API pilot attempt.

Related citations:

- No new literature citation was introduced in this step.

Files changed or created:

- `src/run_llm_pilot.py`
- `tests/test_llm_pilot.py`
- `README.md`
- `docs/research_log.md`

Output / result:

- If parsing fails after all retries, the runner now saves a debug JSON file containing raw model outputs, prompts, observations, invalid responses, current records, metrics, and failure reason.

Verification:

- `python -m unittest tests.test_llm_pilot`
- Result: 4 tests passed.
- `python -m unittest discover`
- Result: 34 tests passed.

Status: Done

Next step:

- Rerun the Phase 8 pilot.
- If parsing fails again, inspect the generated `*_baseline_pilot_failed.json` file before changing prompts or parser rules.

Notes:

- The current parser remains intentionally strict. Whether to loosen it should be decided after inspecting actual failed model outputs.

### 2026-05-29 - Align Pilot Model Setting

Date: 2026-05-29

Phase: Implementation / small LLM pilot configuration

Step: Align model name with local `.env`

Action:

- Checked project files for model-name references.
- Updated `src/run_llm_pilot.py` default model from `gpt-4.1-mini` to `gpt-4.1`.
- Updated README API setup examples to use `gpt-4.1`.
- Updated `configs/experiment_config_stage01.json` `global_settings.model_name` to `gpt-4.1`.
- Updated `docs/detail.md` and previous research-log note to match the selected pilot model.

Why this was done:

- The user configured `OPENAI_MODEL=gpt-4.1` in `.env`.
- Documentation and fallback defaults should match the selected pilot model to avoid accidental runs with a different model.

Evidence / basis:

- Config-based decision.
- User-confirmed local model setting.
- Implementation consistency requirement.

Related citations:

- No new literature citation was introduced in this step.

Files changed or created:

- `src/run_llm_pilot.py`
- `README.md`
- `configs/experiment_config_stage01.json`
- `docs/detail.md`
- `docs/research_log.md`

Output / result:

- The project now consistently uses `gpt-4.1` as the Phase 8 pilot model.

Status: Done

Next step:

- Rerun the Phase 8 pilot using the aligned model setting.

Notes:

- Tests that use `gpt-test` remain unchanged because they use a fake client and do not call the API.

### 2026-05-29 - Handle Markdown-Fenced LLM Pilot Responses

Date: 2026-05-29

Phase: Implementation / small LLM pilot debugging

Step: Handle real BART pilot parser failure

Action:

- Inspected `outputs/pilot/baseline/bart_baseline_pilot_failed.json`.
- Found that the model returned ````text\nACTION: PUMP\n```` instead of a bare `ACTION: PUMP`.
- Added a parser test for valid responses wrapped in a Markdown code fence.
- Updated `src/parser.py` to strip a single surrounding Markdown code fence before strict parsing.
- Updated `src/run_llm_pilot.py` so future parser failures include the debug output path in the error message.
- Updated README test count.

Why this was done:

- The model's decision was semantically valid but wrapped in Markdown formatting.
- The strict parser rejected it as `missing_required_prefix` because the response did not start directly with `ACTION:`.
- For pilot stability, a narrow parser normalisation step is appropriate when the only extra content is a Markdown code fence.

Evidence / basis:

- Pilot-based decision.
- Real API pilot output from `bart_baseline_pilot_failed.json`.
- Implementation necessity.

Related citations:

- No new literature citation was introduced in this step.

Files changed or created:

- `src/parser.py`
- `src/run_llm_pilot.py`
- `tests/test_parser.py`
- `README.md`
- `docs/research_log.md`

Output / result:

- Parser now accepts strict valid responses wrapped in one Markdown code fence.
- Parser still rejects plain missing-prefix responses such as `A`.
- Future LLM pilot failures now show the debug JSON path directly in the raised error.

Verification:

- `python -m unittest tests.test_parser`
- Result: 7 tests passed.
- `python -m unittest tests.test_llm_pilot`
- Result: 4 tests passed.
- `python -m unittest discover`
- Result: 35 tests passed.

Status: Done

Next step:

- Rerun the Phase 8 pilot.
- Inspect any remaining failed debug JSON if another parser issue appears.

Notes:

- This is a narrow parser normalisation, not a broad acceptance of explanatory text.

### 2026-05-29 - Baseline LLM Pilot Completed

Date: 2026-05-29

Phase: Implementation / small LLM pilot

Step: Complete Phase 8 baseline pilot

Action:

- Reran the baseline LLM pilot after parser normalisation.
- Checked all three output files under `outputs/pilot/baseline/`.
- Updated README with pilot completion summary and next-step direction.

Why this was done:

- Phase 8 needed to verify the full baseline prompt + LLM API + parser + task runner + metric pipeline.
- After the previous BART parser failure was fixed, the pilot needed to be rerun and checked.

Evidence / basis:

- Pilot-based decision.
- Generated output files:
  - `outputs/pilot/baseline/horizon_baseline_pilot.json`
  - `outputs/pilot/baseline/igt_baseline_pilot.json`
  - `outputs/pilot/baseline/bart_baseline_pilot.json`

Related citations:

- No new literature citation was introduced in this step.

Files changed or created:

- `outputs/pilot/baseline/horizon_baseline_pilot.json`
- `outputs/pilot/baseline/igt_baseline_pilot.json`
- `outputs/pilot/baseline/bart_baseline_pilot.json`
- `README.md`
- `docs/research_log.md`

Output / result:

- Horizon baseline pilot completed with 300 LLM outputs, 300 trial records, 0 invalid responses, and parse success rate 1.0.
- IGT baseline pilot completed with 100 LLM outputs, 100 trial records, 0 invalid responses, and parse success rate 1.0.
- BART baseline pilot completed with 379 LLM outputs, 379 action records, 40 balloon records, 0 invalid responses, and parse success rate 1.0.

Status: Done

Next step:

- Start Phase 9: write and pilot the remaining prompt conditions.
- Expand the runner to support task and prompt-condition selection before scaling to formal experiment runs.

Notes:

- The previous `bart_baseline_pilot_failed.json` should be treated as a debug artifact from the earlier failed attempt, not as the final BART pilot result.

### 2026-05-29 - Create Neutral Baseline Prompts

Date: 2026-05-29

Phase: Prompt design / baseline refinement

Step: Preserve task-named baseline and create neutral baseline

Action:

- Preserved the original task-name prompt files as:
  - `prompts/bandit/baseline_task_named.md`
  - `prompts/igt/baseline_task_named.md`
  - `prompts/bart/baseline_task_named.md`
- Rewrote current `baseline.md` titles to remove classic task names:
  - Horizon baseline title changed to `Two-Option Decision Task Baseline Prompt`.
  - IGT baseline title changed to `Four-Deck Card Task Baseline Prompt`.
  - BART baseline title changed to `Balloon Decision Task Baseline Prompt`.
- Added `task_named_baseline` paths to `configs/experiment_config_stage01.json`.
- Added tests to confirm neutral baselines do not include classic task names and task-named baseline paths remain available.
- Updated README prompt file list and next-step notes.

Why this was done:

- The first baseline pilot suggested possible task-name leakage, especially in IGT where the model strongly preferred Deck D.
- The original task-named prompts may still be useful later as an explicit comparison condition.
- The main baseline should avoid exposing classic task names so model behaviour is less likely to reflect memorised task knowledge.

Evidence / basis:

- Pilot-based decision.
- Prompt design necessity.
- Based on observed Phase 8 baseline pilot behaviour.

Related citations:

- No new literature citation was introduced in this step.

Files changed or created:

- `prompts/bandit/baseline.md`
- `prompts/bandit/baseline_task_named.md`
- `prompts/igt/baseline.md`
- `prompts/igt/baseline_task_named.md`
- `prompts/bart/baseline.md`
- `prompts/bart/baseline_task_named.md`
- `configs/experiment_config_stage01.json`
- `tests/test_prompt_dry_run.py`
- `README.md`
- `docs/research_log.md`

Output / result:

- The default baseline prompt condition is now neutral with respect to classic task names.
- The original task-named baseline prompts are preserved for future leakage/task-awareness comparison.

Verification:

- `python -m unittest tests.test_prompt_dry_run`
- Result: 6 tests passed.
- `python -m src.run_prompt_dry_run --seed 20260528 --output-path outputs/debug/prompt_dry_run/baseline_prompt_dry_run.json`
- Result: all three neutral baselines rendered and parsed successfully.
- `python -m json.tool configs/experiment_config_stage01.json`
- Result: config JSON is valid.

Status: Done

Next step:

- Rerun a baseline pilot using the neutral baseline prompts.
- Compare neutral baseline behaviour against the previous task-named baseline pilot.

Notes:

- The old pilot outputs under `outputs/pilot/baseline/` were generated with the task-named baseline prompts and should be labelled accordingly during analysis.

### 2026-05-30 - Add History-Rich Observations

Date: 2026-05-30

Phase: Implementation / task observation design

Step: Add structured task memory to IGT and BART

Action:

- Added tests for history-rich observations in `tests/test_igt.py` and `tests/test_bart.py`.
- Updated `IGTTaskEnvironment.get_observation()` to include:
  - previous trial feedback,
  - deck-level selection and net-outcome summary,
  - recent choices and outcomes.
- Updated `BARTTaskEnvironment.get_observation()` to include:
  - previous balloon outcome,
  - recent balloon outcomes,
  - overall completed-balloon summary.
- Updated README to document the history-rich observation design and the recommended next pilot output path.

Why this was done:

- API calls are stateless by default, while human participants remember previous choices and outcomes during continuous cognitive tasks.
- Without task memory in the observation, LLM behaviour in IGT and BART is difficult to compare fairly with human data.
- The previous IGT pilot strongly preferred Deck D despite limited feedback history in the prompt, suggesting the need to make task memory explicit and controlled.

Evidence / basis:

- Pilot-based decision.
- Cognitive task design requirement.
- Implementation necessity.

Related citations:

- No new literature citation was introduced in this step.

Files changed or created:

- `src/tasks/igt.py`
- `src/tasks/bart.py`
- `tests/test_igt.py`
- `tests/test_bart.py`
- `README.md`
- `docs/research_log.md`

Output / result:

- IGT and BART observations now provide structured memory summaries that make trial-by-trial and balloon-by-balloon behaviour more interpretable.
- This supports a fairer comparison between LLM behaviour and human continuous-task behaviour.

Verification:

- `python -m unittest tests.test_igt`
- Result: 6 tests passed.
- `python -m unittest tests.test_bart`
- Result: 7 tests passed.
- `python -m unittest discover`
- Result: 39 tests passed.

Status: Done

Next step:

- Rerun neutral baseline pilot with history-rich observations:
  `python -m src.run_llm_pilot --seed 20260528 --output-dir outputs/pilot/neutral_baseline_with_history`

Notes:

- Horizon already includes observed reward histories for both options, so it was not changed in this step.

### 2026-05-30 - Complete Prompt Expansion And Condition-Aware Pilot Runner

Date: 2026-05-30

Phase: Prompt design / runner expansion

Step: Prepare Phase 9 prompt conditions

Action:

- Added all remaining prompt files:
  - `prompts/bandit/detailed.md`
  - `prompts/bandit/role_human.md`
  - `prompts/bandit/uncertainty_emphasis.md`
  - `prompts/igt/detailed.md`
  - `prompts/igt/role_human.md`
  - `prompts/igt/reward_loss_emphasis.md`
  - `prompts/bart/detailed.md`
  - `prompts/bart/role_human.md`
  - `prompts/bart/risk_emphasis.md`
- Extended `src/run_llm_pilot.py` so the runner supports `--condition`.
- Extended `src/run_llm_pilot.py` so the CLI supports `--tasks`.
- Kept `run_baseline_llm_pilot()` as a compatibility wrapper around the condition-aware runner.
- Added tests confirming all configured prompt paths exist, use `{observation}`, and include valid outputs.
- Added tests confirming non-baseline pilot conditions produce condition-specific output files.
- Updated README, `docs/detail.md`, and `docs/task_parameters.md`.

Why this was done:

- Formal prompt sensitivity evaluation requires all task x prompt-condition combinations to exist before pilot expansion.
- The runner must support running one condition at a time for small pilot checks.
- All formal prompt conditions should share the same history-rich observation structure so differences reflect prompt wording/framing rather than different visible task memory.

Evidence / basis:

- Prompt design necessity.
- Implementation necessity.
- Pilot-based decision from the history-rich observation comparison.

Related citations:

- No new literature citation was introduced in this step.

Files changed or created:

- `prompts/bandit/detailed.md`
- `prompts/bandit/role_human.md`
- `prompts/bandit/uncertainty_emphasis.md`
- `prompts/igt/detailed.md`
- `prompts/igt/role_human.md`
- `prompts/igt/reward_loss_emphasis.md`
- `prompts/bart/detailed.md`
- `prompts/bart/role_human.md`
- `prompts/bart/risk_emphasis.md`
- `src/run_llm_pilot.py`
- `tests/test_prompt_dry_run.py`
- `tests/test_llm_pilot.py`
- `README.md`
- `docs/detail.md`
- `docs/task_parameters.md`
- `docs/research_log.md`

Output / result:

- The project now has prompt files for all configured prompt conditions.
- The LLM pilot runner can run a specified condition using `--condition`.
- The official design now states that all formal prompt conditions use the same history-rich observation structure.

Verification:

- `python -m unittest tests.test_prompt_dry_run`
- Result: 7 tests passed.
- `python -m unittest tests.test_llm_pilot`
- Result: 6 tests passed.

Status: Done

Next step:

- Run small pilots for the non-baseline conditions, one condition at a time.
- Suggested commands:
  - `python -m src.run_llm_pilot --condition detailed --seed 20260528 --output-dir outputs/pilot/detailed`
  - `python -m src.run_llm_pilot --condition role_human --seed 20260528 --output-dir outputs/pilot/role_human`
- Task-specific conditions should be piloted by task using `--tasks`.

Notes:

- The current runner applies one condition name across all requested tasks. Common conditions such as `baseline`, `detailed`, and `role_human` can be run across all tasks directly. Task-specific conditions should be run with the matching task only.

### 2026-05-30 - Task-Specific Prompt Pilots Completed

Date: 2026-05-30

Phase: Pilot / task-specific prompt conditions

Step: Run Phase 10 task-specific prompt pilots

Action:

- Ran Horizon `uncertainty_emphasis` pilot.
- Ran IGT `reward_loss_emphasis` pilot.
- Ran BART `risk_emphasis` pilot.
- Checked output metrics, invalid response counts, and parse success rates.

Why this was done:

- Task-specific prompt conditions are part of the planned prompt sensitivity matrix.
- Each task-specific condition should be piloted separately before any formal repeated-runs experiment.

Evidence / basis:

- Pilot-based decision.
- Prompt sensitivity design.

Related citations:

- No new literature citation was introduced in this step.

Files changed or created:

- `outputs/pilot/horizon_uncertainty/horizon_uncertainty_emphasis_pilot.json`
- `outputs/pilot/igt_reward_loss/igt_reward_loss_emphasis_pilot.json`
- `outputs/pilot/bart_risk/bart_risk_emphasis_pilot.json`
- `docs/research_log.md`

Output / result:

- Horizon uncertainty emphasis: 300 outputs, 0 invalid responses, parse success rate 1.0.
- IGT reward-loss emphasis: 100 outputs, 0 invalid responses, parse success rate 1.0.
- BART risk emphasis: 354 outputs, 0 invalid responses, parse success rate 1.0.

Key pilot metrics:

- Horizon uncertainty emphasis: exploration rate 0.35, directed exploration 0.90, horizon effect 0.10.
- IGT reward-loss emphasis: advantageous choice rate 0.86, Deck C rate 0.30, Deck D rate 0.56, final cumulative score 4100.
- BART risk emphasis: average pumps 8.15, adjusted average pumps 9.43, explosion rate 0.30, total earnings 13.20.

Verification:

- `python -m unittest discover`
- Result: 42 tests passed.

Status: Done

Next step:

- Analyze and compare all available pilot conditions: baseline with history, detailed, role_human, and task-specific prompts.

Notes:

- The first attempt to run Horizon task-specific pilot failed under sandboxed network permissions. It was rerun with approved network access and completed successfully.

### 2026-05-30 - Pilot Run 01 Analysis Document

Date: 2026-05-30

Phase: Pilot analysis / documentation

Step: Summarise first pilot matrix

Action:

- Created `docs/pilot_run01_analysis.md`.
- Summarised completed pilot conditions, parse stability, task-level metrics, cross-task prompt sensitivity patterns, limitations, and next-step recommendations.

Why this was done:

- The first pilot matrix now includes baseline with history, detailed, role_human, and task-specific prompt conditions.
- A written analysis is needed to prepare for supervisor discussion and to guide the next formal-experiment planning step.

Evidence / basis:

- Pilot-based decision.
- Generated pilot JSON outputs under `outputs/pilot/`.

Related citations:

- No new literature citation was introduced in this step.

Files changed or created:

- `docs/pilot_run01_analysis.md`
- `docs/research_log.md`

Output / result:

- A structured pilot analysis document now exists.
- It identifies BART as the task with the strongest apparent prompt sensitivity in the current single-run pilot.
- It identifies history-rich observation as a necessary design choice for sequential cognitive task comparison.

Status: Done

Next step:

- Implement scripts to aggregate multiple pilot/formal runs into run-level metric tables.

Notes:

- The document explicitly marks current findings as pilot observations rather than formal statistical conclusions.

### 2026-06-03 - Rerun Single-Run Pilot Matrix With Average Metrics

Date: 2026-06-03

Phase: Pilot rerun / metric alignment

Step: Regenerate pilot outputs after changing total outcome metrics to average outcome metrics

Action:

- Updated the OpenAI API client to retry transient request failures, including read timeouts, HTTP 429, and HTTP 5xx errors.
- Added a unit test confirming the client retries a transient timeout and then returns a successful response.
- Reran the 12 single-run pilot outputs as separated task-by-task commands:
  - Horizon: `baseline`, `detailed`, `role_human`, `uncertainty_emphasis`
  - IGT: `baseline`, `detailed`, `role_human`, `reward_loss_emphasis`
  - BART: `baseline`, `detailed`, `role_human`, `risk_emphasis`
- Used the updated average run-level metrics:
  - Horizon: `average_reward_per_trial`
  - IGT: `average_net_outcome`
  - BART: `average_earning_per_balloon`

Why this was done:

- Total outcome metrics are harder to compare across human participants and LLM runs when task lengths or dataset scales differ.
- Average outcome metrics are more suitable for later human-data comparison.
- Long API pilot runs had intermittent timeout / 503 failures, so transient retry handling was needed to complete task-level pilot runs robustly.

Evidence / basis:

- Implementation necessity.
- Human-comparison design decision.
- Pilot-based decision from observed API timeout and 503 errors.

Related citations:

- No new academic literature citation was introduced in this step.

Files changed or created:

- `src/llm_client.py`
- `tests/test_llm_pilot.py`
- `README.md`
- Updated pilot JSON outputs under:
  - `outputs/pilot/neutral_baseline_with_history/`
  - `outputs/pilot/detailed/`
  - `outputs/pilot/role_human/`
  - `outputs/pilot/horizon_uncertainty/`
  - `outputs/pilot/igt_reward_loss/`
  - `outputs/pilot/bart_risk/`

Output / result:

- All 12 pilot outputs completed with `done = true`.
- All 12 pilot outputs had `parse_success_rate = 1.0`.
- All 12 pilot outputs had `invalid_response_count = 0`.
- Output metrics now include the updated average outcome fields.

Verification:

- `python -m unittest discover`
- Result: 43 tests passed.

Status: Done

Next step:

- Implement analysis scripts to aggregate pilot JSON files and produce run-level metric tables for prompt-condition comparison.

Notes:

- The current single-run pilots are still pilot observations, not formal statistical results.

### 2026-06-03 - Process Human Datasets Into Comparable Metrics

Date: 2026-06-03

Phase: Human data processing / metric alignment

Step: Convert human raw datasets into participant-level metric tables

Action:

- Added `src/process_human_metrics.py`.
- Processed Horizon human data into participant-level metrics.
- Processed IGT 100-trial human data into participant-level metrics.
- Processed BART 40-balloon human data into participant-level metrics.
- Added tests for the human metric processing functions.
- Updated README and the pilot rerun analysis document with processed human metric paths.

Why this was done:

- Later LLM-human comparison will be simpler and more reproducible if human raw data is converted into metric tables that match LLM run-level metrics.
- Human data should be compared at the metric level rather than directly against raw LLM text or raw task records.

Evidence / basis:

- Dataset-based decision.
- Human-comparison design decision.
- Implementation necessity.

Related citations:

- No new academic literature citation was introduced in this step.

Files changed or created:

- `src/process_human_metrics.py`
- `tests/test_process_human_metrics.py`
- `outputs/processed/human_metrics/horizon_human_metrics.csv`
- `outputs/processed/human_metrics/igt_human_metrics.csv`
- `outputs/processed/human_metrics/bart_human_metrics.csv`
- `outputs/processed/human_metrics/summary.json`
- `README.md`
- `docs/pilot_rerun_average_metrics_analysis.md`
- `docs/research_log.md`

Output / result:

- Horizon processed participants: 60
- IGT processed participants: 504
- BART processed participants: 147

Verification:

- `python -m src.process_human_metrics --output-dir outputs/processed/human_metrics`
- `python -m unittest discover`

Status: Done

Next step:

- Implement a comparison/aggregation script that reads LLM pilot JSON files and human metric CSV files into aligned tables.

Notes:

- Horizon `random_exploration` remains a proxy and should be interpreted cautiously.
- BART earning columns may use dataset-specific scaling, so pump-based metrics should be prioritised for human comparison.

### 2026-06-08 - Remove Redundant BART Cash-Out Threshold

Change:

- Removed `cash_out_threshold` from BART run-level metrics, human-data preprocessing, configuration, schema, README, and current analysis documentation.
- Regenerated `outputs/processed/human_metrics/bart_human_metrics.csv`.

Reason:

- Under the current BART rules, every unexploded balloon ends through `CASH_OUT`.
- Therefore, `cash_out_threshold` and `adjusted_average_pumps` were calculated from exactly the same balloons and were numerically identical.
- Retaining both would duplicate one behavioural construct and could double-weight it in later analyses.

Verification:

- `python -m unittest discover -s tests`: 46 tests passed.
- The regenerated BART human CSV no longer contains a `cash_out_threshold` column.

Status: Done

### 2026-06-13 - Replace Horizon Random-Exploration Proxy

Change:

- Removed the old `random_exploration = exploration_rate` proxy from Horizon run metrics and processed human summaries.
- Added `src/horizon_random_exploration.py`.
- Implemented a first-free-choice logistic model following the choice-model logic of Wilson et al. (2014).
- Defined the formal metric as:

```text
random_exploration_effect = decision_noise_h6 - decision_noise_h1
```

- Added run-level Gaussian shrinkage on log reward sensitivity so repeated 40-game LLM runs can be estimated with partial pooling.
- Added loaders for repeated LLM JSON runs and the raw Horizon human dataset.
- Added explicit `insufficient_runs` output when a prompt condition contains only one run.

Method boundary:

- Wilson et al. (2014) provides the decision-noise interpretation and logistic choice-model logic.
- Hierarchical MAP estimation with fixed Gaussian shrinkage is a project-specific adaptation to the smaller number of games per LLM run.
- The result is interpreted as choice variability consistent with random exploration, not proof of a psychologically random mechanism.

Outputs:

- `outputs/processed/pilot_horizon_random_exploration.json`
- `outputs/processed/human_horizon_random_exploration.json`

Verification:

- The four current single-run pilot conditions are correctly marked `insufficient_runs`.
- The human model used 60 participants and 19,200 first-free choices and converged.
- Human condition estimate: `decision_noise_h1 = 6.245`, `decision_noise_h6 = 14.717`, `random_exploration_effect = 8.473`.
- `uv run python -m unittest discover -s tests`: 51 tests passed.

Status: Done

## 2026-07-20: Chinese and Spanish prompt derivation

- Added a prospective multilingual constraint file before creating any target-
  language prompt.
- Derived six `zh-CN`/`es` baselines from the three frozen English baselines.
- Derived 18 variants only from the corresponding baseline in the same language.
- Preserved `{observation}` and all ASCII parser outputs byte-for-byte.
- Added `--language` support to the dry-run and LLM pilot commands and recorded
  `prompt_language` in raw output provenance.
- Kept English as the default and left the completed English formal experiment
  unchanged.
- Marked the new files `pilot_ready`; independent fluent-language review is still
  required before formal freezing.

Status: Implemented and structurally validated; linguistic sign-off pending.

## 2026-07-25: Complete language-aware experimental pipeline

- Completed final semantic review of all Simplified Chinese and Spanish static
  prompts; no meaning-changing defect required a prompt edit.
- Added language-specific dynamic observation and history renderers for Horizon,
  IGT, and BART.
- Verified that rendering observations in three languages does not mutate hidden
  task state or random outcomes.
- Changed the aggregation identity to
  `prompt_language + task + prompt_condition + seed`, with legacy raw files
  defaulting to English.
- Changed metric summaries, Hedges' g, paired bootstrap intervals, and PSI to
  operate within language.
- Added a three-language, paired-seed Friedman omnibus analysis with Kendall's W
  and within-seed permutation p-values. Pairwise language comparisons are not
  part of the primary analysis.
- Added a second omnibus analysis comparing within-language
  `condition - baseline` prompt effects across all three languages together.
- Added a 36-prompt `--all-languages` dry run and a machine-readable multilingual
  pilot freeze.

Status: Implemented; ready for a small multilingual API pilot before formal data
collection.

## 2026-07-25: Add resumable multilingual experiment runner

- Re-ran the complete 36-prompt multilingual dry run; all prompt loading,
  localized observation rendering, and parser-format checks passed.
- Added `src/run_multilingual_experiment.py` to construct and sequentially run
  the frozen language × task × prompt-condition × seed matrix.
- Added strict identity-aware resume checks and a continuously updated
  `multilingual_run_status.json` containing completed, skipped, and failed runs.
- Added a plan-only mode that makes no API calls and reports request bounds.
- For seeds `20260528,20260531`, the plan contains 72 task runs: 7,200 Horizon
  requests, 2,400 IGT requests, and 960–30,720 BART requests, giving a total
  bound of 10,560–40,320 API requests.
- Added focused tests for matrix size, duplicate seed rejection, full resume
  identity validation, and status persistence when all work is skipped.

Status: Local planning and validation complete; paid API execution awaits an
explicit quota/cost confirmation.

## 2026-07-26: Multilingual pilot blocked by API connectivity

- Received explicit approval to start the two-seed, three-language API pilot.
- The first sandboxed attempt failed with Windows socket permission error
  `WinError 10013`.
- Retried with approved external network access. All 72 task runs still failed:
  70 with TLS `UNEXPECTED_EOF_WHILE_READING` and two with the remote connection
  closing without a response.
- A separate unauthenticated endpoint check could not connect to
  `api.openai.com:443`, confirming an environment/network connectivity problem
  rather than a prompt-rendering or parser failure.
- No successful model response or analysis-ready multilingual run was created.
  Failure details remain in
  `outputs/multilingual_v01/multilingual_run_status.json`.

Status: API pilot blocked until the execution environment can reach the OpenAI
Responses API; the resumable experiment plan remains ready.
## 2026-07-31: English cross-model interaction inference terminology

- Replaced the planned causal-sounding `difference-in-differences` label with
  `model-by-prompt interaction contrast`; the algebraic contrast is unchanged.
- Audited the seed mechanism: Horizon and BART use the seed for environment
  randomness, IGT ignores it, and the API sampling is not seed-coupled.
- Consequently, Horizon/BART uncertainty resamples matched environment-seed
  blocks, whereas IGT resamples runs independently within each model-prompt
  cell.
- Added Efron (1979), Efron (1987), Konietschke and Pauly (2014), and Kleijnen
  (1988) to `docs/citation_map.md`, including explicit limits on what each
  reference supports.

## 2026-07-31: English two-model Figures 2-5

- Added a reproducible Matplotlib figure pipeline and declared/locked the
  plotting dependency.
- Generated run-level distributions, within-model prompt-effect forests,
  metric-specific model-by-prompt interaction forests, and PSI comparison
  panels as both 300-dpi PNG and vector PDF.
- Kept incompatible behavioural metrics on separate axes, disclosed that PSI
  differences are descriptive without intervals, and added manuscript-ready
  captions with interpretation limits.

## 2026-07-31: Two-model human-reference comparison and Figure 6

- Re-ran the frozen human-reference pipeline separately for GPT-4.1 and GPT-5.4
  using identical Horizon (60), IGT (504), and BART (141) reference datasets.
- Added a validated combined table with signed and absolute human-SD distance,
  reference-interval coverage, and changes from each model's baseline.
- Generated Figure 6 with metric-specific human reference bands and prioritised
  pump-based BART measures to avoid monetary-scale mismatch.
- Standardised all figure condition orders to baseline, detailed, human role,
  and the task-specific emphasis condition.
- Retained the explicit boundary that distributional similarity does not imply
  a shared cognitive mechanism.

## 2026-07-31: Main Tables 1-6 and primary-results checklist

- Added a reproducible builder for the six planned main manuscript tables.
- Enforced frozen row counts for design/provenance, primary descriptives,
  within-model effects, model-by-prompt interactions, PSI, and human-reference
  comparisons.
- Generated 218 source-linked checklist statements, covering every row in
  Tables 2-6 exactly once.
- Documented why FDR-adjusted p-values are not inserted into Table 3 without a
  pre-specified null-resampling test; effect sizes and bootstrap intervals
  remain the current frozen inferential outputs.

## 2026-07-31: Chinese analysis and manuscript-output map

- Added a Chinese current-state overview covering the exact two-model LLM
  design, eight primary metrics, supplementary metrics, frozen human datasets,
  required comparisons, six main tables, six main figures, and planned
  supplementary package.
- Distinguished completed artifacts from pending robustness, multiplicity,
  Figure 1, and supplementary work.
- Recorded a pre-writing correction: IGT ignores the nominal run seed, so its
  existing within-model prompt-effect and PSI bootstrap intervals must be
  regenerated using independent model-prompt-cell resampling. Point estimates
  are unaffected; Tables 3/5 and Figures 3/5 are not final until this is done.

## 2026-08-02: Rename prompt-variant generation protocol

- Renamed the current protocol file from the development-oriented
  `meta_prompt_v2.md` to
  `controlled_prompt_variant_generation_protocol.md`.
- Updated the generator default path and current documentation.
- Preserved the old path and heading inside immutable 2026-06-14 request and
  generation records because they document the artifact actually used then.
# 2026-08-05: Draft the thesis Introduction

- Added the first full English Introduction to `docs/introduction_draft.md`
  and inserted the same prose into `tmp/final_working.md`.
- Structured the argument around LLMs as behavioural/cognitive research
  objects, prompt-dependent measurement, the gap in repeated interactive-task
  robustness, controlled cross-language comparison, task coverage, and four
  research questions.
- Kept prompt stability, task performance, and human-reference proximity as
  separate criteria and avoided treating human-like behaviour as evidence of
  shared mechanism.
- Added a 21-item working bibliography covering synthetic participants,
  cognitive-model framing, prompt sensitivity, multilingual evaluation, and
  the Horizon, IGT, and BART paradigms and datasets.
- Web checks used primary publisher, proceedings, and paper records where
  available. A final bibliography-manager audit remains required before
  submission, especially for proceedings pagination and the newest preprint.

## 2026-08-10: Align inference code with the revised Method

- Changed pooled-SD Hedges' g so that every zero pooled-SD case is undefined:
  equal constants retain raw difference 0 with `constant_equal`, and unequal
  constants retain their raw difference with `constant_unequal`.
- Undefined standardised effects are no longer replaced by zero; PSI requires
  all configured component g values to be defined for a complete estimate.
- Added per-interval bootstrap validity diagnostics and frozen reporting gates:
  at least 95% valid for routine reporting, 90%--<95% with a stability warning,
  and below 90% withheld.
- Changed LLM and human Horizon exploration-rate helpers to return missing when
  no eligible non-tied choices exist; Horizon-related exploration change is
  missing when either H1 or H6 is undefined.
- Propagated validity status to within-model effects, PSI, cross-model
  interactions, cross-language contrasts, and hierarchical Random-exploration
  bootstrap outputs.
- Updated the Method and Results/Discussion execution plan to require explicit
  human--LLM Random-exploration specification alignment before RQ4 reporting.
- The targeted suite (45 tests) and full suite (149 tests) passed before any
  formal output regeneration.

## 2026-08-10: Regenerate the final RQ1--RQ4 analysis package

- Added a frozen per-language provenance allowlist for the reused English
  config version 0.5 and newly collected Chinese/Spanish version 0.7. The
  aggregation validator still rejects within-language mixing and unexpected
  versions and records the observed mapping in its quality report.
- Regenerated `outputs/processed/final_analysis_v03/`: English RQ1 outputs for
  GPT-4.1, GPT-5.4 and GPT-5.4 Mini; multilingual GPT-4.1 RQ1/RQ3 outputs; and
  both prespecified candidate-model-minus-GPT-5.4 RQ2 contrast sets.
- The multilingual aggregation contains 720 valid runs, 20 per each of 36
  language-task-prompt cells, with no quality issues. RQ3 contains 16 Neutral
  baseline contrasts and 48 language-by-prompt interactions.
- All RQ1, PSI, RQ2 and RQ3 intervals passed the frozen reporting threshold;
  each used 2,000/2,000 valid replicates.
- Refit human and all formal LLM Random-exploration cells with the same model
  specification and the 0.25/0.5/1.0 shrinkage grid. Every point-estimate and
  sensitivity fit converged, so the metric remains eligible for descriptive
  RQ4 comparison.
- Rebuilt human-reference comparisons for English three-model and GPT-4.1
  multilingual cells. The combined package contains 160 comparison rows and
  120 manipulated-minus-Neutral change rows, using the precise
  `human-SD-scaled mean deviation` terminology.
- Added and ran `src/build_final_analysis_manifest.py`; the final manifest
  reports `analysis_ready=true`, no failures, and hashes every claim-bearing
  table, diagnostic file, run-metric input and frozen configuration.
- Drafted separate Results and Discussion sections in
  `tmp/final_revision_all.md` after the manifest passed. Results report the
  final RQ1--RQ4 estimates without mechanism claims; Discussion interprets the
  patterns against the audited literature and states model, language,
  human-reference, multiplicity and deployment limitations.
- Replaced the Introduction's Results-achieved placeholder with a concise
  findings summary and updated the document-structure paragraph to distinguish
  Results from Discussion.
- Re-audited Method after final output generation. Clarified that the two
  720-run designs share 240 English GPT-4.1 runs (1,200 unique total), promoted
  Neutral baseline language contrasts to primary RQ3 analyses, removed an
  unsupported claim about exact proprietary-tokenizer prompt counts, aligned
  bootstrap diagnostic wording with the actual output schema, and documented
  the frozen English-0.5 versus Chinese/Spanish-0.7 provenance mapping.
- Kept the exact config-version mapping in technical provenance records but
  removed those engineering identifiers from the manuscript body. Method and
  Results now state only the batch-level provenance checks relevant to
  interpretation and direct readers to the appendix/quality report for detail.
- Added `src/build_results_visual_package.py` and generated the final visual
  Results package from `final_analysis_v03`: RQ1/RQ2 forest plots, an RQ3
  baseline forest plot, RQ3 interaction heatmaps, and paired RQ4 deviation/
  coverage heatmaps. Every figure is available as vector PDF and 600-dpi PNG.
- Added two LaTeX tables (sample/quality and RQ summary) plus ready-to-input
  figure environments in `docs/results_visuals/`. Static QA and raster visual
  inspection passed; local LaTeX compilation could not be run because no TeX
  engine is installed in the current environment.
- Integrated the visual package into `tmp/final_revision_all.md`. Rewrote the
  Results prose to point to Tables 1--2 and the RQ-specific figures, retained
  only representative raw estimates, clarified the non-multiplicity-adjusted
  heatmap marker, and merged the separate robustness subsection into the
  analysis-quality section. Results now contains exactly five subsections.
## 2026-08-11 — Symmetric joint-language RQ3 revision

- Replaced the English-reference RQ3 specification with a joint, effect-coded comparison of English, Simplified Chinese, and Spanish.
- Added `src/compute_joint_language_contrasts.py`. Neutral means and within-language prompt effects are centred on their corresponding three-language means; the three language deviations sum to zero, so no language is a reference category.
- Generated 24 centred Neutral deviations and 72 centred prompt-effect deviations with 2,000-replicate task-appropriate bootstrap intervals.
- Updated the analysis manifest, RQ3 figure, Method, Results, Discussion, Conclusion, and README to use only the symmetric three-language estimands.


## 2026-08-16 - Thesis draft copy-edit (skeleton_repaired.tex)

- Copy-edited the submission draft in `skeleton_repaired.tex` (the file that
  produced the 2026-08-12 `dissertation.pdf`). Changes are presentation-level
  precision fixes; no task, metric, model, language, prompt, RQ, estimand, or
  analysis result was altered.
- Clarified the Horizon structure: four forced choices precede one free choice
  in H1 and six free choices in H6, matching `src/tasks/horizon.py`.
- Made the behavioural-metric scopes explicit: information-seeking rate uses
  first free choices in unequal-information games, while the horizon-related
  exploration-change rate includes first free choices from both game types with
  pre-choice mean ties excluded.
- Added the run-level random effect notation to the random-exploration model and
  stated the number of primary metrics per task in the PSI definition.
- Clarified the human-reference wording for the Horizon sample (320 games per
  participant versus 40 games per LLM run) and normalised CI interval spacing
  in Results.
- Removed a garbled non-ASCII comment from the preamble, standardised two
  subsection titles, and added missing publisher fields to eight bibliography
  entries in `mybibfile.bib`.
- Verified all 45 citation keys resolve, all 16 cross-references resolve, brace
  balance is intact, and all 60 representative estimates cited in Results match
  `outputs/processed/final_analysis_v03` exactly (three values differ only by
  3-decimal rounding).


## 2026-08-16 (second pass) - Manuscript re-synced from user export

- The project copy of `skeleton_repaired.tex` was replaced by the user's
  updated export `E:/download/skeleton (2).tex` (same content as the
  pre-copy-edit working tree: it contains the user's earlier uncommitted
  revisions but not the 2026-08-16 copy-edit).
- Re-applied the full copy-edit pass on the restored file: Horizon structure
  wording, metric-scope clarifications, random-exploration notation, human
  reference sample wording, PSI definition, reproducibility wording, preamble
  comment cleanup, subsection title casing, and CI interval spacing.
- `intro_academic_english.tex` remains deleted per the user's file management;
  it is an intermediate draft not referenced by the manuscript.
- Verified after the sync: all 45 citation keys resolve, all cross-references
  resolve, no non-ASCII characters remain in the manuscript, brace balance is
  intact, and the manuscript compiles logically with `mybibfile.bib` (local TeX
  engine still unavailable, so final compilation must run in Overleaf).


## 2026-08-16 (third pass) - Content revision addressing reviewer feedback

- Results interpretation: added per-figure key-pattern prose and precision
  counts to RQ1--RQ4, all verified against final_analysis_v03. RQ1: 29/72
  condition-minus-Neutral intervals exclude zero (43 straddle); RQ2: 19/48
  interaction contrasts exclude zero; RQ3: 15/24 centred baselines and 31/72
  centred prompt effects exclude zero; RQ4: absolute deviation closer in 69/120
  cells, coverage unchanged in 55/120, opposite-direction movement in 49/120.
  Analysis Sample now states explicitly that more than half of the primary
  RQ1--RQ3 intervals straddle zero, so conclusions rest on direction and
  concentration rather than isolated interval exclusions.
- Study design: expanded the 20-runs-per-cell rationale (balanced 720-run arms
  and 1,200-run total under a computational budget, no prespecified precision
  target, bootstrap intervals as the primary uncertainty expression).
- Random exploration: added a non-technical account of the hierarchical choice
  model (evidence score, inverse temperature as consistency, decision noise as
  its inverse, and the H6-vs-H1 noise difference as the random-exploration
  effect).
- Discussion: added a paragraph on framework transferability to vision-language
  models, tool-using agents, and embodied decision-makers (fixed measurement
  specification, prespecified formulation variants, complete-trajectory units,
  bootstrap uncertainty, descriptive reference), and strengthened the
  non-normative reading of the human reference (proximity is a coordinate for
  comparing measurement specifications, not a target for model quality).
- All citation keys, labels, brace balance, and the absence of non-ASCII
  characters were re-verified; added text adds roughly 2,300 characters
  (~0.3--0.4 body pages), so Overleaf compilation should confirm the page count.


## 2026-08-16 (fourth pass) - Horizontal overflow fixes

- Diagnosed the overfull lines by parsing the rendered PDF: the true text right
  edge is 524.4 pt, and characters extending past it were located page by page.
  Overflows were found in the model-settings `texttt` line (up to x=591),
  the BART explosion equation tail ("32." at x=539), the 3.8 GitHub URL
  (x=569), appendix `url` lines (x=544-567), several body lines (x=526-539),
  the abstract Keywords line, and the long section headings 2.1, 2.4, 2.6 and
  4.5.
- Fixes applied to `skeleton_repaired.tex`: split `texttt{parameter = value}`
  into `texttt{parameter} = value` for all four generation settings; moved the
  "for k = 1,...,32" range of the BART formula into prose; replaced the URL
  block's `Urlmuskip` tweak with `sloppy`; added `sloppy` for the appendix;
  added `emergencystretch=2em` to the preamble to absorb residual body-line
  overflows; and shortened headings 2.1, 2.4 and 4.5 (4.5 is now "RQ4:
  Prompt-Associated Proximity Changes"), which also shortens the running
  header on the RQ4 pages.
- Re-verified citations (45/45), labels, brace balance, and the absence of
  non-ASCII characters. Final visual confirmation still requires an Overleaf
  compile because no local TeX engine is available.


## 2026-08-16 (fifth pass) - RQ4 figure redraw

- Redrew `figure_rq4_human_reference_overview` because the bottom-row x-axis
  tick labels (metric x condition, two-line labels) overlapped at the original
  8.2-inch width.
- Changed `figure_rq4_v2` in `src/build_results_visual_package.py`: canvas
  widened from (8.2, 11.0) to (12.4, 11.0) inches, and x tick labels are now
  rotated 30 degrees. Data, colour scales, annotations, and cell values are
  unchanged (read from the same `model_human_distance_changes.csv`).
- Regenerated the 600-dpi PNG and the vector PDF in
  `outputs/figures/final_results_v01/`, then copied the PNG and PDF to
  `figures/` so the dissertation graphics path picks up the new version.
- Verified the output: PNG is now 7509x6826 (wider than tall), and a character-
  coordinate check of the vector PDF found no horizontal overlap between
  distinct tick labels.


## 2026-08-16 (sixth pass) - GitHub URL overflow fix

- The 3.8 research-materials URL still overflowed after the earlier sloppy
  pass because the url package does not break after hyphens by default, and
  the repository-name segment ("A-Systematic-Evaluation-...-Tasks", 64
  characters) exceeded one text line in the package's default typewriter
  font (estimated ~533 pt vs a ~454 pt line).
- Fix: switched the preamble to `usepackage[hyphens]{url}` so explicit hyphen
  characters become legal break points, and set `urlstyle{same}` inside the
  3.8 URL block so the URL is typeset in the body font (widest hyphen-free
  segment is now 11 characters, ~66 pt). Kept `raggedright` and `sloppy` in
  the block.
- Re-verified citations, brace balance, and that the URL block contains all
  four settings. Final confirmation still requires an Overleaf compile.


## 2026-08-16 (seventh pass) - Citation audit: removed strained citations

- Audited every `cite` against the sentence it supports. Kept the 43
  remaining citations, which map one-to-one to task originals, human data
  sources, methods references, and directly supporting studies.
- Removed six strained/stacked citation uses in `skeleton_repaired.tex`:
  * Shanahan2023RolePlay (Introduction): a role-play paper was used to support
    "behavioural similarity does not establish a shared mechanism"; the claim
    is now stated as the study position without a citation.
  * Lampinen2024ContentEffects (3 places): that paper reports LLM-human content
    effects in reasoning, which points in the opposite direction from "no
    shared mechanism / proximity is not mechanistic equivalence"; kept
    Lin2025SixFallacies in all three sentences.
  * Webson2022PromptMeaning (1 of 2 places): kept only the semantically
    misleading-instructions claim, where the paper directly applies; removed
    the measurement-procedure sentence use.
  * Wilson2014, Buelow2009IGTValidity, Wallsten2005BARTModel (Section 2.7): a
    five-citation stack on one sentence; the three task papers do not directly
    support "task length/presentation/familiarisation constrain comparison".
    Kept Dillion2023ReplaceParticipants and Bisbee2024SyntheticSurveyData.
- `Shanahan2023RolePlay` and `Lampinen2024ContentEffects` are now uncited in
  the manuscript but remain in `mybibfile.bib` (unsrt only outputs cited
  entries, so the reference list shrinks automatically from 45 to 43 items).
  Reference numbers will renumber after the next compile.


## 2026-08-16 (eighth pass) - Bibliography cleanup after citation audit

- Removed the now-uncited `Shanahan2023RolePlay` and
  `Lampinen2024ContentEffects` entries from `mybibfile.bib` after the user
  approved the citation-audit changes. The manuscript and bibliography are now
  one-to-one: 43 cited keys and 43 bibliography entries, no missing and no
  uncited entries.
- Verified brace balance in both the manuscript and the bibliography.
- The reference list will contain 43 numbered items on the next compile.


## 2026-08-16 (ninth pass) - Address supervisor-review recommendations

Implemented the reviewer-recommended changes in `skeleton_repaired.tex`:
- Replaced the brief RQ summary table with a wider "Results overview with
  representative estimates" table that reports, for each RQ, the interval
  exclusion counts, representative raw estimates with percentile-bootstrap
  95% intervals, and the interpretive boundary. All table values reuse the
  already-audited final_analysis_v03 numbers.
- Strengthened the human-reference positioning: the human mean, SD, and
  interval are now explicitly described as fixed empirical benchmark
  coordinates rather than estimated population parameters, with their sampling
  uncertainty not propagated.
- Made the prompt-variant non-orthogonality an explicit design limitation in
  Method, and reworded the inferential object as the complete formulation, not
  an isolated causal effect of role, specificity, or emphasis.
- Added a sentence that the random-exploration sensitivity fits all converged
  but their magnitudes changed with shrinkage scale, so the main text treats
  that latent estimate as model-dependent rather than precise.
- Left Abstract and Conclusions mostly unchanged because they already state the
  three main lines (conditional reliability, audit framework, non-normative
  human reference) compactly.
- Re-verified citations (43/43), labels, brace balance, and the absence of
  non-ASCII characters.


## 2026-08-16 (tenth pass) - Human-reference uncertainty, transfer checklist, table slim-down

- Added `src/build_human_reference_uncertainty.py`. It bootstrap-resamples the
  participant-level human summaries (2,000 replicates, seed 20260615) for the
  seven directly computed human-reference metrics and reports 95% percentile
  intervals for the reference mean and SD. Output:
  `outputs/processed/final_analysis_v03/human_reference_results/human_reference_bootstrap.csv`
  plus a summary JSON. Random exploration is excluded because its human-side
  value is hierarchical rather than participant-level.
- Updated Method 3.7.6 and Results 4.5 to report that the human reference
  means have bootstrap half-widths from 0.014 to 0.556 in original units, with
  three examples (Horizon information seeking, IGT advantageous choices, BART
  adjusted pumps). Appendix A.2 now lists the new bootstrap file.
- Replaced the RQ summary table with a slimmer four-column version using
  compact "29/72" style counts and one representative example per RQ, to reduce
  reader load.
- Rewrote the Discussion transfer paragraph as an explicit minimal transfer
  checklist (freeze new degrees of freedom; specify modality-specific variants;
  extend the parser; keep trajectories/seeds/snapshots/diagnostics in the
  measurement specification).
- Re-verified citations (43/43), labels, brace balance, and non-ASCII absence.


## 2026-08-16 (eleventh pass) - Manifest update for human bootstrap

- Extended `src/build_final_analysis_manifest.py` to validate and hash the new
  `human_reference_bootstrap.csv` (7 rows) and its summary JSON, then
  regenerated `analysis_manifest.json`; `analysis_ready` remains true with no
  failures.


## 2026-08-16 (twelfth pass) - Consistency fix after third review

- Aligned three sentences with the new human-reference bootstrap reporting:
  * 5.4 Limitations: replaced "fixed human summary statistics were treated
    without propagating their sampling uncertainty" with "reference-summary
    uncertainty was quantified by bootstrap but not propagated through the
    cell-level deviation and coverage changes".
  * 5.4 Future work: future human-reference work should propagate
    reference-sample uncertainty through cell-level deviation and coverage
    changes (rather than "in the reference samples").
  * Conclusions: same propagation wording for the human-reference future-work
    sentence.
- Re-verified citations (43/43), labels, brace balance, and non-ASCII absence.
