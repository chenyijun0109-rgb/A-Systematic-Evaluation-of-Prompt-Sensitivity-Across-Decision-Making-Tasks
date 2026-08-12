# How Reliable Are LLMs as Cognitive Models?

## A Systematic Evaluation of Prompt Sensitivity Across Decision-Making Tasks

The complete English LaTeX manuscript is `final.tex`. A School-template-aligned copy of the user-supplied complete manuscript is maintained as `skeleton_repaired.tex`. Both use the confirmed title *How Reliable Are LLMs as Cognitive Models? A Systematic Evaluation of Prompt Sensitivity Across Decision-Making Tasks*. Their preambles retain `infthesis` with `msccheck`, use only functional formula, table, figure, rotation, and URL packages, and omit `microtype` because it triggers the School checker's `\showhyphens` guard. The long repository URL is set in its own locally ragged-right block so that it can wrap without changing the dissertation's global layout. The manuscript is a polished British-academic-English translation of the current authoritative Chinese manuscript,
with all manuscript tables embedded directly in the file and all figures linked
through explicit `\includegraphics` paths. `final_references.bib` contains the
corresponding bibliography, and `docs/final_overleaf_figure_manifest.md` lists
the seven figure files that must be uploaded to Overleaf. The two concise design diagrams
are generated as 600-dpi PNG files by `src/build_design_figures.py`;
the five Results figures continue to come from the validated final-results
visual package. The RQ3 text and figure use the symmetric joint three-language
centred analysis and do not designate English as a statistical reference.

The current body-length revision is documented in `docs/manuscript_page_reduction_plan.md`. It targets approximately 34--35 body pages without changing font, margins, or 1.5 spacing. Experimental Procedure now explicitly documents cell identification, task selection, frozen prompt lookup, task-specific parsing, state updates, retry handling, and metric derivation. Results use four clockwise landscape overview figures with reduced axis-label density; RQ4 deviation and coverage share one figure while retaining separate scales.

The School-template manuscript uses `unsrt` so numbered references follow first citation rather than alphabetical bibliography order. Results figures are placed within their corresponding RQ sections, use explicit rightward landscape rotation, and have concise captions. Method Tables 3.1 and 3.2 and the Results summary tables have been shortened; detailed definitions remain in the surrounding prose and supplementary materials.

The current formal thesis-writing handoff is
`docs/thesis_writing_handoff_zh.md`. It records the completed three-model
English data scope, authoritative raw and processed paths, exclusions, analysis
boundaries, required three-model table/figure updates, manuscript structure,
writing rules, limitations, and the remaining freeze checklist. Use it as the
current writing entry point. Model-specific prompt-effect, PSI, and human-
reference outputs now cover GPT-4.1, GPT-5.4, and GPT-5.4 Mini; a unified
three-model manuscript table/figure package remains to be generated.

The current integrated Chinese Introduction and Method draft is
`tmp/final_revision_all.md`; the user-facing copy is maintained separately as
`E:\chen\Documents\final.md`. The Introduction frames reliability as
behavioural robustness to controlled prompt reformulation, separates prompt
stability from task-specific behavioural outcomes and human-reference
proximity, incorporates the fixed-model multilingual comparison, and now uses
15 distinct sources. Bibliographic metadata should receive a final
reference-manager check before submission.

`docs/intro_citation_audit_zh.md` records the source-by-source Introduction
citation audit and the redistribution of detailed prompt and multilingual
sources into Background and Related Work.

Background and Related Work in `tmp/final_revision_all.md` uses a compact
thematic-synthesis structure with eight subsections and 30 distinct sources.
It groups multiple studies under each argumentative claim instead of providing
paper-by-paper summaries. The current sequence is: LLMs as behavioural subjects
and computational models; reliability in behavioural measurement; prompt
sensitivity; model variation and reproducibility; language effects; sequential
decision-task constructs; human-reference comparisons; and the research gap.
All 26 substantive review paragraphs contain supporting citations, and each
section links the state of the literature and its methods to critical limits
and the present design.

The end of the Introduction now reserves an explicit 100--150 Chinese-character
results-achieved paragraph to be completed only after the formal results are
frozen. A completed document-roadmap paragraph follows it and outlines the
Background, Method, Results and Discussion, and Conclusion sections.

The Chinese Introduction uses a continuous, unheaded argument, with short
paragraphs to reduce visual density. Its conceptual sequence remains:
cognitive/behavioural framing; prompt sensitivity and measurement reliability;
multilingual context and task selection; and study design, contributions, and
research questions.

The current Chinese inventory of results that need to be reported and
discussed is `docs/results_discussion_inventory_zh.md`. It organises the
provisional three-model findings by baseline behaviour, within-model prompt
effects, model-by-prompt interactions, PSI, human-reference comparison, and
robustness requirements. It also records the interpretation boundaries that
must be respected before the final three-model result package is frozen.

The current Method revision note is
`docs/method_revision_multilingual_metrics_zh.md`. It audits the 2026-08-04
`final.pdf`, supplies paste-ready wording for the behavioural-metric rationale,
removes prose that duplicates the metric table, and adds the formal GPT-4.1
English/Simplified-Chinese/Spanish comparison. It also separates the
three-model English analysis from the fixed-model multilingual analysis and
records the required language-by-prompt comparison and bootstrap units. The
Statistical Analysis sequence is: within-model/within-language prompt effects;
cross-model comparisons with language fixed to English; and cross-language
comparisons with the model fixed to GPT-4.1.

The manuscript Method keeps only equations needed to define task mechanisms
and primary estimands. Routine sample-size expansions, pooled-SD and
small-sample correction details, expanded interaction contrasts, and complete
human-reference change formulas are maintained in
`tmp/appendix_content_zh.md`, Appendix J. This changes presentation only; the
frozen estimands and analysis implementation are unchanged.

The Study Design and Scope subsection now includes the TikZ overview figure in
`docs/figures/study_design_scope.tex`. It visualises the two 720-run comparison
arms, their shared 240-run English GPT-4.1 sample, the 1,200-run deduplicated
dataset, and the complete-run analysis unit. The manuscript includes it with
`\input{study_design_scope.tex}`; the final LaTeX project must place the figure
file beside the main source or adjust that relative path.

The Experimental Procedure and Data Quality subsection includes a second TikZ
flowchart in `docs/figures/experimental_workflow.tex`. It shows specification
freeze, logical-run definition, the repeated observation/API/parser/task-update
cycle, completion and provenance checks, technical-failure handling, run-level
metric construction, and planned analysis. The manuscript includes it with
`\input{experimental_workflow.tex}`.

The external Informatics thesis template `E:\download\skeleton (3).tex`
contains both complete TikZ figures inline, rather than loading separate figure
files. Its preamble uses TikZ with the `positioning`, `arrows.meta`,
`shapes.geometric`, and `calc` libraries. The figures and their textual
references are located in Study Design and Scope and Experimental Procedure and
Data Quality respectively.

## Supervisor Review Deliverable (2026-07-15)

The current compact handoff view is in:

```text
deliverable/
```

This deliverable is the supervisor-review version of the project. It keeps the
repository source, tests, prompts, configs, and methods in their normal
locations, and adds a small result package with the completed primary formal
English-stage processed outputs:

```text
deliverable/README_DELIVERABLE.md
deliverable/results/README.md
deliverable/results/formal_v01/
```

Included formal result files:

```text
aggregation_quality_report.json
analysis_summary.json
llm_run_metrics.csv
metric_summary.csv
prompt_effects.csv
prompt_sensitivity.csv
```

English formal experiment status:

```text
formal_v01: 3 tasks x 4 prompt cells x 20 runs/cell = 240 valid runs
failed files = 0
invalid responses = 0
incomplete runs = 0
aggregation analysis_complete = true
PSI analysis_complete = true
issues = []
```

The English three-model comparison uses the existing GPT-4.1 baseline and two
newer OpenAI models:

```text
gpt-4.1-2025-04-14: complete, outputs/formal_v01
gpt-5.4: complete, 240/240 valid English task runs,
         outputs/model_comparison_en_v01/gpt-5.4
gpt-5.4-mini: complete, 240/240 valid English task runs,
               outputs/model_comparison_en_v01/gpt-5.4-mini-formal-v01
```

Only English (`en`) is in scope; Chinese and Spanish are not launched. A
briefly started GPT-5.4 mini/nano attempt was stopped before any task run
completed. The current credential connects to the OpenAI Responses API, so
GPT-5.4 can be collected automatically and resolved to the dated
`gpt-5.4-2026-03-05` snapshot in the smoke test. It accepts the frozen
temperature `0.7`, top-p `1.0`, and 16-token response limit. The GPT-5.4 formal
English collection uses 20 matched seeds per
task-prompt cell: 3 tasks x 4 prompt cells x 20 runs = 240 task runs. For
stability it is divided into five sequential waves. Every wave starts two
parallel workers, and every worker handles exactly two seeds, so each wave adds
four runs per cell. The next wave starts only after both workers in the current
wave exit. Every two-seed shard has an independent output directory, status
JSON, and log. Earlier scheduling attempts completed zero valid task runs and
are excluded. The selection and status are recorded in
`configs/english_model_comparison_v01.json`.

Collection was paused on 2026-07-30 after both first-wave shards had completed
two task runs each (`4` valid task runs total, zero failures in the active
restart). All scheduler and worker processes were stopped. Running the same
five-wave launcher again resumes safely: existing successful logical runs are
skipped and interrupted work is rerun.

Collection was subsequently resumed at the user's request. The launcher uses
the same shard directories and resume checks, so the four successful task runs
from before the pause remain part of the formal collection.

