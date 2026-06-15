# 三个认知决策任务说明

Date: 2026-06-07

Status: Implemented specification v0.2

Purpose: 本文档详细说明本项目使用的三个 cognitive decision-making tasks：Horizon Task / two-option bandit、Iowa Gambling Task、Balloon Analogue Risk Task。内容包括任务概述、任务流程、主要变量、prompt 条件、记录字段、分析指标、human dataset 对齐方式和仍需确认的事项。本文档用于后续 task environment 实现、prompt 编写、data schema 设计和 dissertation methodology / appendix 写作。

## 1. 总体实验结构

本项目的核心问题不是让 LLM 单纯完成任务，而是检验：

> 在任务规则不变的情况下，不同 prompt 条件是否会系统性改变 LLM 在经典认知决策任务中的行为。

三个任务分别覆盖三类决策行为：

| Task | 中文说明 | 认知重点 | 主要行为 |
|---|---|---|---|
| Horizon Task / two-option bandit | 两选项老虎机 / 探索-利用任务 | 不确定性下的探索与利用 | 是否选择信息不足但可能有价值的选项 |
| Iowa Gambling Task | 爱荷华赌博任务 | 奖励、惩罚与长期结果学习 | 是否逐渐偏向长期收益更好的牌堆 |
| Balloon Analogue Risk Task | 气球模拟风险任务 | 风险承担与收益权衡 | 是否继续冒险 pump，或及时 cash out |

每个任务都在四个 prompt 条件下运行：

| Prompt condition | 含义 | 变量作用 |
|---|---|---|
| `baseline` | 中性任务说明 | 基准条件 |
| `detailed` | 更详细的规则说明 | 测试规则描述详细程度是否影响行为 |
| `role_human` | 将模型框定为心理学实验中的人类参与者 | 测试 role framing 是否影响行为 |
| task-specific emphasis | 针对任务核心认知维度的强调 | Horizon 强调 uncertainty；IGT 强调 reward/loss；BART 强调 risk |

主实验建议规模：

```text
3 tasks x 4 prompt conditions x 15-20 valid runs
```

当前目标是每个 `task x prompt_condition` 至少获得 15 个有效 runs，理想目标为 20 个 runs。如果 API 成本、时间和 pilot 稳定性允许，可扩展到 30-50 个 runs。

## 2. 跨任务共同变量

### 2.1 自变量

| 变量 | 取值 | 说明 |
|---|---|---|
| `task` | `horizon`, `igt`, `bart` | 当前运行的认知任务 |
| `prompt_condition` | `baseline`, `detailed`, `role_human`, task-specific emphasis | 本项目最核心的 manipulation |
| `run_id` | 整数或唯一字符串 | 同一任务和 prompt 条件下的重复运行编号 |

### 2.2 控制变量

| 变量 | 控制方式 | 原因 |
|---|---|---|
| model name | 主实验固定同一个模型 | 避免把模型差异误认为 prompt effect |
| temperature | 主实验固定，pilot 后确认 | 避免 sampling 设置改变行为分布 |
| top_p | 固定为 `1.0` | 控制 decoding 设置 |
| max_tokens | pilot 后固定 | 保证响应足够短且可解析 |
| response format | 每个任务固定合法输出格式 | 保证 parser 稳定 |
| task rules | 同一任务内四个 prompt 条件完全相同 | prompt condition 只能改变说明方式，不能改变任务本身 |
| random seed | 如果环境存在随机性则记录 | 保证可追踪和可复现 |

### 2.3 因变量 / 行为指标

每个任务有自己的核心指标，但总体上分为四类：

| 指标类别 | 说明 | 示例 |
|---|---|---|
| choice behaviour | 模型选择了什么 | Horizon 中选 A/B；IGT 中选 A/B/C/D；BART 中 pump/cash out |
| reward outcome | 每一步获得或损失什么 | reward、loss、explosion、cumulative score |
| learning / adjustment | 行为是否随反馈改变 | IGT block-wise learning；BART post-explosion adjustment |
| prompt sensitivity | 不同 prompt 条件下行为差异有多大 | prompt sensitivity index、effect size、distribution shift |

### 2.4 Prompt sensitivity 的计算方式

在本项目中，prompt sensitivity 不是一个任务原生指标，而是一个跨 prompt 条件的 derived measure。它用来表示：在同一个 task、同一个模型、同一套任务规则下，改变 prompt condition 后，LLM 的行为指标相对 `baseline` 发生了多大变化。

这些变量不是实验前凭空设定的，而是从 LLM 实际完成 task 后产生的行为数据中一步步计算出来的。基本数据流是：

```text
LLM trial-by-trial choices
→ 每个 run 的 task-specific behavioural metrics
→ 每个 prompt condition 下的 metric mean 和 SD
→ manipulated prompt 与 baseline 的差异
→ standardised prompt effect
→ PSI
```

基本计算单位是：

```text
task x prompt_condition x metric
```

#### 2.4.1 每个 task 先产生什么原始数据

每一次 LLM 完整完成一个 task 记为一个 `run`。每个 run 内部会产生 trial-level 或 action-level 数据，之后再汇总成 run-level behavioural metrics。

Horizon Task 每一轮主要记录：

```text
run_id, prompt_condition, trial_id, choice, reward, information_condition
```

从这些 choices 和 rewards 中计算：

```text
exploration rate
directed exploration
random exploration
switching rate
cumulative reward
```

IGT 每一轮主要记录：

```text
run_id, prompt_condition, trial_id, deck_choice, gain, loss, net_outcome
```

从这些 deck choices 和 outcomes 中计算：

```text
net score = (C + D) - (A + B)
advantageous choice rate = choices from C and D / total choices
deck preference = proportion of choices for A, B, C, D
final cumulative score = sum of net outcomes
post-loss switching = whether model switches deck after a loss
```

BART 每个 balloon 或 action 主要记录：

