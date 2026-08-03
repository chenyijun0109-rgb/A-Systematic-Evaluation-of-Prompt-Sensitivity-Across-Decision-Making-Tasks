# Metric Notes For LLM-Human Comparison

This note records how the current human-comparison metrics should be interpreted.

| Task | Metric | Comparison type |
|---|---|---|
| Horizon | `directed_exploration` | participant-level human CSV vs LLM run-level metrics |
| Horizon | `horizon_effect` | participant-level human CSV vs LLM run-level metrics |
| Horizon | `random_exploration_effect` | human model run estimates vs LLM run-level model estimates |
| IGT | `advantageous_choice_rate` | participant-level human CSV vs LLM run-level metrics |
| IGT | `post_loss_switching_rate` | participant-level human CSV vs LLM run-level metrics |
| BART | `adjusted_average_pumps` | participant-level human CSV vs LLM run-level metrics |
| BART | `explosion_rate` | participant-level human CSV vs LLM run-level metrics |
| BART | `post_explosion_adjustment` | participant-level human CSV vs LLM run-level metrics |

`random_exploration_effect` is not a raw participant CSV column. It is produced
by the Horizon first-free-choice logistic model for both human participants and
LLM runs, so it should be interpreted as a model-derived comparison.
