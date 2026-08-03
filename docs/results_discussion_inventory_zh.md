# 论文结果与讨论事项清单

更新日期：2026-08-03

## 1. 文件用途与当前边界

本文件整理当前三模型正式英文实验中，论文 Results 与 Discussion 需要报告和解释的结果。它不是最终 Results 文稿，也不替代最终三模型表格、稳健性分析或 results checklist。

正式范围为 GPT-4.1、GPT-5.4 和 GPT-5.4 Mini；每个模型包含 3 tasks × 4 prompt conditions × 20 runs，共 240 个有效 task runs，三模型共 720 个。早期 pilots、多语言数据及被替代的失败尝试不进入论文结果。

以下数值来自当前 refit 后的 model-specific prompt effects、GPT-4.1-reference interaction contrasts、PSI 和 model-specific human-reference outputs。最终写作前仍须完成统一三模型结果包、robustness/multiplicity specification 和 claim-to-output audit。

## 2. 论文首先必须报告的数据质量结果

- 三个模型各有 240/240 个有效 runs；每个 model × task × condition cell 均有 20 runs。
- 三模型使用相同的英文 prompts、prompt hashes、task settings、matched environment seeds 和 sampling settings。
- 三个模型的严格聚合及 prompt-sensitivity 分析均完成，且报告 `issues=[]`。
- GPT-5.4 Mini 有一个 Horizon baseline run 出现一次可恢复的 parser retry；最终仍包含全部 300 个有效 choices。该 run 应保留并在 data-quality note 中披露。
- IGT 环境不使用 nominal seed，API sampling 也未被该 seed 配对。因此 IGT 的不确定性采用 independent-cell bootstrap，不能称为 paired-seed inference。

这部分只证明结果包完整、可比较，不属于行为结论。

## 3. Results 中需要组织的六组核心结果

### 3.1 Baseline behavioural profiles

需要先展示三个模型在 neutral baseline 下的原始行为位置，因为后续相同大小的 prompt effect 可能发生在完全不同的 baseline 上。

重点问题：

1. 三模型的 baseline 均值和 run-level dispersion 是否不同？
2. 是否存在 ceiling、floor 或极低方差？
3. baseline 已经接近任务边界时，后续 raw difference 和 standardised effect 是否出现分歧？

特别需要讨论 IGT advantageous-choice rate 的 ceiling/low-variance 问题。Mini 的部分 prompt effect 原始变化仅为 0.007–0.012，但标准化效应约为 0.67–1.06。这不是“大幅行为改变”，而是小原始变化被极低组内方差放大；论文必须同时报告百分点变化、Hedges' g 和 variance warning。

### 3.2 Within-model prompt effects

#### GPT-4.1

- Horizon：uncertainty emphasis 将 directed exploration 提高 0.145（14.5 个百分点；g=1.47，95% CI [1.01, 2.15]），是最清楚的 Horizon prompt effect。role framing 则降低 5.7 个百分点（g=-0.69，CI [-1.19, -0.33]）。Horizon/random-exploration 的其他估计区间普遍较宽。
- IGT：instruction specificity 降低 advantageous choice 4.1 个百分点（g=-0.92，CI [-1.53, -0.33]），并提高 post-loss switching 6.8 个百分点（g=0.65，CI [0.14, 1.10]）。reward/loss emphasis 提高 advantageous choice 6.1 个百分点（g=1.11，CI [0.46, 2.23]），同时降低 post-loss switching 10.1 个百分点（g=-0.69，CI [-1.45, -0.07]）。
- BART：role framing 同时降低 adjusted pumps 1.09、explosion rate 2.4 个百分点，并使 post-explosion adjustment 降低 0.98；三个区间均排除 0。instruction specificity 和 risk emphasis 也影响部分 explosion/post-explosion 指标，但并非所有风险指标同向移动。

#### GPT-5.4

- Horizon：三个 manipulated prompts 对三个主要指标的点估计总体较小，区间均包含 0。相较 GPT-4.1，这一任务呈现更高的 prompt stability。
- IGT：三个 prompts 均提高 advantageous-choice rate，变化分别约为 4.1、3.4 和 7.3 个百分点；对应 g 约为 0.80、0.79 和 1.59，区间均在 0 以上。post-loss switching 没有同样清楚的一致变化。
- BART：role framing 是主要敏感来源，adjusted pumps 降低 0.97（g=-1.45，CI [-2.65, -0.80]），explosion rate 降低 2.8 个百分点（g=-1.48，CI [-2.19, -1.06]）。instruction specificity 和 risk emphasis 的大多数 raw effects 较小或边界性。

#### GPT-5.4 Mini

