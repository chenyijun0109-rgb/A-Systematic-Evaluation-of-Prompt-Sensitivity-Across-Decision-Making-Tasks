# English Two-Model Figure Captions

## Figure 2. Run-level behavioural distributions by model and prompt

Distributions of the eight frozen primary behavioural metrics for GPT-4.1 and
GPT-5.4 across baseline and three manipulated prompt conditions. Each point is
one formal run; boxes show the median and interquartile range, with whiskers at
1.5 times the interquartile range. Metrics retain task-specific scales, so
vertical magnitudes should not be compared across panels. Higher values are not
uniformly better because metric direction is behaviour-specific.

## Figure 3. Within-model prompt effects

Hedges' g for each manipulated condition relative to the same model's baseline.
Points are standardised effects and bars are paired-seed percentile-bootstrap
95% intervals from 2,000 replicates under the frozen within-model analysis.
The vertical line denotes no prompt effect. Sign indicates metric direction,
not improvement.

## Figure 4. Model-by-prompt interaction contrasts

Difference between the GPT-5.4 prompt effect and the corresponding GPT-4.1
prompt effect. Points estimate `[(GPT-5.4 condition - GPT-5.4 baseline) -
(GPT-4.1 condition - GPT-4.1 baseline)]`; bars are percentile-bootstrap 95%
intervals from 2,000 replicates. Horizon and BART resample matched environment
seed blocks. IGT resamples runs independently within model-prompt cells because
its fixed environment ignores the nominal run seed. The contrast measures
cross-model moderation of prompt sensitivity and is not a causal
difference-in-differences estimate.

## Figure 5. Prompt Sensitivity Index by model and task

Top: the project-defined Prompt Sensitivity Index (PSI), with percentile-
bootstrap 95% intervals, for each model, task, and manipulated prompt. Bottom:
the descriptive PSI difference (`GPT-5.4 - GPT-4.1`); no inferential interval is
attached to this difference. PSI averages absolute standardised effects across
the frozen primary metrics and is not a validated psychological scale.

## Figure 6. Model distance from task-specific human reference distributions

Human-SD standardised distance between each LLM condition mean and the frozen
task-specific human mean. Zero denotes the human mean; grey bands show the
human participant-level 2.5th-97.5th percentile interval expressed on the same
human-SD scale. Points are condition means, not inferential estimates of a
shared population parameter. Each task uses one frozen reference dataset
(Horizon 60 participants, IGT 504 participants, BART 141 participants; Horizon
random exploration uses 60 participant-level hierarchical-model estimates).
Pump-based BART metrics are prioritised to avoid monetary-scale mismatch.
Distributional proximity does not establish a shared cognitive mechanism.
