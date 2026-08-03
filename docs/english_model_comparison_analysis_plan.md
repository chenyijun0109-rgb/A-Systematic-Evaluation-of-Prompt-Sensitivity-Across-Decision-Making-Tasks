# English Two-Model Analysis and Paper Plan

## 1. Scope and research questions

This analysis uses only the completed English formal batches:

- GPT-4.1 (`gpt-4.1-2025-04-14`)
- GPT-5.4 (`gpt-5.4-2026-03-05`)
- three tasks, four prompt conditions, and 20 matched seeds per cell
- 240 valid task runs per model (480 runs total)

The Chinese/Spanish experiments are outside the current analysis.

The paper should answer, in this order:

1. Does each model change its task behaviour when prompt wording changes?
2. Is GPT-5.4 less or more prompt-sensitive than GPT-4.1?
3. Are model differences consistent across Horizon, IGT, and BART?
4. Does either model move closer to the task-specific human reference distribution?

Prompt sensitivity and human similarity are separate outcomes. A newer model is
not automatically better, and a positive metric difference is not automatically
beneficial.

## 2. Analysis sequence

### Stage A: freeze and audit

- Retain the completed raw-data audit as the inclusion record.
- Record exact model snapshots, prompt hashes, sampling parameters, seeds, and
  trial counts.
- Freeze the analysis input manifest before generating inferential results.
- Exclude non-English experiment outputs explicitly.

### Stage B: descriptive model profiles

- Summarise every behavioural metric by model, task, and prompt condition.
- Plot run-level observations rather than means alone.
- Inspect ceiling/floor effects and zero-variance cells.
- Treat outcome/reward variables as supplementary unless they directly answer a
  task-specific behavioural question.

### Stage C: within-model prompt effects

- Compare each manipulated condition with that model's baseline using matched
  seeds.
- Report raw paired mean difference, paired bootstrap 95% interval, Hedges' g,
  and the existing PSI.
- Retain the three frozen primary metrics for Horizon, two for IGT, and three for
  BART. Label all other metrics supplementary.

### Stage D: between-model moderation of prompt effects

The primary cross-model estimand is a model-by-prompt interaction contrast:

```text
[(GPT-5.4 condition - GPT-5.4 baseline)
 - (GPT-4.1 condition - GPT-4.1 baseline)]
```

This is an interaction contrast, not a causal difference-in-differences design.
For Horizon and BART, resample matched environment-seed blocks because the seed
controls task randomness. For IGT, resample runs independently within each
model-prompt cell because its fixed payoff schedule ignores the run seed and the
API sampling is not seed-coupled. Use percentile bootstrap 95% intervals. This
is more informative than comparing condition means alone because it directly
estimates whether model identity changes prompt sensitivity.

Also report the descriptive PSI difference (`GPT-5.4 - GPT-4.1`). PSI remains a
project-defined summary, not a validated scale, and should not replace the
metric-level effects.

### Stage E: human-reference comparison

- Reuse the frozen human datasets and aligned participant-level metrics.
- For each model and condition, report standardized distance from the human
  mean, the proportion of LLM runs within the human reference interval, and the
  change relative to that model's baseline.
- Prioritise pump-based BART measures if monetary scaling differs across data
  sources.
- State explicitly that distributional similarity does not establish a shared
  cognitive mechanism.

### Stage F: robustness and multiplicity

- Re-run Horizon random exploration with `run_effect_sd` values 0.25, 0.50, and
  1.00.
- Compare mean-based and median-based summaries.
- Perform leave-one-metric-out PSI checks.
- Flag low baseline variance and ceiling/floor effects.
- Apply Benjamini-Hochberg false-discovery-rate correction within each family of
  primary metric-level tests; show raw intervals/effect sizes regardless of the
  adjusted result.
- Treat reward outcomes, full IGT learning curves, and additional task metrics
  as supplementary analyses.

## 3. Planned figures

### Main-text figures

1. **Study design and analysis map.** Two models x three tasks x four prompt
   conditions x 20 matched seeds, followed by within-model prompt effects,
   cross-model moderation, and human-reference comparison.
2. **Behavioural distributions by task.** Faceted raincloud/box-and-jitter plots
   for the eight primary metrics. X-axis is prompt condition, colour is model,
   and each point is one run. Use task-appropriate metric scales; do not combine
   incompatible metrics on one numerical axis.
3. **Within-model prompt-effect forest plot.** Hedges' g and 95% bootstrap
   intervals for every primary metric and manipulated condition, shown side by
   side for GPT-4.1 and GPT-5.4. Include a zero reference line.
4. **Cross-model interaction-contrast forest plot.** The primary test of
   whether GPT-5.4 changes prompt sensitivity relative to GPT-4.1, with paired
   bootstrap intervals.
