# Task Parameters

Status: Literature-based working decision v0.1

Date: 2026-05-28

Purpose: This document fixes the exact task parameters to be used in the first implementation of the three cognitive decision-making tasks. The decisions below are based on task literature and on the human datasets currently stored in `DATASET/`.

中文说明：这份文档用于最终确定三个认知决策任务在本项目中的具体实现参数。它不是单纯介绍任务概念，而是说明后续代码、prompt、数据记录和论文 methodology 应该按照哪些规则来实现。每个参数决定都尽量对应到已有文献和当前项目中的 human dataset。

## 1. Summary Of Final Parameter Decisions

| Task | Final decision | Main basis |
|---|---|---|
| Horizon Task | Use Wilson et al. style Horizon Task: two options, 4 forced-choice trials, then either 1 or 6 free choices; rewards sampled from Gaussian distributions with SD = 8; option means stable within each game. | Wilson et al. (2014); local `DATASET/BANDIT/allHorizonData_cut.csv` |
| Iowa Gambling Task | Use classic 100-trial IGT with decks A/B/C/D; A/B are disadvantageous, C/D are advantageous; use the Bechara et al. payoff scheme. | Bechara et al. (1994); Steingroever et al. (2015); local `choice_100.csv`, `wi_100.csv`, `lo_100.csv` |
| BART | Use the probabilistic BART version aligned with the local dataset: 2 blocks x 20 balloons = 40 balloons; 5 cents per successful pump; hidden burst probability increases from 1/32 to certain explosion at pump 32. | Sebri et al. (2023); Xu et al. (2016, 2018) as cited by Sebri et al.; local `DATASET/BART/Dataset.xlsx` |

中文解释：

- Horizon Task 采用 Wilson et al. (2014) 的经典设计，因为这个设计专门用来区分 directed exploration 和 random exploration。
- IGT 采用 100 trials 的经典版本，因为这是最常见、最容易和 human dataset 对齐的版本。
- BART 采用 40 balloons 的版本，不采用原始 Lejuez 30 balloons 版本，主要原因是你本地的 BART human dataset 正好是每个 participant 40 个 balloons。

正式 LLM 实验中，所有 prompt conditions 统一使用 history-rich observation。也就是说，prompt 条件可以改变任务说明、角色框定或认知维度强调，但不能改变模型看到的任务历史信息。IGT 会提供 previous trial、deck history summary 和 recent outcomes；BART 会提供 previous balloon、recent balloon outcomes 和 overall summary；Horizon 保留 observed rewards history。这个决定是为了让 LLM 更接近连续任务中的人类被试，并保证不同 prompt conditions 之间可比较。

## 2. Horizon Task / Two-Option Bandit

### 2.1 Final Parameters

| Parameter | Final value |
|---|---|
| Options | `A`, `B` |
| Games per run | 40 games |
| Game structure | 4 forced-choice trials, followed by free-choice trials |
| Horizon conditions | Horizon 1: 1 free choice after forced trials; Horizon 6: 6 free choices after forced trials |
| Total trials per game | Horizon 1 game: 5 trials; Horizon 6 game: 10 trials |
| Information conditions | Unequal information `[1, 3]`; equal information `[2, 2]` |
| Reward distribution | Rounded Gaussian reward, bounded for display to 1-100 if needed |
| Reward SD | 8 points |
| Option means | Stable within a game; one option mean is 40 or 60; the other differs by one of `+/-4`, `+/-8`, `+/-12`, `+/-20`, `+/-30` |
| Main free-choice analysis | First free-choice trial, because reward and information are still experimentally decorrelated |
| Response format | `CHOICE: A` or `CHOICE: B` |

中文解释：

Horizon Task 的核心是让模型在两个选项之间做重复选择。前 4 次不是自由选择，而是 forced-choice trials，目的是人为控制模型看到每个选项多少信息。例如 `[1, 3]` 表示一个选项只被展示过 1 次，另一个选项被展示过 3 次；`[2, 2]` 表示两个选项的信息量相同。

Horizon 1 和 Horizon 6 的区别在于未来还有多少次选择机会。Horizon 1 只有 1 次自由选择，所以探索新信息的价值较低；Horizon 6 有 6 次自由选择，所以探索可能更有价值。这个差异正好可以用来观察模型是否会因为未来机会更多而增加探索行为。

本项目保留 Wilson et al. 的核心结构，但把每个 run 的 game 数量设为 40，而不是原论文中的 320。这样做是为了控制 LLM API 成本和运行时间。论文中需要说明这是一个简化版本，但关键 experimental manipulation 仍然保留。

