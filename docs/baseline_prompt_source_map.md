# Canonical Baseline Prompt Source Map

**Date:** 2026-06-13  
**Status:** Canonical baselines constructed; Protocol 1.3 variants reviewed and frozen

## Method

The three baselines combine:

1. task logic from the original literature;
2. record structure from the local human datasets; and
3. exact parameters from the local task environments.

The literature does not justify silently copying parameters from a classic
version when the implemented experiment differs. Project-specific parameters
are therefore labelled as implementation adaptations.

## Shared Design Decisions

| Prompt content | Basis | Boundary |
|---|---|---|
| Finish with as much total reward as possible | Participant-facing objective in reward-based decision tasks; approved project decision | States the task goal without recommending a strategy |
| Outcome patterns are initially unknown | Core learning/uncertainty structure of the three tasks | Does not disclose which option is better |
| Feedback can inform later decisions | All three tasks provide sequential outcome feedback | Does not instruct the model how to use feedback |
| Exact one-line response | Local parser requirement | Held constant across all prompt conditions |
| Canonical task names omitted | Project control against task-name knowledge leakage | Task names remain in documentation, not experimental baselines |

## Horizon Baseline

### Sources

- Wilson, R. C., Geana, A., White, J. M., Ludvig, E. A., & Cohen,
  J. D. (2014). *Humans use directed and random exploration to solve the
  explore-exploit dilemma*. Journal of Experimental Psychology: General.
  https://doi.org/10.1037/a0038199
- `DATASET/BANDIT/allHorizonData_cut.csv`
- `src/tasks/horizon.py`

### Rule mapping

| Baseline statement | Source |
|---|---|
| Choose between two options | Wilson et al. task logic; local environment |
| Four initial forced choices | Wilson et al.; local environment |
| One or six subsequent free choices | Wilson et al.; dataset `gameLength` 5/10; local environment |
| Rewards reveal initially unknown option patterns | Wilson et al.; dataset reward columns; local environment |
| 40 games per run | Project implementation adaptation |
| `CHOICE: A/B` | Local parser and configuration |

The labels `horizon_1`, `horizon_6`, `equal_information`, and
`unequal_information` are analysis variables. They are retained in records
but removed from the participant-facing observation.

## Four-Deck Baseline

### Sources

- Bechara, A., Damasio, A. R., Damasio, H., & Anderson, S. W. (1994).
  *Insensitivity to future consequences following damage to human prefrontal
  cortex*. Cognition.
  https://doi.org/10.1016/0010-0277(94)90018-3
- Steingroever et al. open data in
  `DATASET/IGT/IGTdataSteingroever2014/`
- `src/tasks/igt.py`

### Rule mapping

| Baseline statement | Source |
|---|---|
| Choose repeatedly from four decks | Bechara et al.; human choice data; local environment |
| Decks have unknown reward/loss patterns | Bechara et al.; human win/loss data; local environment |
| Outcome feedback follows each choice | Bechara et al.; human outcome data; local environment |
| 100 choices | Selected 100-trial human subset; local environment |
| Initial score 2000 | Local implementation parameter |
| `CHOICE: A/B/C/D` | Local parser and configuration |

The baseline does not identify C/D as advantageous or reveal the repeating
payoff schedule. Those facts are environment and analysis information.

## Balloon Baseline

### Sources

- Lejuez, C. W., Read, J. P., Kahler, C. W., Richards, J. B.,
  Ramsey, S. E., Stuart, G. L., Strong, D. R., & Brown, R. A. (2002).
  *Evaluation of a behavioral measure of risk taking: The Balloon Analogue
  Risk Task*. Journal of Experimental Psychology: Applied.
  https://doi.org/10.1037/1076-898X.8.2.75
- `DATASET/BART/Dataset.xlsx`
- `src/tasks/bart.py`

### Rule mapping

| Baseline statement | Source |
|---|---|
| Repeated pump-or-cash-out decisions | Lejuez et al.; local dataset; local environment |
| Successful pumps increase temporary earnings | Lejuez et al.; local dataset; local environment |
| Explosion loses current temporary earnings | Lejuez et al.; local dataset; local environment |
| Cashing out banks temporary earnings | Lejuez et al.; local dataset; local environment |
| 40 balloons | Local dataset structure and project implementation |
| 0.05 per successful pump | Project implementation parameter |
| `ACTION: PUMP/CASH_OUT` | Local parser and configuration |

The local implementation uses a hidden increasing explosion probability with
certain explosion at pump 32. These are environment parameters and are not
participant-facing prompt information.

## Variant Generation Boundary

These three files are frozen inputs to the ELM generation process:

```text
prompts/bandit/baseline.md
prompts/igt/baseline.md
prompts/bart/baseline.md
```

ELM will generate nine candidates:

- three `detailed` variants;
- three `role_human` variants;
- Horizon `uncertainty_emphasis`;
- IGT `reward_loss_emphasis`;
- BART `risk_emphasis`.

No generated variant may introduce a fact listed as hidden in this document.
