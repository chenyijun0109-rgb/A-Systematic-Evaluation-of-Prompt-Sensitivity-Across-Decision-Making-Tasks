# Pilot Rerun Analysis With Average Metrics

日期：2026-06-03

模型：`gpt-4.1`

目的：总结按新 run-level 平均指标重新生成的 single-run pilot matrix。该版本替换了部分旧的 total outcome 指标，以便后续更容易和 human participant-level metrics 对齐。

重要说明：本文件中的结果仍然是 pilot 结果。当前每个 `task x prompt condition` 只有 1 个 run，因此只能用于 pipeline 检查和初步趋势观察，不能作为正式统计结论。

## 1. 已完成的 Pilot Matrix

本次重新跑完 12 个 single-run pilot：

| Task | Prompt conditions |
|---|---|
| Horizon | `baseline`, `detailed`, `role_human`, `uncertainty_emphasis` |
| IGT | `baseline`, `detailed`, `role_human`, `reward_loss_emphasis` |
| BART | `baseline`, `detailed`, `role_human`, `risk_emphasis` |

所有输出均满足：

```text
done = true
parse_success_rate = 1.0
invalid_response_count = 0
```

本次使用的平均 outcome 指标：

| Task | New average metric |
|---|---|
| Horizon | `average_reward_per_trial` |
| IGT | `average_net_outcome` |
| BART | `average_earning_per_balloon` |

总分、累计分数和总收益仍保留在 trial/action records 中，但不作为主要跨 run / human comparison 指标。

## 2. Horizon Task

### 2.1 Results

| Condition | Exploration rate | Directed exploration | Horizon effect | Switching rate | Average reward per trial |
|---|---:|---:|---:|---:|---:|
| `baseline` | 0.279 | 0.850 | 0.250 | 0.559 | 53.257 |
| `detailed` | 0.314 | 0.750 | 0.150 | 0.585 | 52.797 |
| `role_human` | 0.350 | 0.750 | 0.200 | 0.625 | 52.570 |
| `uncertainty_emphasis` | 0.321 | 0.900 | 0.200 | 0.579 | 52.757 |

### 2.2 Interpretation

Horizon behaviour is relatively stable compared with BART, but prompt wording still shifts exploration-related metrics.

Compared with baseline, all non-baseline prompts increased `exploration_rate`. The largest increase was in `role_human`, from 0.279 to 0.350. This suggests that human-participant framing may make the model more willing to choose options that are not currently best according to observed reward means.

`directed_exploration` remained high across all conditions. Baseline was 0.850 and `uncertainty_emphasis` increased it to 0.900, which is consistent with the prompt emphasizing uncertainty and information. However, `detailed` and `role_human` reduced directed exploration to 0.750.

`horizon_effect` remained positive in all conditions, meaning the model generally explored more in Horizon 6 than Horizon 1. However, the effect was smaller outside baseline, especially in `detailed`.

### 2.3 Pilot Conclusion

The model shows a consistent directed-exploration tendency in Horizon Task. Prompt changes affect the magnitude of exploration, but they do not completely change the behavioural pattern. Horizon therefore appears moderately prompt-sensitive in this pilot.

## 3. Iowa Gambling Task

### 3.1 Results

| Condition | Net score | Advantageous choice rate | Deck A | Deck B | Deck C | Deck D | Average net outcome | Post-loss switching |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `baseline` | 72 | 0.86 | 0.04 | 0.10 | 0.29 | 0.57 | 21.75 | 0.682 |
| `detailed` | 72 | 0.86 | 0.04 | 0.10 | 0.30 | 0.56 | 21.00 | 0.652 |
| `role_human` | 76 | 0.88 | 0.02 | 0.10 | 0.28 | 0.60 | 20.25 | 0.810 |
| `reward_loss_emphasis` | 76 | 0.88 | 0.02 | 0.10 | 0.28 | 0.60 | 20.25 | 0.762 |

### 3.2 Interpretation

IGT is fairly stable across prompt conditions in this rerun. All conditions show high advantageous choice rates, from 0.86 to 0.88. The model strongly favours advantageous decks C/D, especially Deck D.

`detailed` is almost identical to baseline in net score and advantageous choice rate. This suggests that more detailed task explanation does not substantially change IGT behaviour when history-rich observations are already provided.

`role_human` and `reward_loss_emphasis` slightly increase advantageous choice rate from 0.86 to 0.88 and reduce Deck A choices from 0.04 to 0.02. However, `average_net_outcome` is lower than baseline because deck-level payoff timing and losses also matter, not just advantageous choice rate.

Post-loss switching is highest under `role_human` at 0.810. This may indicate that human-participant framing makes the model more reactive to negative feedback.

### 3.3 Pilot Conclusion

IGT shows limited prompt sensitivity in the main choice-rate metrics, but role and reward-loss framing may slightly increase feedback reactivity. The larger methodological point remains that IGT requires history-rich observations; otherwise LLM behaviour may reflect task prior or task-name knowledge rather than trial-by-trial learning.

## 4. BART

### 4.1 Results

