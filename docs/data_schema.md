# Data Schema

Status: Current v0.2

Date: 2026-05-28

Purpose: This document defines how data should be recorded for the LLM cognitive decision-making experiments. It covers raw LLM responses, trial-level/action-level records, run-level metrics, invalid response logs, and output file naming.

中文说明：这份文档规定后续实验数据应该如何保存。它的作用是让 task environment、LLM runner、parser 和 analysis scripts 使用同一套字段，避免后期发现某些指标无法计算。

## 1. Data Levels

本项目至少保存四层数据：

| Level | File type | Purpose |
|---|---|---|
| Raw LLM output | `.jsonl` | 保存模型每一次原始回复，方便检查 parser 和复现实验 |
| Trial/action-level data | `.csv` or `.jsonl` | 保存每个 trial/action 的状态、选择、反馈和解析结果 |
| Run-level metrics | `.csv` | 保存每个完整 run 的行为指标 |
| Invalid response log | `.csv` or `.jsonl` | 保存无效输出、重试次数和失败原因 |

中文解释：

- raw LLM output 是最原始的证据，不能只保存 parser 后的结果。
- trial/action-level data 是计算所有行为指标的基础。
- run-level metrics 是后续比较 prompt conditions 的主要分析单位。
- invalid response log 用来说明模型是否稳定遵守输出格式。

## 2. Common Identifiers

所有数据层都应该包含以下共同字段：

| Field | Type | Description |
|---|---|---|
| `experiment_id` | string | 实验批次 ID，例如 `stage01_pilot` 或 `stage01_main` |
| `config_name` | string | 使用的配置文件名，例如 `experiment_config_stage01` |
| `task` | string | `horizon`, `igt`, or `bart` |
| `prompt_condition` | string | 当前 prompt condition |
| `run_id` | integer | 当前 task x prompt condition 下的 run 编号 |
| `model_name` | string | 实际调用的模型名称 |
| `temperature` | float | sampling temperature |
| `top_p` | float | top-p setting |
| `seed` | integer or string | task environment seed / run seed |
| `timestamp_utc` | string | ISO timestamp |

中文解释：

这些字段是数据追踪的骨架。后续如果发现某个结果异常，应该能通过这些字段追溯到：哪个 task、哪个 prompt、哪个 run、哪个模型设置、哪个 seed。

## 3. Raw LLM Output Schema

Recommended path:

```text
outputs/raw/{task}/{prompt_condition}/run_{run_id}.jsonl
```

Each line should represent one model call:

| Field | Type | Description |
|---|---|---|
| `experiment_id` | string | 实验批次 ID |
| `task` | string | task name |
| `prompt_condition` | string | prompt condition |
| `run_id` | integer | run 编号 |
| `step_id` | integer | 当前模型调用编号 |
| `trial_number` | integer or null | 当前 trial/action 编号 |
| `game_id` | integer or null | Horizon 专用 |
| `balloon_id` | integer or null | BART 专用 |
| `prompt_text` | string | 发送给模型的完整 prompt 或 message text |
| `raw_response` | string | 模型原始输出 |
| `model_name` | string | 模型名称 |
| `temperature` | float | temperature |
| `top_p` | float | top-p |
| `max_tokens` | integer or string | max token setting |
| `timestamp_utc` | string | ISO timestamp |

中文解释：

`raw_response` 必须完整保存，不能只保存 `CHOICE: A` 这种解析后的动作。因为后期如果 parser 规则修改，或者模型输出格式有争议，需要能回头检查原始文本。

## 4. Trial-Level / Action-Level Common Fields

Recommended path:

```text
outputs/processed/trial_level/{task}_{prompt_condition}_runs.csv
```

Common fields:

| Field | Type | Description |
|---|---|---|
| `experiment_id` | string | 实验批次 ID |
| `task` | string | task name |
| `prompt_condition` | string | prompt condition |
| `run_id` | integer | run 编号 |
| `trial_number` | integer | 当前 trial/action 编号 |
| `within_task_step` | integer | task 内部连续 step 编号 |
| `raw_response` | string | 模型原始输出 |
| `parsed_action` | string | parser 提取后的动作 |
| `parse_success` | boolean | 是否解析成功 |
| `retry_count` | integer | 当前 trial/action 使用了几次重试 |
| `invalid_reason` | string or null | 无效输出原因 |
| `observation_text` | string | 当前展示给模型的 task state |
| `feedback_text` | string | 当前动作后的反馈文本 |

