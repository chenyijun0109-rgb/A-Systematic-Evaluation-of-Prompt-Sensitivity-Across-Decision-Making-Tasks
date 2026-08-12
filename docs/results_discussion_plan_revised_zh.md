# Results and Discussion 具体计划书（修订版）

日期：2026-08-09  
依据：最新版 `final.md` 的 RQ 与 Method、正式数据目录、`docs/results_data_inventory_20260809.md` 及现有 `refit_v02` 输出。

| 版本 | 适用范围 | 核心分析单位 | 正式数据状态 |
|---|---|---|---|
| v2.2 | 英文三模型比较与 GPT-4.1 三语言比较 | 完整 task run；每个 model--language--task--condition cell 为20个有效 runs | 1,200个去重有效 task runs 已完成采集；部分 processed analyses 尚待生成 |

## 当前分析就绪状态

| 分析模块 | 当前状态 | 写作许可 |
|---|---|---|
| 英文三模型 RQ1 | `refit_v02` outputs 可用 | 可在冻结来源后起草 |
| RQ2 | GPT-4.1 与 GPT-5.4 的现有方向需统一；Mini−GPT-5.4 直接联合 bootstrap 缺失 | 不可定稿 |
| RQ3 | 中文与西班牙语 raw runs 完整；processed multilingual outputs 缺失 | 不可写数值结论 |
| RQ4 | 英文 cell-level long table 可用；权威 change table 与非英文 outputs 缺失 | 仅可搭结构，不可定稿 |
| Random exploration | 正式 refit diagnostics 与 shrinkage sensitivity 尚待完成 | 不可写稳健性结论 |

## 1. 核心修正

1. RQ1 不限于英文。它包括每个 model--language 内 manipulated condition 相对 Neutral 的 prompt effects；因此除英文三模型外，还必须纳入 GPT-4.1 中文和西班牙语 within-language effects。RQ3 只比较语言之间的 Neutral baseline differences 和 language-by-prompt differences。
2. RQ2 必须以 GPT-5.4 为共同参照，直接估计 `GPT-4.1 - GPT-5.4` 和 `GPT-5.4 Mini - GPT-5.4`。现有 Mini−GPT-4.1 文件不能替代后者，两个独立区间也不能相减拼接。
3. RQ4 保持 supplementary/descriptive 定位，只报告 point estimates。术语统一为 `signed human-SD-scaled mean deviation`、`absolute human-SD-scaled mean deviation`、empirical interval coverage、\(\Delta^{abs}\) 和 \(\Delta C\)。
4. PSI 只作补充性同任务多指标摘要，不作为主要结果、能力指标或模型排名。
5. Random exploration 是 hierarchical model-derived、partially pooled estimate。必须单独报告 refit success、failed fits 和 shrinkage sensitivity，不能按普通直接观察比例处理。
6. Table 1 只报告样本流与技术质量；Random-exploration 详细诊断移入附录。

## 2. 写作前必须完成的分析

### P0：阻塞 Results 定稿

1. 冻结三语言 run-level 汇总。
   - 英文输入：`E:\UoE\IPP\project\outputs\processed\formal_v01\llm_run_metrics.csv`
   - 中文 raw：`E:\UoE\IPP\project\outputs\formal_multilingual_v01\gpt-4.1-zh-CN-20run-v01`
   - 西班牙语 raw：`E:\UoE\IPP\project\outputs\formal_multilingual_v01\gpt-4.1-es-20run-v01`
   - 使用修正后的 Horizon tie-exclusion rule；确认每个 language--task--condition cell 为20个有效 runs。