```text
run_id, prompt_condition, balloon_id, pumps, exploded, cashed_out, earnings
```

从这些 balloon-level / action-level records 中计算：

```text
average pumps
adjusted average pumps
explosion rate
total earnings
```

#### 2.4.2 公式变量如何从三个 task 中得到

| Task | 可用于 prompt sensitivity 的指标 |
|---|---|
| Horizon | exploration rate, directed exploration, random exploration effect, switching rate, average reward per trial |
| IGT | net score, advantageous choice rate, deck preference, average net outcome, post-loss switching |
| BART | average pumps, adjusted average pumps, explosion rate, average earning per balloon, post-explosion adjustment |

公式中使用以下记号：

| 记号 | 含义 | 数据来源 |
|---|---|---|
| `m` | behavioural metric，即行为指标 | 从每个 run 的 trial-level / action-level 数据中计算出来，例如 BART 的 average pumps、IGT 的 net score、Horizon 的 exploration rate |
| `p` | manipulated prompt condition | `detailed`、`role_human` 或 task-specific emphasis；baseline 是参照组 |
| `M_{m,p}` | 在某个 task 中，prompt condition `p` 下，所有 runs 的 metric `m` 取值集合 | 例如 BART `risk_emphasis` 下 20 个 runs 各自的 average pumps |
| `M_{m,baseline}` | 在同一个 task 中，baseline prompt 下，所有 runs 的 metric `m` 取值集合 | 例如 BART baseline 下 20 个 runs 各自的 average pumps |
| `mean(M_{m,p})` | condition `p` 下 metric `m` 的 run-level 平均值 | 对 `M_{m,p}` 中所有 run-level metric values 求平均 |
| `mean(M_{m,baseline})` | baseline 下 metric `m` 的 run-level 平均值 | 对 `M_{m,baseline}` 中所有 run-level metric values 求平均 |
| `sd(M_{m,baseline})` | baseline 下 metric `m` 在 repeated runs 之间的标准差 | 表示 baseline 条件下模型行为的自然波动 |
| `S_{m,p}` | metric `m` 在 prompt condition `p` 下的 standardised prompt effect | manipulated prompt 与 baseline 的差异除以 baseline run-level SD |

这里更严谨的公式是：

```text
S_{m,p}
  = [mean(M_{m,p}) - mean(M_{m,baseline})]
    / sd(M_{m,baseline})
```

其中：

```text
M_{m,p}
  = prompt condition p 下，每个 run 的指标值集合

mean(M_{m,p})
  = condition p 下，这些 run-level 指标的平均值

M_{m,baseline}
  = baseline 条件下，每个 run 的指标值集合

sd(M_{m,baseline})
  = baseline 条件下，这些 run-level 指标的标准差
```

这个写法比 `SD(X_{m,baseline})` 更严谨，因为 `X` 通常已经表示均值，严格来说不应该再对单个均值求标准差。分母应当是 baseline 条件下多个 runs 的 run-level metric values 的标准差。

如果 `sd(M_{m,baseline})` 为 0 或非常小，可以改用 pooled standard deviation：

```text
pooled_sd = sqrt((sd_baseline^2 + sd_condition^2) / 2)
```

#### 2.4.3 完整例子：BART 的 average pumps

假设比较 BART 的 `baseline` 和 `risk_emphasis` prompt，metric `m` 是 `average pumps`。

Baseline 条件下 5 次 run：

| run | average pumps |
|---|---:|
| 1 | 7.5 |
| 2 | 8.0 |
| 3 | 7.0 |
| 4 | 8.5 |
| 5 | 7.5 |

因此：

```text
mean(M_{average_pumps,baseline}) = 7.7
sd(M_{average_pumps,baseline}) ≈ 0.57
```

Risk emphasis 条件下 5 次 run：

| run | average pumps |
|---|---:|
| 1 | 9.0 |
| 2 | 8.5 |
| 3 | 9.5 |
| 4 | 9.0 |
| 5 | 8.0 |

因此：

```text
mean(M_{average_pumps,risk_emphasis}) = 8.8
```

raw prompt effect 是：

```text
raw_effect
  = 8.8 - 7.7
  = 1.1
```

意思是 `risk_emphasis` prompt 让 BART 的 average pumps 平均增加了 1.1 次。

标准化后：

```text
S_{average_pumps,risk_emphasis}
  = (8.8 - 7.7) / 0.57
  ≈ 1.93
```

意思是 `risk_emphasis` prompt 对 BART average pumps 的影响，大约等于 baseline 条件下自然波动的 1.93 个标准差。

如果只关心变化幅度而不关心方向，可以取绝对值：

```text
|S_{average_pumps,risk_emphasis}| = 1.93
```

这就是这个 metric 上的 prompt sensitivity magnitude。如果该值为正，说明 `risk_emphasis` 条件下模型平均 pump 更多；如果为负，说明模型平均更早 cash out 或更保守。取绝对值之后，该指标可以和 IGT net score、Horizon exploration rate 等不同量纲的指标一起进入 PSI 计算。

#### 2.4.4 PSI 的计算

对于某个 task 和某个 prompt condition，先分别计算多个 metrics 的 absolute standardised effects：

```text
|S_{m1,p}|, |S_{m2,p}|, |S_{m3,p}|, ...
```

然后取平均，得到该 prompt condition 对该 task 的 Prompt Sensitivity Index：

```text
PSI(task, p)
  = mean(|S_{m,p}| across selected metrics)
```

例如 BART 的 `risk_emphasis` condition 使用 4 个指标：

| metric | absolute standardised effect |
|---|---:|
| average pumps | 1.93 |
| adjusted average pumps | 1.60 |
| explosion rate | 1.20 |
| total earnings | 0.80 |

则：

```text
PSI(BART, risk_emphasis)
  = (1.93 + 1.60 + 1.20 + 0.80) / 4
  = 1.38
```

也就是说，`risk_emphasis` prompt 对 BART 行为的总体敏感度是 1.38。

