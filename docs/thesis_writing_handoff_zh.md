# 正式论文写作交接说明

更新日期：2026-08-01  
研究主题：LLM 在认知决策任务中的 prompt sensitivity 与行为可靠性

## 1. 一页式当前状态

### 已完成

- 三个模型的英文正式实验全部完成：GPT-4.1、GPT-5.4、GPT-5.4 Mini。
- 每个模型包含 240 个有效 task runs，共 720 个有效 runs。
- 每个 `model × task × prompt condition` cell 均有 20 runs。
- 三批数据使用相同英文 prompts、prompt hashes、seeds、任务参数和 sampling settings。
- 三个模型各自的严格聚合、prompt effects 和 PSI 均已生成，`analysis_complete=true`、`issues=[]`。
- GPT-5.4 Mini 的三个失败任务已在正式轮次结束后补跑成功；被取代的失败 JSON 已删除。

### 已删除或排除

- 旧的 GPT-4.1 对 GPT-5.4 两模型正文图、正文表和 results checklist 已删除。
- GPT-5.4 Nano、早期 GPT-5.4 Mini 尝试、多语言实验和 pilots 不进入正式结果。
- 两模型底层 comparison CSV、human comparison CSV 和生成脚本仍保留，仅用于审计和开发三模型分析。

### 尚未完成

- 尚未生成统一的三模型 cross-model interaction analysis。
- GPT-5.4 Mini 的 model-specific human-reference comparison 已生成；统一的三模型 human-reference table/figure 尚未生成。
- 尚未生成最终三模型 Tables 1–6、Figures 1–6 和 supplementary package。
- IGT 的 independent-cell bootstrap 已实现并用于三批正式结果。
- Robustness、multiplicity specification 和最终 results checklist 尚未冻结。

### 当前结论

实验采集阶段已经结束，但论文 Results 尚不能冻结。现在可以正式写 Methods；Results 应在三模型分析、图表和结果清单完成后撰写。

## 2. 最终论文范围

### 2.1 正式模型

| 论文简称 | Requested model | Resolved snapshot | 有效 runs |
|---|---|---|---:|
| GPT-4.1 | `gpt-4.1-2025-04-14` | `gpt-4.1-2025-04-14` | 240 |
| GPT-5.4 | `gpt-5.4` | `gpt-5.4-2026-03-05` | 240 |
| GPT-5.4 Mini | `gpt-5.4-mini` | `gpt-5.4-mini-2026-03-17` | 240 |

正式设计：

```text
3 models × 3 tasks × 4 prompt conditions × 20 runs
= 720 valid task runs
```

共同 sampling settings：

```text
language: English
temperature: 0.7
top_p: 1.0
max_output_tokens: 16
```

### 2.2 正式任务和 prompt conditions

论文、图表和结果表统一使用以下展示名称；反引号中的值仍是代码、配置和
CSV 使用的冻结 machine identifiers，不得直接重命名，否则会破坏已有数据
与 prompt hashes 的可追溯性：`baseline` = Neutral baseline，`detailed` =
Instruction specificity，`role_human` = Role framing，三个任务特定条件分别
显示为 Uncertainty and information emphasis、Reward and loss emphasis 和
Risk-taking and risk-management emphasis。指标展示名统一由
`src/reporting_names.py` 定义，其中 `horizon_effect` 在论文中写作
Horizon-related change in exploration rate。

| Task | Baseline | 通用改写 | 角色 framing | Task-specific emphasis |
|---|---|---|---|---|
| Horizon | `baseline` | `detailed` | `role_human` | `uncertainty_emphasis` |
| IGT | `baseline` | `detailed` | `role_human` | `reward_loss_emphasis` |
| BART | `baseline` | `detailed` | `role_human` | `risk_emphasis` |

任务规模：

- Horizon：40 games，300 choices/run；
- IGT：100 trials/run；
- BART：40 balloons/run，pump-action 数量可变。

正式 baseline 不暴露经典任务名称。`baseline_task_named.md` 不属于当前四条件矩阵。

### 2.3 不进入正式分析的材料

- GPT-5.4 Nano 的空状态或中止尝试；
- `outputs/model_comparison_en_v01/gpt-5.4-mini/` 中的早期失败计划；
- 中文、西班牙语 experiments；
- mini-pilot、single-run pilot 和 debug outputs；
- 已被成功补跑取代并删除的失败尝试。

这些材料只能用于说明方法开发和工程限制，不能增加正式样本量或支持行为结论。

## 3. 论文要回答的问题

论文应依次回答：

