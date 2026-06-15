# Citation Map

这个文件用于记录“项目中哪里需要引用哪篇文献 / 数据集 / 方法依据”。它不是最终参考文献列表，而是 dissertation 写作前的引用追踪表。

## 使用规则

每当后续工作中使用了文献、数据集、方法依据或 pilot evidence，都要在这里登记。目标是让每个设计选择都能追踪到依据。

## 记录模板

```text
Citation key:
Source:
Type:
Used for:
Project location:
Dissertation section:
Claim / decision supported:
Status:
Notes:
```

## Status 标签

- `Planned`：预计需要引用，但还没有写进正文；
- `Used in design`：已经用于项目设计或代码实现；
- `Written in draft`：已经写进 dissertation draft；
- `Needs checking`：引用信息或适用性需要进一步核对；
- `Assumption to verify`：暂时缺少明确文献，需要补证据。

## Core Citation Map

### LLMs as Cognitive Models / Simulated Participants

Citation key: BinzSchulz2023PNAS

Source: Binz, M., & Schulz, E. (2023). Using cognitive psychology to understand GPT-3. Proceedings of the National Academy of Sciences.

Type: Literature

Used for:

- 支撑 LLM 可以被放入经典认知任务中进行行为评估；
- 支撑本项目使用 cognitive psychology tasks 观察 LLM behaviour。

Project location:

- Research motivation；
- Introduction；
- Literature review。

Dissertation section:

- Introduction；
- Literature Review / Background。

Claim / decision supported:

- LLMs can be examined using cognitive psychology paradigms, but behavioural interpretation requires methodological caution.

Status: Planned

Notes:

- 适合用来引出“LLMs as behavioural / cognitive research objects”。

### LLMs as Cognitive Models

Citation key: BinzSchulz2023CognitiveModels

Source: Binz, M., & Schulz, E. (2023). Turning large language models into cognitive models.

Type: Literature

Used for:

- 支撑本项目对 “LLMs as cognitive models” 的核心讨论；
- 支撑 RQ3 的理论背景。

Project location:

- Project aim；
- RQ3；
- Discussion framework。

Dissertation section:

- Introduction；
- Literature Review；
- Discussion。

Claim / decision supported:

- Whether LLMs can be treated as cognitive models depends on the stability and interpretability of their behaviour.

Status: Planned

Notes:

- 需要和 prompt sensitivity 文献一起使用，避免把 LLM behavioural similarity 直接解释成人类认知机制。

### Role Framing and Role Play

Citation key: Shanahan2023RolePlay

Source: Shanahan, M., McDonell, K., & Reynolds, L. (2023). Role play with large language models. Nature.

Type: Literature

Used for:

- 支撑 role_human prompt condition；
- 解释为什么“让模型扮演人类参与者”不是中性的措辞变化。

Project location:

- Prompt design；
- role_human condition；
- Discussion。

Dissertation section:

- Literature Review；
- Methodology / Prompt Design；
- Discussion。

Claim / decision supported:

- Role framing can shape dialogue-agent behaviour, so human-participant framing should be treated as a meaningful prompt manipulation.

Status: Planned

Notes:

- 这是 role_human condition 的关键文献之一。

### Prompt Variation in Decision-Making Tasks

Citation key: LoyaSinhaFutrell2023

Source: Loya, M., Sinha, D., & Futrell, R. (2023). Exploring the sensitivity of LLMs' decision-making capabilities: Insights from prompt variations and hyperparameters. Findings of EMNLP.

Type: Literature

Used for:

- 支撑项目核心变量 prompt sensitivity；
- 支撑在 decision-making tasks 中系统比较 prompt variation 的必要性。

Project location:

- Research motivation；
- Prompt sensitivity analysis；
- Temperature / hyperparameter limitation。

Dissertation section:

- Introduction；
- Literature Review；
- Methodology；
- Discussion / Limitations。

Claim / decision supported:

- Prompt wording and decoding settings can affect LLM decision-making behaviour.

Status: Planned

Notes:

- 是本项目最核心的 prompt sensitivity 依据之一。

### Prompt Formatting Sensitivity

Citation key: Sclar2023PromptFormatting

Source: Sclar, M., Choi, Y., Tsvetkov, Y., & Suhr, A. (2023). Quantifying language models' sensitivity to spurious features in prompt design.

Type: Literature

Used for:

- 支撑 prompt sensitivity 不只是语义内容变化，也可能来自格式变化；
- 解释为什么本项目把 prompt format 作为 controlled variable，而不是主实验变量。

Project location:

- Scope control；
- Controlled variables；
- Limitations。

Dissertation section:

- Literature Review；
- Methodology；
- Limitations / Future Work。

Claim / decision supported:

- Prompt formatting can affect LLM outputs; therefore format should be controlled when testing wording/framing effects.

Status: Planned

Notes:

- 用来说明为什么不把 format variation 放进主实验。

### Prompt Format Complexity

Citation key: He2024PromptFormatting

Source: He, J., Rungta, M., Koleczek, D., Sekhon, A., Wang, F., & Hasan, S. A. (2024). Does prompt formatting have any impact on LLM performance?

Type: Literature

Used for:

- 支撑 prompt format 可能影响 performance；
- 支撑本项目使用统一 natural-language prompt format。

Project location:

- Prompt design；
- Controlled variables。

Dissertation section:

- Literature Review；
- Methodology / Prompt Design。

Claim / decision supported:

- Structured formats may change consistency or performance, so prompt format should be held constant in this project.

Status: Planned

Notes:

- 和 Sclar et al. 一起使用。

### Prompt Sensitivity Benchmarking

Citation key: Razavi2025PromptSensitivity

Source: Razavi, A., Soltangheis, M., Arabzadeh, N., Salamat, S., Zihayat, M., & Bagheri, E. (2025). Benchmarking prompt sensitivity in large language models.

Type: Literature

Used for:

- 支撑将 prompt sensitivity 本身作为可测量对象；
- 支撑 Prompt Sensitivity Index 或相关比较框架。

Project location:

- Prompt sensitivity measurement；
- Analysis framework。

Dissertation section:

- Literature Review；
- Methodology / Statistical Analysis。

Claim / decision supported:

- Prompt sensitivity can be treated as a measurable robustness issue rather than an informal observation.

Status: Planned

Notes:

- 若使用自定义 Prompt Sensitivity Index，需要说明这是本项目的 operational measure。

### Standardised Mean Difference / Effect Size

Citation key: Cohen1988PowerAnalysis

Source: Cohen, J. (1988). Statistical Power Analysis for the Behavioral Sciences. 2nd edition. Lawrence Erlbaum Associates.

Type: Statistical method

Used for:

- 支撑使用 standardised mean difference / effect size 思路量化 prompt condition 与 baseline condition 的差异；
- 支撑不同 task metrics 量纲不同，需要标准化后比较。

Project location:

- `docs/task_details.md` section 2.4；
- Prompt Sensitivity Index operationalisation；
- Statistical analysis plan。

Dissertation section:

- Methodology / Measures；
- Methodology / Statistical Analysis。

Claim / decision supported:

- Mean differences between experimental conditions can be standardised by a standard deviation to express effect magnitude on a comparable scale.

Status: Planned

Notes:

- 本项目不是直接使用 Cohen's d 作为唯一指标，而是借用 standardised mean difference 的 effect-size logic。

### Hedges and Olkin Standardised Mean Difference

Citation key: HedgesOlkin1985MetaAnalysis

Source: Hedges, L. V., & Olkin, I. (1985). Statistical Methods for Meta-Analysis. Academic Press.

Type: Statistical method

Used for:

- 支撑 standardised mean difference 作为比较不同条件均值差异的统计方法；
- 支撑 pooled standard deviation 作为 baseline SD 不稳定时的 fallback。

