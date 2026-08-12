# Background and Related Work 文献审查记录

审查日期：2026-08-09  
审查范围：`tmp/final_revision_all.md` 中 Background and Related Work。子 Agent 仅核验证据，未修改源文件；修订由主 Agent 统一完成。

## 审查结论

- 原稿29篇文献均真实存在。
- 根据正式出版状态和引用适配性完成6项必须修正、9项措辞或书目信息收窄。
- 为 Horizon Task 的具体设计补入原始来源 Wilson et al. (2014)，修订后共30篇独立文献。
- 修订后26个实质性段落均含至少一组支持性引文。

## 已执行的必须修正

| 问题 | 主 Agent 处理 |
|---|---|
| Loya et al. (2023) 被误写为未比较多个模型 | 改为：该研究比较三个 OpenAI 模型，但仅使用一项连续决策范式，且没有多语言比较。来源：[ACL](https://aclanthology.org/2023.findings-emnlp.241/) |
| 翻译段以 Qi 和 Etxaniz 支撑 back-translation 的一般方法论限制 | 删除错位主张；改为依据跨语言迁移、multilingual CoT 和 direct/self-translation 研究说明语义匹配不保证相同测量性质。来源：[Qi et al.](https://aclanthology.org/2023.emnlp-main.658/)、[Etxaniz et al.](https://aclanthology.org/2024.naacl-short.46/) |
| Gershman (2018) 不是 Horizon Task 原始来源 | 在任务设计主张处加入 Wilson et al. (2014)；Gershman 仅用于 directed/random exploration 的计算区分。来源：[Wilson et al.](https://doi.org/10.1037/a0038199) |
| Dasgupta et al. (2022) 为旧预印本 | 统一替换为正式版本 Lampinen et al. (2024), *PNAS Nexus*。来源：[正式论文](https://academic.oup.com/pnasnexus/article/3/7/pgae233/7712372) |
| Chen, Zaharia and Zou (2023) 已有正式版本 | 统一替换为 Chen, Zaharia and Zou (2024), *Harvard Data Science Review*。来源：[正式论文](https://doi.org/10.1162/99608f92.5317da47) |
| 两篇 Hagendorff 2023 文献可能混淆 | 实证论文标为 2023a，*Machine Psychology* 预印本标为 2023b；最终参考文献表须保持相同消歧。来源：[实证论文](https://doi.org/10.1038/s43588-023-00527-x)、[Machine Psychology](https://arxiv.org/abs/2303.13988) |

## 已执行的适配性收窄

| 文献 | 修订后的证据用途 |
|---|---|
| Dillion et al. (2023) | 限于 LLM 作为模拟/替代参与者及其限制，不再承担所有研究工具用途。 |
| Park et al. (2023) | 限于 memory/reflection/planning agent architecture 与连贯行为。 |
| Bisbee et al. (2024) | 支撑异质性压缩和对模型/prompt变化的敏感；删除未被直接支持的“复制刻板关系”。 |
| Sclar et al. (2024) | 限于 prompt formatting 和跨模型格式敏感性。 |
| Hua et al. (2025) | 限于 evaluation/scoring artifacts。 |
| Zhuo et al. (2024) | 以 ProSA 在多任务、多模型中直接量化 prompt sensitivity，替换适配度较弱的 Razavi et al. (2025)。[ACL](https://aclanthology.org/2024.findings-emnlp.108/) |
| Palmer et al. (2024) | 支撑专有模型透明度和复现风险；具体 provenance 字段明确为本文采取的措施。 |
| Mondshine et al. (2025) | 直接比较35种语言中 instruction、context、examples 和 output 的 pre-translation strategies，替换适配度较弱的 Etxaniz et al. (2024)。[ACL](https://aclanthology.org/2025.findings-naacl.73/) |
| Lin (2024) | 替换为同行评审正式版本 Lin (2025), *Six Fallacies in Substituting Large Language Models for Human Participants*。[正式论文](https://doi.org/10.1177/25152459251357566) |

## 无需内容修正的核心来源

以下来源存在、书目信息与核心主张适配：Mizrahi et al. (2024)、Zhao et al. (2021)、Lu et al. (2022)、Pezeshkpour and Hruschka (2024)、Zhang et al. (2023, M3Exam)、Muennighoff et al. (2023)、Shi et al. (2023)、Busemeyer and Stout (2002)、Steingroever, Wetzels and Wagenmakers (2013)、Buelow and Suhr (2009)、Wallsten, Pleskac and Lejuez (2005)，以及 van Ravenzwaaij, Dutilh and Wagenmakers (2011)。

## 定稿提醒

当前正文的 `Bibliography` 仍为空。补参考文献表时必须采用上述正式版本和年份，并确保 Hagendorff 2023a/2023b、Binz and Schulz 2023a/2023b 的消歧与正文一致。

## 第二轮复核后执行的修正

- 在测量程序段补入 Loya et al. (2023) 支持生成温度，补入 Chen, Zaharia and Zou (2024) 支持部署状态与时间漂移。
- 将 role framing 和 construct emphasis 明确写为本文预先界定、需要实证检验的操纵；加入 Kong et al. (2024) 对 role-play prompting 可改变推理表现的直接证据，不再让 Sclar et al. 或 Hua et al. 承担这一主张。
- 连续任务总论只用 Loya et al. 支持连续范式，并明确完整 run 是本文的分析约定。
- IGT 段锁定 Steingroever, Wetzels and Wagenmakers (2013) 为 *Validating the PVL-Delta Model for the Iowa Gambling Task*，DOI `10.3389/fpsyg.2013.00898`。若最终同时收入同作者同年的另一篇论文，须在正文和书目中使用 a/b 消歧。
- 删除 BART 段中超出当前模型文献直接支持的“幸存选择”表述。
- 将任务对齐限制明确标为本文的 design-alignment limitations，并补入 Wilson、Buelow 和 Wallsten 的任务来源。
- 重写 Research Gap：承认已有研究采用多个模型或多个 prompt variants，缺口定位于静态 benchmark、单项连续任务与独立多语言路线尚未形成同一设计组合。
- 将贡献表述改为“把 multi-prompt evaluation 与完整连续 runs 相结合，并扩展到多任务、跨模型和跨语言比较”，不再暗示既有研究没有连续任务。

第二轮复核后，Background 保持 8 个层次清楚的小节和 26 个实质段落；加入 Kong et al. (2024) 后曾使用 31 篇独立文献。第三轮又将 Intro/Method 已使用的 Bechara et al. (1994) 和 Lejuez et al. (2002) 补入 Background 的任务理论段，因此最新版 Background 共使用 33 篇独立文献。文献数量不作为硬性上限，新增来源只用于修复直接证据缺口。最终 Bibliography 仍需补齐，这是定稿前唯一尚未消除的系统性书目问题。

Kong et al. (2024) 的正式书目信息为：*Better Zero-Shot Reasoning with Role-Play Prompting*, NAACL 2024, pp. 4099--4113, DOI `10.18653/v1/2024.naacl-long.228`。

## 第三轮复核后的正文修正

- 将 behavioural-measurement reliability 限定为：固定模型 snapshot、任务实现、生成温度、响应格式和 parser 时，结论方向与幅度在预设 prompt formulations 间的稳定程度；明确不涵盖长期 test--retest reliability、外部效度或机制可靠性。
- 将“改变真实选择”改为“改变模型产生的选项”，避免赋予 LLM choices 未经论证的真实性或心理状态。
- 删除 IGT 段解释 Steingroever 引文身份的元写作句；具体题名与 DOI 只保留在审查记录和最终 Bibliography。
- 在连续任务总论及任务段补入 IGT 原始来源 Bechara et al. (1994) 和 BART 原始来源 Lejuez et al. (2002)，并把一般性主张限定为本文所选三项任务。
- 将 BART 指标表述改为“本文将其作为互补指标报告”，明确这是分析选择。
- 将 `signed human-SD standardised mean difference` 全文改为 `signed human-SD-scaled mean deviation`，将 \(|D|\) 称为 `absolute human-SD-scaled mean deviation`；正文明确该量不称为 standardised mean difference。
- 压缩跨模型、跨语言及研究贡献段中的具体参照、审核字段与 contrast 细节，并将其指向 Method。
- 将 Research Gap 的绝对性表述软化为“在本文所覆盖的文献范围内，尚未发现……”，并把推论限定为现有证据仍不足以回答的稳健性问题，避免暗示已经穷尽整个研究领域。