Standalone repairs for the missing `wave-01-a` Horizon baseline
(`base_seed=20260709`) and `wave-01-b` BART baseline
(`base_seed=20260710`, `task_seed=20260712`) are deferred until the active
formal wave finishes. Their repair processes were stopped so the formal
collection again uses only two concurrent API workers. The deferred repair
queue is recorded in `configs/english_model_comparison_v01.json`.

At the user's request, the active formal scheduler and both formal workers were
paused with 24 valid task runs retained. The two registered baseline repairs
were then started in parallel using the updated `IncompleteRead` retry logic.
Formal collection remains paused until the repairs are reviewed.

After the parallel repairs exhausted their SSL retry budget, they were
restarted sequentially to reduce concurrent API connections: Horizon baseline
runs first, followed by BART baseline. Formal workers remain paused and the
repair concurrency limit is one.

The sequential Horizon repair was later paused before producing a valid JSON
because the user prioritised BART. BART baseline is now run alone with one API
worker; the missing Horizon baseline remains in the deferred repair queue.

The standalone BART repair completed successfully for `base_seed=20260710`
(`task_seed=20260712`) using resolved model `gpt-5.4-2026-03-05`. It produced
101 trials with zero invalid responses and parse success rate `1.0`. Formal
collection remains paused and the Horizon baseline repair is still pending.

Formal collection was then resumed with the explicit policy requested by the
user: do not repair failed logical runs during collection, proceed directly
from each completed wave to the next, finish all five waves, and only then run
a final repair pass for every remaining missing logical run. The successful
BART repair remains valid and is skipped by normal resume checks.

An independent post-collection monitor now waits for the five-wave formal
master to exit. It then scans all ten shard directories and runs missing
logical runs with at most two API workers. Successful files are skipped on
every pass; remaining failures are retried in subsequent passes until all
`240/240` English GPT-5.4 logical runs have valid completed JSON files.

GPT-5.4 English collection completed on 2026-07-31 with all `240/240` logical
runs valid. Strict aggregation found 240 valid runs and no blocking issues.
Prompt-sensitivity analysis completed with 128 metric-summary rows, 24
prompt-effect rows, 9 PSI rows, and `issues=[]`. Processed outputs are in
`outputs/processed/model_comparison_en_v01/gpt-5.4/`.

An additional English GPT-5.4 Mini formal batch uses the same prompts, matched
seeds, sampling parameters, and five-wave dual-worker design. Its isolated raw
output directory is
`outputs/model_comparison_en_v01/gpt-5.4-mini-formal-v01/`. Each worker handles
two seeds. Failures are recorded and skipped during the five formal waves; after
wave 5, the launcher automatically runs two-worker repair passes until all
240 logical runs are valid. Start or safely resume it with:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File scripts/start_gpt54mini_english_20run_five_waves.ps1
```

The GPT-5.4 Mini collection completed with `240/240` successful logical runs.
Three failed attempts that were later repaired were deleted on 2026-08-01 at
the user's request. Formal aggregation reads only the 240 successful runs in
the ten shard directories under `gpt-5.4-mini-formal-v01`.

Strict GPT-5.4 Mini aggregation and prompt-sensitivity analysis are complete in
`outputs/processed/model_comparison_en_v01/gpt-5.4-mini-formal-v01/`: 240 valid
runs, 128 metric-summary rows, 24 prompt-effect rows, 9 PSI rows, and
`issues=[]`. One completed Horizon baseline run (`seed=20260726`) required one
parser retry among 301 responses and has parse success rate `0.99668`; it still
contains all 300 valid task trials. This recovered transient invalid response is
retained and disclosed rather than replacing an otherwise complete run.

The completed GPT-4.1 and GPT-5.4 English batches are compared with
`src.compare_model_results`. It joins identical task-condition-metric keys,
reports GPT-5.4 minus GPT-4.1 mean differences and cross-model pooled-SD
Hedges' g, and separately reports PSI differences. It also computes the primary
model-by-prompt interaction contrast for all 24 primary
task-condition-metric combinations:

```text
[(GPT-5.4 condition - GPT-5.4 baseline)
 - (GPT-4.1 condition - GPT-4.1 baseline)]
```

This is a factorial interaction contrast, not a causal difference-in-differences
design. Uncertainty uses 2,000 bootstrap replicates and the frozen 95%
confidence level. Horizon and BART resample matched environment-seed blocks;
IGT resamples runs independently within model-prompt cells because its fixed
payoff schedule ignores the run seed and API sampling is not seed-coupled.
Metric direction remains task-specific, so a positive value
is not automatically better. Outputs, including
`model_prompt_interaction_contrasts.csv`, are written to
`outputs/processed/model_comparison_en_v01/gpt-4.1_vs_gpt-5.4/`.

For manuscript reporting, GPT-5.4 is the reference model: the planned contrasts
are `GPT-4.1 - GPT-5.4` (old versus new flagship) and
`GPT-5.4 Mini - GPT-5.4` (same-generation mini versus full model). Each raw
interaction is explicitly calculated as the target model's condition-minus-
baseline effect minus GPT-5.4's corresponding effect, separately by task,
condition, and metric. Percentile-bootstrap limits are the 2.5th and 97.5th
percentiles of 2,000 recalculated interaction estimates.

English two-model Figures 2-5 can be generated reproducibly with
`src.plot_english_model_comparison`. The obsolete generated two-model PNG/PDF
files were removed on 2026-08-01 before the three-model paper analysis. Figure 2 shows run-level primary
metric distributions; Figure 3 shows within-model Hedges' g estimates; Figure
4 shows model-by-prompt interaction contrasts on separate metric scales; and
Figure 5 shows PSI with a descriptive, interval-free `GPT-5.4 - GPT-4.1` PSI
panel. Captions and interpretive limits are in
`docs/english_model_comparison_figure_captions.md`. Rebuild with:

```powershell
python -m src.plot_english_model_comparison `
  --model-a-dir outputs/processed/formal_v01 --model-a-label gpt-4.1 `
  --model-b-dir outputs/processed/model_comparison_en_v01/gpt-5.4 `
  --model-b-label gpt-5.4 `
  --comparison-dir outputs/processed/model_comparison_en_v01/gpt-4.1_vs_gpt-5.4 `
  --output-dir outputs/figures/model_comparison_en_v01
```

Matplotlib is now a declared and locked project dependency for reproducible
figure generation.

The two-model human-reference stage uses the same frozen participant-level
datasets for both models and produces 64 model-condition-metric rows plus 48
manipulated-condition changes from baseline in:

```text
outputs/processed/model_comparison_en_v01/human_comparison/
  model_human_comparison.csv
  model_human_distance_changes.csv
  model_human_comparison_summary.json
```

The manuscript-facing three-model human-similarity tables are in:

```text
outputs/processed/model_comparison_en_v01/human_similarity_tables_v01/
  table_human_reference.csv
  table_human_similarity_long.csv
  table_human_similarity_matrix.csv
  table_human_similarity_matrix.md
  table_human_similarity_matrix.tex
  table_manifest.json
```

The matrix has one row per model-task-primary-metric combination. Each prompt
cell reports the LLM condition mean's position relative to the empirical human
2.5th-97.5th percentile interval (`○` within, `↑` above, `↓` below), the signed
human-SD standardised distance, and the proportion of the 20 LLM runs within
that interval. The long table additionally reports the below/within/above run
counts. The empirical interval describes participant-level variation; it is
not a confidence interval for the human population mean and does not replace
the bootstrap intervals for within-model prompt effects. The LaTeX version
contains one `table*` per model and requires `booktabs` and `graphicx`.

Rebuild the tables from the frozen `human_comparison_refit_v02` inputs with:

```powershell
python -m src.build_human_similarity_tables `
  --model-input "gpt-4.1=outputs/processed/model_comparison_en_v01/human_comparison_refit_v02/gpt-4.1/llm_human_comparison.csv=outputs/processed/formal_v01/llm_run_metrics.csv" `
  --model-input "gpt-5.4=outputs/processed/model_comparison_en_v01/human_comparison_refit_v02/gpt-5.4/llm_human_comparison.csv=outputs/processed/model_comparison_en_v01/gpt-5.4/llm_run_metrics.csv" `
  --model-input "gpt-5.4-mini=outputs/processed/model_comparison_en_v01/human_comparison_refit_v02/gpt-5.4-mini/llm_human_comparison.csv=outputs/processed/model_comparison_en_v01/gpt-5.4-mini-formal-v01/llm_run_metrics.csv" `
  --output-dir outputs/processed/model_comparison_en_v01/human_similarity_tables_v01
```

Figure 6 can plot signed human-SD distance for all eight primary metrics, with the
participant-level 2.5th-97.5th percentile reference band transformed to the
same scale. Its obsolete two-model PNG/PDF outputs were removed. Rebuild the combined table and
figure with:

```powershell
python -m src.compare_model_human_results `
  --model-a-dir outputs/processed/model_comparison_en_v01/human_comparison/gpt-4.1 `
  --model-a-label gpt-4.1 `
  --model-b-dir outputs/processed/model_comparison_en_v01/human_comparison/gpt-5.4 `
  --model-b-label gpt-5.4 `
  --output-dir outputs/processed/model_comparison_en_v01/human_comparison

python -m src.plot_model_human_comparison `
  outputs/processed/model_comparison_en_v01/human_comparison/model_human_comparison.csv `
  --output-dir outputs/figures/model_comparison_en_v01
