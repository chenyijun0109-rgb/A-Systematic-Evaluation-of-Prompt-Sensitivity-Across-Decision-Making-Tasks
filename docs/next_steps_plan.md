# 后续研究与实施计划书

**项目：** How Reliable Are LLMs as Cognitive Models?  
**制定日期：** 2026-06-13  
**当前阶段：** Pilot 完成，进入指标验证、分析管线建设与多 run 实验阶段

## 1. 总体目标

接下来的工作不是立即扩大 API 调用规模，而是先确保指标定义、数据处理和统计分析能够支持正式结论。最终需要回答三个问题：

1. 同一 prompt 条件下，LLM 的行为是否稳定且可复现？
2. 不同 prompt 条件是否导致具有实际意义的行为变化？
3. LLM 的行为均值与变异范围是否接近相应 human dataset？

正式实验的目标规模为：

```text
3 tasks x 4 prompt conditions x 15-20 valid runs
```

即最少 180 个、目标 240 个有效 runs。正式采集前必须完成本计划中的方法验证和 mini pilot。

## 2. 当前基础

已经完成：

- Horizon、IGT 和 BART 三个任务环境与统一 runner。
- 四类 prompt 条件及严格输出解析。
- 三个任务的 single-run pilot。
- Human data 的初步 participant-level 指标预处理。
- 删除 BART 中与 `adjusted_average_pumps` 重复的 `cash_out_threshold`。
- 删除原先不严谨的 Horizon `random_exploration` proxy。
- 基于 Wilson et al. (2014) 的 first-free-choice logistic model 实现：

```text
random_exploration_effect
    = decision_noise_h6 - decision_noise_h1
```

当前限制：

- 每个 prompt 条件只有一个 pilot run，无法估计 run 间方差、PSI、ICC 或可靠置信区间。
- 新的 random-exploration 模型尚缺少 bootstrap 区间、参数恢复和 shrinkage 敏感性验证。
- 多 run 自动聚合与正式 PSI 计算管线尚未完成。
- BART 年龄筛选已完成：原始 147 IDs 按 `age >= 18` 过滤后保留 141 人，并保存排除审计。

## 3. 第一阶段：验证 Random Exploration 指标

**优先级：最高**

### 3.1 明确报告定义

正式写作中将 `random_exploration` 定义为：

> Horizon 6 相对于 Horizon 1 的 decision noise 增量，即在未来探索更有价值时增加的选择变异性。

报告时使用更审慎的解释：

> choice variability consistent with random exploration

该指标不再等同于选择当前较低 reward 选项的比例，也不被解释为已经证明 LLM 内部存在真正的心理随机机制。

### 3.2 增加不确定性估计

为以下参数计算 95% bootstrap confidence intervals：

- `decision_noise_h1`
- `decision_noise_h6`
- `random_exploration_effect`
- 必要时同时报告 information bonus 参数

抽样单位：

- LLM：以 run 为 cluster 进行重抽样，保留每个 run 内部的 trials。
- Human：以 participant 为 cluster 进行重抽样，保留每名参与者内部的 games。

不能把同一 run 或 participant 内的 trial 当作相互独立样本。

### 3.3 做模型恢复测试

生成已知参数的模拟数据，检验模型能否恢复：

- Horizon 1 与 Horizon 6 相同 decision noise。
- Horizon 6 decision noise 高于 Horizon 1。
- Horizon 6 decision noise 低于 Horizon 1。
- information bonus 改变但 decision noise 不改变。

验收标准：

- 参数方向能够被正确恢复。
- 在合理样本量下估计值不存在持续性严重偏差。
- information bonus 的变化不会被系统性错误识别为 decision-noise 变化。

### 3.4 做 shrinkage 敏感性分析

当前 hierarchical MAP 和固定 Gaussian shrinkage 是本项目对小样本 LLM runs 的方法调整，并非 Wilson et al. (2014) 的原始估计方法。

至少比较三组合理的 `run_effect_sd` 设置，例如：

```text
0.25, 0.50, 1.00
```

比较内容：

- `random_exploration_effect` 的方向是否一致。
- 点估计和区间是否对 shrinkage 设置高度敏感。
- 单个 run 参数是否出现极端值。

验收标准：

- 主要结论不应只在某一个 shrinkage 设置下成立。
- 如果结论对先验或 shrinkage 高度敏感，正式结果必须完整报告，而不能只保留最有利设置。

