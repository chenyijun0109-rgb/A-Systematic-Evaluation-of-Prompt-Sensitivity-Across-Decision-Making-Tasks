# LLM-Human Comparison 中文分析

日期：2026-07-18

本文档比较正式实验的 English 阶段 `formal_v01` 与三个任务的人类数据。这里采用的策略是：

```text
LLM: formal_v01，每个 task-condition 20 runs
Human: 每个 task 使用一个已有 human dataset 的全部有效 participants
```

参与者数量：

| Task | Human dataset | 有效 participants |
|---|---|---:|
| Horizon | `DATASET/BANDIT/allHorizonData_cut.csv` | 60 |
| IGT | `DATASET/IGT/IGTdataSteingroever2014` 100-trial subset | 504 |
| BART | `DATASET/BART/Dataset.xlsx`, age >= 18 | 141 |

解释边界：

- 一个 LLM run 被当作一个 participant-level behavioural summary。
- Human data 是 task-specific reference distribution，不是全部人类行为的最终标准。
- 当前 English 阶段比较使用 `formal_v01`；中文和西班牙语完成后将使用同一套 human reference datasets。

## 1. Human Reference Summary

| Task | Metric | Human n | Human mean | Human SD | Median | 95% reference interval |
|---|---|---:|---:|---:|---:|---|
| Horizon | directed_exploration | 60 | 0.544 | 0.083 | 0.537 | [0.378, 0.698] |
| Horizon | horizon_effect | 60 | 0.111 | 0.087 | 0.101 | [-0.000, 0.311] |
| Horizon | random_exploration_effect | 60 | 8.910 | 6.390 | 7.218 | [1.569, 25.397] |
| IGT | advantageous_choice_rate | 504 | 0.538 | 0.159 | 0.520 | [0.206, 0.850] |
| IGT | post_loss_switching_rate | 504 | 0.695 | 0.264 | 0.764 | [0.156, 1.000] |
| BART | adjusted_average_pumps | 141 | 8.320 | 3.281 | 7.931 | [3.146, 15.412] |
| BART | explosion_rate | 141 | 0.285 | 0.114 | 0.275 | [0.075, 0.475] |
| BART | post_explosion_adjustment | 140 | 1.191 | 1.608 | 1.150 | [-1.679, 4.492] |

注意：Horizon 的 `random_exploration_effect` 来自同一个 first-free-choice logistic model 的 human run estimates，不是原始 participant CSV 里的直接列。

## 2. 每个指标最接近 Human 的 Prompt Condition

| Task | Metric | Closest prompt | Standardised distance | LLM mean | Human mean | LLM mean position | LLM runs within human reference |
|---|---|---|---:|---:|---:|---|---:|
| Horizon | directed_exploration | baseline | -0.020 | 0.543 | 0.544 | within | 0.900 |
| Horizon | horizon_effect | uncertainty_emphasis | -0.784 | 0.043 | 0.111 | within | 0.550 |
| Horizon | random_exploration_effect | uncertainty_emphasis | -1.094 | 1.921 | 8.910 | within | 0.550 |
| IGT | advantageous_choice_rate | detailed | 2.070 | 0.867 | 0.538 | above | 0.000 |
| IGT | post_loss_switching_rate | detailed | -0.215 | 0.638 | 0.695 | within | 1.000 |
| BART | adjusted_average_pumps | role_human | -0.110 | 7.959 | 8.320 | within | 1.000 |
| BART | explosion_rate | baseline | -0.069 | 0.277 | 0.285 | within | 1.000 |
| BART | post_explosion_adjustment | baseline | -0.552 | 0.303 | 1.191 | within | 0.950 |

解释：

- BART 三个 primary metrics 都能找到非常接近 human mean 的 prompt condition。
- Horizon 的 `directed_exploration` 很接近人类；但 `horizon_effect` 和 `random_exploration_effect` 偏低。
- IGT 的 `post_loss_switching_rate` 接近人类；但 `advantageous_choice_rate` 明显高于人类，即 LLM 更偏向长期有利牌堆。

