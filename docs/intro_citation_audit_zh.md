# Introduction 文献逐篇审查

审查日期：2026-08-08  
审查范围：`final_revision_all.md` 的 Introduction；逐项核对论文身份、出版状态、原文所支持的主张，以及该文献在当前句子中的适配度。

> 结构调整说明：完成逐篇审查后，Introduction 已进一步精简为 15 篇独立文献；Lu et al. (2022)、Pezeshkpour and Hruschka (2024)、Razavi et al. (2025) 和 Zhang et al. (2023) 已移至 Background and Related Work。Sclar et al. (2024) 同时作为 Intro 研究缺口的直接依据，并在 Background 展开讨论。Background 当前包含 30 篇独立文献。

## 总体结论

逐篇适配性审查覆盖了原 Introduction 的 19 篇文献；进一步按章节功能精简后，Introduction 保留 15 篇，其他合适但论述较细的来源转入 Background。原稿中的实质性问题已经修正：

1. `Hagendorff et al. (2023)` 存在同年文献身份混淆风险，实证结果现明确写为 `Hagendorff, Fabi and Kosinski (2023)`；machine psychology 的概念性文献留在 Background。
2. `Binz and Schulz (2023b)` 研究的是通过微调把 LLM 转化为认知模型，不直接证明 prompt robustness，已从相应 Intro 句子移除。
3. `Toplak et al. (2010)` 是 IGT 构念与临床解释综述，并非任务原始来源，已从 Intro 的任务定义句移除；其更适合保留在 Background。
4. 多语言文献支持的是跨语言、跨任务表现不均衡，不能直接证明本研究各行为指标的“response distributions”必然不同；正文已收窄措辞。

当前最大遗留问题不是引文适配，而是正文的 `Bibliography` 仍为空。定稿前必须补全以下全部条目的参考文献记录，并确保作者—年份消歧一致。

## 逐篇审查