### 2.2 Literature Basis

Wilson et al. (2014) designed the Horizon Task specifically to separate directed exploration from random exploration. Their task used two slot-machine options, four forced-choice trials, and then either one free choice in Horizon 1 or six free choices in Horizon 6. They used the forced-choice phase to create equal `[2, 2]` or unequal `[1, 3]` information before the first free decision.

Key content from the paper:

- Participants played games lasting either 5 or 10 trials.
- The first four trials were forced choices.
- The forced-choice phase created unequal information `[1, 3]` or equal information `[2, 2]`.
- After forced choices, participants made either 1 or 6 free choices.
- Rewards were sampled from Gaussian distributions with SD = 8.
- One option mean was set to 40 or 60, and the other was offset by fixed mean differences.
- Their main analysis focused on the first free-choice trial because reward and information are not yet confounded there.

Project decision:

Use this structure because it gives clean operational definitions for:

- directed exploration: increased choice of the more informative option in Horizon 6 relative to Horizon 1;
- random exploration: increased choice variability / weaker sensitivity to observed mean reward difference in Horizon 6;
- horizon effect: behavioural change from Horizon 1 to Horizon 6.

中文解释：

这里的 directed exploration 指的是模型是否主动选择“信息更少但更值得了解”的选项。例如在 `[1, 3]` 条件下，被观察过 1 次的选项信息更少，因此选择它可以获得更多新信息。

random exploration 指的是选择是否变得更随机。Wilson et al. 的逻辑是，如果 Horizon 6 中模型更愿意探索，那么它不仅可能更偏向信息少的选项，也可能表现出更高的 choice variability，即选择不再完全由当前观察到的平均 reward 决定。

第一自由选择 trial 很重要，因为在这个时点，reward 和 information 还没有因为后续自由选择而混在一起。因此分析这个 trial 可以更干净地判断探索行为。

### 2.3 Local Dataset Alignment

The local Horizon dataset `DATASET/BANDIT/allHorizonData_cut.csv` has columns such as:

```text
gameLength, uc, m1, m2, r1-r10, c1-c10
```

The observed rows include `gameLength` values of 5 and 10, matching the Horizon 1 / Horizon 6 structure. The reward means `m1` and `m2` also show values consistent with the Wilson-style setup.

Implementation note:

For the LLM version, use 40 games per run rather than the full 320 games used by Wilson et al. This is a pragmatic reduction for API cost and runtime. It must be reported as a simplified implementation, while preserving the core forced-choice, horizon, information, and reward-generation structure.

中文解释：

本地数据中的 `gameLength` 有 5 和 10，正好对应 Horizon 1 和 Horizon 6。`m1` 和 `m2` 是两个选项的真实 reward mean，`r1-r10` 是每个 trial 的 reward，`c1-c10` 是 participant 的选择。LLM 任务实现时，应该尽量记录相同或可对应的字段，方便后续 human-LLM comparison。

## 3. Iowa Gambling Task

### 3.1 Final Parameters

| Parameter | Final value |
|---|---|
| Decks | `A`, `B`, `C`, `D` |
| Trials per run | 100 trials |
| Initial loan / starting score | 2000 points or dollars |
| Reward on A/B | +100 on every selection |
| Reward on C/D | +50 on every selection |
| Disadvantageous decks | A and B |
| Advantageous decks | C and D |
| Block size | 20 trials |
| Number of blocks | 5 |
| Response format | `CHOICE: A`, `CHOICE: B`, `CHOICE: C`, or `CHOICE: D` |

中文解释：

IGT 的核心是让模型反复从四个 deck 中选牌。A/B 看起来短期收益更高，因为每次选择都会得到 +100；C/D 每次只有 +50，看起来更保守。但长期来看，A/B 的惩罚更大，所以净收益是负的；C/D 的惩罚更小，所以长期净收益是正的。

因此，这个任务主要测试模型是否能通过 trial-by-trial feedback 慢慢学会避开 A/B，转向 C/D。100 trials 分成 5 个 block，每个 block 20 trials，可以观察模型是否随着时间逐渐学习。

### 3.2 Payoff Scheme

Use the standard Bechara et al. payoff scheme:

| Deck | Gain on every trial | Loss frequency per 10 selections | Loss amounts per 10 selections | Net return per 10 selections |
|---|---:|---:|---|---:|
| A | +100 | 5 losses | -150, -200, -250, -300, -350 | -250 |
| B | +100 | 1 loss | -1250 | -250 |
| C | +50 | 5 losses | -25, -50, -50, -50, -75 | +250 |
| D | +50 | 1 loss | -250 | +250 |