2. 生成中文和西班牙语的 `metric_summary.csv`、`prompt_effects.csv`、`prompt_sensitivity.csv` 与质量报告，完成 RQ1。
3. 以 GPT-5.4 为共同参照直接联合 bootstrap，生成两组 RQ2 contrasts。
4. 生成 RQ3 的16项 Neutral-baseline language contrasts、48项 language-by-prompt contrasts，以及 valid/failed bootstrap diagnostics。
5. 完成 Random exploration 的 SD=0.5 正式拟合和 SD=0.25、1.0 sensitivity；保存 condition estimates、partially pooled run estimates、optimizer status、requested/valid/failed refits。
6. 在 RQ4 前验证 human 与 LLM Random exploration 的 choice model、编码、H1/H6 方向、priors、MAP optimizer、partial-pooling level 和 shrinkage grid 完全一致；若不能对齐，则从正式 human-SD-scaled comparison 中排除或降为不可直接比较的 exploratory result。
7. 从最新英文 long table生成权威 \(\Delta^{abs}\)/\(\Delta C\) 表，并生成中文、西班牙语 human-reference outputs。
8. 冻结统一结果包：manifest、source hashes、分析版本、quality summary、逐RQ完成清单和表图输入。

### 统一 bootstrap 重采样规则

- 所有主要 prompt effects、Hedges' \(g\)、model-by-prompt contrasts、language baseline contrasts、language-by-prompt contrasts 和 PSI 使用2,000次 percentile-bootstrap replicates；固定 bootstrap seed 为20260615。
- Horizon Task 与 BART 按 matched task-environment seed blocks 联合重采样，保留被比较的 model--prompt 或 language--prompt cells 之间共享的环境结构。
- IGT 的 payoff schedule 固定，同一 seed 不构成可用于配对的共同随机环境；因此在每个相关 cell 内独立重采样完整 runs。
- Model-by-prompt 和 language-by-prompt contrasts 必须在同一个 bootstrap replicate 内，从该 replicate 的全部相关 cells 联合计算；不得用两个独立区间相减构造 interaction interval。
- Horizon Random exploration 在每个相关 replicate 中以完整 run 为 cluster 重新拟合层级 logistic choice model；不得直接重采样最终拟合产生的固定 estimates。
- 每项输出记录 requested、valid 和 failed replicates；percentile 95% CI 由有效 replicate estimates 的第2.5和第97.5百分位数构成。对每个拟报告 interval 分别计算 \(p_{\mathrm{valid}}=B_{\mathrm{valid}}/B_{\mathrm{requested}}\)：\(p_{\mathrm{valid}}\geq0.95\) 时正式报告；\(0.90\leq p_{\mathrm{valid}}<0.95\) 时报告并添加稳定性警告、检查失败机制；\(p_{\mathrm{valid}}<0.90\) 时不作为正式区间。不得依据已观察区间选择性追加 replicates。

### P1：提交前完成

- low-/zero-variance cell audit；
- BART post-explosion eligible \(n\)；
- GPT-5.4 Mini parser retry 披露；
- standardised-effect valid replicate 数；
- 图表与源 CSV 的自动核对；
- appendix diagnostics 和完整 cell descriptives。

## 主要行为指标与分析单位

| Task | 正文指标名称 | 操作性含义 | 分析单位与解释边界 |
|---|---|---|---|
| Horizon | Information-seeking choice rate | 不等信息条件下第一次自由选择时选择较少观察选项的比例；代码字段为 `directed_exploration` | 直接计算的 run-level summary；不等同于经典 horizon-dependent directed exploration |
| Horizon | Horizon-related exploration change | 每局仅使用第一次自由选择；在 equal- 与 unequal-information games 中，将选择该次选择前观察均值较低的选项记为 exploratory choice；观察均值相等的 choices 从分子和分母中排除；分别计算 H6 与 H1 的 eligible-choice proportions，并取 H6−H1 | 直接计算的 run-level summary；正值表示 H6 下这种 value-based exploratory choice 比例较高；不是 information-seeking choice rate 的 horizon difference；某一 horizon 无 eligible choice 时该 run 的指标不可计算 |
| Horizon | Random exploration effect | H6 与 H1 的估计 choice variability 之差 | 层级 choice model 产生的 condition-level 与 partially pooled run estimates；正值仅表示 H6 的估计 choice variability 更高 |
| IGT | Advantageous choice rate | C/D 牌组选择比例 | 直接计算的 run-level summary；描述长期选择分配 |
| IGT | Post-loss switching rate | signed loss component 小于0后，下一 trial 更换牌组的比例 | 直接计算的 run-level summary；较高值不自动代表更好的学习 |
| BART | Adjusted average pumps | 未爆炸气球的平均 pumps | 直接计算的 run-level summary；不作为单一规范性风险指标 |
| BART | Explosion rate | 爆炸气球比例 | 直接计算的 run-level summary；同时受选择和任务随机结果影响 |
| BART | Post-explosion adjustment | 爆炸后下一气球 pumps 相对前一气球的变化 | 仅在存在 eligible transition 时计算；描述反馈后的行为调整 |