```

Absolute human-distance change and reference-coverage change are reported
relative to each model's own baseline. Distributional proximity is not treated
as evidence that an LLM and humans share a cognitive mechanism.

The obsolete two-model manuscript tables and source-linked results checklist
under `outputs/processed/model_comparison_en_v01/main_tables/` were removed on
2026-08-01. They can be regenerated for audit with the command below, but must
not be used as final three-model thesis tables.
The frozen row counts are Table 1 = 24, Table 2 = 64, Table 3 = 48, Table 4 =
24, Table 5 = 18, and Table 6 = 64. The checklist contains 218 statements—one
for every row in Tables 2-6—with a result family, source file, composite key,
and verification status. Table definitions and interpretation boundaries are
in `docs/english_model_comparison_table_notes.md`. Rebuild with:

```powershell
python -m src.build_english_model_comparison_tables `
  --model-a-dir outputs/processed/formal_v01 --model-a-label gpt-4.1 `
  --model-b-dir outputs/processed/model_comparison_en_v01/gpt-5.4 `
  --model-b-label gpt-5.4 `
  --comparison-dir outputs/processed/model_comparison_en_v01/gpt-4.1_vs_gpt-5.4 `
  --human-comparison-dir outputs/processed/model_comparison_en_v01/human_comparison `
  --output-dir outputs/processed/model_comparison_en_v01/main_tables
```

Table 3 intentionally does not report FDR-adjusted p-values yet: the frozen
analysis provides effect sizes and bootstrap intervals but no pre-specified
null-resampling p-values. Multiplicity correction will only be added together
with an explicit test statistic, null scheme, and correction family.

The analysis and manuscript plan for this English two-model study is frozen in
`docs/english_model_comparison_analysis_plan.md`. It prioritises within-model
prompt effects, matched-seed cross-model difference-in-differences, descriptive
PSI comparison, and a separate human-reference analysis. The Chinese/Spanish
experiments are outside this analysis. The planned reporting
package contains six main figures, supplementary task-dynamic and robustness
figures, descriptive/effect-size tables, and a Methods-first manuscript
workflow.

A Chinese current-state map of exactly which LLM/human data are analysed, which
comparisons are required, and which main/supplementary tables and figures are
complete or pending is in
`docs/english_model_comparison_analysis_overview_zh.md`. It also records the
completed methodological correction: IGT ignores the nominal run seed, so its
within-model prompt-effect and PSI uncertainty now use independent cell-level
resampling. Horizon and BART retain paired environment-seed block resampling.
The bootstrap unit is recorded in every prompt-effect and PSI row.

Stage A of that plan is complete. The frozen analysis input manifest, JSON
audit report, and 12-cell audit table are in
`outputs/processed/model_comparison_en_v01/gpt-4.1_vs_gpt-5.4/`. The audit
requires 240 valid runs per model, identical task-condition-seed keys, 20
matched seeds per cell, identical prompt hashes, frozen sampling provenance,
complete task trial counts, parse success rate 1.0, and zero invalid responses.
It explicitly excludes non-English runs. Rebuild the
freeze before inferential analysis with:

```powershell
python -m src.freeze_model_comparison_inputs `
  --model-a-dir outputs/processed/formal_v01 --model-a-label gpt-4.1 `
  --model-b-dir outputs/processed/model_comparison_en_v01/gpt-5.4 `
  --model-b-label gpt-5.4 `
  --output-dir outputs/processed/model_comparison_en_v01/gpt-4.1_vs_gpt-5.4
```

Start or resume the five-wave GPT-5.4 English-only collection:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File scripts/start_gpt54_english_20run_five_waves.ps1
```

After all ten shards complete, aggregate them together:

```powershell
python -m src.aggregate_experiment_results `
  outputs/model_comparison_en_v01/gpt-5.4/wave-* `
  --expected-runs-per-cell 20 --languages en `
  --output-dir outputs/processed/model_comparison_en_v01/gpt-5.4
```

Formal shard workers use `--skip-recorded-failures`: on resume, successful
files are skipped as usual and failures already present in that shard's status
JSON are deferred rather than retried immediately. This lets all five formal
waves finish before a separate repair pass handles the final missing-run list.

The formal design now includes language as an experimental factor. The English
batch above supplies 240 task runs. Formal completion requires the same four
prompt conditions and 20 matched base seeds for Simplified Chinese and Spanish:

```text
3 languages x 3 tasks x 4 prompt conditions x 20 seeds = 720 task runs
English complete: 240
Chinese and Spanish to collect: 480
```

The frozen completion design is in
`configs/multilingual_experiment_freeze_v01.json`. New formal language runs
must be written to `outputs/formal_multilingual_v01/`. Earlier attempts under
`outputs/multilingual_v01/` are excluded from formal analysis.

Formal multilingual collection status (2026-07-29): the 36-prompt dry run and
480-run plan validation passed. The first formal Chinese Horizon baseline cell
completed all 300 trials with parse success rate 1.0 and zero invalid
responses. The remainder of the matched one-seed Chinese/Spanish smoke matrix
is running before the other 19 seeds are released.

Chinese formal collection resumed on 2026-08-03 with pinned model
`gpt-4.1-2025-04-14`, the frozen 12-prompt Simplified Chinese matrix, and all
20 matched base seeds. The active batch is
`outputs/formal_multilingual_v01/gpt-4.1-zh-CN-20run-v01/`: five waves run two
workers in parallel, each worker processes two seeds, and recorded failures are
deferred until all five waves finish. An automatic repair phase then reruns only
incomplete shards until all 240 Chinese task-runs are valid. Start or resume the
same workflow with:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File scripts/start_gpt41_chinese_20run_five_waves.ps1
```

As of 2026-08-04, Chinese collection is still active. A handoff monitor waits
for 240/240 valid Chinese task-runs, then automatically starts the frozen
Spanish 12-prompt matrix with the same model, seeds, five-wave/two-worker
schedule, failure deferral, and final repair policy. Spanish outputs are written
to `outputs/formal_multilingual_v01/gpt-4.1-es-20run-v01/`; handoff status is
recorded in `outputs/formal_multilingual_v01/logs/gpt-4.1-es-20run-v01/handoff.log`.

Later on 2026-08-04, collection was paused at the user's request after 220/240
Chinese task-run files had completed. The two Chinese workers, their scheduler,
and the Spanish handoff monitor were stopped; Spanish had not started. Existing
outputs and shard status files are retained for resumable continuation.

Collection resumed on 2026-08-05 from those retained shard checkpoints. The
Chinese scheduler skips existing successes, completes the remaining formal
wave work, and then repairs deferred failures until 240/240 valid task-runs are
present. The handoff monitor is active again and will start the Spanish
five-wave collection only after Chinese completion.

Chinese collection reached 240/240 valid task-runs on 2026-08-05. Duplicate
handoff monitors left by repeated background launches were stopped before they
could run concurrent Spanish workers, and one Spanish scheduler was started at
12:04 local time. Spanish wave 1 is active with exactly two workers; later
waves and the final repair phase remain automatic.

Spanish collection reached 236/240 valid task-runs before its repair process
stopped. On 2026-08-07 the final repair scheduler was restarted from the saved
shard checkpoints; it skips the 236 existing successes and is completing the
four missing `wave-04-b` results.

Spanish collection completed on 2026-08-07 at 240/240 valid task-runs. The
final `wave-04-b` repair finished with 23 existing successes skipped and one
new success recorded in its last status pass. Chinese and Spanish GPT-4.1
formal collection are therefore both complete; no collection worker remains
active.

Local process artifacts are intentionally excluded from the deliverable view:
`.env`, `.venv/`, `.tmp/`, `.uv-cache/`, `DATASET/`, raw JSON runs under
`outputs/`, and early pilot/debug outputs. They are not deleted by the
packaging step. Raw formal JSON runs remain local audit and
regeneration materials; the deliverable includes processed CSV/JSON analysis
tables only.

Current English-stage LLM-human comparison is in:

```text
deliverable/results/human_comparison_formal_v01/
```

This comparison uses the English `formal_v01` stage and one frozen human
reference dataset per task: Horizon 60 participants, IGT 504 participants, and
BART 141 participants. Each LLM run is treated as a participant-level
behavioural summary. Chinese and Spanish will use these same reference datasets
after collection. The current English-stage headline is that BART metrics are
broadly human-compatible, Horizon directed exploration is close to human
behaviour, but Horizon random exploration and IGT advantageous choice rate
diverge from the human reference distributions.

## Frozen Validation Method (2026-06-15)

The current validation configuration is frozen in:

```text
configs/experiment_config_stage01.json
configs/formal_experiment_freeze.json
configs/multilingual_experiment_freeze_v01.json
docs/formal_experiment_freeze.md
```

Experiment sampling settings:

```text
model: gpt-4.1-2025-04-14
temperature: 0.7
top_p: 1.0
max_output_tokens: 16
max retries per trial: 1
```

`src.run_llm_pilot` now takes its default model and sampling parameters from
the experiment config. `--model`, `--temperature`, and `--top-p` are explicit
overrides. Every new raw JSON records the requested model, API-resolved model,
temperature, top-p, token limit, config version, prompt path, and prompt hash.
Transient timeouts, URL errors, remote disconnects, connection errors, and TLS
errors are retried up to five times with exponential backoff. Truncated HTTP
response bodies (`http.client.IncompleteRead`) are also retried; this prevents
an otherwise valid task run from being lost when the response body is cut off
during transport. This network
retry does not change task state, prompt content, or sampling parameters.

Primary PSI metrics:

| Task | Primary metrics |
|---|---|
| Horizon | `directed_exploration`, `horizon_effect`, `random_exploration_effect` |
| IGT | `advantageous_choice_rate`, `post_loss_switching_rate` |
| BART | `adjusted_average_pumps`, `explosion_rate`, `post_explosion_adjustment` |