1. 同一个模型是否会因 meaning-preserving prompt changes 而改变行为？
2. GPT-5.4 和 GPT-5.4 Mini 的 prompt sensitivity 是否不同于 GPT-4.1？
3. 三模型差异是否在 Horizon、IGT 和 BART 中一致？
4. Mini 模型是否表现出不同的能力—稳定性关系？
5. 哪些模型—prompt 组合更接近 human reference distributions？
6. Prompt stability、task performance 和 human similarity 是否指向相同结论？

不得把研究问题简化为“哪个模型最好”。以下三个标准必须分别报告：

- **Prompt stability**：meaning-preserving wording changes 下行为是否稳定；
- **Task performance**：奖励、有利选择或任务结果是否更高；
- **Human similarity**：行为指标是否接近人类参考分布。

## 4. 主要指标

| Task | Primary metrics | 解释边界 |
|---|---|---|
| Horizon | `directed_exploration` | 是否更常选择信息较多选项 |
| Horizon | `horizon_effect` | 长短 horizon 间的探索变化 |
| Horizon | `random_exploration_effect` | 长 horizon 是否增加 choice variability |
| IGT | `advantageous_choice_rate` | 选择 C/D 有利牌组的比例 |
| IGT | `post_loss_switching_rate` | loss 后切换牌组的比例 |
| BART | `adjusted_average_pumps` | 未爆炸气球的平均 pumps |
| BART | `explosion_rate` | 气球爆炸比例 |
| BART | `post_explosion_adjustment` | 爆炸后下一气球 pumps 的变化 |

指标方向必须逐项解释。正数不自动代表更优、更稳定或更像人。

以下属于 supplementary analyses：IGT block learning curves、learning slope、deck rates、reward/outcome metrics、Horizon supplementary rates、完整 BART pump dynamics。

## 5. 数据质量与可复现性

### 5.1 三模型共同质量状态

- 每个模型 240/240 有效 runs；
- 每个 task-condition cell 20 runs；
- 三模型逻辑 keys 完全一致；
- 对应 prompt SHA-256 完全一致；
- task trial/game/balloon 结构完整；
- model-specific aggregation 和 PSI 均完成；
- processed analysis reports 均为 `issues=[]`。

### 5.2 GPT-5.4 Mini 的披露事项

`Horizon / baseline / seed 20260726` 在 301 次响应中出现一次格式无效响应，随后自动重试成功。最终 run 含全部 300 个有效 trials，parse success rate 为 `0.99668`。

该事件属于已恢复的 parser retry，不造成行为数据缺失。为避免 outcome-dependent replacement，该有效 run 保留，并在 data-quality note 中披露。

### 5.3 Human reference data

| Task | 冻结参考样本 |
|---|---:|
| Horizon | 60 participants |
| IGT | 504 participants |
| BART | 141 adults |

每个 LLM run 作为 participant-level behavioural analogue 与 human participant distributions 比较。分布接近不等于认知机制相同。BART 优先比较 pump-based metrics，避免不同来源的货币尺度问题。

## 6. 权威数据位置

### 6.1 Raw formal data

```text
GPT-4.1
outputs/formal_v01/

GPT-5.4
outputs/model_comparison_en_v01/gpt-5.4/wave-*/

GPT-5.4 Mini
outputs/model_comparison_en_v01/gpt-5.4-mini-formal-v01/wave-*/
```

### 6.2 Model-specific processed data

```text
outputs/processed/formal_v01/
outputs/processed/model_comparison_en_v01/gpt-5.4/
outputs/processed/model_comparison_en_v01/gpt-5.4-mini-formal-v01/
```

每个目录包含：

- `llm_run_metrics.csv`；
- `metric_summary.csv`；
- `prompt_effects.csv`；
- `prompt_sensitivity.csv`；
- `aggregation_quality_report.json`；
- `analysis_summary.json`。

### 6.3 仅供审计的两模型材料

```text
outputs/processed/model_comparison_en_v01/gpt-4.1_vs_gpt-5.4/
outputs/processed/model_comparison_en_v01/human_comparison/
docs/english_model_comparison_analysis_overview_zh.md
docs/english_model_comparison_figure_captions.md
docs/english_model_comparison_table_notes.md
```

旧两模型图表目录已经删除：

```text
outputs/figures/model_comparison_en_v01/
outputs/processed/model_comparison_en_v01/main_tables/
```

不得在最终论文中引用旧两模型图表编号或行数。

## 7. 冻结的分析逻辑

### 7.1 描述统计

对每个 `model × task × condition × metric` 报告 n、mean、SD、median、minimum、maximum、run-level distribution，以及 ceiling/floor 和 low-variance flags。

Baseline model differences 只描述模型原始行为位置，不能回答哪个模型更 prompt-sensitive。

### 7.2 Within-model prompt effects

三种 manipulated conditions 分别与同模型 baseline 比较：