也可以对三个 manipulated prompt conditions 再取平均，得到某个 task 的总体 prompt sensitivity：

```text
PSI(task)
  = mean(
      PSI(task, detailed),
      PSI(task, role_human),
      PSI(task, task_specific_emphasis)
    )
```

需要注意：`PSI(task)` 只是一个 summary-level index，用来粗略概括某个 task 整体上对 prompt variation 是否敏感。它不应该作为最主要的分析结果，也不能替代 condition-level analysis。正式结果中更重要的是分别报告：

```text
PSI(task, detailed)
PSI(task, role_human)
PSI(task, task_specific_emphasis)
```

原因是不同 prompt manipulation 可能代表不同机制。如果直接平均，可能会掩盖有意义的差异。例如：

- `detailed` prompt 可能让行为更接近任务规则或理性策略；
- `role_human` prompt 可能让行为更接近 human dataset；
- `risk_emphasis` prompt 可能让 BART 行为更保守或更冒险；
- `uncertainty_emphasis` prompt 可能主要影响 Horizon 中的 exploration；
- `reward_loss_emphasis` prompt 可能主要影响 IGT 中的 deck learning。

因此，本项目的主分析应以 `PSI(task, condition)`、raw difference、standardised effect 和方向性结果为主；`PSI(task)` 只作为跨任务比较时的辅助概览指标。

PSI 的解释方式：

| PSI 大小 | 含义 |
|---|---|
| 接近 0 | 该 task 下 LLM 行为对 prompt condition 比较稳定 |
| 较大 | 该 task 下 LLM 行为明显受 prompt condition 影响 |
| 某个 condition 特别大 | 说明该 prompt manipulation 对行为影响较强 |
| 某个 task 特别大 | 说明该 task 可能比其他 task 更 prompt-sensitive |

需要同时报告方向性结果。例如，`risk_emphasis` 可能让 BART 的 average pumps 上升或下降；PSI 只说明变化幅度，不说明变化方向。因此正式分析中应同时报告：

- raw difference；
- standardised effect；
- absolute effect / PSI；
- 每个 condition 下的均值和置信区间；
- 如果样本量允许，再做 distribution comparison。

#### 2.4.5 这个公式的文献依据和定位

需要明确：上面的公式不是从某一篇 LLM prompt sensitivity 论文中直接照搬的固定公式，而是本项目的 operational definition。它结合了两类已有方法：

1. 统计学中的 standardised mean difference / effect size 思路；
2. LLM 研究中比较不同 prompt variations 下模型输出或表现差异的实验思路。

统计学依据是 standardised mean difference。`S_{m,p}` 的核心形式是“两个条件的均值差除以一个标准差”：

```text
S_{m,p}
  = [mean(M_{m,p}) - mean(M_{m,baseline})]
    / sd(M_{m,baseline})
```

这和 Cohen's d、Hedges' g、Glass's Delta 等 effect size 指标属于同一类思想：当不同指标量纲不同、不能直接比较时，用标准差对均值差进行标准化，使差异进入相对可比较的尺度。因此，本项目可以表述为：

> Prompt sensitivity is operationalised as a standardised mean difference between each manipulated prompt condition and the baseline prompt condition.

中文表述为：

> 本项目将 prompt sensitivity 操作化为 manipulated prompt 条件与 baseline prompt 条件之间的标准化均值差。

本项目使用 baseline condition 的标准差作为分母，是因为 baseline prompt 在实验中作为 reference / control condition。这更接近 Glass-type standardisation 的逻辑，即用参照组或控制组的标准差提供比较尺度，而不是默认使用 pooled SD。因此可写作：

> The use of the baseline standard deviation follows the logic of standardised mean-difference effect sizes, particularly Glass-type standardisation, where the reference or control condition provides the scale of comparison.

如果 baseline standard deviation 为 0 或非常小，则使用 pooled SD 作为 fallback。这对应 Cohen's d / Hedges' g 中常见的 pooled standard deviation 思路，可以避免仅依赖某一个条件的极小变异而得到不稳定估计。若每个 prompt condition 的 run 数相同，可以使用简化版本：

```text
pooled_sd = sqrt((sd_baseline^2 + sd_condition^2) / 2)
```

若不同 prompt condition 的 run 数不同，更严格的 pooled SD 为：

```text
s_pooled
  = sqrt(
      ((n_baseline - 1) * sd_baseline^2
       + (n_condition - 1) * sd_condition^2)
      / (n_baseline + n_condition - 2)
    )
```

### 2.4.6 Task literature 与 prompt design literature 的证据边界

Wilson et al. (2014)、Bechara et al. (1994) 和 Lejuez et al. (2002) 是三个认知任务的理论与方法依据，但不是四种 LLM prompt 的直接来源。它们支持任务测量的认知构念、基本规则和经典 behavioural metrics：

| Task | 核心任务文献 | 文献直接支持的内容 | 本项目的改动或补充依据 |
|---|---|---|---|
| Horizon | Wilson et al. (2014) | explore-exploit dilemma、Horizon 1/6、4 次 forced choices、`[2,2]` / `[1,3]` information condition、directed/random exploration | 每个 LLM run 减少为 40 games；human comparison 结合 Feng et al. (2021) 和本地数据 |
| IGT | Bechara et al. (1994) | 四牌堆决策、即时 reward 与长期 consequence 的冲突、feedback-based learning | 100 trials、具体 payoff 实现、block metrics 和 human comparison 还结合 Steingroever et al. (2015) |
| BART | Lejuez et al. (2002) | pump/cash-out/explosion 机制、risk-taking 构念、adjusted average pumps | 当前使用 40 balloons 和 32-pump probabilistic rule，主要结合 Sebri et al. (2023) 与本地 human dataset，而非完全复制原始版本 |

因此，不应写：

```text
The four prompt conditions were derived from Wilson et al. (2014),
Bechara et al. (1994), and Lejuez et al. (2002).
```