Canonical manuscript terminology is centralised in `src/reporting_names.py`.
Raw and processed files retain stable machine identifiers for reproducibility,
while manuscript tables and figures use the corresponding frozen display names:

| Machine identifier | Frozen manuscript name |
|---|---|
| `baseline` | Neutral baseline |
| `detailed` | Instruction specificity |
| `role_human` | Role framing |
| `uncertainty_emphasis` | Uncertainty and information emphasis |
| `reward_loss_emphasis` | Reward and loss emphasis |
| `risk_emphasis` | Risk-taking and risk-management emphasis |
| `directed_exploration` | Information-seeking choice rate |
| `horizon_effect` | Horizon-related exploration change |
| `random_exploration_effect` | Random exploration effect |
| `advantageous_choice_rate` | Advantageous choice rate |
| `post_loss_switching_rate` | Post-loss switching rate |
| `adjusted_average_pumps` | Adjusted average pumps |
| `explosion_rate` | Explosion rate |
| `post_explosion_adjustment` | Post-explosion adjustment |

Manuscript-table CSVs include both the machine-ID columns and explicit
`task_label`, `prompt_condition_label`, and (where applicable) `metric_label`
columns. Source keys and frozen raw/processed schemas continue to use machine
identifiers, so this reporting change does not alter experimental inputs or
existing result identity.

The formal manuscript-facing name of
`prompts/generation/controlled_prompt_variant_generation_protocol.md` is
**Controlled Prompt Variant Generation Protocol**. The file was renamed from
the development name `meta_prompt_v2.md` on 2026-08-02. Immutable historical
request and generation records retain the original filename where it records
the path actually used.

IGT `learning_slope`, `learning_curve_change`, and the complete five-block
curve are supplementary trajectory analyses. They are not primary PSI
metrics because a model that starts at ceiling can have a slope near zero.

The primary standardized effect is pooled-SD Hedges' g. The previous
baseline-SD standardized difference is retained as a sensitivity column.
PSI is the mean absolute Hedges' g across the task's primary metrics.
Raw differences, task-valid 95% bootstrap intervals, and valid bootstrap
replicate counts must be reported with PSI. Horizon and BART use paired
environment-seed blocks; IGT resamples runs independently within the baseline
and manipulated-condition cells.

Horizon random exploration uses the first-free-choice hierarchical logistic
MAP model. Its run-level values are partially pooled, model-derived estimates,
not directly observed summaries. For prompt-effect, cross-model interaction,
and PSI intervals, every bootstrap replicate resamples complete Horizon run
clusters, refits the hierarchical model, and then recomputes the raw effect,
pooled-SD Hedges' g, and PSI. This propagates model-fitting uncertainty instead
of treating the fitted run estimates as fixed observations. Formal reporting
checks `run_effect_sd` values `0.25`, `0.50`, and `1.00`. Results with fewer
than 15 valid runs are diagnostic only; the target is 20 runs per condition.

The legacy machine field `directed_exploration` is reported as
**Information-seeking choice rate**: among unequal-information games, it is the
proportion of first free choices selecting the less-observed option. The
separate `horizon_effect` is **Horizon-related exploration change**: the
Horizon-6 minus Horizon-1 difference in the proportion of eligible first free
choices selecting the option with the lower observed mean. It includes both
equal- and unequal-information games; choices for which the two observed means
are tied are excluded because neither option can be classified as lower-valued.
This tie rule is shared by LLM and human preprocessing. The 2026-08-08 audit
found 160 tied first-free choices among 16,000 formal English LLM games and 151
among 19,200 human games. The affected English Horizon run metrics, prompt-
sensitivity outputs, model comparisons, human comparisons, and similarity
tables were regenerated from retained raw records. Any later multilingual
aggregation must use the same corrected preprocessing rule.

IGT stores loss as a signed component: `0` means no loss and negative values
mean that a loss occurred. Both the LLM payoff schedule and the human
`lo_100.csv` source use this direction. Post-loss switching therefore uses
`loss < 0`, not `loss > 0` and not `net_outcome < 0`; trial 100 is ineligible
because it has no subsequent choice.

In the Horizon hierarchical choice model, the code variable
`reward_sensitivity` is the coefficient on observed reward difference because
that term has unit coefficient inside the subjective-evidence bracket. The
same parameter multiplies the entire bracket, including information bonus and
label bias, so mathematically it is also the inverse-temperature for overall
subjective evidence. Its reciprocal `decision_noise` must be interpreted with
that parameterisation in mind.

The manuscript now prespecifies pooled-SD Hedges' g as undefined whenever the
pooled SD is zero: equal constant groups retain raw difference 0 and are flagged
`constant_equal`; unequal constant groups retain their raw difference and are
flagged `constant_unequal`. The analysis implementation and tests now follow
that rule; no undefined standardised effect is replaced with zero. PSI is
complete only when all configured component g values are defined. The
analysis also enforces per-interval bootstrap validity gates
of >=95% for routine reporting, 90%--<95% with a stability warning, and <90%
withheld from formal inference. These diagnostics are written for raw,
standardised, PSI, model-interaction, language-interaction, and hierarchical
Random-exploration intervals. Horizon-related exploration change is missing
rather than zero if either horizon has no eligible non-tied first-free choices.
Human-reference coverage uses the number of non-missing LLM metric
values as its denominator. Human empirical 2.5th and 97.5th percentiles use
linear interpolation between adjacent ordered observations.

BART `post_explosion_adjustment` averages `next balloon pumps - exploded
balloon pumps` over explosions for which a subsequent balloon exists. A run or
human participant with no eligible transition has a missing value for this
metric; missing values are never replaced by zero. The formal LLM audit found
no such runs among the 240 BART runs. One of the 141 adult human participants
has no eligible transition, so the effective human sample for this metric is
140 while the other BART human metrics retain 141 participants.

The historical 36-run mini-pilot in `outputs/mini_pilot_v01` actually used
API-resolved `temperature=1.0`, because the old runner did not send the
configured value. Its reprocessed outputs diagnose the analysis pipeline but
do not replace the required validation rerun under the frozen settings.

本项目是一个毕业设计实验项目，目标是系统评估大型语言模型在经典认知决策任务中的行为是否稳定，以及这种行为是否会受到 prompt wording / framing 的影响。

核心问题不是单纯判断 LLM 是否“像人类”，而是：

1. 同一个 LLM 在相同任务规则下，是否会因为 prompt 条件变化而产生不同选择行为。
2. 这种 prompt sensitivity 能否用任务行为指标和标准化差异量化。
3. LLM 的行为指标是否能与真实 human datasets 中的 participant-level metrics 进行比较。
4. 如果模型行为明显依赖 prompt，那么这对 LLM 作为 reliable cognitive model 意味着什么。

Human data 在本项目中是行为参照，不是唯一目标。正式比较时会将 human raw data 处理成与 LLM run-level metrics 对应的 participant-level metrics。

## 当前任务

项目包含三个 cognitive decision-making tasks：

| Task | 中文说明 | 当前实现 |
|---|---|---|
| Horizon Task | 探索-利用任务 | 40 games；4 forced-choice trials；Horizon 1 / Horizon 6；equal / unequal information |
| Iowa Gambling Task | 奖励-损失学习任务 | 100 trials；A/B/C/D 四副牌；A/B disadvantageous，C/D advantageous |
| BART | 风险决策任务 | 40 balloons；2 blocks x 20；每次 successful pump +0.05 |

任务参数与当前方法材料见：

- `docs/task_parameters.md`
- `docs/task_details.md`
- `docs/data_schema.md`
- `docs/pilot_rerun_average_metrics_analysis.md`
- `configs/experiment_config_stage01.json`

## Prompt Conditions

计划中的正式实验仍包含一个 neutral baseline、两个 common prompt
manipulations，以及一个 task-specific emphasis：

| 条件类型 | Horizon | IGT | BART |
|---|---|---|---|
| Neutral baseline | `baseline` | `baseline` | `baseline` |
| More detailed rules | `detailed` | `detailed` | `detailed` |
| Human participant framing | `role_human` | `role_human` | `role_human` |
| Task-specific emphasis | `uncertainty_emphasis` | `reward_loss_emphasis` | `risk_emphasis` |

`baseline_task_named.md` 文件会保留，用于 future task-name leakage / task-name exposure 对照；当前正式 baseline 使用不暴露经典任务名称的 neutral prompt。

**当前状态（2026-06-14）：** 三份 canonical baselines 和九份 manipulated
variants 已完成生成、最小语义修订、完整矩阵 dry run、parser 检查和 SHA-256
冻结。12 个正式实验 prompts 均已在 config 中启用。三个
`baseline_task_named.md` 文件不属于当前四条件实验矩阵。

## Prompt Generation Protocol

LLM 在本项目中不负责设计任务，只作为受约束的 prompt rewriting tool。任务规则先由原始论文、human dataset 文档和本地 task implementation 固定，再生成语言条件变体。

完整的可复现流程见：

```text
docs/prompt_generation_protocol.md
docs/prompt_generation_and_review_record.md
docs/prompt_generation_and_review_record_zh.md
prompts/generation/controlled_prompt_variant_generation_protocol.md
prompts/generation/generation_record_template.md
prompts/generation/manual_review_checklist.md
prompts/generation/current_prompt_provenance.md
prompts/generation/records/2026-06-13_canonical_baselines/review.md
```

协议要求保存：

- Canonical task specification 和 frozen baseline。
- 给 prompt-generation LLM 的完整 meta-prompt。
- Provider、准确 model ID、日期、temperature、top-p、token limit 和 seed。
- 未编辑的原始 request 与 response。
- Candidate selection rule。
- 人工审核结果和逐项 edit log。
- 最终 prompt 文件的 Git commit 或 hashes。

