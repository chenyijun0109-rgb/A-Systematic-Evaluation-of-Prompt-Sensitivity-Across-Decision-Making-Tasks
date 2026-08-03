# English 双模型研究：数据、比较、表格与图像总览

更新时间：2026-07-31

## 1. 这项研究到底要回答什么

当前论文只研究英文正式实验中的两个 OpenAI 模型：

- GPT-4.1：`gpt-4.1-2025-04-14`
- GPT-5.4：`gpt-5.4-2026-03-05`

核心问题不是笼统判断哪个模型“更好”，而是分别回答：

1. 同一个模型的行为是否会因 prompt 写法改变？
2. GPT-5.4 是否比 GPT-4.1 更稳定，或者反而对 prompt 更敏感？
3. 这种差异是否在 Horizon、IGT、BART 三项任务中一致？
4. 两个模型的行为分别离人类参考分布多远？
5. Prompt 稳定性、任务表现和接近人类是否指向相同结论？

“更稳定”“任务收益更高”和“更接近人类”是三个不同标准，不能互相替代。

## 2. 我们实际收集了哪些 LLM 数据

### 2.1 总体实验规模

```text
2 models × 3 tasks × 4 prompt conditions × 20 runs
= 480 valid task runs
```

每个模型有 240 个有效 runs；每个 model-task-condition cell 有 20 个
runs。两批实验均使用 temperature `0.7`、top-p `1.0`、最大输出 16
tokens，并使用相同的英文 prompts 和 prompt hashes。

中文实验和西班牙语实验不属于这篇双模型论文。

### 2.2 三项任务和四种 prompt conditions

| 任务 | Baseline | 通用变化 | 人类角色变化 | 任务特定变化 | 每个 run 的结构 |
|---|---|---|---|---|---|
| Horizon | baseline | detailed | role_human | uncertainty_emphasis | 40 games，300 choices |
| IGT | baseline | detailed | role_human | reward_loss_emphasis | 100 trials |
| BART | baseline | detailed | role_human | risk_emphasis | 40 balloons，pump actions 数量可变 |

### 2.3 八个主要行为指标

这些指标进入主要推断分析、Figures 2–6 和 Tables 2–6。

| 任务 | 主要指标 | 指标回答的问题 |
|---|---|---|
| Horizon | `directed_exploration` | 信息更多的选项是否更容易被选择 |
| Horizon | `horizon_effect` | 长 horizon 相对短 horizon 的探索变化 |
| Horizon | `random_exploration_effect` | 长 horizon 是否增加随机探索 |
| IGT | `advantageous_choice_rate` | 选择有利牌组 C/D 的比例 |
| IGT | `post_loss_switching_rate` | 损失后更换牌组的比例 |
| BART | `adjusted_average_pumps` | 未爆炸气球的平均 pumps |
| BART | `explosion_rate` | 气球爆炸比例 |
| BART | `post_explosion_adjustment` | 爆炸后下一气球 pumps 的变化 |

指标正负方向必须按任务解释。正值不自动代表更优、更稳定或更接近人类。

### 2.4 补充行为数据

以下数据已经记录，但不属于八个主要指标：

- Horizon：`exploration_rate`、`switching_rate`、平均 reward、directed/random
  exploration decomposition；
- IGT：五个 block 的 learning curve、`learning_slope`、
  `learning_curve_change`、各牌组选择率、net score；
- BART：`average_pumps`、每气球平均 earning、完整 pump/explosion 分布；
- 所有任务：parser validity、invalid response、trial 数、模型和 prompt
  provenance。

这些指标用于补充图表、机制解释和稳健性分析，不应与主要指标混为同一
confirmatory family。

## 3. 我们使用了哪些 human reference data

每项任务只使用一套冻结的人类参考数据：

| 任务 | 人数 | 用途 |
|---|---:|---|
| Horizon | 60 | directed exploration、horizon effect 和其他 participant-level metrics |
| Horizon random exploration | 60 | participant-level hierarchical-model estimates |
| IGT | 504 | advantageous choice、post-loss switching 等 participant summaries |
| BART | 141 | pump-based、explosion 和 post-explosion metrics |

LLM 的每个 run 被当作一个 participant-level behavioural summary，与人类
participant 分布比较。该比较只说明分布位置是否接近，不能证明 LLM 和
人类采用相同认知机制。

BART 主要比较 pump-based measures，避免不同数据来源中的货币单位和支付
规则不一致。

## 4. 必须完成哪些比较

### 4.1 数据质量和实验一致性

首先确认：