更准确的表述是：

```text
The original task literature determined the cognitive constructs, task rules,
feedback structure, and behavioural measures. The four prompt conditions were
project-defined experimental manipulations informed by research on LLM prompt
sensitivity and role framing.
```

四种 prompt conditions 的依据和定位如下：

| Prompt condition | 设计目的 | 直接依据 | 应如何定位 |
|---|---|---|---|
| `baseline` | 提供完成任务所需的最少充分、中性说明，作为 reference condition | 实验控制逻辑；Loya et al. (2023) 表明 prompt variation 会改变 LLM decision-making | 项目定义的 control condition，不是某篇文献中的标准 prompt |
| `detailed` | 在不改变规则、state information 和 response format 的情况下，更明确说明反馈、历史信息和决策流程 | Prompt sensitivity literature 支持比较 instruction wording；Sclar et al. (2024) 说明细微 prompt design choices 也可能影响结果 | 项目定义的 instruction-detail manipulation；不能声称从某篇论文原样复制 |
| `role_human` | 将模型框定为心理学实验中的 participant，检验角色框定是否改变行为 | Shanahan et al. (2023) 提供 role-play 理论框架；persona-prompting 研究表明角色指定可改变输出分布 | 文献支持其作为有意义的 manipulation，但具体措辞为项目自定义 |
| task-specific emphasis | 分别突出 uncertainty、reward/loss 或 risk，而不提供策略建议 | 强调的认知维度分别来自 Wilson、Bechara 和 Lejuez；Loya et al. (2023) 支持在决策任务中检验 prompt variation | 认知构念来自 task literature；将其显著化为 prompt 是项目自定义操纵 |

task-specific emphasis 与任务文献的关系为：

```text
Horizon uncertainty_emphasis -> uncertainty / information asymmetry
                                from Wilson et al. (2014)
IGT reward_loss_emphasis      -> reward, punishment and long-term consequences
                                from Bechara et al. (1994)
BART risk_emphasis            -> incremental reward versus explosion risk
                                from Lejuez et al. (2002)
```

这些 prompts 必须保持相同的信息边界：相同 task state、history、可选动作、response format 和环境规则。不同条件只能改变说明的详细程度、角色框定或认知维度的显著性，不能透露最优策略、隐藏概率、真实 option means 或 advantageous decks。这样才能把条件差异解释为 prompt framing effect，而不是额外信息造成的差异。

LLM prompt sensitivity 的总体依据来自 prompt variation / prompt sensitivity 研究。Loya et al. (2023) 直接在 Horizon decision-making task 中发现，prompt variation 和 temperature 会影响 LLM 的探索-利用行为。Sclar et al. (2024) 进一步表明，即使语义基本保持不变，prompt formatting 也可能显著影响模型表现。因此，本项目比较同一任务在不同 prompt 条件下的行为差异，同时固定格式、task state 和 decoding settings。

需要特别说明：这些文献支持“prompt variation 值得被系统检验”，但不证明本项目选择的四种 conditions 是唯一正确或完整的 prompt taxonomy。这四种条件是 theory-informed、predefined experimental manipulations，目的是覆盖中性控制、说明详细度、角色框定和任务构念显著性四个可解释维度。

可以在 proposal 中这样写：

```text
The cognitive tasks and behavioural measures were derived from the original
Horizon Task, Iowa Gambling Task, and BART literature. The prompt conditions
were not taken directly from those studies; they were predefined, project-specific
manipulations informed by evidence that LLM decision-making is sensitive to prompt
variation and role framing. Prompt sensitivity is quantified by comparing each
condition with a neutral baseline while holding task information, response format,
model settings, and environment rules constant.
```

最后，`PSI(task, p)` 应明确写成项目自定义的 descriptive composite index，而不是文献中已有的标准心理学量表：

```text
PSI(task, p)
  = mean(|S_{m,p}| across selected metrics)
```

它的合理性来自三个步骤：

1. 每个 `S_{m,p}` 是基于 standardised mean difference 的 effect-size-like measure；
2. 一个 task 会产生多个 behavioural metrics，因此需要一个描述性综合指标概括整体 prompt-induced behavioural change；
3. 取绝对值是因为 PSI 关注变化幅度，而不是变化方向。

因此应避免写成：

```text
PSI is a standard measure in the literature.
```

更准确的写法是：

```text
Based on standardised mean-difference effect sizes, this project constructs a descriptive Prompt Sensitivity Index by averaging the absolute standardised effects across selected behavioural metrics. PSI is an operational summary index for this project, while signed effects and raw differences are also reported to preserve direction.
```

相关 citation basis：

| 用途 | Citation keys |
|---|---|
| standardised mean difference / effect size | Cohen1988PowerAnalysis; HedgesOlkin1985MetaAnalysis |
| control-group SD / Glass-type standardisation | Glass1976Delta |
| prompt variation in LLM decision-making | LoyaSinhaFutrell2023 |
| prompt formatting / prompt design sensitivity | Sclar2023PromptFormatting |
| role framing | Shanahan2023RolePlay |
| prompt sensitivity benchmarking | Razavi2025PromptSensitivity |
| Horizon task construct and uncertainty emphasis | Wilson2014HorizonTask |
| IGT construct and reward/loss emphasis | Bechara1994IGT; Steingroever2015IGTData |
| BART construct and risk emphasis | Lejuez2002BART; Sebri2023BART |

本节关键参考文献：