第四个 prompt condition 按任务分别为 `uncertainty_emphasis`、`reward_loss_emphasis` 和 `risk_emphasis`。生成器只能提高 baseline 中已有信息的显著性，不能增加任务事实、策略提示、行为指标或 human benchmark。

历史 prompt 生成信息不完整，因此原文件已删除。历史上没有保存的信息继续
标为 `not recorded`。三份 baseline 由研究者根据任务来源重新构建；ELM
只使用 `controlled_prompt_variant_generation_protocol.md` 生成 9 个 manipulated variants，并保存完整记录。

现有 12 个实验 prompts 的生成来源、修改记录和冻结状态记录在
`prompts/generation/current_prompt_provenance.md`。新建的
`controlled_prompt_variant_generation_protocol.md` 是 prospective protocol，不能被描述为历史 prompts
当初实际使用过的 meta-prompt。

## 当前进度

已经完成：

| Phase | 内容 | 状态 |
|---|---|---|
| Parser | 严格解析 `CHOICE: ...` / `ACTION: ...` | Done |
| Task interface | 三个任务共用统一 environment 接口 | Done |
| Horizon environment | 40-game Horizon Task | Done |
| IGT environment | 100-trial IGT payoff schedule | Done |
| BART environment | 40-balloon probabilistic BART | Done |
| Random baseline | 不调用 LLM 的任务逻辑检查 | Done |
| Prompt dry run | 检查 prompt loading、observation rendering、parser format | Done |
| History-rich observations | IGT 和 BART 显式提供历史摘要 | Done |
| Condition-aware LLM runner | 支持 `--condition` 和 `--tasks` | Done |
| Single-run pilot matrix | baseline / detailed / role_human / task-specific pilot | Done, historical outputs |
| Canonical baseline reconstruction | 三个 literature- and implementation-aligned baselines | Done |
| Generated prompt variants | 3 tasks x 3 variants through university ELM | Done, Protocol 1.3 isolation review passed |
| Human metric preprocessing | 三个 human datasets 转换为 participant-level metrics | Done, BART 筛选待修正 |
| Horizon random exploration | first-free-choice logistic model 与 hierarchical MAP estimation | Done, validation pending |

最近一次指标设计更新：

- 将 run-level total 类指标改成更适合 human comparison 的平均指标。
- Horizon: `average_reward_per_trial`
- IGT: `average_net_outcome`
- BART: `average_earning_per_balloon`
- 删除 Horizon 中不严谨的 `random_exploration = exploration_rate` proxy。
- 正式定义 `random_exploration_effect = decision_noise_h6 - decision_noise_h1`。
- 删除与 `adjusted_average_pumps` 数值重复的 BART `cash_out_threshold`。

旧 pilot JSON 可能仍包含旧字段名；如果要使用最新指标进行分析，需要重新跑 pilot。

## 项目结构

```text
configs/
  experiment_config_stage01.json

docs/
  bart_human_preprocessing.md
  baseline_prompt_source_map.md
  citation_map.md
  data_schema.md
  next_steps_plan.md
  pilot_rerun_average_metrics_analysis.md
  prompt_generation_and_review_record.md
  prompt_generation_and_review_record_zh.md
  prompt_generation_protocol.md
  research_log.md
  superpowers/
    plans/
    specs/
  task_details.md
  task_parameters.md

prompts/
  generation/
    current_prompt_provenance.md
    generation_record_template.md
    manual_review_checklist.md
    meta_prompt_v1.md  # superseded historical protocol
    controlled_prompt_variant_generation_protocol.md
    records/
      2026-06-13_canonical_baselines/
        review.md
  bandit/
    baseline.md
    baseline_task_named.md
  igt/
    baseline.md
    baseline_task_named.md
  bart/
    baseline.md
    baseline_task_named.md

src/
  aggregate_experiment_results.py
  compute_prompt_sensitivity.py
  generate_prompt_variants.py
  horizon_random_exploration.py
  llm_client.py
  parser.py
  process_human_metrics.py
  prompt_loader.py
  run_llm_pilot.py
  run_prompt_dry_run.py
  run_random_baseline.py
  tasks/
    base.py
    horizon.py
    igt.py
    bart.py

tests/
  test_aggregate_experiment_results.py
  test_bart.py
  test_generate_prompt_variants.py
  test_horizon.py
  test_horizon_random_exploration.py
  test_igt.py
  test_llm_pilot.py
  test_parser.py
  test_process_human_metrics.py
  test_prompt_dry_run.py
  test_prompt_sensitivity.py
  test_random_baseline.py
  test_task_base.py
```

`DATASET/`、`outputs/`、`.venv/` 和本地 agent/editor 状态不属于 Git
仓库内容，因此未列入上面的版本控制结构。

## GitHub Storage Policy

GitHub 仓库保存可复现的项目主体：源码、测试、配置、prompt、依赖锁文件和
当前研究文档。

以下内容默认只保存在本地：

- `DATASET/`：human datasets 可能受授权、再分发或参与者数据约束；
- `outputs/`：包含可由仓库命令重新生成的大体积 raw runs 和分析产物；
- `.env`：包含本地 API credentials；
- `.venv/`、`.superpowers/` 和编辑器缓存：属于机器或工具状态；
- `IPP_proposal*.pdf`：可能包含个人或考核信息。

克隆仓库后，需要由研究者根据原始授权来源恢复 `DATASET/`。运行 README
中的命令会重新创建所需的 `outputs/` 子目录。`.env.example` 只提供变量名，
不包含真实 credential。

## Run Tests

```bash
python -m unittest discover
```

当前测试状态：

```text
Ran 92 tests
OK
```

## Run Random Baseline

Random baseline 不调用 LLM，只用 random agent 跑通三个任务，用于检查 task logic、records、metrics 和 config loading。

```bash
python -m src.run_random_baseline --seed 20260528 --output-dir outputs/debug/random_baseline
```

输出文件：

```text
outputs/debug/random_baseline/horizon_random_baseline.json
outputs/debug/random_baseline/igt_random_baseline.json
outputs/debug/random_baseline/bart_random_baseline.json
```

当前 run-level metrics 使用平均指标：

| Task | Average outcome metric |
|---|---|
| Horizon | `average_reward_per_trial` |
| IGT | `average_net_outcome` |
| BART | `average_earning_per_balloon` |

Trial-level records 仍会保存 cumulative score、total earning 等状态字段，因为这些字段用于 task state 和后续分析。

## Run Prompt Dry Run

Prompt dry run 不调用 LLM。它检查：

- prompt 文件能否从 config 正确读取；
- `{observation}` 是否能正常替换；
- config 中列出的合法输出能否被 parser 正确解析。

```bash
python -m src.run_prompt_dry_run --seed 20260528 --output-path outputs/debug/prompt_dry_run/baseline_prompt_dry_run.json
```

完整 12-prompt 实验矩阵使用：

```bash
python -m src.run_prompt_dry_run --all-conditions --seed 20260528 --output-path outputs/debug/prompt_dry_run/prompt_matrix_dry_run.json
```

## Prepare LLM Pilot

LLM pilot 会调用 OpenAI API。不要把 API key 写进代码或提交到 git。

Runner 使用的 OpenAI client 会对临时 timeout、429、以及 5xx API 错误做少量 retry。401 / 403 这类认证或权限错误不会重试。

PowerShell 临时设置：

```powershell
$env:OPENAI_API_KEY="你的 API key"
$env:OPENAI_MODEL="gpt-4.1"
$env:PROMPT_GENERATOR_MODEL="gpt-4o-2024-11-20"
```

也可以在本地 `.env` 文件中设置：

```text
OPENAI_API_KEY=你的 API key
OPENAI_MODEL=gpt-4.1
PROMPT_GENERATOR_MODEL=gpt-4o-2024-11-20
```

`.env` 已加入 `.gitignore`。

`OPENAI_MODEL` 只用于执行认知任务；`PROMPT_GENERATOR_MODEL` 只用于生成
prompt variants。两者复用同一个 API credential 和 Responses API endpoint，
但模型参数、输出目录和研究记录彼此独立。

## Generate Prompt Variants

以下命令使用固定快照 GPT-4o `gpt-4o-2024-11-20` 分别为三个任务生成 `detailed`、`role_human` 和
task-specific emphasis，共九个 candidates：

```bash
python -m src.generate_prompt_variants
```

默认生成设置：

```text
model: gpt-4o-2024-11-20
reasoning.effort: not sent
text.verbosity: not sent
max_output_tokens: 6000
temperature: 0.0
top_p: 1.0
candidate sets per task: 1
```

`temperature=0.0` 用于尽量降低采样随机性；`top_p=1.0` 是不截断概率质量的
中性设置。两项都会被发送到 API 并写入每个 `generation_record.json`。

也可以显式指定记录目录：

```bash
python -m src.generate_prompt_variants --output-dir prompts/generation/records/2026-06-14_gpt-4o-2024-11-20
```

脚本对每个 task 调用一次 API，并保存：

```text
request.md
raw_response.json
raw_output.md
generation_record.json
```

生成结果只进入 review 目录，不会自动写入正式 prompt 路径。必须先完成人工
审核，确认规则等价、没有策略提示或隐藏信息，才能安装和冻结。

2026-06-14 的三次生成调用已经成功完成，返回模型均为
`gpt-4o-2024-11-20`。九个 candidates 和完整 API 记录保存在：

```text
prompts/generation/records/2026-06-14_gpt-4o-2024-11-20/
```