## 3. 最终章节树

### Results

1. Analysis Sample and Technical Quality
2. RQ1 -- Within-Model Prompt Sensitivity
   - English comparison across three models
   - GPT-4.1 within-language effects in English, Chinese and Spanish
   - Supplementary PSI pattern
3. RQ2 -- Cross-Model Variation in Prompt Effects
4. RQ3 -- Cross-Language Variation
   - Neutral-baseline language contrasts
   - Language-by-prompt interaction contrasts
5. RQ4 -- Descriptive Human-Reference Sensitivity
   - Baseline human-relative position
   - Changes in absolute human-SD-scaled deviation
   - Changes in empirical coverage
6. Robustness and Diagnostic Checks
7. Descriptive Synthesis

### Discussion

1. Principal Findings
2. Prompt Formulation and Model/Language Variation
3. Task-Specific Interpretation
4. Human-Reference Interpretation
5. Reliability, Limitations and Generalisability
6. Future Work and Conclusion

## 4. 各 Results 小节的执行规格

### 4.1 Analysis Sample and Technical Quality

- 输入：最终三模型/三语言 run metrics、aggregation reports、run logs、Mini retry record、BART eligibility。
- 主文 Table 1：planned、valid、technical failures、repaired、每cell \(n\)。
- 段落：总样本与共享英文计数；cell completeness；invalid/repair；BART eligibility；RE拟合质量一句总结。
- 完成标准：1,200个 runs 的去重逻辑可复核；英文 GPT-4.1 只计一次；不把技术有效性称为行为可靠性。

### 4.2 RQ1

主要 estimand：

\[
\Delta_{m,\ell,t,c,k}
=\bar Y_{m,\ell,t,c,k}-\bar Y_{m,\ell,t,0,k}.
\]

- 主报 raw difference 与 percentile-bootstrap 95% CI；Hedges' \(g\) 为辅助。
- 先报告英文三模型，再报告 GPT-4.1 三语言内 effects。
- Horizon 三指标、IGT 两指标、BART 三指标分别解释；`directed_exploration` 在正文称 information-seeking choice rate。
- Figure 1：英文三模型按任务分面的 raw effects；不同原始单位不共用数轴。
- Figure 1 的每个 metric 使用独立横轴，并明确显示 raw difference 与 bootstrap 95% CI。比例指标、pumps 和 estimated choice variability 不共享尺度；Hedges' \(g\) 不与 raw differences 放在同一坐标轴。
- 非英文 within-language effects 与 Figure 3 协调展示或放附图，避免 Figure 1 过载。
- PSI 正文最多一段，完整表及 CI 入附录。
- Hedges' \(g\) 使用 manipulated 与 Neutral 两组 run-level distributions 的 pooled SD，并应用基于两组总自由度的小样本修正 \(J\)。若两组均为同一个常数，则 raw difference 为0、\(g=\mathrm{NA}\)，并标记 `constant_equal`；若两组各自为常数但常数不同，则保留 raw difference、\(g=\mathrm{NA}\)，并标记 `constant_unequal`。Bootstrap 中每个 pooled SD 为0的 \(g\) replicate 必须计入 invalid-replicate diagnostics，不得以0替代；raw contrast 始终保留为主要结果。
- 正文提供紧凑的 Neutral-baseline mean (SD) 表，或在相应任务小节引用附录中的完整 raw cell-means figure，使 contrasts 始终可结合原始行为位置解释。

### 4.3 RQ2

\[
I^{M}_{m,c,t,k}
=\Delta_{m,\mathrm{en},t,c,k}
-\Delta_{\mathrm{GPT\mbox{-}5.4},\mathrm{en},t,c,k}.
\]