- Wilson, R. C., Geana, A., White, J. M., Ludvig, E. A., & Cohen, J. D. (2014). Humans use directed and random exploration to solve the explore-exploit dilemma. *Journal of Experimental Psychology: General, 143*(6), 2074-2081. https://doi.org/10.1037/a0038199
- Bechara, A., Damasio, A. R., Damasio, H., & Anderson, S. W. (1994). Insensitivity to future consequences following damage to human prefrontal cortex. *Cognition, 50*(1-3), 7-15. https://doi.org/10.1016/0010-0277(94)90018-3
- Lejuez, C. W., Read, J. P., Kahler, C. W., et al. (2002). Evaluation of a behavioral measure of risk taking: The Balloon Analogue Risk Task (BART). *Journal of Experimental Psychology: Applied, 8*(2), 75-84. https://doi.org/10.1037/1076-898X.8.2.75
- Loya, M., Sinha, D., & Futrell, R. (2023). Exploring the sensitivity of LLMs' decision-making capabilities: Insights from prompt variations and hyperparameters. *Findings of EMNLP 2023*, 3711-3716. https://doi.org/10.18653/v1/2023.findings-emnlp.241
- Sclar, M., Choi, Y., Tsvetkov, Y., & Suhr, A. (2024). Quantifying language models' sensitivity to spurious features in prompt design. *ICLR 2024*. https://arxiv.org/abs/2310.11324
- Shanahan, M., McDonell, K., & Reynolds, L. (2023). Role play with large language models. *Nature, 623*, 493-498. https://doi.org/10.1038/s41586-023-06647-8

## 3. Task 1: Horizon Task / Two-Option Bandit

### 3.1 概述

Horizon Task 是一个探索-利用任务。参与者在两个选项之间做选择，每个选项会产生奖励。任务的关键不只是获得当前最高奖励，而是在奖励信息不完全时决定是否探索不确定选项。

本项目使用它来观察 LLM 是否会表现出：

- exploitation：选择当前看起来平均收益更高的选项；
- directed exploration：主动选择信息较少、不确定性更高的选项以获得信息；
- random exploration：在选项之间产生更随机的选择；
- horizon effect：当未来还有更多选择机会时，是否更愿意探索。

### 3.2 任务内容

当前设计为每个 run 包含若干个 independent games。每个 game 中，模型面对两个选项，例如 `A` 和 `B`。在做出选择后，环境返回该选项的 reward。模型下一步可以利用已观察到的信息继续选择。

当前实现：

```text
每个 run: 40 games
20 个 Horizon 1 games: 4 forced choices + 1 free choice
20 个 Horizon 6 games: 4 forced choices + 6 free choices
共 300 trials，其中 140 次为 free-choice decisions
可选动作: CHOICE: A / CHOICE: B
```

Horizon 1 和 Horizon 6 按 game id 交替生成，因此每个 run 各有 20 games。每个 game 的前 4 trials 为 forced choices，信息条件为 equal `[2, 2]` 或 unequal `[1, 3]`。之后分别进行 1 或 6 次 free choices。reward 从标准差为 8 的 Gaussian distribution 生成，选项均值在单个 game 内保持稳定。

### 3.3 单次 trial / decision 流程

1. 系统向模型展示当前 game 的已有信息，例如两个选项过去得到过的 reward。
2. 模型必须在 `A` 和 `B` 之间选择一个。
3. parser 读取模型输出。
4. 环境根据选择返回 reward。
5. 系统记录 choice、reward、当前 game 状态和 raw response。
6. 如果 game 尚未结束，进入下一次 decision；如果结束，进入下一个 game。

推荐 response format：

```text
CHOICE: A
```

或：

```text
CHOICE: B
```

### 3.4 任务变量

| 变量 | 类型 | 说明 | 当前状态 |
|---|---|---|---|
| `n_games_per_run` | task parameter | 每个 run 包含多少个 games | 固定：40 |
| `horizon_type` | task parameter | Horizon 1 或 Horizon 6 | 固定：各 20 games |
| `option` | action variable | `A` 或 `B` | 固定 |
| `reward_schedule` | environment variable | Gaussian reward，SD = 8，均值在 game 内固定 | 已实现 |
| `observed_rewards_A` | state variable | A 选项已有 reward history | 已实现 |
| `observed_rewards_B` | state variable | B 选项已有 reward history | 已实现 |
| `information_difference` | derived variable | 已观察信息量差 `n_observed_A - n_observed_B` | 已实现 |
| `information_value_difference` | model variable | A更少被观察取`+1`，B更少被观察取`-1`，相等取`0` | 待分析模型实现 |
| `mean_reward_difference` | derived variable | 两个选项已观察均值差异 | 已实现 |
| `choice` | dependent variable | 模型当前选择 | 固定记录 |
| `reward` | outcome variable | 当前选择得到的 reward | 固定记录 |

### 3.5 Prompt 条件

| Condition | Horizon 中的具体含义 |
|---|---|
| `baseline` | 只说明两个选项、选择格式和反馈方式 |
| `detailed` | 更清楚解释 reward history、game / trial 结构和选择流程 |
| `role_human` | 要求模型以心理学实验中的人类参与者身份完成任务 |
| `uncertainty_emphasis` | 强调有些选项信息更少、决策涉及 uncertainty，但不能直接建议“多探索” |

### 3.6 主要指标

| Metric | 说明 | 所需字段 |
|---|---|---|
| exploration rate | 选择非当前最高平均收益选项的比例 | choice, observed rewards |
| directed exploration | 选择信息较少 / 不确定性更高选项的倾向 | choice, information difference |
| random exploration | Horizon 6 相对 Horizon 1 的估计 decision-noise 增量 | first free choices, reward difference, information value, horizon |
| switching rate | 相邻 decision 中是否更换选项 | previous choice, current choice |
| horizon effect | long horizon 相比 short horizon 是否有更多探索 | horizon type, exploration indicator |
| average reward per trial | 每个 trial 的平均收益 | reward |

#### 3.6.1 Random exploration 的严格定义

早期pilot代码曾使用 `random_exploration = exploration_rate` 作为proxy，该字段现已从run-level metrics和human summaries中移除。根据Wilson et al. (2014)，正式的random exploration应操作化为Horizon 6相对于Horizon 1的估计decision noise增加。

主分析只使用每个 game 的第一次 free choice。采用与 Wilson et al. 原模型逻辑等价的 logistic 参数化：