- 每个模型是否有 240 个有效 runs；
- 每个 cell 是否有 20 个 runs；
- 模型快照、temperature、top-p、token limit 是否冻结；
- prompt hashes 是否跨模型一致；
- trial/game/balloon 数是否完整；
- parse success 是否为 1.0，invalid responses 是否为 0；
- 非英文数据是否被排除。

这是分析能否开始的前置条件，不是行为结果。

### 4.2 描述统计和 baseline 模型差异

对每个模型、任务、condition 和主要指标报告：

- n、mean、SD、median、minimum、maximum；
- run-level distribution；
- ceiling/floor 和低方差情况。

Baseline 下的模型差异用于描述两个模型原本的行为位置，但不能直接回答
哪个模型更 prompt-sensitive。

### 4.3 每个模型内部的 prompt effect

对每个 manipulated condition 计算：

```text
condition − baseline
```

需要报告：

- raw mean difference；
- raw bootstrap 95% interval；
- Hedges' g；
- Hedges' g bootstrap 95% interval；
- low-variance warning。

这一步回答“同一模型是否因 prompt 改变行为”。GPT-4.1 和 GPT-5.4 分开
估计，不能用一个模型显著、另一个不显著来证明模型之间存在差异。

### 4.4 跨模型的 model-by-prompt interaction

直接比较两个模型的 prompt effects：

```text
[(GPT-5.4 condition − GPT-5.4 baseline)
 − (GPT-4.1 condition − GPT-4.1 baseline)]
```

这是真正回答“GPT-5.4 的 prompt sensitivity 是否不同于 GPT-4.1”的主要
contrast。它是 factorial interaction contrast，不是政策研究中的因果
difference-in-differences。

重采样规则：

- Horizon/BART：相同 seed 控制任务环境随机性，因此整体重采样 matched
  environment-seed blocks；
- IGT：任务环境忽略 seed，API sampling 也没有由该 seed 耦合，因此在四个
  model-prompt cells 内独立重采样 runs。

### 4.5 Prompt Sensitivity Index

PSI 是各任务主要指标的绝对标准化 prompt effects 的平均值：

```text
PSI = mean(abs(standardised primary-metric effects))
```

需要报告：

- 每个模型、任务和 manipulated condition 的 PSI；
- 模型内 PSI bootstrap interval；
- 描述性的 `GPT-5.4 − GPT-4.1` PSI difference；
- leave-one-metric-out PSI；
- mean-based 与 median-based robustness。

PSI 是本项目自定义的描述指标，不是经过心理测量验证的量表。它不能替代
metric-level results。

### 4.6 Human-reference comparison

对每个模型、任务、condition 和主要指标报告：

- LLM mean 与 human mean；
- `(LLM mean − human mean) / human SD`；
- absolute human-SD distance；
- human participant 2.5th–97.5th percentile reference interval；
- 落入 reference interval 的 LLM runs 比例；
- manipulated condition 相对该模型 baseline 的距离和 coverage 变化。

必须分开回答“更接近人类”和“对 prompt 更稳定”，不能把两者合并成一个
模型优劣结论。

### 4.7 稳健性和 multiplicity

正式写 Results 前还需要：

- Horizon `run_effect_sd = 0.25, 0.50, 1.00`；
- leave-one-metric-out PSI；
- mean-based 与 median-based summaries；
- ceiling/floor 和低 baseline variance 检查；
- raw difference 与 standardised effect 对照；
- 定义 null statistic 和 null-resampling scheme 后，再进行 family-level
  Benjamini-Hochberg FDR correction。

不能从 bootstrap CI 临时反推一个未经预先定义的 p-value，然后为了填表而
进行 FDR correction。

## 5. 论文需要哪些主表

| 表格 | 内容 | 当前状态 |
|---|---|---|
| Table 1 | 设计、模型 snapshots、prompt hashes、sampling、seeds、任务长度和有效 run 数 | 已生成，24 行 |
| Table 2 | 八个主要指标按 model × condition 的 mean、SD、median、range | 已生成，64 行 |
| Table 3 | 模型内 raw prompt effects、Hedges' g 和 bootstrap intervals | 已生成，48 行；FDR 尚未加入 |
| Table 4 | 24 个 model-by-prompt interaction contrasts 和 intervals | 已生成，24 行 |
| Table 5 | 两模型 PSI、PSI intervals 和描述性 PSI difference | 已生成，18 行；robustness 待补 |
| Table 6 | human-SD distance、reference coverage 和 baseline change | 已生成，64 行 |

主表文件位于：

```text
outputs/processed/model_comparison_en_v01/main_tables/
```

### 5.1 需要的补充表格