- 输入：新生成的 GPT-5.4-reference joint-bootstrap contrasts。
- Figure 2：`GPT-4.1 - GPT-5.4` 与 `Mini - GPT-5.4` 两个 panels。
- 按 Horizon、IGT、BART 报告，不进行跨任务 omnibus average。
- 标题、图例、CSV字段和正文方向必须完全一致。

### 4.4 RQ3

Neutral baseline：

\[
B_{\ell,t,k}
=\bar Y_{\mathrm{GPT\mbox{-}4.1},\ell,t,0,k}
-\bar Y_{\mathrm{GPT\mbox{-}4.1},\mathrm{en},t,0,k}.
\]

Language-by-prompt：

\[
I^{L}_{\ell,c,t,k}
=\Delta_{\mathrm{GPT\mbox{-}4.1},\ell,t,c,k}
-\Delta_{\mathrm{GPT\mbox{-}4.1},\mathrm{en},t,c,k}.
\]

- Figure 3A：中文−英文、西班牙语−英文 baseline contrasts。
- Figure 3B：对应 language-by-prompt contrasts。
- 先区分 baseline variation 与 sensitivity variation，再描述跨任务模式。
- 只称 language-associated differences；不是语言人群差异或“语言本身”的因果效应。

### 4.5 RQ4

\[
D=\frac{\bar Y_{\mathrm{LLM}}-\bar Y_{\mathrm{human}}}{s_{\mathrm{human}}},
\qquad |D|,
\]

\[
\Delta^{abs}=|D|_c-|D|_0,
\qquad \Delta C=C_c-C_0.
\]

- 先描述 Neutral 的 human-relative position，再报告 \(\Delta^{abs}\) 和 \(\Delta C\)。
- Figure 4A 为 \(\Delta^{abs}\)，Figure 4B 为 \(\Delta C\)；不共用数轴。
- signed \(D\) 和完整 cell positions 入附录或紧凑表。
- 不称 Cohen's \(d\)、standardised mean difference、effect size、normative interval 或 confidence interval。
- 不进行显著性判断，不从 coverage 推断机制相同或“更像人类”。
- RQ4 不附 inferential interval，因为该分析将选定的人类数据集作为固定的描述性参照，不尝试进行 population-level equivalence inference。Discussion 同时承认 human mean、SD 和经验分位数本身来自有限样本，当前 point estimates 未传播这部分 sampling uncertainty。

### 4.6 Robustness and Diagnostic Checks

- 正文仅一段或极简表：RE shrinkage、refit成功率、low/zero variance、raw与standardised estimates的一致性。
- 详细结果全部入附录。
- raw estimand为首要解释；若 \(g\) 因低SD而放大，必须同时报告raw幅度。

### 4.7 Descriptive Synthesis

- 最多一段，依次用一句回答 RQ1--RQ4 的观察模式。
- 不引文、不解释机制、不重复全部数值。

## 5. Discussion 段落逻辑

1. **Principal findings**：逐RQ概括最重要发现，不重复数表。
2. **Prompt formulation and model/language variation**：解释 prompt 为何属于测量程序；区分有意义的 construct manipulation 与无关表述波动；讨论 model-specific 和 language-associated patterns，但不归因于架构、规模或语言人群心理差异。
3. **Task-specific interpretation**：分 Horizon、IGT、BART 解释，不构造总体决策能力。
4. **Human-reference interpretation**：解释 human proximity 不是表现、等价性或共同机制证据，并讨论固定人类样本参照的边界。
5. **Reliability, limitations and generalisability**：集中讨论服务漂移、task-environment seeds 与不可控的专有API内部采样状态、翻译等价、run非人类个体、cell \(n=20\)、RE模型依赖及 multiple contrasts，避免与独立 limitations 小节重复。
6. **Future work and conclusion**：提出预注册、多snapshot复现、更多语言/任务、独立prompt审计和开放模型验证，并仅总结最终结果直接支持的贡献。

## 6. Results 与 Discussion 的边界

Results 只写：样本与技术质量、point estimates、CI、方向、幅度、区间宽度、相似方向的 effects 是否在相关指标、prompt conditions、models 或 tasks 中再次出现，以及 sensitivity analysis 是否改变描述性结论。