- Horizon：role framing 提高 directed exploration 4.0 个百分点（g=0.49，CI [0.17, 0.95]），并明显提高 random-exploration effect（raw +1.89；g=1.86，CI [0.70, 3.30]）。random-exploration estimates 的不确定性仍需结合层级 refit 和宽区间解释。
- IGT：advantageous-choice rate 的 raw changes 很小（0.7–1.6 个百分点），但因组内方差很低，g 为 0.65–1.06。这里应优先描述为“接近 ceiling 下的小幅但一致变化”，不能只写“大效应”。post-loss switching 的区间大多包含 0。
- BART：这是 Mini 最突出的敏感性来源。instruction specificity 增加 adjusted pumps 1.98（g=2.10）和 explosion rate 5.9 个百分点（g=2.02）；risk emphasis 则降低 adjusted pumps 1.31（g=-2.01）和 explosion rate 3.6 个百分点（g=-2.02）。两种提示导致相反方向的大变化，显示的是 framing-dependent behavioural instability，而不是稳定的“风险偏好改善”。

### 3.3 Model-by-prompt interactions

跨模型结论必须依据 interaction contrast，而不是比较“一个模型显著、另一个不显著”。正值表示 GPT-5.4/Mini 的 prompt effect 比 GPT-4.1 更正向；它不自动表示更好或更稳定。

#### GPT-5.4 相对 GPT-4.1

- Horizon uncertainty emphasis 对 directed exploration 的 interaction 为 -0.148，95% CI [-0.203, -0.095]：GPT-4.1 的强正向反应在 GPT-5.4 中基本消失。
- Horizon role framing 的 directed-exploration interaction 为 +0.052 [0.015, 0.088]：GPT-4.1 的下降在 GPT-5.4 中减弱。
- IGT instruction specificity 和 role framing 对 advantageous choice 的 interactions 分别为 +0.082 和 +0.040，区间排除 0，说明两模型对这些 wording changes 的方向不同。
- BART 最清楚的差异集中在 post-explosion adjustment：instruction specificity、role framing 和 risk emphasis 的 interactions 分别约为 +1.74、+1.25 和 +0.68。该指标需要结合两个模型各自变化解释，不能仅报告 interaction 正负号。

#### GPT-5.4 Mini 相对 GPT-4.1

- Horizon uncertainty-emphasis interaction 与 GPT-5.4 相同，directed exploration 为 -0.148 [-0.200, -0.095]；但 role framing 同时改变 directed 和 random exploration。
- IGT interactions 呈混合方向，没有形成“Mini 一致更敏感/更稳定”的简单模式。
- BART interactions 最强：instruction specificity 使 Mini 相对 GPT-4.1 的 adjusted-pump effect 高约 2.21，risk emphasis 则低约 1.21；explosion-rate interactions 也呈相反方向。这支持 Mini 在 BART 上具有强烈、方向依赖的 prompt response。

### 3.4 Prompt Sensitivity Index

PSI 只能作为多个主要指标绝对标准化效应的描述性摘要，不能替代 metric-level results，也不能解释为百分比。

值得讨论的模式：

- GPT-4.1：Horizon uncertainty emphasis PSI=0.94；IGT instruction specificity 和 reward/loss emphasis 分别为 0.79 和 0.90；BART role framing 为 0.68。
- GPT-5.4：Horizon 三个 PSI 均较低（0.20–0.25）；IGT reward/loss emphasis 为 0.85；BART role framing 为 1.06。
- GPT-5.4 Mini：BART instruction specificity 和 risk emphasis 分别为 1.41 和 1.42，是全套结果中最突出的综合敏感性；Horizon role framing 为 0.87。

总体上，PSI 支持“敏感性取决于模型、任务和 prompt 类型”，不支持按模型规模建立单一稳定性排名。最终结论仍需等待 PSI model-difference uncertainty 和 leave-one-metric-out robustness。

### 3.5 Human-reference comparison

必须分别回答 human proximity、prompt stability 和 task performance，不能将三者合并为“哪个模型最好”。

- GPT-4.1：Horizon directed exploration 的最佳条件几乎与人类均值重合（baseline signed distance=-0.02 human SD）；BART 的 pump/explosion 指标也总体较接近人类。IGT advantageous-choice rate 即使在最近的 condition 下仍高于人类约 2.07 SD。
- GPT-5.4：Horizon directed exploration 尚接近人类（最佳约 -0.44 SD），但 random exploration 最佳仍约低 1.32 SD。IGT advantageous choice 最佳仍约高 2.24 SD。BART 三个主要指标的最佳距离约为 1.26–1.82 human SD，不能因为部分 run 落入宽 reference interval 就称为均值接近。
- GPT-5.4 Mini：三个任务的最佳 human-SD distances 多数仍约为 1–2 SD；IGT advantageous choice 最佳约高 1.97 SD，Horizon random exploration 最佳约低 1.30 SD。BART 虽有较高 run coverage，但均值距离仍约 1.07–1.30 SD，说明 coverage 和 mean proximity 可以给出不同印象。

