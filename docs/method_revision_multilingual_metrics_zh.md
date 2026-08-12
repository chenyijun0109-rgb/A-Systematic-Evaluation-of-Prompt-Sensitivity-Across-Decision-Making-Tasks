# Method 修订稿：行为指标与多语言比较

本文件针对 2026-08-04 的 `final.pdf`。以下文字可直接替换或补入论文的
Method。它不改变已经实现的指标或实验参数；重点是删除重复说明、补足指标
选择依据，并把三语言比较与三模型英文比较清楚地区分。

## 审阅结论

当前 Method 的总体结构可用，但定稿前应修正以下问题：

1. `Study Design and Scope` 只描述了三模型英文实验，并称所有正式实验均使用
   英文 prompts，与新增的中文、西班牙语实验冲突。
2. 研究问题没有明确覆盖语言效应。多语言比较应作为独立问题，不能混入
   cross-model comparison，因为该比较固定模型为 GPT-4.1。
3. `Prompt Construction and Validation` 仅说明英文 prompt 的生成与冻结，没有
   交代中文和西班牙语由英文规范版本翻译、语义审查和冻结的过程。
4. `Behavioural Metrics` 的表格后又逐项重复定义，篇幅过长。表格应承担操作性
   定义，正文只保留选择逻辑和必要的公式/边界情况。
5. “选择这些指标是因为预先冻结”不是理论或测量依据。冻结只能说明分析决策
   在查看正式结果前已确定，不能说明指标为什么合适。
6. 当前 `directed_exploration` 是不等信息条件下选择较少观察选项的总体比例；
   `horizon_effect` 才是长、短 horizon 的探索率之差。为避免与经典 Horizon
   Task 中“directed exploration 常指 horizon-dependent information seeking”
   混淆，正文应明确前者是 information-seeking choice rate，并将
   `Horizon-related change in exploration rate` 单独解释。若不更改代码和结果列
   名，可保留表中的 `Directed exploration`，但必须加上这一区分。
7. 模型配置表仍含 `[verified dates]` 占位符，正式提交前必须填入真实采集日期。
8. 文中称八项指标均为 “participant-level” 不够准确：
   `random_exploration_effect` 是由分层选择模型得到的部分汇聚估计。应称为
   run-level behavioural summary 或 model-derived run estimate，并在不确定性部分
   说明 bootstrap 中重新拟合模型。

## 可替换的 Study Design and Scope

本研究包含两个相互补充的比较。第一部分检验模型差异：在英文 prompt 下比较
GPT-4.1、GPT-5.4 和 GPT-5.4 Mini。三个模型完成相同的三项决策任务、四种
prompt conditions 和 20 个重复运行。第二部分检验语言差异：固定使用
`gpt-4.1-2025-04-14`，比较英文（en）、简体中文（zh-CN）和西班牙语（es）
版本。三种语言使用相同的任务实现、四种 prompt conditions、20 个 matched
base seeds、生成参数和输出格式；中文与西班牙语 prompt 保持英文规范版本的
任务规则、信息内容、操纵意图和响应要求，仅改变表达语言。因而，模型比较不受
语言变化混入，而语言比较不受模型版本变化混入。

完整 task run 是主要分析单位。单个 trial、choice、game 或 balloon 是 run 内的
嵌套观察，用于计算任务特定的 run-level behavioural summaries；一个完整 LLM
run 被视为一个 participant-level behavioural analogue，但不被视为真实的人类
参与者。英文三模型分析与 GPT-4.1 三语言分析分别估计和报告，不将二者合并为
一个全因子模型。

建议新增研究问题：

> **RQ4: Cross-language variation.** 在模型、任务、prompt 操纵含义、任务环境
> 与生成参数保持不变时，英文、简体中文和西班牙语是否产生不同的基线行为或
> prompt effects？

## 可补入的 Multilingual Prompt Construction and Validation

英文 prompt 是规范源版本。简体中文和西班牙语版本逐条对应相同的三项任务和
四种 prompt conditions。翻译要求保留任务规则、动作集合、反馈结构、隐藏信息
边界、操纵意图、响应格式和语用强度，不增加策略建议、文化情境或额外解释。
翻译后对 24 个目标语言 prompts 进行双语语义审查，重点检查遗漏、增译、条件间
信息不对称、操纵强度漂移和响应格式变化；审查通过后记录文本及 SHA-256 hashes
并冻结。这里的 “semantically matched” 指经约束翻译和人工审查后在实验相关
含义上匹配，不主张三种自然语言表达在所有语用维度上完全等价。