初步审核见同目录的 `pre_review.md`，最终逐项审核和 hashes 见
`final_review.md`。完整的生成 instruction、三个 task-specific inputs、
`temperature=0.0`、`top_p=1.0` 以及两轮 review 修改记录见
`docs/prompt_generation_and_review_record.md`。第二轮审核将 role 条件收紧为
baseline 加一条角色句，将 task-specific 条件收紧为只替换一个授权段落。
Raw outputs 保持不变。

## Run LLM Pilots

全部四种 condition 当前均可用。

当前正式 baseline 建议输出到 `neutral_baseline_with_history`：

```bash
python -m src.run_llm_pilot --condition baseline --seed 20260528 --output-dir outputs/pilot/neutral_baseline_with_history
```

Common prompt conditions：

```bash
python -m src.run_llm_pilot --condition detailed --seed 20260528 --output-dir outputs/pilot/detailed
python -m src.run_llm_pilot --condition role_human --seed 20260528 --output-dir outputs/pilot/role_human
```

Task-specific prompt conditions：

```bash
python -m src.run_llm_pilot --condition uncertainty_emphasis --tasks horizon --seed 20260528 --output-dir outputs/pilot/horizon_uncertainty
python -m src.run_llm_pilot --condition reward_loss_emphasis --tasks igt --seed 20260528 --output-dir outputs/pilot/igt_reward_loss
python -m src.run_llm_pilot --condition risk_emphasis --tasks bart --seed 20260528 --output-dir outputs/pilot/bart_risk
```

每个 pilot JSON 保存：

- raw LLM outputs
- parsed action
- invalid responses
- trial/action-level records
- run-level metrics
- BART balloon-level records

如果 parser 失败，runner 会在停止前写出 `*_pilot_failed.json` debug 文件，包含 raw output、observation、full prompt、invalid reason 和已有 records。

新的 pilot 文件名包含 canonical task seed：

```text
horizon_baseline_seed-20260528.json
igt_baseline_seed-20260529.json
bart_baseline_seed-20260530.json
```

Task seed offsets 固定为 Horizon `+0`、IGT `+1`、BART `+2`。即使只运行一个
task，也保持相同 offset，因此 task-specific prompt 可以和 common prompt
conditions 使用同一组配对环境。

## Multi-Run Aggregation and PSI

Mini pilot 规模为：

```text
3 tasks x 4 prompt conditions x 3 paired seeds = 36 runs
```

完成 API 采集后，先聚合 raw JSON：

```powershell
python -m src.aggregate_experiment_results outputs/mini_pilot `
  --expected-runs-per-cell 3 `
  --output-dir outputs/processed/mini_pilot
```

再计算描述统计、signed standardised effects 和 PSI：

```powershell
python -m src.compute_prompt_sensitivity `
  outputs/processed/mini_pilot/llm_run_metrics.csv `
  --expected-runs-per-cell 3 `
  --output-dir outputs/processed/mini_pilot
```

默认使用严格模式。重复 logical runs、缺失 cells、未配对 seeds、混用 model
或 prompt versions、缺失 primary metrics，以及无法定义的标准化效应都会停止
分析并写入质量报告。

探索性恢复必须显式开启：

```powershell
python -m src.aggregate_experiment_results outputs/mini_pilot `
  --expected-runs-per-cell 3 `
  --duplicate-policy latest `
  --allow-incomplete `
  --output-dir outputs/processed/mini_pilot
```

`--duplicate-policy latest` 选择最新的成功文件，并记录所有重复候选。
`--allow-incomplete` 不会填补缺失数据；输出会标记
`analysis_complete=false`。

输出文件：

```text
llm_run_metrics.csv
aggregation_quality_report.json
metric_summary.csv
prompt_effects.csv
prompt_sensitivity.csv
analysis_summary.json
```

Primary PSI metrics：

| Task | Metrics |
|---|---|
| Horizon | `directed_exploration`, `horizon_effect`, `random_exploration_effect` |
| IGT | `advantageous_choice_rate`, `post_loss_switching_rate` |
| BART | `adjusted_average_pumps`, `explosion_rate`, `post_explosion_adjustment` |

`learning_curve_change` 定义为 IGT block 5 net score 减去 block 1 net score。
PSI 是三个 absolute standardised effects 的等权平均。它是本项目定义的描述性
指标，正式解释仍需同时报告 signed effects。

## Current Pilot Status

**Validation mini-pilot v02, run on 2026-06-15, is now the current diagnostic
mini-pilot.** It used the frozen settings in
`configs/formal_experiment_freeze.json`: `gpt-4.1-2025-04-14`,
`temperature=0.7`, `top_p=1.0`, `max_output_tokens=16`, config v0.5.

Outputs:

```text
outputs/validation_mini_pilot_v02
outputs/processed/validation_mini_pilot_v02
docs/validation_mini_pilot_v02_summary.md
```

Quality summary:

- 36/36 valid runs.
- 12 task-condition cells x 3 paired runs.
- 0 invalid responses.
- Prompt hashes, resolved model, temperature, top-p, and token limit were
  consistent across the batch.
- Aggregation and PSI analyses were both `analysis_complete=true`.
- The batch produced 24 primary prompt-effect rows and 9 PSI rows.

Main diagnostic finding: the frozen runner and analysis pipeline work, but
v2 is still not a formal experiment. IGT `post_loss_switching_rate` can
produce very large standardized effects with only three runs, and Horizon
random-exploration intervals remain diagnostic only. The next empirical step
is the 15-20 valid runs per task-condition cell batch.

按最新平均指标重新生成的 single-run pilot matrix 已经完成，见
`docs/pilot_rerun_average_metrics_analysis.md`。更早的实施历史保留在
`docs/research_log.md`。主要结论：

- 所有已完成 pilot 条件 parse success rate 为 1.0，invalid responses 为 0。
- Horizon 整体较稳定，但 exploration-related metrics 会随 prompt 有小幅变化。
- IGT 显示 history-rich observation 很关键。
- BART 显示当前最明显的 prompt sensitivity。

重要：由于 run-level total 指标已经改为平均指标，旧 pilot outputs 不适合直接作为最新分析输入。重新跑 pilot 后，新 JSON 会包含 `average_reward_per_trial`、`average_net_outcome` 和 `average_earning_per_balloon`。

36-run mini pilot 已于 2026-06-14 完成：

```text
outputs/mini_pilot_v01
outputs/processed/mini_pilot_v01
```

质量检查结果：

- 36/36 valid runs；
- 12 个 task-condition cells 均有 3 个配对 runs；
- 所有 runs 的 parse success rate 为 1.0；
- invalid response 总数为 0；
- aggregation 与 PSI analysis 均为 `analysis_complete=true`；
- 27 个 prompt-effect rows 和 9 个完整 PSI rows；
- aggregation quality report 中没有 issues。

## Next Steps

完整执行计划见 `docs/next_steps_plan.md`。当前顺序为：

1. Validate the frozen 36-prompt English/Chinese/Spanish matrix.
2. Run one matched formal base seed for Chinese and Spanish as a smoke test.
3. After quality control, complete the remaining 19 matched base seeds.
4. Aggregate all three languages into the 720-run formal design.
5. Run within-language PSI, language omnibus, language-by-prompt analysis,
   single-human-dataset comparison, robustness checks, figures, and thesis
   writing.

No second LLM batch or second human reference dataset is part of the design.

## Process Human Metrics

Human raw data can be converted into participant-level metric tables that match the LLM run-level metrics:

```bash
python -m src.process_human_metrics --output-dir outputs/processed/human_metrics
```

Estimate Horizon random exploration from repeated LLM runs:

```bash
python -m src.horizon_random_exploration outputs/formal --output outputs/processed/horizon_random_exploration.json
```

Fit the same first-free-choice model to the raw human Horizon data:

```bash
python -m src.horizon_random_exploration --human-data DATASET/BANDIT/allHorizonData_cut.csv --output outputs/processed/human_horizon_random_exploration.json
```

The formal metric is:

```text
random_exploration_effect = decision_noise_h6 - decision_noise_h1
```

The analysis requires at least two runs per prompt condition. With only one run, it reports `insufficient_runs` rather than returning the old exploration-rate proxy.

Outputs:

```text
outputs/processed/human_metrics/horizon_human_metrics.csv
outputs/processed/human_metrics/igt_human_metrics.csv
outputs/processed/human_metrics/bart_human_metrics.csv
outputs/processed/human_metrics/bart_exclusions.csv
outputs/processed/human_metrics/summary.json
```

Current processed participant counts:

| Task | Participants | Main comparable metrics |
|---|---:|---|
| Horizon | 60 | `exploration_rate`, `directed_exploration`, `horizon_effect`, `average_reward_per_trial` |
| IGT | 504 | `net_score`, `advantageous_choice_rate`, deck rates, `average_net_outcome`, post-loss switching |
| BART | 141 | `average_pumps`, `adjusted_average_pumps`, `explosion_rate`, `post_explosion_adjustment` |

BART 原始文件包含 147 个 IDs。预处理从第 9 列读取年龄并应用
`age >= 18`，排除 IDs `4, 5, 7, 13, 79, 86`，最终保留 141 名成年人。
完整筛选依据和审计记录见 `docs/bart_human_preprocessing.md`。

## Documentation Maintenance Rule

以下规则适用于之后的所有项目修改：

- 任何代码行为、研究方法、指标、prompt、任务参数、运行命令、依赖、输出 schema、实验进度或分析流程的变化，都必须在同一次修改中同步更新 `README.md`。
- `README.md` 只描述当前有效状态；详细变更理由记录在 `docs/research_log.md`。
- 尚未完成的工作及其验收标准记录在 `docs/next_steps_plan.md`。
- README 更新不是可选的收尾工作，而是每项修改的完成条件。

## Multilingual Prompts (2026-07-20)

The active prompt system now supports English (`en`), Simplified Chinese
(`zh-CN`), and neutral Spanish (`es`). English remains the default and canonical
source. Chinese and Spanish baselines were created first; their `detailed`,
`role_human`, and task-specific emphasis variants were then derived from the
baseline in the same language.

The derivation rules and audit record are:

```text
prompts/multilingual/translation_constraints.md
prompts/multilingual/generation_and_audit_record.md
```

The 24 target-language prompt files are under:

```text
prompts/multilingual/zh-CN/{bandit,igt,bart}/
prompts/multilingual/es/{bandit,igt,bart}/
```

Parser strings remain English ASCII tokens (`CHOICE: ...` and `ACTION: ...`) in
every language. Each prompt contains exactly one `{observation}` placeholder.
The Chinese and Spanish prompts have passed final bilingual semantic review and
are frozen for formal multilingual completion in
`configs/multilingual_experiment_freeze_v01.json`.

Validate a complete language-specific 12-prompt matrix without API calls:

```powershell
python -m src.run_prompt_dry_run --all-conditions --language zh-CN `
  --output-path outputs/debug/prompt_dry_run/prompt_matrix_zh-CN.json
python -m src.run_prompt_dry_run --all-conditions --language es `
  --output-path outputs/debug/prompt_dry_run/prompt_matrix_es.json