```text
P(choice A)
  = logistic(
      (delta_reward
       + information_bonus * delta_information_value
       + position_bias * delta_position)
      / decision_noise
    )
```

其中所有差值的正方向均定义为“更支持选择 A”：

```text
delta_reward
  = observed_mean_A - observed_mean_B

delta_information_value
  = +1  if A has been observed fewer times
  = -1  if B has been observed fewer times
  =  0  if both have been observed equally often
```

这里必须区分：

- `information_difference = n_observed_A - n_observed_B` 表示已经拥有的信息量差；
- `delta_information_value` 表示再次选择某一选项的潜在信息价值差。

因此，当 A 被观察 1 次、B 被观察 3 次时：

```text
information_difference = 1 - 3 = -2
delta_information_value = +1
```

A 已有信息更少，但进一步选择 A 的潜在信息价值更高。

`position_bias` 在 Wilson et al. (2014) 中是 spatial / side bias。当前 LLM 任务没有真正的左右空间布局，A/B 总以文本标签呈现，因此本项目若保留该项，应将其解释为 label / presentation-order bias，而不能直接称为人类实验中的 spatial bias。若后续随机化 A/B 的显示位置，才可以更接近原文的 spatial-bias控制。

分别估计两个 horizon 下的 decision noise：

```text
sigma_H1 = decision noise in Horizon 1
sigma_H6 = decision noise in Horizon 6
```

正式指标定义为：

```text
random_exploration_effect = sigma_H6 - sigma_H1
```

- 大于 0：Horizon 6 的选择变异性更高，与 random exploration 一致；
- 等于 0：decision noise 不随 horizon 改变；
- 小于 0：Horizon 6 的选择反而更受 reward evidence 约束。

Decision noise 是模型中的残余选择变异参数。它可能包含真正的随机探索，也可能吸收未建模的确定性策略、价值估计误差或推断噪声。因此，正式写作应使用：

> choice variability consistent with random exploration

而不应声称 decision noise 已经证明了心理机制上的真正随机选择。

Wilson et al. (2014) 提供random exploration的概念和choice-model定义。由于本项目每个LLM run只有40 games，分析模块使用跨runs的hierarchical MAP model和partial pooling；这是本项目对较小run-level样本的估计调整，不是Wilson et al.原文的方法。应表述为：

> Following the choice-model logic of Wilson et al. (2014), the estimation procedure is adapted to the smaller number of games per LLM run using hierarchical partial pooling.

### 3.7 Human dataset 对齐

计划使用：

```text
DATASET/BANDIT/allHorizonData_cut.csv
```

对齐目标：

- 比较 human participants 和 LLM runs 的 exploration rate；
- 比较 directed / random exploration 相关指标；
- 比较 short horizon 与 long horizon 下的行为差异。

待确认：

- dataset 中 exact task structure 是否和本项目实现完全一致；
- human data 的字段如何对应 LLM trial-level log；
- 如果本项目简化 Horizon Task，需要在 limitation 中说明。

### 3.8 待确认事项

| 问题 | 为什么重要 |
|---|---|
| exact reward schedule | 决定 reward、exploration 和 cumulative reward 的计算 |
| short / long horizon structure | 决定 horizon effect 是否可解释 |
| previous outcomes presentation | 决定 LLM 能看到什么信息 |
| directed / random exploration definition | 决定核心指标如何 operationalise |
| human dataset alignment | 决定 LLM-human comparison 是否可靠 |

## 4. Task 2: Iowa Gambling Task

### 4.1 概述

Iowa Gambling Task 是一个经典的 reward-punishment learning 任务。参与者反复从四个牌堆中选择，每次选择会得到即时收益，并可能伴随损失。某些牌堆短期奖励高但长期结果差，另一些牌堆即时奖励较低但长期结果更好。

本项目使用 IGT 来观察 LLM 是否能在反馈中逐渐学习长期有利的选择。

### 4.2 任务内容

当前实现：

```text
每个 run: 100 trials
可选牌堆: A, B, C, D
advantageous decks: C, D
disadvantageous decks: A, B
block size: 20 trials
```

每个 trial 中，模型从四个 deck 中选择一个。环境返回 reward 和 loss，并更新 cumulative score。分析时通常将 100 trials 分为 5 个 blocks，每个 block 包含 20 trials，用来观察学习曲线。

payoff table 已按照经典 IGT schedule 固定：A/B 每次 gain 为 100，长期净结果较差；C/D 每次 gain 为 50，长期净结果较好。每个 deck 的 10-card loss cycle 按该 deck 被选择的次数独立重复。

### 4.3 单次 trial 流程

1. 系统提示当前 trial 编号、可选 deck 和必要的历史反馈。
2. 模型输出一个 deck choice。
3. parser 读取 `CHOICE: A/B/C/D`。
4. 环境根据 payoff table 返回 reward、loss 和 net outcome。
5. cumulative score 更新。
6. 记录 trial-level 数据。
7. 进入下一个 trial，直到 100 trials 完成。

推荐 response format：

```text
CHOICE: A
```

合法选项为：

```text
CHOICE: A
CHOICE: B
CHOICE: C
CHOICE: D
```

### 4.4 任务变量

| 变量 | 类型 | 说明 | 当前状态 |
|---|---|---|---|
| `n_trials` | task parameter | 每个 run 的 trial 数量 | 固定：100 |
| `deck` | action variable | 模型选择的牌堆 | A/B/C/D |
| `payoff_table` | environment variable | 每个 deck 的 reward/loss 规则 | 已实现 |
| `reward` | outcome variable | 当前 trial 的即时收益 | 已实现 |
| `loss` | outcome variable | 当前 trial 的惩罚 / 损失 | 已实现 |
| `net_outcome` | derived outcome | 当前 trial 的 gain 与 loss 之和 | 已实现 |
| `cumulative_score` | outcome variable | 当前 run 的累计分数 | 固定记录 |
| `block_number` | derived variable | trial 所属 20-trial block | 固定：5 blocks |
| `advantageous_choice` | derived variable | 是否选择 C 或 D | 固定计算 |
| `post_loss_switch` | derived variable | 损失后下一 trial 是否换 deck | 固定计算 |