### 3.5 本阶段产出

建议新增或更新：

```text
src/horizon_random_exploration.py
tests/test_horizon_random_exploration.py
method notes in this document
outputs/processed/random_exploration_validation/
```

完成条件：

- 模拟恢复测试通过。
- Bootstrap 区间可重复生成。
- Human 与 LLM 使用同一模型定义。
- 方法文档明确区分 Wilson et al. 的理论依据与本项目的估计调整。

## 4. 第二阶段：补全 Prompt Generation Provenance

正式实验前执行 `docs/prompt_generation_protocol.md`：

- 确认每个任务的 canonical specification 和 neutral baseline。
- 保存从每份 frozen baseline 生成三个 manipulated variants 所用的完整
  meta-prompt。
- 记录 generator model、日期和 sampling parameters。
- 保存 raw request、raw response、selection rule 和 edit log。
- 对 12 个最终 prompts 完成 rule-equivalence 和 manipulation-isolation 审核。
- 通过 dry run 和 parser tests 后冻结文件版本。

原有 prompt 文件早于该协议建立。无法确认的历史信息只能记录为
`not recorded`，不能事后补造。项目已于 2026-06-13 选择第二条路径：
删除原有实验 prompts，重新建立三份 canonical baselines，并按 Protocol
1.2 使用 `meta_prompt_v2.md` prospective generation 生成九个 variants。
该阶段已于 2026-06-14 完成：所有最小修改、完整矩阵 dry run、parser
检查和最终 SHA-256 hashes 均记录在 generation records 中。

完成条件：

- 每个 task 都有完整 generation record。
- 所有手工修改都有逐项记录。
- 最终 prompt paths 与 Git commit 或 hashes 已保存。
- 正式实验不混用不同 prompt versions。
- Replacement prompts 完成前，不运行新的四条件 LLM pilot。

## 5. 第三阶段：修正 Human Data 预处理

### 5.1 BART 样本筛选

本地文件包含 147 个 IDs。该步骤已完成：预处理从第 9 列读取年龄，
应用 `age >= 18`，排除 6 名未成年人并保留 141 人。

已完成：

- 在预处理代码中加入明确的年龄筛选；
- 记录筛选前人数、排除原因和筛选后人数；
- 重新生成 `bart_human_metrics.csv`、`bart_exclusions.csv` 和 `summary.json`；
- 增加自动测试，锁定阈值、排除 IDs 和行数。

详细记录见 `docs/bart_human_preprocessing.md`。

### 5.2 核对指标可比性

为每个 human metric 标记：

- 是否与 LLM 使用完全相同的公式。
- 是否只在概念上相近。
- 是否存在量纲或 payoff scaling 差异。

优先比较：

| Task | Primary comparable metrics |
|---|---|
| Horizon | `directed_exploration`, `horizon_effect`, `random_exploration_effect` |
| IGT | `advantageous_choice_rate`, learning-curve change/slope, `post_loss_switching_rate` |
| BART | `adjusted_average_pumps`, `explosion_rate`, `post_explosion_adjustment` |

BART earning 指标在 payoff scaling 完全核实前只作为补充结果，不作为主要 human comparison 指标。

### 5.3 本阶段产出

```text
outputs/processed/human_metrics/
docs/data_schema.md
docs/task_details.md
docs/research_log.md
```

完成条件：

- BART 最终有效样本与文献筛选逻辑一致。
- 每个 primary metric 都有相同公式、单位和聚合层级的说明。

## 6. 第四阶段：建立多 Run 聚合与 PSI 管线

Status: Completed on 2026-06-14. Run-level aggregation, strict/incomplete
validation, signed standardised effects, and PSI outputs are implemented and
tested. Bootstrap intervals remain a later formal-analysis step.

### 6.1 自动聚合

实现分析脚本，递归读取 LLM JSON，生成一行一个 run 的整洁数据表。至少包含：

- task
- prompt condition
- model
- task seed
- run/repetition ID
- parse success rate
- invalid-response count
- primary behavioural metrics
- output file path
- code/config version

脚本还应检测：

- 重复 runs。
- 缺失条件。
- 失败或不完整 runs。
- 混用不同 model、prompt version 或 task parameters 的情况。

### 6.2 正式定义 PSI