跨模型最重要的描述性结论是：更强/更新的模型没有自动更接近人类。尤其 IGT 的 advantageous-choice rate 在三个模型中都明显高于人类，提示可能存在过度一致、过度最优化或 ceiling behaviour。该结果支持行为分布失配，但不能单独证明其认知机制。

### 3.6 Robustness and task dynamics

最终 Results 还必须报告：

- Horizon random-exploration hierarchical refit 对 `run_effect_sd` 的敏感性；
- leave-one-metric-out PSI，确认综合结论是否由单个大效应驱动；
- mean-based 与 median-based summaries；
- ceiling/floor、低 baseline variance 和 raw-versus-standardised effect 对照；
- IGT learning curves、Horizon exploration decomposition 和 BART pump/explosion dynamics；
- 若实施 multiplicity correction，必须预先冻结 null statistic、resampling scheme 和 correction family。

## 4. Discussion 应围绕的五条主线

### 主线 A：不存在跨任务一致的“最稳定模型”

GPT-5.4 在 Horizon 上明显比 GPT-4.1 稳定，但在 IGT 的 advantageous choice 和 BART 的 role framing 下仍有清楚反应。Mini 在 IGT 的 raw changes 较小，却在 BART 中表现出极强且方向相反的 prompt effects。因此模型版本或规模不能单独预测行为稳定性。

### 主线 B：Prompt sensitivity 是 task × prompt × model 的交互属性

任务特定强调并不总产生最大影响：GPT-4.1 对 Horizon uncertainty emphasis 很敏感，GPT-5.4 对 BART role framing 更敏感，Mini 则对 BART instruction specificity 和 risk emphasis 都高度敏感。这说明提示中的哪些语义线索会支配决策，取决于模型与任务表征的组合。

### 主线 C：标准化“大效应”不一定等于大的行为改变

Mini 的 IGT 结果是核心例子：不到 2 个百分点的 raw change 可对应约 0.65–1.06 的 g，原因是行为集中、方差很低。相反，Horizon random exploration 的 raw differences 可以较大，但区间很宽。论文应把 raw magnitude、standardised magnitude 和 uncertainty 分开解释。

### 主线 D：稳定、任务表现和 human similarity 相互分离

GPT-5.4 在 Horizon 上较稳定，但这不意味着它在所有 Horizon 指标上最接近人类；三个模型在 IGT 都可能表现出更高 advantageous choice，却比人类更远；Mini 的 BART prompts 可大幅改变任务行为，但改变方向未必更 human-like。可靠的 cognitive model 不能只以高收益或表面 human-likeness定义。

### 主线 E：对 synthetic-participant 方法的影响

单一 prompt、单次运行或只报告平均 performance 都可能低估模型的不稳定性。若把 LLM 用作 cognitive model 或 synthetic participant，最低要求应包括多个 meaning-preserving prompts、重复 stochastic runs、任务级而非单一总分分析，以及 human-reference distribution comparison。

## 5. 暂时不能写成定论的事项

- 不能宣称 GPT-5.4 或 Mini “总体显著更稳定”，因为任务和 prompt 的方向不一致，且最终三模型 PSI-difference uncertainty 尚未冻结。
- 不能仅凭 CI 是否跨 0 排名模型；应报告 effect magnitude 和 interval width。
- 不能把正向 effect 自动解释为 improvement。
- 不能把人类 reference interval coverage 当作均值接近，更不能当作相同认知机制的证据。
- 不能把 PSI=0.2 解释为 20% change，也不能机械套用所有单指标的 Cohen thresholds。
- 不能根据当前结果事后更换 primary metrics、删除极端但有效的 runs 或选择有利的 prompt conditions。

## 6. 推荐的 Results 写作顺序

1. 数据完整性和 response validity；
2. 三模型 baseline profiles、dispersion 及 ceiling/floor；
3. 按任务报告 within-model prompt effects；
4. 报告 GPT-5.4/Mini 相对 GPT-4.1 的 interaction contrasts；
5. 用 PSI 总结，但立即回到驱动 PSI 的具体 metrics；
6. 分别报告三模型的 human-SD distance 和 coverage；
7. 报告 robustness、task dynamics 和限制；
8. Discussion 再综合稳定性、performance 与 human similarity 的分离。

每个关键结果统一回答四个问题：原始行为改变多少、标准化后有多大、估计有多确定、在该任务中意味着什么。
