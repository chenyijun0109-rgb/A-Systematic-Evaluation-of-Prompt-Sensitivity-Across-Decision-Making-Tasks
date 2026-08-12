# Results 数据库存与定稿阻塞项（2026-08-09）

本记录由主 Agent 汇总只读数据审计结果。实验采集已经完成，但现有分析输出尚不足以覆盖 RQ1--RQ4，因此不能据此定稿完整 Results。

## 已确认的数据规模

- 去重后的正式数据共 1,200 个有效 task runs：英文三模型 720 个，中文与西班牙语各新增 240 个；英文 GPT-4.1 的 240 个 runs 在两种比较中共享，不重复计数。
- 中文与西班牙语共 480 个 raw JSON 均可解析，`done=true`、`parse_success_rate=1.0`、`invalid_responses=0`，每个 task--condition cell 各 20 个 runs。
- GPT-5.4 Mini 含一个成功恢复的 parser retry；其完整 task records 保留，可纳入分析，但需在质量报告中披露。

## 当前权威输入与输出

英文 run-level 输入：

- `outputs/processed/formal_v01/llm_run_metrics.csv`
- `outputs/processed/model_comparison_en_v01/gpt-5.4/llm_run_metrics.csv`
- `outputs/processed/model_comparison_en_v01/gpt-5.4-mini-formal-v01/llm_run_metrics.csv`

多语言 raw 数据：

- `outputs/formal_multilingual_v01/gpt-4.1-zh-CN-20run-v01`
- `outputs/formal_multilingual_v01/gpt-4.1-es-20run-v01`

英文 prompt effects 与 PSI 应只使用 2026-08-08 Horizon tie-rule 修正后的目录：

- `outputs/processed/formal_v01_refit_v02`
- `outputs/processed/model_comparison_en_v01/gpt-5.4_refit_v02`
- `outputs/processed/model_comparison_en_v01/gpt-5.4-mini-formal-v01_refit_v02`

英文 human-reference 总表：

- `outputs/processed/model_comparison_en_v01/human_similarity_tables_v01/table_human_similarity_long.csv`

早于 `refit_v02` 的 prompt-effect 文件、旧 pairwise outputs、`deliverable/results` 副本以及 2026-07-20 的 GPT-4.1-only figures 均不得作为最终结果来源。

## 按研究问题的完成度

| 研究问题 | 当前状态 | 尚缺内容 |
|---|---|---|
| RQ1 | 英文三模型 within-model effects 与 PSI 完整 | 中文、西班牙语的聚合、within-language effects、PSI 与质量报告 |
| RQ2 | `GPT-5.4 - GPT-4.1` 可用；另有 `Mini - GPT-4.1` | 现行参照方向下的 `GPT-4.1 - GPT-5.4` 和直接联合 bootstrap 的 `Mini - GPT-5.4` |
| RQ3 | 三种语言的 raw 数据均完整 | 16项 baseline language contrasts、48项 language-by-prompt interactions、非英文 prompt effects/PSI 及其区间 |
| RQ4 | 英文三模型的 signed \(D\)、\(|D|\) 和 coverage 可用 | 最新 \(\Delta^{abs}\)/\(\Delta C\) change table，以及中文和西班牙语 human-reference outputs |

## Results 定稿前的 P0 工作

1. 聚合三语言正式数据，并按修正后的 Horizon tie-exclusion rule 完成质量审计。
2. 生成完整 RQ3 输出，包括有效 bootstrap replicate 和失败拟合诊断。
3. 以 GPT-5.4 为参照直接生成两组 RQ2 contrasts，尤其是 `GPT-5.4 Mini - GPT-5.4`。
4. 补齐 Random exploration 的 condition estimates、收敛率、failed refits，以及 run-effect SD 为 0.25、0.5、1.0 的 sensitivity analysis。
5. 生成非英文 human-reference outputs，并从最新英文 long table 生成权威 change table。
6. 冻结一个带 manifest、hash、quality summary 和 source-keyed checklist 的统一结果包，再据此写正文与重画图。

## 写作边界

- 目前可以起草英文 RQ1 的结构和部分数值，但不能把它写成完整 RQ1。
- 当前不能定稿 RQ2--RQ4，也不能复用旧图填补缺失输出。
- 不使用“显著/不显著”；不以单个未校正 bootstrap interval 是否跨零作为强证据。
- 标准化效应必须同时报告 raw magnitude，特别是组内方差很低的 cells。