```

Validate all 36 language-task-condition prompts and their language-specific
dynamic observations in one command:

```powershell
python -m src.run_prompt_dry_run --all-languages `
  --output-path outputs/debug/prompt_dry_run/multilingual_matrix.json
```

Plan the formal Chinese and Spanish completion matrix without making API calls:

```powershell
python -m src.run_multilingual_experiment `
  --languages zh-CN,es `
  --seeds 20260708,20260709,20260710,20260711,20260712,20260713,20260714,20260715,20260716,20260717,20260718,20260719,20260720,20260721,20260722,20260723,20260724,20260725,20260726,20260727 `
  --output-dir outputs/formal_multilingual_v01 --plan-only
```

The completion plan contains 480 task runs: 240 Chinese and 240 Spanish.
Together with the completed 240 English task runs, the formal design contains
720 task runs. The two new languages require 48,000 Horizon requests, 16,000
IGT requests, and between 6,400 and 204,800 BART requests, for a total bound of
70,400 to 268,800 API requests. The BART range depends on when balloons
explode.

After confirming API quota and cost, remove `--plan-only` to execute the same
matrix. The runner writes `multilingual_run_status.json` after every completed,
failed, or skipped task run. It is resumable by default and skips an existing
output only when its success flag, language, task, condition, and seed all match
the planned run. Use `--no-resume` only when intentionally rerunning all cells.

**Historical pilot status (2026-07-26):** pilot attempts under
`outputs/multilingual_v01/` encountered unstable API connectivity. Those
outputs use non-formal seeds and are excluded from formal analysis.

Run an LLM pilot with a selected language:

```powershell
python -m src.run_llm_pilot --condition baseline --language zh-CN `
  --seed 20260528 --output-dir outputs/pilot/multilingual_zh-CN
python -m src.run_llm_pilot --condition baseline --language es `
  --seed 20260528 --output-dir outputs/pilot/multilingual_es
```

Non-English filenames include `_lang-zh-CN` or `_lang-es`. Every raw JSON records
`prompt_language`, `prompt_path`, and `prompt_sha256`; existing English commands
and filenames remain unchanged. Dynamic observations and history summaries are
rendered in the selected language while the underlying rewards, payoff schedule,
explosion points, seeds, and parser action tokens remain unchanged.

Aggregation and prompt-sensitivity analysis now treat
`prompt_language + task + prompt_condition + seed` as the logical experimental
unit. Each language's manipulated conditions are compared only with the baseline
in the same language. The resulting `metric_summary.csv`,
`prompt_effects.csv`, and `prompt_sensitivity.csv` include
`prompt_language`.

Three-language omnibus effects and language-by-prompt differences are computed
after aggregation:

```powershell
python -m src.aggregate_experiment_results outputs/multilingual_v01 `
  --expected-runs-per-cell 20 --languages all `
  --output-dir outputs/processed/multilingual_v01
python -m src.compute_prompt_sensitivity `
  outputs/processed/multilingual_v01/llm_run_metrics.csv `
  --expected-runs-per-cell 20 `
  --output-dir outputs/processed/multilingual_v01
python -m src.compute_language_interactions `
  outputs/processed/multilingual_v01/llm_run_metrics.csv `
  --output-dir outputs/processed/multilingual_v01
```

This writes:

```text
language_baseline_contrasts.csv
language_prompt_interactions.csv
language_interaction_summary.json
```

`language_baseline_contrasts.csv` uses English as the prespecified reference
and reports Simplified-Chinese-minus-English and Spanish-minus-English neutral-
baseline differences in raw units and pooled-SD Hedges' g, with percentile-
bootstrap 95% confidence intervals.

`language_prompt_interactions.csv` first calculates, within every language:

```text
condition - same-language baseline
```

It then reports the English-reference interaction contrasts
`(target-language condition - target-language baseline) - (English condition -
English baseline)` in raw and standardised units. Horizon and BART use matched-
seed block bootstrap; deterministic-schedule IGT uses independent-cell run
bootstrap. All intervals use 2,000 percentile-bootstrap replicates. The former
Friedman/Kendall's W/permutation analysis is superseded.

The manuscript treats the model and language contrasts as estimation-focused
analyses. It does not apply family-wise multiplicity adjustment to the
percentile intervals and does not make a claim solely because one unadjusted
interval excludes zero. Interpretation emphasises prespecified raw contrasts,
effect direction and magnitude, interval width, and consistency across related
metrics and tasks. Standardised language interaction differences are
supplementary because their component Hedges' g values can use different
pooled standard deviations.

## Important Principles

## Manuscript evidence and Results status (2026-08-09)