中文解释：

`trial_number` 是任务意义上的 trial 或 action 编号；`within_task_step` 是 runner 内部从 1 开始递增的调用编号。BART 中一个 balloon 可能有多个 action，所以这两个字段都需要。

## 5. Horizon Trial-Level Fields

Horizon rows should extend the common fields with:

| Field | Type | Description |
|---|---|---|
| `game_id` | integer | 当前 game 编号 |
| `game_trial_number` | integer | 当前 game 内第几次 trial |
| `horizon_type` | string | `horizon_1` or `horizon_6` |
| `information_condition` | string | `equal_information` or `unequal_information` |
| `is_forced_choice` | boolean | 是否 forced-choice trial |
| `forced_choice_target` | string or null | forced-choice 阶段指定的选项 |
| `choice` | string | `A` or `B` |
| `reward` | integer | 当前选择得到的 reward |
| `mean_A` | float | 当前 game 中 A 的真实 reward mean |
| `mean_B` | float | 当前 game 中 B 的真实 reward mean |
| `observed_rewards_A` | string | 当前 trial 前 A 的已观察 rewards，可用 JSON list 字符串 |
| `observed_rewards_B` | string | 当前 trial 前 B 的已观察 rewards，可用 JSON list 字符串 |
| `n_observed_A` | integer | 当前 trial 前 A 被观察次数 |
| `n_observed_B` | integer | 当前 trial 前 B 被观察次数 |
| `observed_mean_A` | float or null | 当前 trial 前 A 的观察均值 |
| `observed_mean_B` | float or null | 当前 trial 前 B 的观察均值 |
| `information_difference` | integer | `n_observed_A - n_observed_B` |
| `observed_mean_difference` | float or null | `observed_mean_A - observed_mean_B` |
| `first_free_choice` | boolean | 是否该 game 的第一个 free-choice trial |

中文解释：

Horizon 的关键是区分 reward 信息和 uncertainty 信息。因此必须记录两个选项各自已经被观察了几次、观察到哪些 rewards、观察均值是多少。`first_free_choice` 是后续计算 directed exploration 和 `random_exploration_effect` 的核心筛选字段。

## 6. IGT Trial-Level Fields

IGT rows should extend the common fields with:

| Field | Type | Description |
|---|---|---|
| `deck` | string | `A`, `B`, `C`, or `D` |
| `deck_selection_count` | integer | 当前 deck 已被选择到第几次 |
| `reward` | integer | 当前 trial gain |
| `loss` | integer | 当前 trial loss，通常为 0 或负数 |
| `net_outcome` | integer | `reward + loss` |
| `cumulative_score` | integer | 当前 run 累计分数 |
| `block_number` | integer | 1-5 |
| `advantageous_choice` | boolean | 是否选择 C/D |
| `previous_deck` | string or null | 上一 trial 的 deck |
| `previous_loss` | integer or null | 上一 trial 的 loss |
| `post_loss_trial` | boolean | 上一 trial 是否发生 loss |
| `switched_after_loss` | boolean or null | 如果上一 trial 有 loss，本 trial 是否换 deck |

中文解释：

IGT 的重点是长期学习，所以必须记录每一步的 deck、reward、loss、net outcome 和 cumulative score。`deck_selection_count` 很重要，因为 payoff schedule 是按某个 deck 被选择第几次来计算，而不是按全局 trial number。

## 7. BART Action-Level Fields

BART rows should extend the common fields with:

| Field | Type | Description |
|---|---|---|
| `balloon_id` | integer | 当前 balloon 编号 |
| `block_number` | integer | 1 or 2 |
| `balloon_action_number` | integer | 当前 balloon 内第几次 action |
| `action` | string | `PUMP` or `CASH_OUT` |
| `pump_count_before_action` | integer | action 前当前 balloon 已 pump 次数 |
| `pump_count_after_action` | integer | action 后当前 balloon 已 pump 次数 |
| `temporary_earning_before_action` | float | action 前 temporary earning |
| `temporary_earning_after_action` | float | action 后 temporary earning |
| `total_earning_before_action` | float | action 前 total earning |
| `total_earning_after_action` | float | action 后 total earning |
| `exploded` | boolean | 当前 action 是否导致爆炸 |
| `cashed_out` | boolean | 当前 action 是否 cash out |
| `balloon_ended` | boolean | 当前 action 后 balloon 是否结束 |
| `explosion_point` | integer | 当前 balloon 的隐藏爆炸点 |