## 3. Horizon: LLM vs Human

### 3.1 directed_exploration

含义：信息不平衡时，选择信息较少、因此更有探索价值选项的倾向。

| Prompt | LLM mean | Human mean | Difference | Human-SD distance | Position | Within human reference |
|---|---:|---:|---:|---:|---|---:|
| baseline | 0.543 | 0.544 | -0.002 | -0.020 | within | 0.900 |
| detailed | 0.580 | 0.544 | 0.036 | 0.433 | within | 0.850 |
| role_human | 0.485 | 0.544 | -0.059 | -0.715 | within | 0.900 |
| uncertainty_emphasis | 0.687 | 0.544 | 0.143 | 1.731 | within | 0.500 |

解释：

- Baseline 几乎与 human mean 完全一致。
- Detailed 也在人类范围内，并略高于 human mean。
- Role_human 偏低，但仍在人类 reference interval 内。
- Uncertainty_emphasis 明显提高 directed exploration，接近 human reference interval 上沿。

结论：Horizon 的 directed exploration 是 LLM-human alignment 最好的 Horizon 指标。

### 3.2 horizon_effect

含义：Horizon 6 与 Horizon 1 之间的行为差异。

| Prompt | LLM mean | Human mean | Difference | Human-SD distance | Position | Within human reference |
|---|---:|---:|---:|---:|---|---:|
| baseline | -0.010 | 0.111 | -0.121 | -1.386 | below | 0.500 |
| detailed | 0.003 | 0.111 | -0.108 | -1.243 | within | 0.650 |
| role_human | -0.003 | 0.111 | -0.113 | -1.300 | below | 0.650 |
| uncertainty_emphasis | 0.043 | 0.111 | -0.068 | -0.784 | within | 0.550 |

解释：

- 所有 LLM prompt 的 horizon_effect 都低于 human mean。
- Uncertainty_emphasis 最接近 human，但仍偏低。
- Baseline 和 role_human 的 mean 低于 human reference interval 下界。

结论：LLM 对 long horizon vs short horizon 的行为调节弱于人类。

### 3.3 random_exploration_effect

含义：`decision_noise_h6 - decision_noise_h1`，表示 Horizon 6 相对 Horizon 1 的选择变异性增加。

| Prompt | LLM mean | Human mean | Difference | Human-SD distance | Position | Within human reference |
|---|---:|---:|---:|---:|---|---:|
| baseline | 0.492 | 8.910 | -8.418 | -1.317 | below | 0.200 |
| detailed | -0.255 | 8.910 | -9.165 | -1.434 | below | 0.100 |
| role_human | -0.055 | 8.910 | -8.965 | -1.403 | below | 0.000 |
| uncertainty_emphasis | 1.921 | 8.910 | -6.989 | -1.094 | within | 0.550 |

解释：

- Human random_exploration_effect 明显高于 LLM。
- Uncertainty_emphasis 最接近 human，但仍低约 1.09 个 human SD。
- Baseline、detailed、role_human 都明显低于 human reference distribution。

结论：LLM 没有像人类一样强烈增加 long-horizon choice variability。Uncertainty prompt 可以提高这个指标，但不足以达到 human mean。

## 4. IGT: LLM vs Human

### 4.1 advantageous_choice_rate

含义：选择长期有利牌堆 C/D 的比例。

| Prompt | LLM mean | Human mean | Difference | Human-SD distance | Position | Within human reference |
|---|---:|---:|---:|---:|---|---:|
| baseline | 0.908 | 0.538 | 0.370 | 2.328 | above | 0.000 |
| detailed | 0.867 | 0.538 | 0.329 | 2.070 | above | 0.000 |
| reward_loss_emphasis | 0.969 | 0.538 | 0.431 | 2.711 | above | 0.000 |
| role_human | 0.902 | 0.538 | 0.364 | 2.290 | above | 0.000 |

解释：