Project location:

- `docs/task_details.md` section 2.4；
- Statistical analysis plan。

Dissertation section:

- Methodology / Statistical Analysis。

Claim / decision supported:

- Standardised mean differences and pooled-standard-deviation variants are established effect-size approaches for comparing condition means.

Status: Planned

Notes:

- 如果每个 prompt condition 的 run 数不同，pooled SD 应使用带样本量权重的版本。

### Glass-Type Standardisation

Citation key: Glass1976Delta

Source: Glass, G. V. (1976). Primary, secondary, and meta-analysis of research. Educational Researcher.

Type: Statistical method

Used for:

- 支撑使用 reference / control condition 的 standard deviation 作为标准化分母；
- 解释为什么本项目默认使用 baseline prompt condition 的 SD。

Project location:

- `docs/task_details.md` section 2.4；
- Prompt Sensitivity Index operationalisation。

Dissertation section:

- Methodology / Statistical Analysis。

Claim / decision supported:

- A standardised mean difference can use the control or reference condition's standard deviation as the comparison scale.

Status: Planned

Notes:

- 本项目的 baseline prompt 是 reference/control condition，因此 baseline SD 的使用应表述为 Glass-type standardisation，而不是标准 Cohen's d。

### Horizon Task

Citation key: Wilson2014HorizonTask

Source: Wilson, R. C., Geana, A., White, J. M., Ludvig, E. A., & Cohen, J. D. (2014). Humans use directed and random exploration to solve the explore-exploit dilemma. Journal of Experimental Psychology: General.

Type: Literature

Used for:

- 支撑 Horizon Task 的认知目标；
- 支撑 directed exploration 和 random exploration 指标。

Project location:

- Horizon task design；
- Horizon metrics；
- Human comparison。

Dissertation section:

- Literature Review；
- Methodology / Tasks；
- Methodology / Metrics。

Claim / decision supported:

- Horizon Task can separate directed and random exploration in exploration-exploitation decision-making.

Status: Planned

Notes:

- Horizon Task 最核心引用。

### Horizon Human Dataset

Citation key: Feng2021ExploreExploit

Source: Feng, S. F., Wang, S., Zarnescu, S., & Wilson, R. C. (2021). The dynamics of explore-exploit decisions reveal a signal-to-noise mechanism for random exploration. Scientific Reports.

Type: Literature / Dataset basis

Used for:

- 支撑 Horizon human reference data；
- 支撑 human distribution comparison。

Project location:

- Human dataset processing；
- Horizon metrics；
- Human comparison。

Dissertation section:

- Methodology / Human Datasets；
- Results / Human Comparison。

Claim / decision supported:

- Human Horizon Task data can provide reference distributions for exploration-related measures.

Status: Planned

Notes:

- 需要和本项目使用的 `DATASET/BANDIT/allHorizonData_cut.csv` 对齐。

### Iowa Gambling Task

Citation key: Bechara1994IGT

Source: Bechara, A., Damasio, A. R., Damasio, H., & Anderson, S. W. (1994). Insensitivity to future consequences following damage to human prefrontal cortex. Cognition.

Type: Literature

Used for:

- 支撑 IGT 的任务来源；
- 支撑 reward-punishment learning 和 long-term consequence interpretation。

Project location:

- IGT task design；
- IGT prompt baseline；
- IGT metrics。

Dissertation section:

- Literature Review；
- Methodology / Tasks。

Claim / decision supported:

- IGT is a classic paradigm for studying feedback-based learning and long-term outcome decision-making.

Status: Planned

Notes:

- IGT 任务来源核心引用。

### IGT Review and Metrics

Citation key: Toplak2010IGTReview

Source: Toplak, M. E., Sorge, G. B., Benoit, A., West, R. F., & Stanovich, K. E. (2010). Decision-making and cognitive abilities: A review of associations between Iowa Gambling Task performance, executive functions, and intelligence. Clinical Psychology Review.