Implementation note:

The loss schedule should repeat across the 100 trials according to the number of times each deck has been selected, not according to the global trial number. For example, the 11th selection from deck A starts the next cycle of deck A's 10-card schedule.

中文解释：

payoff schedule 的关键点是：loss 不是按全局 trial number 走，而是按某个 deck 被选择了第几次来走。例如模型第 1 次选择 deck A，就使用 A 的第 1 张牌规则；第 10 次选择 deck A，就使用 A 的第 10 张牌规则；第 11 次选择 deck A，则重新进入 A 的下一轮 10-card cycle。

这个设计可以保证每个 deck 都有自己固定的长期收益结构。模型如果一直选 A 或 B，长期会亏；如果逐渐转向 C 或 D，长期会赚。

### 3.3 Literature Basis

The IGT literature commonly uses 100 trials and computes learning over five 20-trial blocks. Bechara et al.'s original design distinguishes high immediate reward but negative long-term decks A/B from lower immediate reward but positive long-term decks C/D.

Key content from the literature:

- Participants repeatedly select from four decks.
- A/B give larger immediate gains but negative expected value.
- C/D give smaller immediate gains but positive expected value.
- The classic net score is `(C + D) - (A + B)`.
- Standard analysis often uses 100 trials and 20-trial blocks.

Project decision:

Use 100 trials because the local Steingroever dataset includes a standard 100-trial subset and because this is the cleanest version for block-wise learning and dissertation explanation.

中文解释：

本项目选择 100 trials 有两个原因。第一，这是 IGT 最经典、最常见的版本，适合写进 methodology。第二，你本地的 Steingroever human dataset 里有 `choice_100.csv`、`wi_100.csv` 和 `lo_100.csv`，可以直接和 LLM 的 100-trial run 对齐。

主要分析指标中，`net score = (C + D) - (A + B)` 是最重要的 summary measure。值越高，说明模型越偏向长期有利的 deck。

### 3.4 Local Dataset Alignment

The local folder `DATASET/IGT/IGTdataSteingroever2014/` includes:

```text
choice_100.csv
wi_100.csv
lo_100.csv
index_100.csv
```

The local files confirm that:

- choices are recorded across 100 trials;
- wins and losses are separately available;
- the first rows show +100 rewards for decks A/B and +50 rewards for decks C/D;
- loss values include the expected values from the classic payoff scheme, such as -1250, -350, -250, -75, and -50.

Use the 100-trial data as the main human comparison subset. The 95-trial and 150-trial subsets can be ignored in the first implementation or used only in sensitivity checks.

中文解释：

本地 IGT 数据已经把 choice、win 和 loss 分开存储，所以后续可以直接计算 human participant 的 net score、advantageous choice rate 和 block-wise learning curve。为了让 LLM 和 human comparison 更清楚，第一阶段只使用 100-trial subset，不混入 95 或 150 trial 的版本。

## 4. Balloon Analogue Risk Task

### 4.1 Final Parameters

| Parameter | Final value |
|---|---|
| Balloons per run | 40 |
| Block structure | 2 blocks x 20 balloons |
| Practice balloons | Exclude from LLM implementation unless needed for a separate pilot; Sebri et al. used 5 familiarisation balloons |
| Actions | `PUMP`, `CASH_OUT` |
| Pump reward | 0.05 currency units per successful pump |
| Temporary earning | `pump_count * 0.05` for current balloon |
| Cash out | Add temporary earning to permanent total and end current balloon |
| Explosion | Lose current temporary earning and end current balloon |
| Explosion rule | Probabilistic version: pump 1 has burst probability 1/32, pump 2 has 1/31, pump 3 has 1/30, ..., pump 31 has 1/2, pump 32 explodes with certainty |
| Participant/model knowledge | Do not reveal the exact burst probability or maximum pump |
| Response format | `ACTION: PUMP` or `ACTION: CASH_OUT` |

中文解释：

BART 的核心是风险-收益权衡。每 pump 一次，当前 balloon 的 temporary earning 增加，但爆炸风险也增加。如果模型选择 `CASH_OUT`，当前 balloon 的钱会进入 permanent total；如果继续 pump 并爆炸，当前 balloon 的 temporary earning 会归零。