- 所有 prompt condition 都高于 human 95% reference upper bound 0.850。
- 即使最接近 human 的 detailed condition，LLM mean 仍然比 human mean 高 2.07 个 human SD。
- LLM 比人类更快或更稳定地偏向长期有利牌堆 C/D。

结论：IGT 的 advantageous choice 上，LLM 不像普通 human distribution，而是表现得更接近“高表现/高理性”的策略。

### 4.2 post_loss_switching_rate

含义：出现 loss 后下一 trial 换牌堆的概率。

| Prompt | LLM mean | Human mean | Difference | Human-SD distance | Position | Within human reference |
|---|---:|---:|---:|---:|---|---:|
| baseline | 0.570 | 0.695 | -0.125 | -0.473 | within | 1.000 |
| detailed | 0.638 | 0.695 | -0.057 | -0.215 | within | 1.000 |
| reward_loss_emphasis | 0.469 | 0.695 | -0.226 | -0.855 | within | 1.000 |
| role_human | 0.611 | 0.695 | -0.084 | -0.316 | within | 1.000 |

解释：

- 所有 LLM runs 都落在人类 reference interval 内。
- Detailed 最接近 human mean。
- Reward_loss_emphasis 明显降低 post-loss switching，但仍在人类范围内。

结论：IGT 的 post-loss switching 与 human reference distribution 对齐较好。

## 5. BART: LLM vs Human

### 5.1 adjusted_average_pumps

含义：未爆炸 balloons 上的平均 pump 数，是 BART 常用风险承担指标。

| Prompt | LLM mean | Human mean | Difference | Human-SD distance | Position | Within human reference |
|---|---:|---:|---:|---:|---|---:|
| baseline | 9.051 | 8.320 | 0.731 | 0.223 | within | 1.000 |
| detailed | 8.818 | 8.320 | 0.498 | 0.152 | within | 1.000 |
| risk_emphasis | 8.951 | 8.320 | 0.631 | 0.192 | within | 1.000 |
| role_human | 7.959 | 8.320 | -0.362 | -0.110 | within | 1.000 |

解释：

- 所有 BART prompt conditions 都与 human mean 很接近。
- 所有 LLM runs 都落在人类 95% reference interval 内。
- Role_human 最接近 human mean。

结论：BART adjusted_average_pumps 的 LLM-human alignment 很好。

### 5.2 explosion_rate

含义：爆炸 balloons 的比例。

| Prompt | LLM mean | Human mean | Difference | Human-SD distance | Position | Within human reference |
|---|---:|---:|---:|---:|---|---:|
| baseline | 0.277 | 0.285 | -0.008 | -0.069 | within | 1.000 |
| detailed | 0.302 | 0.285 | 0.017 | 0.152 | within | 1.000 |
| risk_emphasis | 0.294 | 0.285 | 0.008 | 0.075 | within | 1.000 |
| role_human | 0.254 | 0.285 | -0.032 | -0.278 | within | 1.000 |

解释：

- 所有 prompt conditions 都非常接近 human mean。
- Baseline 最接近 human mean。
- 所有 LLM runs 都在人类 reference interval 内。

结论：BART explosion_rate 是最强的人类对齐指标之一。

### 5.3 post_explosion_adjustment

含义：爆炸后下一只 balloon 相对于发生爆炸 balloon 的 pump 数变化。正值表示下一只 balloon 的 pumps 更多，负值表示更少；该指标描述相邻行为变化，不直接等同于学习或风险管理能力。

| Prompt | LLM mean | Human mean | Difference | Human-SD distance | Position | Within human reference |
|---|---:|---:|---:|---:|---|---:|
| baseline | 0.303 | 1.191 | -0.888 | -0.552 | within | 0.950 |
| detailed | -1.004 | 1.191 | -2.195 | -1.365 | within | 0.750 |
| risk_emphasis | -0.123 | 1.191 | -1.315 | -0.817 | within | 0.950 |
| role_human | -0.681 | 1.191 | -1.872 | -1.164 | within | 0.800 |

解释：