Discussion 才写：可能原因、规则表征或角色语境、训练与语言覆盖、与文献的一致或冲突、机制假说、外部效度、局限和未来工作。

Results 禁止出现 `because`、`proves`、`demonstrates a cognitive strategy` 等机制或因果措辞。

本研究以估计为中心，不对 bootstrap intervals 进行 family-wise multiplicity adjustment，也不依据某一个未经校正的区间是否排除0作实质性结论。解释应同时考虑预设 raw contrasts、效应幅度、区间宽度，以及相关指标和任务中是否出现可重复的描述性模式。中文正文避免以“显著／不显著”作为主要判断。

## 7. 主文与附录分流

主文：Table 1；Figures 1--4；紧凑的 Neutral-baseline mean (SD) 表；每RQ关键 raw contrasts 与 CI；RQ4 的主要 \(\Delta^{abs}\)/\(\Delta C\)；一段 robustness summary。

附录：所有 cell descriptives 与完整 raw cell-means figure；完整 Hedges' \(g\)；完整 PSI；signed \(D\)、\(|D|\)、coverage；RE参数、condition/run estimates、convergence、failed refits；三种 shrinkage；bootstrap diagnostics；low/zero variance；missingness；prompt length/token audit 和 provenance。

## 8. 当前不可写的内容

- 中文和西班牙语 RQ1 数值；
- 全部 RQ3 结论；
- Mini−GPT-5.4 的直接 interaction interval；
- 最终 GPT-5.4-reference RQ2 表；
- RE convergence、failed refits 和 shrinkage结论；
- 中文、西班牙语 human-reference结果；
- 最终 \(\Delta^{abs}\) 和 \(\Delta C\) 表；
- “跨语言稳健”“模型间一致”“更接近人类”等总体结论；
- 任何旧图、旧pairwise或non-refit数值。

## 9. 最终验收清单

- [ ] RQ1覆盖所有预设 model--language 内 prompt effects。
- [ ] RQ1 保持为所有预设 model--language cells 内的 prompt effects；RQ3 仅承担语言间 baseline 和 prompt-effect contrasts。该分工与 Introduction 的一般性 RQ1 及 Method 的 within-language analysis 范围保持一致。
- [ ] RQ2两组 contrasts 均为 target model minus GPT-5.4。
- [ ] RQ3的16项 baseline 与48项 interaction 齐全。
- [ ] RQ4始终保持 descriptive/supplementary 定位。
- [ ] Random exploration 每个 bootstrap replicate 重新拟合层级模型。
- [ ] Horizon/BART 使用 matched environment-seed blocks；IGT 使用 independent-cell run bootstrap；所有 interaction contrasts 在同一 replicate 内联合计算。
- [ ] RE convergence、failed refits 和三种 shrinkage 均报告。
- [ ] PSI 未被解释为能力、表现、人类相似性或模型排名。
- [ ] raw effect 为主要量，Hedges' \(g\) 为辅助。
- [ ] 未使用“显著/不显著”作为主要判断。
- [ ] 未将单个未经 multiplicity adjustment 的 CI 当作强证据。
- [ ] `signed human-SD-scaled mean deviation` 术语统一；signed \(D\) 不称 distance。
- [ ] empirical human interval 不称 confidence、normal 或 normative interval。
- [ ] 不跨任务平均 raw effects，不构造总体能力分数。
- [ ] 图、表和正文数字均可追溯到冻结结果包。
- [ ] Results 不含机制解释；Discussion 不补造未完成结果。
- [ ] Introduction 的 results-achieved 段只在最终结果冻结后填写。

## 10. 建议篇幅

| 部分 | 建议页数 | 内容重点 |
|---|---:|---|
| Results | 5--6页 | 数据质量约0.5页；RQ1与RQ2约3页；RQ3、RQ4及robustness约1.5--2.5页 |
| Discussion | 5--6页 | 主要发现约1页；方法学、模型、语言、任务和人类参照解释约2.5--3页；局限、未来工作和结论约1.5--2页 |