对 task \(t\)、prompt condition \(c\) 和预先选定指标 \(m\)，计算 signed standardised effect：

\[
E_{tcm} =
\frac{\bar{x}_{tcm}-\bar{x}_{t,\mathrm{baseline},m}}
{s_{t,\mathrm{baseline},m}}
\]

任务或条件层面的描述性 Prompt Sensitivity Index：

\[
\mathrm{PSI}_{tc}
=
\frac{1}{M_t}
\sum_{m=1}^{M_t}|E_{tcm}|
\]

正式输出必须同时保存：

- 原始均值差。
- Signed standardised effect。
- 每个指标的绝对效应。
- 综合 PSI。
- Bootstrap confidence interval。

PSI 是本项目构建的描述性综合指标，不应称为已有文献验证过的心理测量量表。

### 6.3 PSI 的边界处理

提前规定：

- Baseline SD 接近 0 时的处理方法。
- 缺失指标是否允许计算 PSI。
- 每个 task 纳入 PSI 的指标列表。
- 不让高度重复的指标被重复计权。
- 是否采用等权平均；若采用，说明这是为了透明性而非理论上断言权重完全相同。

### 6.4 本阶段产出

建议新增：

```text
src/aggregate_experiment_results.py
src/compute_prompt_sensitivity.py
tests/test_aggregate_experiment_results.py
tests/test_prompt_sensitivity.py
outputs/processed/llm_run_metrics.csv
outputs/processed/prompt_sensitivity.csv
```

完成条件：

- 使用人工构造的小数据可以正确恢复预期 PSI。
- 同一输入重复分析得到相同结果。
- 单个 run 不会被误当成独立 trial 重复计入。

## 7. 第五阶段：运行 3-Run Mini Pilot

实验规模：

```text
3 tasks x 4 prompt conditions x 3 runs = 36 runs
```

设计原则：

- 同一 task 下，不同 prompt 条件使用相同的一组 environment seeds。
- 每个 run 的 LLM 调用保持独立，不跨条件共享对话历史。
- 锁定 model、temperature、prompt 文件、任务参数、parser 和代码版本。
- 失败 run 保留 debug 文件，按预先规定的规则补跑。

Mini pilot 检查：

- 各条件 parse success 和 invalid responses。
- 每个指标是否存在 run 间方差。
- 新 random-exploration 模型是否能够收敛。
- Baseline SD 是否足以支持标准化。
- API 时间、调用量和成本。
- 是否存在 prompt 泄漏、输出格式偏差或明显任务误解。

进入正式实验的最低条件：

- 36 个设计单元均有预期数量的有效 runs。
- 无系统性 parser failure。
- Random-exploration 模型可以输出有效估计和区间。
- 聚合表与原始 JSON 抽查一致。
- PSI 不依赖明显错误或重复指标。

Mini pilot 只能用于发现问题和估计方差，不作为最终假设检验数据，除非在正式实验前明确决定并记录将其纳入。

## 8. 第六阶段：正式数据采集

目标：

```text
3 tasks x 4 prompt conditions x 20 runs = 240 valid runs
```

资源受限时最低接受：

```text
3 tasks x 4 prompt conditions x 15 runs = 180 valid runs
```

采集策略：

- 按 task 和 seed 组成配对 block，再在 block 内运行四个 prompt 条件。
- 随机化或轮换 prompt 条件执行顺序，降低时间和服务状态变化的混淆。
- 分批保存，每批结束后只做质量控制，不根据中间结果修改 prompt 或主要指标。
- 若必须修改方法，从新版本开始重新采集，并把版本作为独立实验处理。

正式采集前冻结：

- LLM model/version。
- Sampling parameters。
- 三个 task 的规则和 payoff。
- 四类 prompt 文件。
- 环境 seeds。
- Primary metrics 与 PSI 列表。
- Exclusion/retry rules。
- Human preprocessing rules。

## 9. 第七阶段：可靠性与正式统计分析

### 9.1 同条件稳定性

报告：

- Run-level mean、SD、median、IQR。
- Bootstrap confidence intervals。
- 分布图和异常 run。

若要检验 test-retest reliability，需要在相同任务 seeds 和参数下运行第二批独立实验。主要指标可报告 ICC(2,1)，即 two-way random-effects、absolute-agreement、single-measure ICC。

根据 Koo and Li (2016)，可将 ICC 点估计描述为：