- 所有 LLM means 仍在人类 reference interval 内，但普遍低于 human mean。
- Human 平均值为正，表示样本中的下一只 balloon 平均具有更多 pumps。
- LLM 尤其在 detailed 和 role_human 下表现出更负的相邻 pump-count change。

结论：BART post_explosion_adjustment 在范围上仍与人类参考分布重叠，但 LLM 均值较低；由于该指标受爆炸 balloon 本身 pump 数的机械影响，这一差异不单独解释为学习或风险管理能力。

## 6. 总体结论

### 6.1 哪些地方最像人类？

最接近 human distribution 的部分：

- Horizon `directed_exploration`，尤其 baseline。
- IGT `post_loss_switching_rate`，尤其 detailed。
- BART 三个 primary metrics 整体都较接近 human，尤其 `explosion_rate` 和 `adjusted_average_pumps`。

### 6.2 哪些地方不像人类？

主要偏离：

- IGT `advantageous_choice_rate`：LLM 所有 prompt conditions 都高于 human reference interval，说明 LLM 过度偏向长期有利牌堆。
- Horizon `random_exploration_effect`：LLM 明显低于 human mean，说明 LLM 没有人类那么强的 long-horizon random exploration。
- Horizon `horizon_effect`：LLM 低于 human mean，说明 horizon manipulation 对 LLM 的影响弱于人类。

### 6.3 Prompt 对 human-likeness 的影响

不同 prompt 会改变 LLM 与 human reference 的距离：

- `Horizon uncertainty_emphasis` 让 Horizon 的 `horizon_effect` 和 `random_exploration_effect` 更接近 human，但也把 `directed_exploration` 推到 human range 上沿。
- `IGT detailed` 是 IGT 中最接近 human 的 prompt，但 only for the two primary metrics considered separately：它降低了过高的 advantageous choice，同时提高了 post-loss switching。
- `BART role_human` 最接近 human adjusted pumps，但 BART baseline 最接近 human explosion rate 和 post-explosion adjustment。

因此，没有一个 prompt 在所有任务和所有指标上都“最像人类”。Human-likeness 是 task-specific 和 metric-specific 的。

## 7. 论文可用表述

英文：

```text
The primary LLM-human comparison used the first completed formal batch
(`formal_v01`) with 20 LLM runs per task-condition cell. Each LLM run was
treated as analogous to a participant-level behavioural summary and compared
against the available task-specific human reference distribution. The human
datasets contained 60 Horizon participants, 504 IGT participants, and 141 BART
participants.

The comparison showed task-dependent alignment. BART metrics were broadly
human-compatible: all prompt-condition means fell within the human reference
intervals for adjusted average pumps, explosion rate, and post-explosion
adjustment. Horizon directed exploration was also close to the human
distribution, especially under baseline prompting. However, LLMs showed weaker
horizon and random-exploration effects than humans. In IGT, post-loss switching
fell within the human reference range, but advantageous choice rates were above
the human reference interval across all prompt conditions, suggesting more
consistently advantageous deck selection than typical human participants.
```

中文：

```text
当前 English LLM-human comparison 使用 formal_v01，即每个 task-condition
20 个 LLM runs。每个 LLM run 被视为一个 participant-level 行为摘要，并与对应任务的
human reference distribution 比较。三个 human datasets 分别包含 Horizon 60 名、
IGT 504 名和 BART 141 名有效参与者。

结果显示，LLM-human alignment 具有明显任务差异。BART 的三个 primary metrics
整体与人类较为一致，所有 prompt-condition means 都落在人类 reference intervals 内。
Horizon 的 directed exploration 也接近人类，尤其 baseline prompt。但 LLM 的
horizon_effect 和 random_exploration_effect 低于 human mean，说明 long-horizon
exploration 调节弱于人类。IGT 中，post-loss switching 落在人类范围内；但
advantageous_choice_rate 在所有 prompt conditions 下都高于 human reference interval，
说明 LLM 比典型人类参与者更稳定地选择长期有利牌堆。
```