```text
condition − baseline
```

报告：

- raw mean difference；
- bootstrap 95% interval；
- Hedges' g；
- standardised-effect interval；
- low-variance warning。

### 7.3 Model-by-prompt interaction contrasts

正文以 GPT-4.1 为参考，计算：

```text
[(GPT-5.4 condition − GPT-5.4 baseline)
 − (GPT-4.1 condition − GPT-4.1 baseline)]

[(GPT-5.4 Mini condition − GPT-5.4 Mini baseline)
 − (GPT-4.1 condition − GPT-4.1 baseline)]
```

Mini 对 GPT-5.4 可作为补充 comparison。

这些是 factorial interaction contrasts，不是具有政策因果含义的 difference-in-differences。

重采样单位：

- Horizon/BART：matched environment-seed blocks；
- IGT：在各 model-prompt cell 内独立 resampling。

IGT 的环境忽略 seed，API token sampling 也没有由该 seed 耦合。因此 IGT 相同 seed 只是 run label，不能声称 paired inference。

### 7.4 Prompt Sensitivity Index

```text
PSI = mean(abs(standardised primary-metric prompt effects))
```

报告每个模型、任务、manipulated condition 的 PSI 及 uncertainty，同时给出模型间 PSI differences。

PSI 是项目自定义的描述性汇总指标，不是 validated psychometric scale，也不能替代 metric-level results。

### 7.5 Human-reference comparison

对三模型分别报告：

- signed human-SD distance；
- absolute human-SD distance；
- human 2.5th–97.5th percentile reference interval；
- LLM runs 落入 reference interval 的比例；
- manipulated prompt 相对本模型 baseline 的 distance/coverage change。

Human proximity 与 prompt stability 必须分开解释。

### 7.6 Robustness 与 multiplicity

最终 Results 前需要完成：

- Horizon `run_effect_sd = 0.25, 0.50, 1.00`；
- leave-one-metric-out PSI；
- mean-based 与 median-based summaries；
- ceiling/floor 和 low baseline variance checks；
- IGT independent-cell bootstrap 已完成验证；
- raw 与 standardised effects 对照。

若实施 BH-FDR，必须预先定义 test statistic、null-resampling scheme 和 correction family。不能从 percentile-bootstrap CI 临时反推 p-values。

## 8. 最终论文图表包

### 8.1 Main figures

| Figure | 内容 |
|---|---|
| Figure 1 | 三模型实验设计与分析流程 |
| Figure 2 | 八个 primary metrics 的三模型 run-level distributions |
| Figure 3 | 三模型 within-model prompt-effect forest plots |
| Figure 4 | GPT-5.4/Mini 相对 GPT-4.1 的 interaction contrasts |
| Figure 5 | 三模型 PSI 与模型间 PSI differences |
| Figure 6 | 三模型相对 human reference 的标准化距离 |

### 8.2 Main tables

| Table | 内容 |
|---|---|
| Table 1 | Design、model snapshots、sampling、prompt hashes、seeds、valid runs |
| Table 2 | Primary metric descriptives |
| Table 3 | Within-model prompt effects |
| Table 4 | Model-by-prompt interactions |
| Table 5 | PSI 与 robustness summary |
| Table 6 | Human-reference comparison |

### 8.3 Supplementary package

- S1：所有 secondary metric distributions；
- S2：Horizon/BART environment-seed slope plots；
- S3：IGT five-block learning curves；
- S4：Horizon exploration decomposition 和 shrinkage sensitivity；
- S5：BART pump/explosion dynamics；
- S6：PSI robustness；
- S7：data-quality、parser validity 和 provenance；
- S8：primary metric redundancy diagnostics；
- supplementary tables：完整统计、prompt provenance、quality flags 和 robustness results。

## 9. 论文结构与写法

### 9.1 Working title

**How Reliable Are Language Models as Cognitive Models? Prompt Sensitivity Across GPT-4.1, GPT-5.4, and GPT-5.4 Mini in Three Decision-Making Tasks**

“Reliable” 应操作化为 meaning-preserving prompt changes 下的 behavioural stability，而不是泛指模型质量。

### 9.2 Introduction

建议四段：

1. LLM 被用作 synthetic participants 或 behavioural models，但 cognitive modelling 要求稳定性和可重复性；
2. 现有研究常关注能力或 human-likeness，对 prompt sensitivity 的系统评估不足；
3. Horizon、IGT 和 BART 分别覆盖 exploration、learning 和 risk-taking；
4. 本研究通过三模型、冻结 prompts 和 repeated runs，比较 prompt stability、跨模型差异及 human-reference proximity。

不得预设更新或更大的模型必然更稳定，也不得预设 Mini 必然更差。