5. **Prompt Sensitivity Index.** PSI by task and manipulated condition for both
   models, with a second panel showing `GPT-5.4 - GPT-4.1`. Describe PSI as a
   descriptive summary.
6. **Human-reference distance.** Standardized human distance for baseline and
   manipulated prompts, faceted by task/metric and coloured by model. A zero
   line denotes the human mean and a shaded band denotes the chosen human
   reference interval where possible.

### Supplementary figures

- S1: complete descriptive distributions for every recorded metric.
- S2: paired-seed slope plots from baseline to each manipulated condition.
- S3: IGT five-block learning curves by model and prompt condition.
- S4: Horizon directed/random exploration decomposition and shrinkage
  sensitivity.
- S5: BART pump distributions, explosion rates, and post-explosion adjustment.
- S6: leave-one-metric-out PSI and mean-versus-median robustness.
- S7: per-cell parse validity and provenance/audit summary.
- S8: correlation matrix of primary metrics, used only to diagnose redundancy.

## 4. Planned tables

- Table 1: experimental design, model snapshots, prompts, sampling settings,
  seeds, task lengths, and valid run counts.
- Table 2: means, SDs, medians, and ranges for all primary metrics by model and
  condition.
- Table 3: within-model prompt effects: raw paired difference, bootstrap 95% CI,
  Hedges' g, and FDR-adjusted p-value if computed.
- Table 4: model-by-prompt interaction contrasts comparing prompt sensitivity.
- Table 5: PSI and robustness summaries.
- Table 6: LLM-human standardized distances and reference-interval coverage.
- Supplementary tables: all secondary metrics, IGT blocks, Horizon sensitivity
  settings, data-quality audit, and exact prompt provenance.

## 5. Paper structure and writing order

### Working title

**Are More Capable Language Models More Reliable Cognitive Models? An English
Prompt-Sensitivity Comparison of GPT-4.1 and GPT-5.4**

### Recommended manuscript structure

1. **Introduction**
   - Motivate LLMs as candidate cognitive/behavioural models.
   - Define reliability as stability under meaning-preserving prompt changes.
   - Explain why capability and human similarity do not guarantee robustness.
   - Introduce the three decision tasks and state preregistered-style research
     questions without predicting a universally superior model.
2. **Methods**
   - Models and API provenance.
   - Tasks and frozen prompt conditions.
   - Matched-seed repeated-run design and sampling settings.
   - Primary behavioural metrics and human datasets.
   - Within-model effects, interaction contrasts, PSI, bootstrap procedure,
     multiplicity control, and robustness checks.
   - Data-quality and exclusion rules.
3. **Results**
   - Data completeness and response validity.
   - Baseline behavioural differences between models.
   - Prompt effects within GPT-4.1 and GPT-5.4.
   - Cross-model moderation of prompt sensitivity.
   - Human-reference comparison.
   - Robustness and supplementary task dynamics.
4. **Discussion**
   - State which behaviours are stable and which are prompt-dependent.
   - Separate capability, behavioural stability, and human similarity.
   - Discuss task heterogeneity rather than forcing one global winner.
   - Explain implications for using LLMs as cognitive models.
   - Limitations: two models from one provider family, 20 stochastic runs per
     cell, API snapshots, project-defined PSI, prompt set coverage, and human
     datasets collected in different settings.
5. **Conclusion**
   - Give a restrained answer about whether the newer model is more reliable,
     supported by metric-level and PSI evidence.

### Efficient writing order

Write the manuscript in this practical order:

1. Freeze Methods and Table 1.
2. Generate the analysis tables and figures.
3. Write Results directly from a frozen result checklist.
4. Write Discussion after the direction and uncertainty of every primary effect
   are known.
5. Write Introduction, then Conclusion and Abstract last.

## 6. Result-reporting rules

- Lead with effect sizes and uncertainty, not significance labels.
- Never interpret the sign of an effect without the metric definition.
- Do not call a model "better" unless the criterion is named (more stable,
  closer to humans, or higher task reward).
- Report null/uncertain results and heterogeneous task effects.
- Keep confirmatory primary metrics separate from exploratory metrics.
- Preserve exact model snapshot IDs and disclose the shared provider/API context.

## 7. Deliverables and completion order

1. Frozen input manifest and audit report.
2. Cross-model metric and PSI comparison tables.
3. New model-by-prompt interaction table with bootstrap intervals.
4. Human-distance comparison table for both models.
5. Six main figures and eight supplementary figures.
6. Main and supplementary tables.
7. Results checklist containing one verified statement per primary result.
8. Full manuscript draft, followed by reproducibility and claim-to-output audit.

The frozen input audit, Figures 2-6, main Tables 1-6, and source-linked primary
results checklist are implemented. The next analysis step is the pre-specified
robustness and multiplicity stage before drafting the Results section.
