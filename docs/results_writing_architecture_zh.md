# Results 写作结构（定稿前模板）

建议在 `Results and Discussion` 下明确分开 Results 与 Discussion。Results 按 RQ 组织，并保持逐任务、逐指标分析；Discussion 再解释机制、外部效度与文献关系。

## 推荐章节树

1. Analysis Sample, Data Quality, and Model Diagnostics
2. RQ1: Within-Model Prompt Sensitivity
   - Horizon Task
   - Iowa Gambling Task
   - Balloon Analogue Risk Task
   - Supplementary PSI Summary
3. RQ2: Cross-Model Variation in Prompt Effects
4. RQ3: Cross-Language Variation
   - Neutral-Baseline Language Contrasts
   - Language-by-Prompt Contrasts
5. RQ4: Descriptive Human-Reference Sensitivity
   - Human-Standardised Mean Position
   - Absolute-Distance and Empirical-Coverage Changes
6. Robustness and Sensitivity Analyses
7. Summary of Empirical Findings

## 主文最小表图

- Table 1：attempted、invalid、repaired、valid runs，各 cell 的有效 \(n\)，BART eligible observations 和 Random-exploration fit diagnostics。
- Figure 1：RQ1 的三任务分面 raw prompt effects 与 bootstrap 95% CI；不同指标保持自己的原始单位。
- Figure 2：以 GPT-5.4 为参照的两组 model-by-prompt raw contrasts。
- Figure 3：RQ3 的 Neutral baseline language contrasts 与 language-by-prompt contrasts。
- Figure 4：RQ4 的 \(\Delta^{abs}\) 和 \(\Delta C\)，两者分面且不共用数值轴。

完整 cell descriptives、Hedges' \(g\)、PSI、human-reference cell summaries、Random-exploration diagnostics、shrinkage sensitivity 和 bootstrap diagnostics 放入附录。

## 报告原则

- RQ1 以 raw condition-minus-Neutral difference 和 bootstrap interval 为主，Hedges' \(g\) 为辅助。
- RQ2、RQ3 报告预先规定的 raw interaction contrasts；不称为因果 difference-in-differences。
- PSI 仅表示同一任务内多指标的 formulation sensitivity，不是能力、表现或模型排名。
- `directed_exploration` 字段在正文称为 information-seeking choice rate，不等同于经典 directed exploration。
- Random exploration 是 model-derived、partially pooled estimate；正值只表示 H6 的 estimated choice variability 高于 H1。
- signed \(D\) 不是“距离”或 Cohen's \(d\)；无方向距离是 \(|D|\)。Empirical human interval 不是 human mean 的置信区间或规范范围。
- 指标方向不自动代表表现改善；不跨任务平均 raw effects，不构造总体决策能力得分。
- 英文 GPT-4.1 的共享样本只描述一次，不称为独立 replication。

## Results 与 Discussion 的边界

Results 只报告样本、质量、估计值、区间、方向、幅度、跨指标模式与稳健性。Prompt 可能改变策略的原因、模型训练或语言覆盖的解释、与既有文献的比较、机制推断、局限和未来工作均放在 Discussion。