- Supplementary Table S1：所有 secondary metrics 描述统计；
- S2：完整 IGT block-wise learning data；
- S3：Horizon shrinkage sensitivity；
- S4：leave-one-metric-out PSI 和 mean/median robustness；
- S5：完整 parser、trial 和 provenance audit；
- S6：全部 prompt 文本路径与 hashes；
- S7：ceiling/floor、zero/low variance flags；
- S8：若实施，原始及 FDR-adjusted multiplicity results。

## 6. 论文需要哪些主图

| 图 | 内容 | 当前状态 |
|---|---|---|
| Figure 1 | Study design 和 analysis workflow | 尚未生成 |
| Figure 2 | 两模型八个主要指标的 run-level box-and-jitter distributions | 已生成 |
| Figure 3 | 两模型各自的 Hedges' g prompt-effect forest plots | 已生成；IGT intervals 待方法修正 |
| Figure 4 | 24 个 model-by-prompt interaction contrasts | 已生成 |
| Figure 5 | 两模型 PSI、PSI intervals 和描述性 PSI difference | 已生成；IGT PSI intervals 待方法修正 |
| Figure 6 | 两模型相对 human distributions 的标准化距离 | 已生成 |

主图文件位于：

```text
outputs/figures/model_comparison_en_v01/
```

### 6.1 需要的补充图像

- Figure S1：所有 recorded metrics 的完整 distributions；
- Figure S2：baseline 到 manipulated condition 的 seed-level slope plots；
- Figure S3：IGT 五个 block 的 learning curves；
- Figure S4：Horizon directed/random exploration decomposition 与 shrinkage
  sensitivity；
- Figure S5：BART pump distributions、explosion 和 post-explosion dynamics；
- Figure S6：leave-one-metric-out PSI 与 mean/median robustness；
- Figure S7：每个 cell 的 parse validity 和 provenance audit；
- Figure S8：主要指标 correlation matrix，仅用于检查 redundancy。

## 7. 当前必须修正的方法问题

### 7.1 IGT 不是 matched-seed paired data

IGT 的 `reset(seed)` 明确忽略 seed；OpenAI API sampling 也未使用该 seed。
因此 IGT 中相同 seed 只是 run label，不产生真实配对依赖。

当前跨模型 interaction contrast 已经正确改为 cell 内独立 bootstrap。但
现有 within-model prompt-effect pipeline 和 PSI bootstrap 仍对 IGT 使用了
paired-seed resampling。因此在正式论文写作前必须：

1. 将 IGT within-model raw effect、Hedges' g 和 PSI 的不确定性改为独立
   cell-level bootstrap；
2. 重新生成 IGT Table 3 intervals；
3. 重新生成 IGT Table 5 PSI intervals；
4. 更新 Figures 3 和 5；
5. 保留 point estimates，并核对修正前后 interval 变化。

Horizon/BART 的 environment seed 具有 blocking 意义，但它只耦合任务环境，
不耦合模型 token sampling，论文中也必须明确这一限制。

### 7.2 FDR 尚未实施

目前已有 effect sizes 和 percentile-bootstrap intervals，但没有冻结的
null-resampling p-values。因此 Table 3 不能声称已经完成 FDR correction。
应先定义检验统计量、任务级重采样方法和 correction family，再执行 BH。

### 7.3 Figure 1、robustness 和 supplementary package 尚未完成

Figures 2–6 和 Main Tables 1–6 已经生成，不代表完整论文分析已经结束。
Figure 1、Stage F robustness、Supplementary Tables/Figures 和最终 claim audit
仍是写 Results 前的必要步骤。

## 8. 当前完成状态和建议顺序

### 已完成

- 两模型 480 个正式有效 runs；
- frozen input manifest 和 audit；
- primary descriptives；
- model-by-prompt interaction contrasts；
- 双模型 human-reference comparison；
- Figures 2–6；
- Main Tables 1–6；
- 覆盖 Tables 2–6 的 218 条 source-linked results checklist；
- 方法学 references 和 citation map。

### 接下来应按此顺序完成

1. 修正 IGT within-model 和 PSI bootstrap；
2. 重新生成受影响的 Table 3、Table 5、Figure 3、Figure 5；
3. 完成 robustness 和 multiplicity specification；
4. 生成 Supplementary Tables S1–S8 和 Figures S1–S8；
5. 生成 Figure 1 study-design map；
6. 冻结最终 Tables、Figures 和 results checklist；
7. 从 checklist 写 Results；
8. 最后写 Discussion、Introduction、Conclusion 和 Abstract；
9. 执行 claim-to-output、citation 和 reproducibility audit。

这份顺序能够保证论文文字来自冻结结果，而不是在写作过程中选择性挑选
结果或临时改变统计方法。
