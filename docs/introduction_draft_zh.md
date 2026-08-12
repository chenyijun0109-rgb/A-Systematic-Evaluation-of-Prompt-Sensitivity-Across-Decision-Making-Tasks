# Introduction（中文版初稿）

大型语言模型（large language models, LLMs）正日益被视为不仅是语言技术工具，也是可以接受行为实验检验的研究对象。由于 LLM 能够理解自然语言指令、与实验环境连续交互并反复作出选择，研究者已开始利用它们复现经典实验结果、模拟具有不同特征的受访者，并探索心理学、行为科学和经济学中的理论问题（Argyle et al., 2023; Aher et al., 2023; Horton, 2023）。与此同时，认知任务也被用于刻画不同 GPT 模型所表现出的行为规律和推理偏差（Binz and Schulz, 2023a; Hagendorff et al., 2023）。这类研究为 LLM 提供了一种潜在的方法学角色：作为成本较低、易于重复调用的计算系统，其行为可以在受控任务操纵下接受检验。

尽管这类系统便于重复调用，一次 LLM 运行并不等同于一名人类参与者，行为上的相似性也不能单独证明二者具有相同的认知机制。LLM 的输出是以文本训练为基础、又受到指令微调、部署设置和当前语言情境共同影响的条件性样本。因此，LLM 能否作为有科学价值的认知模型，不仅取决于它能否完成任务或接近人类参考样本，还取决于当实验上无关或理论上次要的语言情境发生变化时，由其行为得出的结论能否保持稳定（Binz and Schulz, 2023b; Shanahan et al., 2023）。

Prompt 的具体表述是这一可靠性问题的核心。Prompt 不只是传递任务规则的载体；它还会界定模型所扮演的角色、突出环境中的特定信息，并规定模型应以何种方式产生回答。既有研究表明，措辞、格式、few-shot demonstrations 或选项顺序等看似细微的变化，都可能显著改变模型的任务表现和选择结果（Lu et al., 2022; Loya et al., 2023; Sclar et al., 2024; Pezeshkpour and Hruschka, 2024）。当研究要求 LLM 充当实验参与者时，角色指令尤其重要，因为这种 framing 可能诱发某种特定的模拟身份，而非揭示一种脱离语境的稳定倾向（Shanahan et al., 2023）。

因此，prompt sensitivity 不只是一个工程上的不便。在行为研究中，prompt 本身就是实验测量程序的一部分。如果两种 prompt 传达相同的任务规则和可用信息，却产生了实质不同的探索、学习或风险承担模式，那么关于模型的行为结论便可能部分反映测量工具本身，而不完全是模型在目标任务中的稳定特征。

现有研究已经充分说明 prompting 会影响模型输出，但尚未完整解决本研究所关注的行为可靠性问题。大量 LLM 评估主要关注任务准确率、总体上的人类相似性，或能否复现某一个经验效应。与此相对，prompt robustness 研究往往集中于 benchmark accuracy、few-shot 示例顺序、表面格式或孤立的单次决策（Lu et al., 2022; Sclar et al., 2024; Razavi et al., 2025）。已有决策研究发现，prompt 措辞和 decoding parameters 能够改变 LLM 的选择（Loya et al., 2023），但较少有研究系统考察：在完整的连续交互任务中，受控且基本保持语义的 prompt manipulations 是否会改变重复行为；这些效应是否因模型而异；以及更高的 prompt stability 是否同时意味着更好的任务表现或更接近人类行为分布。

这些评价维度必须加以区分。一个模型可能稳定地表现得不像人类，也可能只在某一种 prompt 下接近人类，还可能在不同 prompts 下行为变化明显，却保持相近的平均收益。因此，prompt stability、task performance 和 human similarity 是相互关联但不能彼此替代的评价标准。