### 4.5 Prompt 条件

| Condition | IGT 中的具体含义 |
|---|---|
| `baseline` | 说明四个 deck、trial 数量、反馈和选择格式 |
| `detailed` | 更详细解释 reward、loss、cumulative score 和重复选择流程 |
| `role_human` | 要求模型以心理学实验中的人类参与者身份完成任务 |
| `reward_loss_emphasis` | 强调选择会产生 reward/loss 和长期结果，但不能直接告诉模型哪些 deck 更好 |

### 4.6 主要指标

| Metric | 说明 | 所需字段 |
|---|---|---|
| net score | advantageous choices 减去 disadvantageous choices，常见形式为 `(C + D) - (A + B)` | deck choice |
| advantageous choice rate | 选择 C/D 的比例 | deck choice |
| deck preference | A/B/C/D 各自被选择的比例 | deck choice |
| block-wise learning curve | 每 20 trials 的 net score 或 advantageous choice rate | trial number, deck choice |
| average net outcome | 每个 trial 的平均净收益 | net outcome |
| post-loss switching | 发生 loss 后下一 trial 是否换牌堆 | loss, previous deck, current deck |

### 4.7 Human dataset 对齐

计划使用：

```text
DATASET/IGT/IGTdataSteingroever2014
```

对齐目标：

- 比较 human participants 与 LLM runs 的 net score；
- 比较 advantageous choice rate；
- 比较 block-wise learning curve；
- 比较 deck preference distribution。

待确认：

- human dataset 中 deck labels、trial count 和 payoff version；
- 是否需要统一 score 方向和 block definition；
- 如果 human dataset 的 payoff table 与本项目实现不同，需要记录为 limitation。

### 4.8 待确认事项

| 问题 | 为什么重要 |
|---|---|
| exact A/B/C/D payoff table | 决定 reward/loss 和长期优劣 |
| reward/loss 是否分别记录 | 决定 post-loss switching 和 feedback sensitivity 指标 |
| deck history 是否展示给 LLM | 决定任务信息条件 |
| human dataset payoff version | 决定 LLM-human comparison 是否可直接对齐 |

## 5. Task 3: Balloon Analogue Risk Task

### 5.1 概述

Balloon Analogue Risk Task 是一个风险承担任务。参与者面对一系列气球，每次可以选择继续给气球打气，也可以选择兑现当前收益。每次 pump 通常会增加潜在收益，但气球可能爆炸；一旦爆炸，当前气球的未兑现收益会损失。

本项目使用 BART 来观察 LLM 如何在即时收益和爆炸风险之间权衡。

### 5.2 任务内容

当前实现：

```text
每个 run: 40 balloons
2 blocks x 20 balloons
每个 balloon 内可重复选择 pump 或 cash out
可选动作: ACTION: PUMP / ACTION: CASH_OUT
```

每个 balloon 开始时临时收益为 0。模型可以选择 `PUMP` 增加该 balloon 的临时收益；如果没有爆炸，模型可以继续 pump 或 cash out。如果选择 `CASH_OUT`，临时收益加入总收益并进入下一个 balloon。如果 pump 导致 explosion，则该 balloon 的临时收益归零并进入下一个 balloon。

每次成功 pump 增加 `0.05` 收益。第 `k` 次 pump 的爆炸概率为 `1/(33-k)`，第 32 次 pump 必然爆炸；具体概率与最大 pump 次数不直接告诉模型。该 40-balloon 版本与本地 human dataset 的每名参与者 40 条 balloon records 对齐。

### 5.3 单次 balloon 流程

1. 新 balloon 开始，temporary earning 为 0。
2. 系统提示当前 balloon 编号、当前 pump 次数、temporary earning、total earning。
3. 模型选择 `PUMP` 或 `CASH_OUT`。
4. 如果选择 `CASH_OUT`，temporary earning 加入 total earning，当前 balloon 结束。
5. 如果选择 `PUMP` 且没有爆炸，temporary earning 增加，继续同一个 balloon。
6. 如果选择 `PUMP` 且爆炸，temporary earning 归零，当前 balloon 结束。
7. 记录 action-level 或 balloon-level 数据。

推荐 response format：

```text
ACTION: PUMP
```

或：

```text
ACTION: CASH_OUT
```

### 5.4 任务变量

| 变量 | 类型 | 说明 | 当前状态 |
|---|---|---|---|
| `n_balloons` | task parameter | 每个 run 的 balloon 数量 | 固定：40 |
| `pump_reward` | environment variable | 每次成功 pump 增加多少收益 | 固定：0.05 |
| `explosion_point` | environment variable | 每个 balloon 在第几次 pump 爆炸 | 每个 balloon 独立采样 |
| `explosion_rule` | environment variable | 第 k 次 pump 的概率为 `1/(33-k)`，第 32 次必然爆炸 | 已实现 |
| `action` | action variable | `PUMP` 或 `CASH_OUT` | 固定 |
| `pump_count` | state variable | 当前 balloon 已 pump 次数 | 固定记录 |
| `temporary_earning` | state / outcome variable | 当前 balloon 未兑现收益 | 固定记录 |
| `total_earning` | outcome variable | 当前 run 累计收益 | 固定记录 |
| `exploded` | outcome variable | 当前 balloon 是否爆炸 | 固定记录 |
| `cashed_out` | outcome variable | 当前 balloon 是否主动兑现 | 固定记录 |

### 5.5 Prompt 条件

| Condition | BART 中的具体含义 |
|---|---|
| `baseline` | 说明 pump、cash out、explosion 和收益规则 |
| `detailed` | 更详细解释 temporary earning、total earning 和 balloon 结束条件 |
| `role_human` | 要求模型以心理学实验中的人类参与者身份完成任务 |
| `risk_emphasis` | 强调收益和爆炸风险之间的权衡，但不能直接建议保守或冒险策略 |