本项目采用 40 balloons，因为本地 human dataset 是每个 participant 40 个 balloon records。爆炸概率不告诉模型，因为人类实验中 participant 通常也不知道具体概率，只能通过经验学习风险结构。

### 4.2 Literature Basis

Lejuez et al. introduced the BART as a behavioural risk-taking task in which each pump increases possible reward and also increases the risk of losing the temporary earnings for that balloon. The standard dependent variable is adjusted average pumps, computed only on unexploded balloons.

Sebri et al. (2023), which is the closest match to the local dataset, used an online probabilistic BART. Their participants completed two independent BART blocks of 20 balloons each. They used 5 cents per pump and an increasing burst probability: 1/32 on the first pump, 1/31 on the second, continuing until certain explosion at pump 32. They also used per-trial number of pumps and adjusted number of pumps as key measures.

Project decision:

Use the Sebri-style 40-balloon version rather than the original 30-balloon Lejuez version because the raw local `Dataset.xlsx` contains 147 participants with 40 rows per participant. The adult analysis sample contains 141 participants after applying `age >= 18`. This gives better LLM-human alignment for the selected human dataset.

中文解释：

Lejuez et al. 的原始 BART 通常是 30 balloons，并且常用 adjusted average pumps 作为主要风险指标。但你的本地数据更接近 Sebri et al. (2023) 的版本：两个 20-balloon blocks，总共 40 balloons。因此，为了让 LLM 数据和 human 数据可比，本项目优先采用 40-balloon 版本。

adjusted average pumps 只计算没有爆炸的 balloons，因为爆炸的 balloon 会被系统强制终止，不能完全反映 participant 或模型原本想 pump 到多少次。

### 4.3 Local Dataset Alignment

The local BART file `DATASET/BART/Dataset.xlsx` has:

```text
5880 rows = 147 participants x 40 balloons
```

Inspection of the file shows:

- 40 balloon records per participant;
- participant age in the ninth column (zero-based index 8);
- observed pump counts and explosion indicators;
- reward and earning columns appear to be transformed or scaled for analysis, so the implementation should follow the source-paper task rule and document any scaling used during human-data processing.

The analysis sample applies `age >= 18`, excluding six participants and
retaining 141 adults (5,640 balloon rows). The exclusion audit is stored in
`outputs/processed/human_metrics/bart_exclusions.csv`.

Implementation note:

For the LLM version, record both action-level data and balloon-level summaries. The main human comparison can use balloon-level metrics:

- average pumps;
- adjusted average pumps;
- explosion rate;
- total earnings;
- post-explosion adjustment.

中文解释：

BART 的 LLM 实现最好同时记录 action-level 和 balloon-level 数据。action-level 数据能看出模型每一步是继续 pump 还是 cash out；balloon-level 数据更适合和 human dataset 对齐，例如每个 balloon 最终 pump 了多少次、是否爆炸、是否 cash out、最终收益是多少。

特别需要注意的是，本地 BART 数据中的部分 reward / earning 列可能已经经过转换或缩放。因此实现任务时应以文献中的原始规则为准，即每次 successful pump 增加 0.05；处理 human dataset 时再单独记录它的缩放方式。

## 5. References Used For Parameter Decisions

- Wilson, R. C., Geana, A., White, J. M., Ludvig, E. A., & Cohen, J. D. (2014). Humans use directed and random exploration to solve the explore-exploit dilemma. Journal of Experimental Psychology: General, 143(6), 2074-2081. https://doi.org/10.1037/a0038199
- Bechara, A., Damasio, A. R., Damasio, H., & Anderson, S. W. (1994). Insensitivity to future consequences following damage to human prefrontal cortex. Cognition, 50(1-3), 7-15. https://doi.org/10.1016/0010-0277(94)90018-3
- Steingroever, H., et al. (2015). Data from 617 healthy participants performing the Iowa Gambling Task: A "many labs" collaboration. Journal of Open Psychology Data, 3, e5. https://doi.org/10.5334/jopd.ak
- Lejuez, C. W., et al. (2002). Evaluation of a behavioral measure of risk taking: The Balloon Analogue Risk Task (BART). Journal of Experimental Psychology: Applied, 8(2), 75-84. https://doi.org/10.1037/1076-898X.8.2.75
- Sebri, V., Triberti, S., Granic, G. D., & Pravettoni, G. (2023). Reward-dependent dynamics and changes in risk taking in the Balloon Analogue Risk Task. Journal of Cognitive Psychology, 35(3), 340-354. https://doi.org/10.1080/20445911.2023.2181065
