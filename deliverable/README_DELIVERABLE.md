# 导师审阅交付材料

本目录是项目的精简审阅视图。它面向需要查看当前方法、可复现实验材料和正式结果表的导师或评阅人，不包含本地过程文件。

## 首先阅读

请从仓库根目录开始阅读：

```text
README.md
docs/formal_experiment_freeze.md
docs/task_parameters.md
docs/data_schema.md
docs/research_log.md
```

代码、提示词、测试和冻结配置仍保留在项目的常规位置：

```text
configs/
prompts/
src/
tests/
```

## 当前已包含的结果

当前交付包包含已完成的 English 正式阶段：

```text
deliverable/results/formal_v01/
```

其中仅包含处理后的分析输出：

```text
aggregation_quality_report.json
analysis_summary.json
llm_run_metrics.csv
metric_summary.csv
prompt_effects.csv
prompt_sensitivity.csv
```

English 阶段状态：

```text
formal_v01: 3 个任务 x 4 个提示词条件 x 每个条件 20 次运行 = 240 次有效运行
失败文件：0
无效响应：0
未完成运行：0
聚合分析 analysis_complete：true
PSI 分析 analysis_complete：true
```

完整正式实验将语言作为实验因素：

```text
3 languages x 3 tasks x 4 prompt conditions x 20 matched seeds
= 720 task runs
```

中文和西班牙语正式采集正在
`outputs/formal_multilingual_v01/` 中进行。其处理结果尚未复制到本交付包。
因此，当前 `formal_v01` 和 `human_comparison_formal_v01` 应解释为完整
三语言正式实验中的 English 阶段结果，而不是最终三语言结果。

## 本交付材料未包含的内容

以下内容仍作为本地工作材料保留，并有意排除在审阅视图之外：

```text
.env
.venv/
.tmp/
.uv-cache/
DATASET/
outputs/debug/
outputs/pilot/
outputs/mini_pilot_v01/
outputs/validation_mini_pilot_v02/
outputs/formal_v01/               原始正式实验 JSON 运行结果
outputs/formal_multilingual_v01/  中文和西班牙语正式运行结果
outputs/processed/*               早期或诊断用处理输出
```

此打包步骤不会删除原始运行结果和人工数据集。它们仍保留在本地，以便在需要时审计或重新生成分析。