| ICC | 描述 |
|---:|---|
| < 0.50 | Poor |
| 0.50-0.75 | Moderate |
| 0.75-0.90 | Good |
| > 0.90 | Excellent |

解释时同时报告 95% confidence interval，不能只看点估计。

### 9.2 Prompt sensitivity

对每个 manipulated prompt 与 baseline 比较：

- 原始差异。
- Standardised effect 与区间。
- PSI 与区间。
- 必要时进行 paired analysis，因为不同 prompt 使用相同 environment seeds。
- 多项指标推断时使用预先选定的 primary metrics，并对补充检验进行多重比较控制。

如要支持“差异足够小”而不只是“不显著”，使用 equivalence testing，并在分析前规定 smallest effect size of interest。该阈值必须被明确标记为项目的实质性标准，而不是通用定律。

### 9.3 Human comparison

LLM 不仅要接近 human mean，还要比较：

- Mean difference 或 standardised distance。
- LLM runs 落入 human reference interval 的比例。
- Human 与 LLM 的变异程度。
- 关键机制方向，例如 Horizon 6 是否增加 directed exploration 和 decision noise。

Human 95% reference interval 可用于描述 LLM 是否处于常见人类行为范围，但不能单独证明两者来自同一认知机制。

### 9.4 Reliability retest 的资源方案

理想方案：

```text
对全部 20 个 seeds 重复第二批实验
```

最低方案：

```text
预先抽取 10 个 seeds，在全部 task x prompt 条件中进行独立 retest
```

最终论文必须说明采用哪一方案及其精度限制。

## 10. 第八阶段：稳健性检查与论文输出

稳健性分析：

- Random-exploration shrinkage 设置变化。
- PSI 去掉任一指标后的 leave-one-metric-out 分析。
- Median-based 与 mean-based 描述结果。
- 是否包含失败后补跑的 runs。
- 不同正式批次之间的结果一致性。

建议最终图表：

1. 三个 task 的 condition-level behavioural metrics。
2. 每个 prompt 相对 baseline 的 signed standardised effects。
3. Task-level PSI 及 bootstrap intervals。
4. LLM run distributions 与 human participant distributions。
5. Horizon information bonus 与 decision noise 的分解图。
6. Test-retest scatter plots 与 ICC intervals。

## 11. 建议时间安排

| 周次 | 工作 | 核心产出 |
|---|---|---|
| Week 1 | Random-exploration 验证；prompt generation provenance | 可验证指标、冻结 prompts |
| Week 2 | BART human 修正；多 run 聚合与 PSI 实现 | 141 人 BART 数据、统一分析管线 |
| Week 3 | 36-run mini pilot、问题修复和方法冻结 | Mini-pilot 报告、冻结配置 |
| Week 4 | 180-240 个正式 runs | 完整正式数据 |
| Week 5 | Retest、ICC、PSI 与 human comparison | 正式统计结果 |
| Week 6 | 稳健性分析、图表和论文 Methods/Results | 可提交的结果材料 |

API 调用速度、预算或模型服务状态可能使 Week 4-5 延长，因此应优先保证配对设计和有效 run 数，而不是为了赶时间混用不同模型版本。

## 12. 立即执行顺序

接下来按以下顺序开展：

1. 为 Horizon random-exploration 模型加入 bootstrap、模拟恢复和 shrinkage 敏感性分析。
2. 完成 prompt generation records、人工审核和 prompt version freeze。
3. 实现多 run aggregation 和 PSI 计算，并加入测试。
4. 锁定 mini-pilot 配置和三组配对 seeds。
5. 完成 36-run mini pilot，通过阶段检查后再运行正式实验。
6. 正式数据完成后执行 retest、ICC、prompt sensitivity 和 human comparison。

## 13. 最终完成标准

只有同时满足以下条件，才可以在论文中讨论 LLM 是否是 reliable cognitive model：

- Primary metrics 已预先定义并有文献或任务机制依据。
- Random exploration 不再使用简单行为比例 proxy。
- 每个 task-condition 有足够的独立 runs。
- Prompt effects 有效应量和不确定区间，而非只比较单次结果。
- 稳定性有 run 间变异和 test-retest 证据。
- Human comparison 同时考虑均值和变异范围。
- PSI 的项目自定义性质、指标选择和局限性被明确说明。
- 所有分析都可以从原始 JSON 和 human raw data 重复生成。