Type: Literature

Used for:

- 支撑 IGT behavioural interpretation；
- 支撑 net score、advantageous choice 等分析指标。

Project location:

- IGT metrics；
- Discussion。

Dissertation section:

- Literature Review；
- Methodology / Metrics；
- Discussion。

Claim / decision supported:

- IGT performance is commonly interpreted through advantageous/disadvantageous choices and learning across trials.

Status: Planned

Notes:

- 可用于说明 IGT 指标的解释边界。

### IGT Human Dataset

Citation key: Steingroever2015IGTData

Source: Steingroever, H., Wetzels, R., Horstmann, A., Neumann, J., & Wagenmakers, E.-J. (2015). Data from 617 healthy participants performing the Iowa Gambling Task: A many labs collaboration. Journal of Open Psychology Data.

Type: Dataset

Used for:

- 支撑 IGT human reference dataset；
- 支撑 participant-level human comparison。

Project location:

- Human dataset processing；
- IGT human comparison。

Dissertation section:

- Methodology / Human Datasets；
- Results / Human Comparison。

Claim / decision supported:

- The IGT human dataset provides participant-level reference behaviour for comparison with LLM runs.

Status: Planned

Notes:

- 对应本项目 `DATASET/IGT/IGTdataSteingroever2014`。

### BART

Citation key: Lejuez2002BART

Source: Lejuez, C. W., Read, J. P., Kahler, C. W., Richards, J. B., Ramsey, S. E., Stuart, G. L., Strong, D. R., & Brown, R. A. (2002). Evaluation of a behavioral measure of risk taking: The Balloon Analogue Risk Task. Journal of Experimental Psychology: Applied.

Type: Literature

Used for:

- 支撑 BART 任务来源；
- 支撑 pump / cash-out / explosion 风险结构。

Project location:

- BART task design；
- BART prompt baseline；
- BART metrics。

Dissertation section:

- Literature Review；
- Methodology / Tasks。

Claim / decision supported:

- BART is a behavioural measure of risk-taking based on repeated reward-risk decisions.

Status: Planned

Notes:

- BART 任务来源核心引用。

### BART and Real-World Risk Behaviour

Citation key: Lejuez2003BARTAdolescent

Source: Lejuez, C. W., Aklin, W. M., Zvolensky, M. J., & Pedulla, C. M. (2003). Evaluation of the Balloon Analogue Risk Task as a predictor of adolescent real-world risk-taking behaviours. Journal of Adolescence.

Type: Literature

Used for:

- 支撑 BART 作为 risk-taking measure 的解释；
- 支撑 Discussion 中关于风险行为指标的谨慎解释。

Project location:

- BART background；
- Discussion。

Dissertation section:

- Literature Review；
- Discussion。

Claim / decision supported:

- BART has been used as a behavioural proxy for risk-taking tendencies.

Status: Planned

Notes:

- 可作为 Lejuez 2002 的补充引用。

### BART Review

Citation key: Canning2022BARTReview

Source: Canning, J. R., Schallert, M. R., & Larimer, M. E. (2022). A systematic review of the Balloon Analogue Risk Task in alcohol research. Alcohol and Alcoholism.

Type: Literature

Used for:

- 支撑 BART 的广泛使用；
- 支撑 BART 指标和解释边界。

Project location:

- BART literature review；
- Limitations。

Dissertation section:

- Literature Review；
- Discussion / Limitations。

Claim / decision supported:

- BART is widely used, but interpretation depends on task implementation and population/context.

Status: Planned

Notes:

- 用于谨慎解释 BART human comparison。

### BART Human Dataset / Reward Dynamics

Citation key: Sebri2023BART

Source: Sebri, V., Triberti, S., Granic, G. D., & Pravettoni, G. (2023). Reward-dependent dynamics and changes in risk taking in the Balloon Analogue Risk Task. Journal of Cognitive Psychology.

Type: Literature / Dataset basis

Used for:

- 支撑 BART human reference data；
- 支撑 reward-dependent risk-taking analysis。

Project location:

- Human dataset processing；
- BART human comparison；
- BART metrics。

Dissertation section:

- Methodology / Human Datasets；
- Results / Human Comparison。

Claim / decision supported:

- BART human data can be used to examine reward-dependent changes and risk-taking measures such as adjusted pumps.

Status: Planned

Notes:

- 需要和本项目 `DATASET/BART/Dataset.xlsx` 的实际字段对齐。

## Claim-to-Citation Checklist

后续写论文或设计文档时，至少保证以下 claim 有引用：

| Claim / decision | Required citation or basis | Status |
|---|---|---|
| LLMs can be evaluated in cognitive tasks | BinzSchulz2023PNAS | Planned |
| LLMs as cognitive models require behavioural reliability | BinzSchulz2023CognitiveModels | Planned |
| Role framing can affect LLM behaviour | Shanahan2023RolePlay | Planned |
| Prompt variation affects LLM decision-making | LoyaSinhaFutrell2023 | Planned |
| Prompt format should be controlled | Sclar2023PromptFormatting; He2024PromptFormatting | Planned |
| Prompt sensitivity can be measured | Razavi2025PromptSensitivity | Planned |
| Prompt sensitivity can be operationalised using standardised mean-difference logic | Cohen1988PowerAnalysis; HedgesOlkin1985MetaAnalysis; Glass1976Delta | Planned |
| Horizon Task measures exploration-exploitation | Wilson2014HorizonTask | Planned |
| Horizon human data can support comparison | Feng2021ExploreExploit | Planned |
| IGT measures feedback-based learning and long-term outcomes | Bechara1994IGT; Toplak2010IGTReview | Planned |
| IGT human reference data source | Steingroever2015IGTData | Planned |
| BART measures risk-taking | Lejuez2002BART; Lejuez2003BARTAdolescent | Planned |
| BART interpretation and limitations | Canning2022BARTReview | Planned |
| BART human reference data source | Sebri2023BART | Planned |

## Work-Step Citation Records

### 2026-05-26 - Recording and Citation Workflow

Citation key: ProjectRecordingRule2026

Source: Project-level research management rule defined by the student.

Type: Project design decision

Used for:

- Requiring every future step to be recorded;
- Requiring citation and evidence mapping for academic work.

Project location:

- `plan.md` section 19;
- `docs/research_log.md`;
- `docs/citation_map.md`.

Dissertation section:

- Not necessarily cited directly in dissertation;
- Supports reproducibility and audit trail.

Claim / decision supported:

- Every research, implementation, and analysis step must be traceable to literature, data, pilot evidence, config, or an explicitly marked project decision.

Status: Used in design

Notes:

- This is not a literature citation; it is a project governance rule.

### 2026-05-26 - Final Experiment Design Table

Citation key: FinalExperimentDesignTable2026

Historical source: the initial project-design discussion recorded in
`docs/research_log.md`

Type: Project design decision / citation mapping record

Used for:

- Fixing the first draft of the experiment matrix;
- Mapping tasks, prompt conditions, run counts, trial counts, metrics, and human datasets to literature support;
- Identifying unresolved implementation decisions before coding.

Project location:

- `docs/research_log.md` (historical project-design record);
- `plan.md` section 15;
- Phase 1 design work.

Dissertation section:

- Methodology / Overview of experimental design;
- Methodology / Tasks;
- Methodology / Behavioural metrics;
- Methodology / Human datasets.

Claim / decision supported:

- The project will compare LLM behaviour across three cognitive decision-making tasks and four prompt conditions, using task-specific behavioural metrics and human reference datasets.

Status: Used in design

Notes:

- This entry does not replace primary citations. Primary literature citations remain required for each task, prompt manipulation, and metric.
- The config file `configs/experiment_config_stage01.json` is currently empty on disk, so the design table is marked as draft and includes open decisions to verify.