中文解释：

BART 中一个 balloon 会包含多个 action，因此 action-level 数据比单纯 balloon-level 数据更细。它可以分析模型是否在爆炸后变保守，或者是否形成相对稳定的 pump / cash-out 策略。

## 8. BART Balloon-Level Summary Fields

Recommended path:

```text
outputs/processed/trial_level/bart_{prompt_condition}_balloon_summary.csv
```

| Field | Type | Description |
|---|---|---|
| `experiment_id` | string | 实验批次 ID |
| `task` | string | `bart` |
| `prompt_condition` | string | prompt condition |
| `run_id` | integer | run 编号 |
| `balloon_id` | integer | balloon 编号 |
| `block_number` | integer | block 编号 |
| `final_pump_count` | integer | 当前 balloon 最终 pump 次数 |
| `exploded` | boolean | 是否爆炸 |
| `cashed_out` | boolean | 是否 cash out |
| `earning_from_balloon` | float | 当前 balloon 最终进入 total 的收益 |
| `explosion_point` | integer | 隐藏爆炸点 |
| `previous_balloon_exploded` | boolean or null | 上一个 balloon 是否爆炸 |
| `pump_change_after_explosion` | integer or null | 如果上一个 balloon 爆炸，本 balloon pump 数变化 |

中文解释：

balloon-level summary 用于和 human dataset 对齐。BART 的主要指标，例如 average pumps、adjusted average pumps 和 explosion rate，都可以从这个表中直接计算。

## 9. Run-Level Metrics Schema

Recommended path:

```text
outputs/processed/run_level/{task}_run_metrics.csv
```

Common fields:

| Field | Type | Description |
|---|---|---|
| `experiment_id` | string | 实验批次 ID |
| `task` | string | task name |
| `prompt_condition` | string | prompt condition |
| `run_id` | integer | run 编号 |
| `valid_run` | boolean | 是否为有效完整 run |
| `n_valid_trials_or_actions` | integer | 有效 trial/action 数 |
| `n_invalid_responses` | integer | 无效响应数 |
| `parse_success_rate` | float | 解析成功比例 |
| `average_outcome` | float | 当前 run 的平均 reward / net outcome / earning |

Task-specific metrics:

| Task | Metric fields |
|---|---|
| Horizon | `exploration_rate`, `directed_exploration`, `random_exploration_effect`, `switching_rate`, `horizon_effect`, `average_reward_per_trial` |
| IGT | `net_score`, `advantageous_choice_rate`, `deck_A_rate`, `deck_B_rate`, `deck_C_rate`, `deck_D_rate`, `average_net_outcome`, `post_loss_switching_rate` |
| BART | `average_pumps`, `adjusted_average_pumps`, `explosion_rate`, `average_earning_per_balloon`, `post_explosion_adjustment` |

中文解释：

run-level metrics 是正式分析的基本单位。prompt sensitivity 的计算不是直接对每个 trial 做，而是先把每个 run 汇总成指标，再比较不同 prompt condition 下这些 run-level metrics 的分布。

## 10. Invalid Response Log

Recommended path:

```text
outputs/processed/invalid_responses/{task}_{prompt_condition}_invalid.csv
```

Fields:

| Field | Type | Description |
|---|---|---|
| `experiment_id` | string | 实验批次 ID |
| `task` | string | task name |
| `prompt_condition` | string | prompt condition |
| `run_id` | integer | run 编号 |
| `trial_number` | integer or null | trial/action 编号 |
| `step_id` | integer | 模型调用编号 |
| `raw_response` | string | 原始无效输出 |
| `expected_format` | string | 期望格式 |
| `invalid_reason` | string | 无效原因 |
| `retry_count` | integer | 已重试次数 |
| `resolved_after_retry` | boolean | 重试后是否解决 |

Common `invalid_reason` values:

```text
missing_required_prefix
invalid_option
multiple_actions
empty_response
non_parseable_text
api_error
timeout
```

中文解释：

invalid response 不应该被悄悄丢弃。它本身也是结果的一部分，因为不同 prompt condition 可能会影响模型是否遵守格式。

## 11. Human Preprocessing Audit

BART human preprocessing writes:

```text
outputs/processed/human_metrics/bart_human_metrics.csv
outputs/processed/human_metrics/bart_exclusions.csv
outputs/processed/human_metrics/summary.json
```

`bart_exclusions.csv` contains:

| Field | Type | Description |
|---|---|---|
| `participant_id` | integer | Excluded local participant ID |
| `age` | integer | Age read from zero-based Excel column 8 |
| `n_balloons` | integer | Number of raw balloon rows |
| `exclusion_reason` | string | Current value is `age_below_18` |

`summary.json.bart_filter` records the minimum age, source/included/excluded
participant counts, excluded IDs and ages, and source/included/excluded row
counts.

## 12. File Naming Rules

Use lowercase task names and prompt condition names:

```text
outputs/raw/horizon/baseline/run_001.jsonl
outputs/raw/igt/reward_loss_emphasis/run_001.jsonl
outputs/raw/bart/risk_emphasis/run_001.jsonl

outputs/processed/trial_level/horizon_baseline_runs.csv
outputs/processed/trial_level/igt_baseline_runs.csv
outputs/processed/trial_level/bart_baseline_actions.csv

outputs/processed/run_level/horizon_run_metrics.csv
outputs/processed/run_level/igt_run_metrics.csv
outputs/processed/run_level/bart_run_metrics.csv
```

中文解释：

文件命名要让人一眼看出 task、prompt condition 和 run。不要把不同 prompt condition 混在同一个 raw 文件里；processed summary 可以合并，但必须保留 `task` 和 `prompt_condition` 字段。

## 13. Minimum Completion Criteria

Before the main experiment, the pilot must show:

- raw responses are saved for every model call;
- trial/action-level files contain all fields needed for metrics;
- run-level metrics can be computed for all three tasks;
- invalid responses are logged rather than silently dropped;
- each `task x prompt_condition` can be traced back to config, prompt, raw output, and processed data.

中文解释：

只有当这些条件满足后，才适合进入正式 LLM 实验。否则后期即使跑出了结果，也可能无法解释、无法复现，或者无法和 human dataset 对齐。

## 14. Multi-Run Aggregation Outputs

Raw pilot files use:

```text
{task}_{prompt_condition}_seed-{task_seed}.json
{task}_{prompt_condition}_seed-{task_seed}_failed.json
```

The logical run identifier is:

```text
run_id = task:prompt_condition:seed
```

`llm_run_metrics.csv` contains one row per valid logical run:

| Field | Description |
|---|---|
| `run_id` | Stable logical run key |
| `task`, `prompt_condition` | Experimental cell |
| `model` | Exact model ID |
| `seed` | Canonical task seed |
| `config_name`, `config_version` | Configuration provenance |
| `prompt_path`, `prompt_sha256` | Prompt provenance |
| `done`, `n_trials` | Completion and task size |
| `parse_success_rate`, `invalid_response_count` | Parser quality |
| `source_path` | Resolved raw JSON path |

Task metrics are additional numeric columns. Derived fields:

```text
learning_curve_change =
    IGT block 5 net score - IGT block 1 net score

random_exploration_effect =
    Horizon decision_noise_h6 - decision_noise_h1
```

`aggregation_quality_report.json` records expected runs per cell, duplicate
policy, discovered and valid counts, ignored files, issue codes, and
`analysis_complete`.

## 15. Prompt-Sensitivity Outputs

`metric_summary.csv` stores `n`, mean, sample SD using `n - 1`, median,
minimum, and maximum for every available task-condition metric.

`prompt_effects.csv` stores:

| Field | Description |
|---|---|
| `baseline_mean`, `condition_mean` | Run-level group means |
| `raw_mean_difference` | Condition minus baseline |
| `baseline_sd`, `condition_sd` | Sample SDs |
| `denominator`, `sd_source` | Standardisation scale |
| `signed_standardised_effect` | Directional effect |
| `absolute_standardised_effect` | Effect magnitude |
| `warning_flags` | Variance warnings |

`prompt_sensitivity.csv` contains PSI, expected and valid metric counts,
excluded metrics, and status. Status is `complete`, `partial`, or
`insufficient`. Strict mode requires all three configured metrics.
`--allow-incomplete` requires at least two valid metrics for a partial PSI;
one metric is never labelled PSI.

`analysis_summary.json` records the analysis mode, source table, row counts,
issues, completeness, and the explicit boundary that PSI is a project-defined
descriptive composite rather than a validated psychological scale.
