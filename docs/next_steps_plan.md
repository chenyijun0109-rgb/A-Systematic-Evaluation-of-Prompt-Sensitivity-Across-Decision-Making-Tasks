# 当前后续计划

更新时间：2026-07-29

## 1. 统一项目范围

项目只包含一个正式实验。语言是该实验的一个实验因素：

```text
3 languages x 3 tasks x 4 prompt conditions x 20 matched seeds
= 720 task runs
```

语言：

- English (`en`)
- 简体中文 (`zh-CN`)
- Spanish (`es`)

English 部分 `formal_v01` 已完成 240 个有效 runs。当前只补充相同设计、
相同模型、相同参数和 matched seeds 下的中文与西班牙语 480 个 runs。

项目只使用每项任务一套开放 human reference dataset：

- Horizon：60 participants
- IGT：504 participants
- BART：141 adults

项目不包含第二批 LLM 实验、独立复测、ICC、第二套 human datasets 或
cross-dataset robustness analysis。

## 2. 已完成

- 三项任务环境与 history-rich observations。
- 四类 prompt conditions。
- English、中文和西班牙语共 36 个冻结 prompts。
- 固定模型 `gpt-4.1-2025-04-14`、temperature `0.7`、top-p `1.0`。
- English `formal_v01`：240 个有效 task runs。
- English prompt sensitivity、PSI 和主 LLM-human comparison。
- Human participant-level preprocessing。
- Horizon hierarchical random-exploration model。
- 36-prompt multilingual dry run。
- 中文/西班牙语 480-run 正式矩阵 plan validation。
- API transient disconnect retry 与 exponential backoff。

## 3. 当前进行中：正式多语言补全

正式 base seeds：

```text
20260708 through 20260727
```

任务 seed offsets：

```text
Horizon: base seed + 0
IGT:     base seed + 1
BART:    base seed + 2
```

新正式输出只写入：

```text
outputs/formal_multilingual_v01/
```

早期 `outputs/multilingual_v01/` pilot/debug 文件不进入正式分析。

当前执行顺序：

1. 完成 base seed `20260708` 的中文/西班牙语 24-cell smoke matrix。
2. 核对每个 cell 的完成状态、trial 数、模型、prompt hash、解析率和无效响应。
3. smoke matrix 无系统性问题后，释放其余 19 个 base seeds。
4. 不同 cells 可以有限并行；每个 cell 内的 sequential trials 必须保持串行。

## 4. 数据质量门槛

每个正式 run 必须：

- `done = true`
- 使用冻结模型和 sampling parameters
- 使用冻结 prompt hash
- 使用预定 language、task、condition 和 seed
- 完成预期任务结构
- 保存完整 raw responses 和 trial records
- 无未解决的 parser failure

行为极端、零方差或不符合预期方向不是排除理由。

## 5. 三语言聚合与分析

完成 480 个新 runs 后：

1. 将 English、中文和西班牙语合并为 720-run 正式分析数据。
2. 在每种语言内部比较 manipulated condition 与同语言 baseline。
3. 报告 raw difference、Hedges' g、paired bootstrap interval 和 PSI。
4. 对三种语言进行 paired-seed Friedman omnibus analysis。
5. 报告 Kendall's W 和 within-seed permutation p-value。
6. 比较三种语言的 within-language `condition - baseline` prompt effects。
7. primary analysis 不进行事后挑选的 pairwise language tests。

## 6. Human comparison

三种语言的 LLM runs 使用同一套 task-specific human reference datasets。

报告：

- LLM 与 human mean/SD
- standardized distance
- human reference interval
- LLM runs 落入 reference interval 的比例
- 不同语言和 prompt condition 下的 human-distance 变化

接近 human distribution 不证明 LLM 与人类使用相同认知机制。

## 7. 稳健性分析

- Horizon `run_effect_sd = 0.25, 0.50, 1.00`
- leave-one-metric-out PSI
- mean-based 与 median-based summaries
- raw differences 与 standardized effects 对照
- 低 baseline variance 检查
- 网络重试和补跑审计
- English 先采集、中文/西班牙语后采集造成的 batch/time limitation

## 8. 最终论文与交付

完成顺序：

1. 更新 Methods 为三语言正式设计。
2. 完成三项任务、prompt sensitivity、language effects 和 human comparison 结果。
3. 生成 condition distributions、effect sizes、PSI、language omnibus、
   learning curves、Horizon decomposition 和 LLM-human comparison 图表。
4. 在 Discussion 中明确单模型、单 human dataset set、非同期语言采集和
   自定义 PSI 的限制。
5. 更新 `deliverable/`，加入完成后的三语言处理结果。
6. 从原始 JSON 和 human raw data 完整重跑分析并执行最终测试。

## 9. 完成标准

只有在以下条件满足后，三语言正式实验才算完成：

- 720 个预定 task runs 全部被审计。
- 每个 language-task-condition 有 20 个有效 matched-seed runs。
- 聚合和 PSI quality reports 没有未解决 issues。
- 三语言 omnibus 与 language-by-prompt outputs 完成。
- Human comparison 只使用冻结的一套 reference datasets。
- README、冻结配置、研究日志、结果表和论文方法描述一致。