| Intro 引文 | 核对结果与当前用途 | 结论 | 处理建议 |
|---|---|---|---|
| Argyle et al. (2023) | *Out of One, Many*，*Political Analysis*。以条件化 persona 模拟人类样本，直接支持“模拟不同特征的受访者”。 | 合适 | 保留；不要延伸为 LLM 可替代真实人类样本。DOI: [10.1017/pan.2023.2](https://doi.org/10.1017/pan.2023.2) |
| Aher et al. (2023) | *Using Large Language Models to Simulate Multiple Humans and Replicate Human Subject Studies*，ICML/PMLR。直接支持复现若干人类实验，同时论文也报告复制失真。 | 合适 | 保留，并维持“复现经典实验结果”的审慎表述。来源：[PMLR](https://proceedings.mlr.press/v202/aher23a.html) |
| Horton (2023) | *Large Language Models as Simulated Economic Agents: What Can We Learn from Homo Silicus?*，NBER Working Paper 31122。支持将 LLM 作为模拟经济主体。 | 合适但属工作论文 | 保留；参考文献表须标明 NBER Working Paper。DOI: [10.3386/w31122](https://doi.org/10.3386/w31122) |
| Binz and Schulz (2023a) | *Using cognitive psychology to understand GPT-3*，PNAS。用经典认知任务分析 GPT-3 的决策与推理规律，也显示任务变体会改变表现。 | 很合适 | 保留。DOI: [10.1073/pnas.2218523120](https://doi.org/10.1073/pnas.2218523120) |
| Hagendorff, Fabi and Kosinski (2023) | *Human-like intuitive behavior and reasoning biases emerged in large language models but disappeared in ChatGPT*，*Nature Computational Science*。是认知偏差的实证研究。 | 很合适 | 已用三位作者全称与同年概念文献消歧。DOI: [10.1038/s43588-023-00527-x](https://doi.org/10.1038/s43588-023-00527-x) |
| Shanahan, McDonell and Reynolds (2023) | *Role play with large language models*，Nature。论证 LLM 的 persona/role-play 输出不应被简单归因为人类式内在机制。 | 很合适 | 保留在“行为相似不等于机制相同”的句子；不把它当作定量 prompt-sensitivity 证据。DOI: [10.1038/s41586-023-06647-8](https://doi.org/10.1038/s41586-023-06647-8) |
| Loya, Sinha and Futrell (2023) | *Exploring the Sensitivity of LLMs’ Decision-Making Capabilities*，Findings of EMNLP。研究 prompt variations、temperature 与决策，且包含 Horizon Task。 | 核心文献 | 必须保留；它是与本研究最接近的先例，但研究范围仍不足以覆盖当前完整设计。DOI: [10.18653/v1/2023.findings-emnlp.241](https://doi.org/10.18653/v1/2023.findings-emnlp.241) |
| Sclar et al. (2024) | *Quantifying Language Models’ Sensitivity to Spurious Features in Prompt Design...*，ICLR。直接展示 few-shot prompt 格式特征导致显著表现波动。 | 合适 | 用于 Intro 的研究缺口，并在 Background 展开；证据范围限定为 prompt formatting/few-shot benchmark。来源：[OpenReview](https://openreview.net/forum?id=RIu5lyNXjT) |
| Lu et al. (2022) | *Fantastically Ordered Prompts and Where to Find Them*，ACL。研究 few-shot demonstrations 的顺序敏感性。 | 合适且范围明确 | 保留在“demonstration order”论述，不用于泛化证明所有措辞效应。DOI: [10.18653/v1/2022.acl-long.556](https://doi.org/10.18653/v1/2022.acl-long.556) |
| Pezeshkpour and Hruschka (2024) | *Large Language Models Sensitivity to the Order of Options in Multiple-Choice Questions*，Findings of NAACL。直接支持选项顺序效应。 | 合适 | 保留；明确其对象是 MCQ，而非连续行为任务。DOI: [10.18653/v1/2024.findings-naacl.130](https://doi.org/10.18653/v1/2024.findings-naacl.130) |
| Razavi et al. (2025) | *Benchmarking Prompt Sensitivity in Large Language Models*，arXiv:2502.06065。支持轻微 prompt 变化影响 benchmark accuracy。 | 可保留，但为预印本 | 参考文献表必须标明 arXiv preprint；若学校要求尽量使用同行评审来源，可删除而不损害论证。来源：[arXiv](https://arxiv.org/abs/2502.06065) |
| Ahuja et al. (2023) | *MEGA: Multilingual Evaluation of Generative AI*，EMNLP。覆盖大量语言与任务，支持模型在不同语言上的表现不均衡。 | 很合适 | 保留；正文已避免把 benchmark 证据过度解释为行为分布证据。DOI: [10.18653/v1/2023.emnlp-main.258](https://doi.org/10.18653/v1/2023.emnlp-main.258) |
| Zhang et al. (2023) | 按当前作者年份和上下文，应为 *M3Exam: A Multilingual, Multimodal, Multilevel Benchmark for Examining Large Language Models*，arXiv:2306.05179。支持跨语言考试表现与文化知识差异。 | 内容合适，但书目信息有歧义 | 在参考文献表明确完整题名和 arXiv 身份；若实际引用的不是 M3Exam，必须改 citation key。来源：[arXiv](https://arxiv.org/abs/2306.05179) |
| Wilson et al. (2014) | *Humans use directed and random exploration to solve the explore–exploit dilemma*，JEP: General。Horizon Task 及其关键操纵的原始来源。 | 必需且准确 | 保留。DOI: [10.1037/a0038199](https://doi.org/10.1037/a0038199) |
| Bechara et al. (1994) | *Insensitivity to future consequences following damage to human prefrontal cortex*，Cognition。IGT 的原始研究。 | 必需且准确 | 保留；已删除任务定义句中非必要的 Toplak 综述。DOI: [10.1016/0010-0277(94)90018-3](https://doi.org/10.1016/0010-0277(94)90018-3) |
| Lejuez et al. (2002) | *Evaluation of a behavioral measure of risk taking: The Balloon Analogue Risk Task*，JEP: Applied。BART 的原始任务来源。 | 必需且准确 | 保留。DOI: [10.1037/1076-898X.8.2.75](https://doi.org/10.1037/1076-898X.8.2.75) |
| Steingroever et al. (2015) | *Data from 617 healthy participants performing the Iowa gambling task: A many labs collaboration*，*Journal of Open Psychology Data*。与使用的人类 IGT 数据集直接对应。 | 很合适 | 保留；这是数据来源而非任务理论依据。DOI: [10.5334/jopd.ak](https://doi.org/10.5334/jopd.ak) |
| Feng et al. (2021) | *The dynamics of explore–exploit decisions reveal a signal-to-noise mechanism for random exploration*，*Scientific Reports*。与使用的 Horizon 发布数据及 random-exploration 分析直接对应。 | 很合适 | 保留；避免暗示 60 名参与者全部由 Feng et al. 新招募。DOI: [10.1038/s41598-021-82530-8](https://doi.org/10.1038/s41598-021-82530-8) |
| Sebri et al. (2023) | *Reward-dependent dynamics and changes in risk taking in the Balloon Analogue Risk Task*，*Journal of Cognitive Psychology*。与人类 BART 参考数据直接对应。 | 很合适 | 保留；作为数据来源使用。DOI: [10.1080/20445911.2023.2181065](https://doi.org/10.1080/20445911.2023.2181065) |

## 已从 Introduction 调整出去的文献

| 文献 | 原因 | 更适合的位置 |
|---|---|---|
| Binz and Schulz (2023b), *Turning large language models into cognitive models* | 核心方法是 fine-tuning 以预测人类行为，并非当前句子所说的 prompt robustness。 | Background 中关于 LLM cognitive modelling 的方法路线。来源：[arXiv](https://arxiv.org/abs/2306.03917) |
| Toplak et al. (2010), *Decision-making and cognitive abilities: A review of associations between Iowa Gambling Task performance...* | 是 IGT 构念/临床关联综述，不是任务来源；放在 Intro 的三任务定义句会显得证据功能重复。 | Background 的 IGT 构念效度与解释限制。DOI: [10.1016/j.cpr.2010.04.002](https://doi.org/10.1016/j.cpr.2010.04.002) |

## 定稿前必须完成

1. 补全 `Bibliography`，并统一采用学校要求的参考文献格式。
2. 将两篇同为 2023 年的 Hagendorff 文献设置为可明确区分的 citation keys；不要只依赖自动生成的 `et al.`。
3. 明确 Zhang et al. (2023) 是否确为 M3Exam；当前空参考文献表无法从正文唯一确定。
4. 将 Horton (2023) 标为 NBER working paper，将 Razavi et al. (2025) 与 Zhang et al. (2023) 的预印本状态如实列出。
