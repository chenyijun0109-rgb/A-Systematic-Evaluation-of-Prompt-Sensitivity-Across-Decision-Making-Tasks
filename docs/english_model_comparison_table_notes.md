# English Two-Model Main Table Notes

## Table 1. Experimental design and provenance

Exact requested/resolved model snapshots, task-prompt cells, prompt SHA-256
hashes, sampling settings, task lengths, matched-seed counts, valid run counts,
and audit status. Non-English runs are excluded.

## Table 2. Primary metric descriptives

Run-level n, mean, sample SD, median, minimum, and maximum for all eight frozen
primary metrics by model and prompt condition. Metric directions and scales are
task-specific.

## Table 3. Within-model prompt effects

Each manipulated prompt is compared with the same model's baseline. The table
reports raw mean differences and percentile-bootstrap intervals plus Hedges' g
and its bootstrap interval. No FDR-adjusted p-values are included at this stage
because the frozen analysis currently estimates effect sizes and uncertainty,
not null-resampling p-values. Any later multiplicity analysis must define the
test statistic, null resampling scheme, and correction family before adding
adjusted values.

## Table 4. Model-by-prompt interaction contrasts

`[(GPT-5.4 condition - GPT-5.4 baseline) - (GPT-4.1 condition - GPT-4.1
baseline)]` with task-valid percentile-bootstrap intervals. Horizon and BART
resample matched environment-seed blocks; IGT resamples runs independently
within model-prompt cells. These are factorial interaction contrasts, not causal
difference-in-differences estimates.

## Table 5. Prompt Sensitivity Index

Model-specific PSI estimates and bootstrap intervals plus the descriptive
`GPT-5.4 - GPT-4.1` PSI difference. PSI is a project-defined mean absolute
standardised effect and not a validated psychological scale. The cross-model
PSI difference currently has no inferential interval.

## Table 6. Human-reference comparison

Signed and absolute human-SD distance, participant-level reference interval,
run-level reference coverage, and changes from each model's own baseline.
Distributional proximity does not establish a shared cognitive mechanism.

## Primary-results checklist

`primary_results_checklist.csv` contains exactly one mechanically generated
statement for every row in Tables 2-6. Each statement has a stable result ID,
family, source filename, composite source key, and verification status. The
checklist is a writing control: manuscript prose must remain consistent with
these frozen values, but the generated sentences are not substitutes for
scientific interpretation.