语言本身构成了另一种重要的情境变化。即使不同语言的 prompts 是由同一任务翻译而来，多语言 LLM 也不必然在各语言中表现出相同的能力或反应分布。跨语言评估已经发现，LLM 在英语与其他语言之间存在表现不均衡和迁移不完全的现象（Ahuja et al., 2023; Zhang et al., 2023）。因此，仅从英文 prompts 得到的证据不能自动推广到模型在中文或西班牙语中的行为。另一方面，如果语言、模型版本、任务实现和 prompt 内容同时变化，观察到的跨语言差异也很难得到清晰解释。较为严格的比较需要固定模型与实验环境，使用在实验相关含义上匹配的 prompts，并承认受约束的翻译可以保持任务内容和操纵意图，却不能保证不同自然语言表达在所有语用维度上完全等价。

本研究通过三项经典决策任务考察 LLM 的行为可靠性。这些任务覆盖适应性选择的不同方面。Horizon Task 通过 explore--exploit dilemma 区分信息寻求以及随决策时域变化的探索行为（Wilson et al., 2014）。Iowa Gambling Task（IGT）要求参与者根据反复出现的收益和损失，逐步区分长期有利与长期不利的选项，用于测量 feedback-based learning 和对长期结果的适应（Bechara et al., 1994; Toplak et al., 2010）。Balloon Analogue Risk Task（BART）则要求参与者在增加潜在收益的同时承受不断上升的损失概率，从而测量连续的风险承担行为（Lejuez et al., 2002）。

这三项任务使评估超越单次问答，分别覆盖探索、反馈学习和风险管理。它们也具有既有的人类数据，可用于比较 LLM run-level behaviour 与人类参与者行为指标的分布和位置（Steingroever et al., 2015; Feng et al., 2021; Sebri et al., 2023）。本研究将这种 human proximity 视为描述性的行为证据，而不将其解释为 LLM 与人类具有相同潜在认知过程的证明。

在三项任务中，本研究设置四种 prompt conditions，并保持任务规则、环境参数、响应要求和生成设置不变：Neutral baseline、Instruction specificity、Role framing，以及针对各任务核心构念的 Task-specific construct emphasis。每个 model--task--prompt cell 均包含重复运行，因此 prompt effects 是根据完整任务运行的分布估计，而不是依据单次响应判断。主要的英文模型比较使用完全相同且已冻结的 prompts 和任务环境，对 GPT-4.1、GPT-5.4 与 GPT-5.4 Mini 进行比较。作为补充，跨语言比较将模型固定为 GPT-4.1，并使用实验相关含义相匹配的英文、简体中文和西班牙语 prompts。模型比较与语言比较被有意分开，从而避免在解释某一因素时，另一因素也同时发生变化。

本研究具有三方面贡献。第一，本研究将 behavioural reliability 操作化为模型行为对受控 prompt reformulations 的稳健性，并在任务特定行为指标层面测量 prompt effects。第二，本研究考察 prompt sensitivity 是否因模型、任务和行为构念而异，而不是将可靠性压缩为一个总体模型排名。第三，本研究明确区分 prompt stability、task performance 与 human-reference proximity，并通过固定模型的多语言比较将分析扩展到英文之外。

基于此，本研究回答以下四个研究问题：

1. **RQ1 — Prompt sensitivity：** 与 Neutral baseline 相比，Instruction specificity、Role framing 和 Task-specific construct emphasis 会在多大程度上改变模型的任务特定行为？
2. **RQ2 — Cross-model and cross-task variation：** Prompt effects 的方向和标准化幅度是否因模型和任务而异？
3. **RQ3 — Reliability as cognitive models：** 不同 prompt formulations 是否会改变对模型决策倾向及其与 human reference data 关系的实质性结论，这些变化对 LLM 作为认知模型的可靠性意味着什么？
4. **RQ4 — Cross-language variation：** 当模型、任务环境、prompt manipulation 的含义和生成参数保持不变时，英文、简体中文和西班牙语是否产生不同的基线行为或 within-language prompt effects？

通过回答这些问题，本研究所评估的不只是 LLM 能否完成认知任务，更是由这些任务得出的行为结论是否具有足够的稳定性，从而能够支持审慎的科学解释。

## 本稿引用的参考文献

按正文首次出现顺序整理的 21 条参考文献及 DOI/会议页码见 [Introduction 引用顺序表](introduction_references_ordered.md)。正式排版时应将这些条目导入论文的统一 bibliography，并按学院要求的引用格式输出。
