# Result Files

## formal_v01

`formal_v01` is the completed English stage of the single three-language
formal experiment. The matched Chinese and Spanish stages are still being
collected and are not yet included in this result package.

Files:

```text
aggregation_quality_report.json  input completeness and quality checks
analysis_summary.json            PSI analysis completion summary
llm_run_metrics.csv              one row per valid LLM run
metric_summary.csv               descriptive summaries by task and prompt condition
prompt_effects.csv               signed prompt effects relative to baseline
prompt_sensitivity.csv           task-condition PSI values and intervals
```

Quality checks from the copied summaries:

```text
valid_run_count: 240
expected_runs_per_cell: 20
aggregation issues: []
PSI issues: []
```

## human_comparison_formal_v01

`human_comparison_formal_v01` compares the completed English formal stage
against one human reference dataset per task. The same frozen human reference
datasets will be used for Chinese and Spanish after collection.

Files:

```text
human_metric_summary.csv
llm_human_comparison.csv
closest_prompt_by_metric.csv
human_comparison_summary.json
human_comparison_analysis_zh.md
metric_notes.md
README.md
```

Human reference samples:

```text
Horizon: 60 participants
IGT:     504 participants
BART:    141 participants
```

Headline finding: BART metrics are broadly human-compatible, Horizon directed
exploration is close to human behaviour, but Horizon random exploration and IGT
advantageous choice rate show clear LLM-human divergence.

PSI is a project-defined descriptive index: the mean absolute Hedges' g across pre-selected primary metrics. Higher PSI means the model's behavior changed more under that prompt condition relative to the neutral baseline; it does not mean the behavior is better or more human-like.
