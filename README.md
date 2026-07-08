# How Reliable Are LLMs as Cognitive Models?

## A Systematic Evaluation of Prompt Sensitivity Across Decision-Making Tasks

## Frozen Validation Method (2026-06-15)

The current validation configuration is frozen in:

```text
configs/experiment_config_stage01.json
configs/formal_experiment_freeze.json
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

Primary PSI metrics:

| Task | Primary metrics |
|---|---|
| Horizon | `directed_exploration`, `horizon_effect`, `random_exploration_effect` |
| IGT | `advantageous_choice_rate`, `post_loss_switching_rate` |
| BART | `adjusted_average_pumps`, `explosion_rate`, `post_explosion_adjustment` |

IGT `learning_slope`, `learning_curve_change`, and the complete five-block
curve are supplementary trajectory analyses. They are not primary PSI
metrics because a model that starts at ceiling can have a slope near zero.

The primary standardized effect is pooled-SD Hedges' g. The previous
baseline-SD standardized difference is retained as a sensitivity column.
PSI is the mean absolute Hedges' g across the task's primary metrics.
Raw differences, paired-seed 95% bootstrap intervals, and valid bootstrap
replicate counts must be reported with PSI.

Horizon random exploration uses the first-free-choice hierarchical logistic
MAP model. Formal reporting uses whole-run cluster bootstrap intervals and
checks `run_effect_sd` values `0.25`, `0.50`, and `1.00`. Results with fewer
than 15 valid runs are diagnostic only; the target is 20 runs per condition.

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
prompts/generation/meta_prompt_v2.md
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
只使用 `meta_prompt_v2.md` 生成 9 个 manipulated variants，并保存完整记录。

现有 12 个实验 prompts 的生成来源、修改记录和冻结状态记录在
`prompts/generation/current_prompt_provenance.md`。新建的
`meta_prompt_v2.md` 是 prospective protocol，不能被描述为历史 prompts
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
    meta_prompt_v2.md
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

1. 为 Horizon random-exploration 模型加入 bootstrap confidence intervals、模拟参数恢复和 shrinkage 敏感性分析。
2. 检查 36-run mini pilot 的低 baseline variance 和异常大标准化效应。
3. 方法与配置冻结后，运行每个 task-condition 15-20 个有效 runs。
4. 完成 ICC、bootstrap intervals 和 human comparison 分析。

在 random-exploration validation、human preprocessing 修正和 aggregation tests 通过前，不开始大规模正式 API 实验。

Prompt regeneration、审核和冻结已完成。新的 mini pilot 应只使用当前冻结的
12 个 prompt 文件。

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

## Important Principles

- 正式实验前锁定 task rules、prompt set、parser、model settings 和 output schema。
- Prompt 修改必须记录在 `docs/research_log.md`。
- Human comparison 使用处理后的行为指标，不直接比较 raw human data 和 raw LLM text。
- PSI 是本项目构建的描述性综合指标，不是已有文献中的标准心理量表。
- Pilot 结果只能用于方法学检查和趋势观察，不能作为正式统计结论。