- The current Background and Related Work has been re-audited paragraph by paragraph. It contains 8 thematic sections, 26 substantive paragraphs, and 33 unique sources; source count is not treated as a hard cap. The original IGT and BART task sources are now cited in the task-theory section. Evidence-boundary corrections and bibliography caveats are recorded in `docs/background_citation_audit_zh.md`.
- The manuscript operationally limits behavioural-measurement reliability to robustness across prespecified prompt formulations under fixed model snapshot, task implementation, generation temperature, response format, and parser. The human-reference quantity \(D\) is named a `signed human-SD-scaled mean deviation`, not a standardised mean difference or conventional effect size.
- Formal data collection is complete at 1,200 deduplicated valid task runs. The regenerated `outputs/processed/final_analysis_v03/` package now contains RQ1 effects/PSI, both GPT-5.4-reference RQ2 comparisons, RQ3 multilingual contrasts, Random-exploration diagnostics, and RQ4 human-reference outputs. Results prose must use this package rather than historical `*_refit_v02` or July deliverables.
- The authoritative data/output inventory is `docs/results_data_inventory_20260809.md`; the Results chapter and figure plan is `docs/results_writing_architecture_zh.md`.
- The multilingual aggregation explicitly audits the prespecified provenance split: reused English GPT-4.1 runs use `experiment_config_stage01` 0.5, while newly collected Chinese and Spanish runs use 0.7. This cross-language difference is accepted only through the frozen per-language allowlist; mixed or unexpected versions within a language remain errors.
- Following completion of all analysis gates, `tmp/final_revision_all.md` now contains a source-linked Results draft covering RQ1--RQ4 and a separate Discussion draft. The Introduction's former Results-achieved placeholder has also been replaced with a non-numeric findings summary. These drafts use only `final_analysis_v03` outputs.
- The post-analysis Method audit now states the deduplicated 1,200-run total, treats Neutral baseline language contrasts as primary RQ3 analyses, limits prompt-length provenance to reproducible text/character information rather than unverifiable proprietary-tokenizer counts, and describes the exact bootstrap diagnostic fields and frozen language-specific config provenance used by the code.
- The corrected, analysis-gated writing plan is `docs/results_discussion_plan_revised_zh.md`. It supersedes the earlier Results architecture draft and explicitly separates RQ1 within-language effects from RQ3 cross-language contrasts, requires GPT-5.4-reference joint bootstraps for RQ2, and blocks prose until multilingual, Random-exploration, and human-reference change outputs are complete.
- The Results/Discussion execution plan source is version 2.2. It aligns the zero-variance Hedges' g rule with the revised Method, adds per-interval bootstrap-validity gates, and makes human--LLM Random-exploration specification alignment a P0 requirement. The Word copy has been refreshed for external handoff.
- `final_analysis_v03` contains 72 multilingual within-language prompt effects, 24 symmetric three-language centred Neutral deviations, 72 symmetric centred prompt-effect deviations, and two 24-row model-by-prompt interaction tables. English, Simplified Chinese, and Spanish are analysed jointly: each language is expressed relative to the three-language mean, the three deviations sum to zero, and no language is the statistical reference. Every generated interval currently has 2,000/2,000 valid replicates and status `report`.
- Superseded English-reference RQ3 CSVs and figures are not part of the authoritative manifest or manuscript package; they are retained only under explicitly named archival folders for provenance.
- A final independent manuscript audit corrected the last English-centred narrative sentence, distinguished the two RQ3 standardisation schemes in the caption and Results prose, replaced variance-decomposition language with descriptive centred-profile language, and stated the exact coverage resolution as `1 / n_valid` (with change-score resolution depending on both cells).
- `tmp/final_revision_all.md` now begins with a thesis-aligned Abstract and keywords. It reports the 1,200-run design, task/model/language scope, primary estimands, joint three-language centred analysis, main conditionality finding, descriptive human-reference boundary, and auditable evaluation contribution without adding unsupported claims.
- The Method's task-appropriate bootstrap description distinguishes general percentile-bootstrap support (Efron and Tibshirani, 1993) from dependence-preserving cluster/block resampling support (Field and Welsh, 2007). Matched seed blocks remain a design-specific application derived from the Horizon/BART randomisation structure, while IGT uses independent cell-run resampling and only Horizon Random exploration is hierarchically refitted.
- The Introduction roadmap now mirrors the actual chapter functions: Results answers RQ1--RQ4; Discussion integrates measurement implications, methodological contribution, human-reference boundaries, limitations and reproducibility priorities; Conclusion directly answers the core objective and identifies the highest-priority extensions rather than merely repeating the limitations list.
- `final.tex` now uses the School-provided `infthesis`/`msccheck` structure rather than the generic `article` class. The explicit `geometry`, `11pt`, `lmodern`, compressed-list spacing, longtable spacing overrides, `caption`, `enumitem`, `natbib`, and `cleveref` settings were removed. Abstract, declaration, and contents are preliminary material; Introduction is the first numbered body chapter and therefore begins at body page 1 under the class. The default thesis margins, font sizing, and 1.5 line spacing are left untouched. The 40-page body limit still requires an actual Overleaf compilation check.
- No reduced-size text remains in the manuscript tables or table notes. The repository does not contain the official `infthesis.cls` or `msccheck.sty`; `final.tex` must therefore be compiled inside the University's official Overleaf template, not as a standalone generic project.
- The Sebri et al. (2023) BART reference was corrected against the publisher record: the first author is Valeria Sebri (not Vincenzo), and the third author's full bibliographic form is Georg D. Granic.
- Human-reference results contain 160 model-language cells and 120 manipulated-minus-Neutral change rows. Final schemas call the quantity a signed/absolute `human-SD-scaled mean deviation`; it is not Cohen's d. Human and LLM Random-exploration estimates passed the same-model-specification audit and all formal 0.25/0.5/1.0 shrinkage fits converged.
- `python -m src.build_final_analysis_manifest` validates frozen row counts, interval statuses, aggregation completeness and Random-exploration convergence, then writes SHA-256 provenance to `outputs/processed/final_analysis_v03/analysis_manifest.json`. Results writing is permitted only when `analysis_ready` is true and `failures` is empty.
- `python -m src.build_results_visual_package` converts the validated final tables into the main Results displays. Each figure is exported as vector PDF and 600-dpi PNG under `outputs/figures/final_results_v01/`; two manuscript tables and ready-to-input figure environments are written under `docs/results_visuals/`. Visual consistency comes from a common low-saturation, colour-vision-friendly blue--grey--brown-red palette, shared typography, and shared line weights rather than forcing every RQ into one chart type. RQ1 uses three task-grouped signed-Hedges-$g$ forest panels with formal standardised bootstrap intervals; RQ2 retains the compact interaction heatmap because its two-contrast matrix structure is naturally tabular; RQ3 jointly displays English, Simplified Chinese, and Spanish as centred Neutral and centred prompt-effect profiles, with no reference language. RQ4 remains split into separate absolute-deviation and coverage heatmaps. Labels and annotations are sized for A4 landscape reproduction, and the previous detailed RQ1--RQ3 figures remain under `outputs/figures/final_results_v01/detail_or_appendix/`.
- For visual-version comparison, current manuscript displays are copied to `outputs/figures/final_results_v01/new_version/`, while the still-available superseded RQ3/RQ4 displays are copied to `outputs/figures/final_results_v01/old_version/`. Root-level files remain in place because the generated LaTeX environments reference those stable paths. Verified old RQ1/RQ2 copies were unavailable after their same-name outputs were regenerated.
- The manuscript Results section now follows the revised visual logic: forest plots support RQ1, a compact interaction matrix supports RQ2, dot/forest panels support RQ3, and separate heatmaps support RQ4. Prose reports representative raw estimates and cross-cell patterns rather than narrating every cell. Discussion is consolidated into four sections: integrated findings and methodological contribution; conditionality of behavioural measurement; human-reference interpretation; and limitations, reproducibility implications, and future work. The former task-by-task discussion and duplicate concluding synthesis have been removed.
- The final Results/Discussion boundary audit now limits matched-seed block bootstrap to Horizon/BART and hierarchical refitting to Horizon Random exploration; distinguishes run-level replication from independent synthetic-population sampling; states RQ2 and RQ3 interaction directions; distinguishes RQ1's standardised figure axis from raw prose estimates; records RQ4's no-CI status and coverage quantisation; and makes the fixed-human-reference inference explicitly conditional. The BART adjusted-pumps denominator and retained audit fields for three failed Mini attempts are also stated.
- The previously empty Conclusion and Future Work section is now populated with a concise synthesis and forward-looking priorities. RQ4 figure captions and Results wording explicitly match the Method: human-reference proximity changes are descriptive point estimates, and no inferential intervals were constructed for those measures.
- The conclusion now states the central finding as structured, conditional prompt sensitivity without a universal formulation ranking; frames the computer-science contribution as an auditable evaluation workflow; distinguishes LLM-run behaviour from human-population distributional equivalence; and prioritises replication before orthogonal prompt, multilingual, and human-reference extensions.
- The four main Results displays are portrait-page figures: task panels are stacked vertically (RQ1/RQ2), or tasks occupy rows with two complementary analysis columns (RQ3/RQ4). No page or image rotation package is used, and the School class margins, font sizes, and line spacing remain unchanged.
- Each Results RQ now uses two concise evidence paragraphs before its figure: one reports the principal cross-cell pattern and representative raw estimates, and the other states the RQ-level answer and statistical boundary. This restores necessary result detail without repeating the Discussion or narrating every plotted cell.
- After the line-level compression pass, approximately 510 words of substantive Method explanation were restored: factorial-design logic, the limits of run-level replication, task-selection rationale, prompt-manipulation boundaries, language freezing, complete-run dependence, human-reference selection and interpretation, and multiplicity-aware contrast interpretation. Engineering version detail remains in the technical appendix; no task parameter, metric definition, contrast, equation, bootstrap gate, or provenance limitation was removed.
- The Method now explicitly motivates the prespecified two-sided 95% percentile-bootstrap intervals, defines their 2.5th/97.5th percentile construction and interpretation boundary, and cites Efron and Tibshirani's classic bootstrap framework. The consolidated bibliography therefore contains 44 external sources.
- The thesis Method has been edited to separate scientific design from implementation audit detail. The main text retains model versions, collection dates, generation settings, response-validity rules, analysis units and uncertainty procedures; internal data labels, hashes, client/network retry details, full prompt-generation settings and configuration mappings are routed to the technical appendix.
- Introduction citation roles were tightened: Sclar et al. (2024) supports static benchmark/format sensitivity, whereas Loya et al. (2023) is presented as a sequential Horizon Task extension rather than evidence about single-turn responses.
- `mybibfile.bib` is the consolidated BibTeX database for all 43 external sources currently cited in the manuscript. It uses the formal published versions where available and locks the ambiguous Lin, Hua, Kong, Steingroever, Hagendorff, Horton, Zhang, Mondshine, and Palmer records to the versions documented in the citation audits.
- `intro_academic_english.tex` is the grammar-checked, British-academic-English LaTeX version of the current Introduction. Its citation commands use plain `\cite{...}` because the current dissertation skeleton uses `\bibliographystyle{plain}` and does not load `natbib`; every key resolves against `mybibfile.bib`.
- `background_academic_english.tex` is the grammar-checked, British-academic-English LaTeX version of the eight-part Background and Related Work section. It uses template-compatible `\cite{...}` commands and removes the Method-direction sentence from the final research-positioning paragraph so that the literature review ends on the contribution.

- `skeleton_repaired.tex` now contains a result-led Discussion revision. It interprets the reported RQ1--RQ4 estimates and sign reversals directly, separates observed behavioural patterns from possible cue-salience explanations, removes repeated Background definitions and duplicate literature-led discussion, and turns limitations into result-specific replication priorities. Results figures now use flexible top/bottom/page floats at a maximum height of `0.72\textheight`; intermediate float barriers were removed while the barrier before Discussion remains, reducing blank page areas without allowing Results figures to drift into the next chapter. The empty template appendix has been replaced by a concise research-materials appendix that indexes all frozen English, Chinese, and Spanish prompt files, the prompt provenance and translation-audit records, the authoritative `final_analysis_v03` outputs, bootstrap diagnostics, and detailed figures. It explicitly records why participant-information and consent-form appendices do not apply. The ethics declaration is set to the no-approval-required statement on the current design assumption that the project recruited no participants and used only existing human-reference datasets; this wording must still be confirmed with the supervisor. The acknowledgements block contains explicit placeholders that must be personalised or removed before submission.
- For Overleaf portability, `skeleton_repaired.tex` now declares `\graphicspath{{figures/}{./}}`: the four Results images are referenced by filename and can be uploaded under `figures/`, while the two design images may remain either in `figures/` or the Overleaf project root. The appendix's reproducibility locations are presented as clickable GitHub URLs rather than local filesystem paths. `mybibfile.bib` remains a project-relative bibliography and must be uploaded beside the main `.tex` file.

- 正式实验前锁定 task rules、prompt set、parser、model settings 和 output schema。
- Prompt 修改必须记录在 `docs/research_log.md`。
- Human comparison 使用处理后的行为指标，不直接比较 raw human data 和 raw LLM text。
- PSI 是本项目构建的描述性综合指标，不是已有文献中的标准心理量表。
- Pilot 结果只能用于方法学检查和趋势观察，不能作为正式统计结论。
