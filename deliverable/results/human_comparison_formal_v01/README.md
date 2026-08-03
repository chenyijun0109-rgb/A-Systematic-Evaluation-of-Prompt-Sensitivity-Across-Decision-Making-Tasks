# LLM-Human Comparison: formal_v01

This folder contains the primary LLM-human comparison using:

```text
LLM:   formal_v01, 20 runs per task-condition cell
Human: one participant-level dataset per task
```

Human reference datasets:

```text
Horizon: 60 participants
IGT:     504 participants
BART:    141 participants
```

Files:

```text
human_metric_summary.csv          human participant-level reference summaries
llm_human_comparison.csv          LLM condition means compared with human references
closest_prompt_by_metric.csv      prompt condition closest to human mean per metric
human_comparison_summary.json     machine-readable analysis summary
human_comparison_analysis_zh.md   Chinese written interpretation
```

Interpretation boundary:

Each LLM run is treated as analogous to one participant-level behavioural
summary. Human datasets are task-specific reference distributions, not
population-level definitive benchmarks.