### 9.3 Methods

推荐小节：

1. Study design and scope；
2. Models, API and sampling settings；
3. Tasks；
4. Prompt construction and conditions；
5. Repeated-run and seed design；
6. Primary/supplementary metrics；
7. Human datasets；
8. Data quality and exclusions；
9. Within-model effects；
10. Interaction contrasts；
11. PSI；
12. Human comparison；
13. Robustness and multiplicity。

Methods 可以现在开始写，但统计部分必须与最终三模型实现逐项核对。

### 9.4 Results

必须在最终图表冻结后按以下顺序写：

1. Data completeness and response validity；
2. Baseline behavioural profiles；
3. Prompt effects within each model；
4. Model-by-prompt interactions；
5. PSI comparison；
6. Human-reference comparison；
7. Robustness and task dynamics。

每段先报告 direction、magnitude 和 uncertainty，再进行解释。不能只写“显著/不显著”。跨任务异质性可以是主要结果，不应为了排名而强行合并方向不同的指标。

### 9.5 Discussion

Discussion 应回答：

- 哪些行为对 prompt 稳定，哪些敏感？
- 更强或更新的模型是否一致地更稳定？
- Mini 对能力、规模和行为可靠性的关系意味着什么？
- Stability、performance 和 human similarity 是否分离？
- 为什么不同任务可能表现不同？
- 这些结果对 LLM cognitive models 和 synthetic participants 有什么方法学影响？

### 9.6 Conclusion 与 Abstract

Conclusion 应给出有条件的回答，不应给出没有任务限定的模型总排名。若结果异质，可明确写成：没有一个模型在所有任务和 prompt manipulations 上表现出一致优势。

Abstract 最后写，只包含最终冻结分析支持的结论。

## 10. 必须披露的限制

- 三个模型均属于 OpenAI 产品系列，不能代表跨-provider generalisation；
- 每个 cell 只有 20 stochastic runs；
- API snapshot 和服务端 token sampling 不可完全控制；
- environment seed 不等于 token-sampling seed；
- IGT 不是真正的 paired-seed design；
- 只测试英文和四种 prompts；
- PSI 是项目自定义指标；
- 每项任务只有一套 human reference dataset；
- Human 与 LLM 数据并非同一采集环境；
- Human-like distributions 不证明相同认知机制；
- GPT-5.4 Mini 有一次已恢复的 invalid-response retry。

## 11. 写作纪律

- 始终报告 resolved model snapshot IDs；
- 区分 runs、task trials 和 human participants；
- 以 effect sizes 和 uncertainty 为主，不只报告显著性；
- 不把正向 effect 自动解释为 improvement；
- 将 LLM run 称为 participant-level analogue，而非真正 participant；
- 不把 PSI 称为 validated scale；
- 不把 human proximity 写成 cognitive mechanism evidence；
- 不用“一个模型显著、另一个不显著”证明模型之间存在差异；应使用 interaction contrast；
- 不将 IGT seed labels 写成 paired sampling；
- 不从 pilots 或旧两模型图表提取正式结论；
- 不在观察结果后修改 primary metrics 或排除极端但有效的 runs。

## 12. 接下来按此顺序执行

### Phase A：冻结三模型分析

- [ ] 建立统一三模型 input manifest 和 audit report；
- [ ] 验证三模型 model-specific processed outputs；
- [x] 修正并验证 IGT independent-cell bootstrap；
- [ ] 生成 GPT-5.4/Mini 相对 GPT-4.1 的 interaction contrasts；
- [ ] 将 GPT-5.4 Mini 加入 human-reference comparison；
- [ ] 完成 PSI robustness 和 multiplicity specification。

### Phase B：生成论文材料

- [ ] 重新生成三模型 Tables 1–6；
- [ ] 重新生成三模型 Figures 1–6；
- [ ] 生成 supplementary figures/tables；
- [ ] 建立唯一的 frozen result package；
- [ ] 生成三模型 primary-results checklist；
- [ ] 记录 final manifests、hashes 和生成命令。

### Phase C：正式写作

- [ ] 先完成 Methods；
- [ ] 逐条依据 results checklist 写 Results；
- [ ] 写 Discussion；
- [ ] 写 Introduction；
- [ ] 最后写 Conclusion 和 Abstract；
- [ ] 执行 claim-to-output audit；
- [ ] 执行 citation audit；
- [ ] 从 raw JSON 重跑全分析并执行 reproducibility tests。

## 13. 下一步决策

下一步应优先升级现有两模型分析脚本，使其原生支持三个模型，并生成一个新的三模型论文结果包。在该结果包冻结以前，可以写 Methods 和论文背景，但不应正式撰写或锁定 Results、Discussion 中的模型比较结论。