| Condition | Average pumps | Adjusted average pumps | Explosion rate | Average earning per balloon | Post-explosion adjustment |
|---|---:|---:|---:|---:|---:|
| `baseline` | 5.875 | 6.000 | 0.200 | 0.240 | 0.125 |
| `detailed` | 5.525 | 5.333 | 0.250 | 0.200 | -0.900 |
| `role_human` | 7.650 | 7.889 | 0.325 | 0.266 | -1.154 |
| `risk_emphasis` | 6.775 | 6.828 | 0.275 | 0.247 | -1.727 |

### 4.2 Interpretation

BART shows the clearest prompt sensitivity in this pilot.

`detailed` makes the model more conservative than baseline. Average pumps decrease from 5.875 to 5.525, adjusted average pumps decrease from 6.000 to 5.333, and average earning per balloon decreases from 0.240 to 0.200.

`role_human` produces the most risk-taking behaviour. Average pumps increase to 7.650, adjusted average pumps increase to 7.889, and explosion rate rises to 0.325. Despite more explosions, average earning per balloon is also highest at 0.266.

`risk_emphasis` also increases risk-taking relative to baseline, but less strongly than `role_human`. Average pumps increase to 6.775 and explosion rate rises to 0.275.

The direction of `risk_emphasis` is important. Emphasizing risk does not make the model more conservative; instead, the model appears to treat the prompt as highlighting a risk-reward trade-off and accepts more risk.

### 4.3 Pilot Conclusion

BART is the most prompt-sensitive task in the current pilot. Prompt framing changes pump behaviour, explosion rate, post-explosion adjustment, and earnings. This strongly supports the need to treat prompt wording as an experimental manipulation rather than a neutral instruction detail.

## 5. Cross-Task Comparison

### 5.1 Prompt Sensitivity Pattern

| Task | Apparent sensitivity | Main evidence |
|---|---|---|
| Horizon | Moderate | Exploration rate and directed exploration shift, but core pattern remains stable |
| IGT | Low to moderate | Advantageous choice rate is stable; post-loss switching changes more |
| BART | High | Average pumps, adjusted average pumps, and explosion rate shift clearly across prompts |

### 5.2 Prompt Manipulation Pattern

| Prompt manipulation | Main observed effect |
|---|---|
| `detailed` | Slightly increases Horizon exploration; makes BART more conservative; little effect on IGT choice rate |
| `role_human` | Increases Horizon exploration; increases IGT post-loss switching; strongly increases BART risk-taking |
| Task-specific emphasis | Increases Horizon directed exploration and BART risk-taking; only small change in IGT |

## 6. Methodological Notes

### 6.1 Average Metrics And Human Comparison

This rerun uses average outcome metrics because they are easier to compare with human participant-level summaries:

- `average_reward_per_trial` is easier to compare with human Horizon data because individual rewards in the dataset are trial-level values (`r1`-`r10`). A previous per-game average was less intuitive because Horizon 1 games contain 5 trials and Horizon 6 games contain 10 trials.
- `average_net_outcome` is easier to compare across IGT runs or participants than final total score.
- `average_earning_per_balloon` is more interpretable for BART human comparison than total earnings, especially if reward scales differ across datasets.

### 6.2 Random Exploration Limitation

The pilot files were generated when `random_exploration` was still represented using `exploration_rate` as a simple proxy. That proxy has since been removed. The formal analysis now estimates `random_exploration_effect` as the Horizon-6 minus Horizon-1 decision-noise difference using a hierarchical logistic choice model. Therefore, the historical pilot conclusions remain focused on `exploration_rate`, `directed_exploration`, and `horizon_effect`.

### 6.3 Pilot Limitation

The current matrix has only one run per condition. Differences should be interpreted as preliminary trends. Formal conclusions require repeated runs, ideally at least 15 valid runs per `task x prompt condition`.

## 7. Short Meeting Summary

The rerun completed all 12 pilot conditions with zero invalid responses and perfect parse success. Using average outcome metrics makes the results easier to compare later with human datasets. The strongest prompt sensitivity appears in BART, where role and risk framing increase risk-taking. Horizon shows moderate prompt effects on exploration-related metrics, while IGT is relatively stable in advantageous choice rate but varies in post-loss switching. These results support moving to a multi-run pilot and then formal repeated-run experiments.

## 8. Next Steps

1. Implement an aggregation script that converts pilot JSON files into a run-level metrics table.
2. Run a 3-run mini pilot for each `task x prompt condition`.
3. Compute descriptive condition-baseline differences.
4. Use the processed human metrics in `outputs/processed/human_metrics/` for LLM-human comparison.
5. After repeated runs, compute formal Prompt Sensitivity Index values.

## 9. Human Metrics Processing Status

Human datasets have been processed into participant-level metric tables:

| Task | Output file | Participants |
|---|---|---:|
| Horizon | `outputs/processed/human_metrics/horizon_human_metrics.csv` | 60 |
| IGT | `outputs/processed/human_metrics/igt_human_metrics.csv` | 504 |
| BART | `outputs/processed/human_metrics/bart_human_metrics.csv` | 141 |

These tables use metric names aligned with LLM run metrics where possible. Horizon random exploration is now estimated separately from first-free-choice records rather than stored as a participant-level proxy, and BART earnings may reflect dataset-specific scaling. The strongest human-comparison metrics are Horizon exploration metrics, IGT choice/learning metrics, and BART pump-based metrics.