## Behavioural Metrics：建议保留的精简正文

每个完整 LLM run 产生一组任务特定的行为汇总，具体操作性定义见表 X。指标的
选择基于三个标准。第一，它们对应各任务要测量的核心行为构念：Horizon Task
区分信息导向探索、随决策时域变化的探索和随机探索；IGT 同时衡量长期有利选择
与损失后的即时调整；BART 同时衡量持续承担风险、实际爆炸结果和爆炸后的行为
调整。第二，这些指标可由完整的逐步选择记录直接计算，或由预先规定的选择模型
估计，而不依赖模型的文字解释或隐藏推理。第三，它们能够在 LLM runs 与所选
human datasets 中以相同或尽可能一致的单位构造，从而支持 participant/run-level
比较。组合使用这些指标可避免以单一的总收益或选择比例代替探索、学习和风险
调整等不同构念。

表 X 已给出各指标的计算单位，因此表后不再逐项复述定义。正文仅需补充两个
技术说明。首先，表中的 `Directed exploration` 在本研究中具体表示不等信息
条件下首次自由选择中选择较少观察选项的比例；它是信息寻求倾向的水平指标，
不同于另行报告的长、短 horizon 探索率之差。其次，`Random exploration effect`
由 first-free-choice 分层 logistic choice model 估计为
`decision noise(H6) - decision noise(H1)`，属于 model-derived estimate；其
bootstrap 区间通过在每次重采样中重新拟合选择模型获得。BART 的
`Post-explosion adjustment` 仅在一次爆炸后仍有下一只 balloon 时定义；没有
eligible transition 时记为 missing，而不是 0。

指标在正式结果分析前冻结的事实只用于说明分析的时间顺序、降低结果导向选择的
风险；它不作为指标选择本身的理由。

## 建议新增的 Cross-Language Comparisons

三语言分析仅使用 GPT-4.1。首先，分别对每个
language--task--prompt condition--metric cell 报告有效 run 数、均值、标准差、
中位数、范围和分布。基线语言差异通过比较三种语言的 neutral-baseline cells
描述；prompt effect 则在每种语言内部定义为 manipulated condition 相对同语言
neutral baseline 的差值。主要跨语言问题通过 language-by-prompt interaction
检验，即比较三种语言的 within-language prompt effects，而不是仅比较某一语言
显著、另一语言不显著。英文为预先指定的参照语言，中文和西班牙语相对英文的
interaction contrasts 用于定位差异；同时报告 signed raw differences、标准化
效应和 bootstrap 95% confidence intervals。

Horizon Task 与 BART 的语言比较按 matched task-environment seed blocks 联合
重采样，以保留三种语言面对相同环境实例所形成的配对结构。IGT 的 payoff
schedule 是确定性的，nominal seeds 不产生不同的任务环境，因此不把 seed
matching 描述为环境配对；其不确定性分析应按既定的独立 cell/run 重采样规则
进行。多语言分析只支持对这些经审查的 prompt 版本、指定 API snapshot 和任务
设置作出结论；观察到的差异可称为 language-associated differences，但不能仅凭
本设计归因于语言的某个具体语言学或文化机制。

## 其他应同步改写的位置

- `Models and API Configuration`：表后明确“三模型比较使用英文；三语言比较只
  使用 GPT-4.1”，避免读者误以为 3 models x 3 languages 已全部运行。
- `Experimental Procedure`：将 “每个 model--task--prompt cell 20 runs” 扩写为
  英文模型比较的 720 个 runs，以及 GPT-4.1 三语言比较中每种语言 240 个 runs；
  英文 GPT-4.1 的既有 240 runs 可作为语言比较的英文层，无需重复采集。
- `Prompt Sensitivity Index`：若跨语言报告 PSI，应在每种语言内部按同一公式计算，
  再把 PSI 的语言差异标为描述性结果；不要把不同语言的指标先合并后计算 PSI。
- `Reproducibility`：新增 `prompt_language`、翻译审查记录、目标语言 prompt hash
  和 multilingual freeze configuration。