### 5.6 主要指标

| Metric | 说明 | 所需字段 |
|---|---|---|
| average pumps | 所有 balloons 的平均 pump 次数 | pump_count |
| adjusted average pumps | 只计算未爆炸 balloons 的平均 pump 次数 | pump_count, exploded |
| explosion rate | 爆炸 balloons 比例 | exploded |
| average earning per balloon | 每个 balloon 的平均收益 | total_earning / n_balloons |
| post-explosion adjustment | 爆炸后下一个 balloon 的 pump 数是否下降 | exploded, next pump_count |

### 5.7 Human dataset 对齐

计划使用：

```text
DATASET/BART/Dataset.xlsx
```

对齐目标：

- 比较 human participants 与 LLM runs 的 average pumps；
- 比较 adjusted average pumps；
- 比较 explosion rate；
- 比较 average earning per balloon；
- 如果字段允许，比较 post-explosion adjustment。

当前对齐情况：

- human dataset 和 LLM run 均使用 40 balloons；
- raw human dataset 有 147 IDs；按第 9 列年龄字段应用 `age >= 18` 后，排除 6 名未成年人并保留 141 名成年人；
- human data 已能计算 average pumps、adjusted average pumps 和 explosion rate；
- human earning 字段可能经过转换或缩放，`average_earning_per_balloon` 暂不作为最稳妥的直接比较指标；
- pump-based metrics 是当前 BART human-LLM comparison 的主要指标。

### 5.8 剩余注意事项

| 问题 | 为什么重要 |
|---|---|
| human earning 的原始量纲 | 决定收益指标能否直接比较 |
| human 数据列的语义确认 | 原始 Excel 无标准列名，当前预处理依赖列位置 |
| 年龄筛选审计 | `bart_exclusions.csv` 和 `summary.json` 记录 147 → 141 的筛选过程 |
| action-level 与 balloon-level logging | 两者均保留，分别用于过程分析和 human comparison |
| post-explosion adjustment 的稳定性 | 该指标依赖相邻 balloons，可能比总体 pump 指标噪声更大 |

## 6. 三个任务的变量对比

| 维度 | Horizon | IGT | BART |
|---|---|---|---|
| 决策类型 | 二选一 repeated choice | 四选一 repeated deck choice | 连续 pump / cash-out |
| 核心认知过程 | exploration vs exploitation | reward-punishment learning | risk-taking |
| 主要不确定性 | 哪个选项长期更好、信息量不同 | 哪些 deck 长期有利 | 当前 balloon 何时爆炸 |
| 单位 | game / decision | trial | balloon / action |
| 当前实现规模 | 40 games per run | 100 trials per run | 40 balloons per run |
| 关键自变量 | prompt condition, horizon type | prompt condition, block | prompt condition, balloon risk |
| 关键因变量 | choice, exploration, reward | deck choice, net score, cumulative score | pump count, explosion, total earning |
| human data | `DATASET/BANDIT/allHorizonData_cut.csv` | `DATASET/IGT/IGTdataSteingroever2014` | `DATASET/BART/Dataset.xlsx` |
| 当前状态 | 已实现 | 已实现 | 已实现；earning 尺度仍需确认 |

## 7. 建议 trial-level / action-level 记录字段

所有任务都应该记录这些共同字段：

| 字段 | 说明 |
|---|---|
| `run_id` | 当前 run 编号 |
| `task` | `horizon`, `igt`, `bart` |
| `prompt_condition` | 当前 prompt 条件 |
| `model_name` | 使用的 LLM |
| `temperature` | sampling temperature |
| `top_p` | top-p 设置 |
| `seed` | 任务环境或 run seed |
| `trial_number` | 当前 trial / decision / action 编号 |
| `raw_response` | 模型原始输出 |
| `parsed_action` | parser 提取的选择 |
| `parse_success` | 是否成功解析 |
| `retry_count` | 是否重试 |
| `invalid_reason` | 如果无效，记录原因 |

任务特定字段：

| Task | 字段 |
|---|---|
| Horizon | `game_id`, `horizon_type`, `choice`, `reward`, `observed_rewards_A`, `observed_rewards_B`, `information_difference`, `mean_reward_difference` |
| IGT | `deck`, `reward`, `loss`, `net_outcome`, `cumulative_score`, `block_number`, `advantageous_choice` |
| BART | `balloon_id`, `action`, `pump_count`, `temporary_earning`, `total_earning`, `exploded`, `cashed_out`, `explosion_point` |

## 8. 和 dissertation 的对应关系

本文档后续可以拆分进论文不同位置：

| Dissertation section | 可使用内容 |
|---|---|
| Methodology / Tasks | 三个 task 的概述、流程、action format |
| Methodology / Experimental Design | prompt conditions、runs、trial counts、控制变量 |
| Methodology / Measures | 每个 task 的 behavioural metrics |
| Methodology / Human Datasets | human dataset 对齐说明 |
| Results | 指标定义和分组方式 |
| Limitations | 简化设计、代理指标及 human-LLM alignment 不一致事项 |
| Appendix | 任务参数表、变量表、response format |

## 9. 当前优先待办

三个 task environments、response parsers 和 run-level metrics 已经实现。下一阶段重点是：

1. 为每个 `task x prompt_condition` 收集至少 15 个、目标 20 个有效 LLM runs。
2. 确认 BART human dataset 中 earning 相关列的原始量纲和转换方式。
3. 将 human participants 与 repeated LLM runs 按相同 metric definition 进行分布比较。
4. 使用正式多run数据运行hierarchical logistic choice model，并检查`sigma_H6 - sigma_H1`的收敛性、稳定性和不确定区间。
5. 计算 condition-level effect sizes 和项目自定义的 PSI，并同时报告变化方向。
