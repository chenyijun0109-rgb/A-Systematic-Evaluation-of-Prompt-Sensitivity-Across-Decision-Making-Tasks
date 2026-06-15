# Canonical Baseline Prompts Design

**Date:** 2026-06-13  
**Status:** Approved design  
**Scope:** Three neutral baseline prompts and the Horizon participant-facing observation

## 1. Goal

Create one canonical baseline prompt for each task before using the university
ELM to generate nine controlled variants. Each baseline must be:

- complete enough to perform the task;
- concise and neutral;
- consistent with the local environment;
- traceable to the original literature and local human dataset;
- free of strategy hints, behavioural metrics, task names, and hidden rules.

## 2. Evidence Rule

The source hierarchy is:

1. Original task literature defines the task logic.
2. Human dataset structure confirms the comparable trial and outcome records.
3. The local environment defines the exact parameters used in this project.

Where the implementation differs from a classic version, the prompt describes
the implemented task and the adaptation is documented outside the prompt.

Primary task sources:

- Wilson et al. (2014), *Humans use directed and random exploration to solve
  the explore-exploit dilemma*, https://doi.org/10.1037/a0038199
- Bechara et al. (1994), *Insensitivity to future consequences following
  damage to human prefrontal cortex*,
  https://doi.org/10.1016/0010-0277(94)90018-3
- Lejuez et al. (2002), *Evaluation of a behavioral measure of risk taking:
  The Balloon Analogue Risk Task*,
  https://doi.org/10.1037/1076-898X.8.2.75

Local comparison data:

- `DATASET/BANDIT/allHorizonData_cut.csv`
- `DATASET/IGT/IGTdataSteingroever2014/`
- `DATASET/BART/Dataset.xlsx`

## 3. Common Baseline Rules

All three baselines:

- state the neutral objective: finish with as much total reward as possible;
- explain that options may have different, initially unknown outcome patterns;
- state that feedback can be used to learn about those patterns;
- include all facts needed to perform the task;
- preserve the `{observation}` placeholder;
- require exactly one parser-compatible response;
- do not reveal an optimal strategy or human benchmark.

The objective is a task goal, not a strategy instruction. It must not be
strengthened into wording such as "always choose the optimal option" or
"maximise every individual decision."

## 4. Horizon Baseline

Participant-visible content:

- The run contains 40 independent games.
- Every game contains four initial forced choices.
- The observation explicitly states which option must be chosen during a
  forced choice.
- After the forced choices, the game contains either one or six free choices.
- A and B may have different unknown reward patterns.
- Every choice returns the reward from the selected option.
- The displayed reward history and remaining choices can inform decisions.
- Valid outputs are `CHOICE: A` and `CHOICE: B`.

Hidden content:

- The canonical task name.
- `horizon_1`, `horizon_6`, `equal_information`, and
  `unequal_information` analysis labels.
- True option means and reward-distribution parameters.
- Directed exploration, random exploration, decision noise, or other metrics.

The observation must replace analysis labels with:

- `Choices remaining in this game: N`
- observed rewards for A and B;
- either the required forced option or a free-choice statement.

## 5. IGT Baseline

Participant-visible content:

- The task contains 100 choices.
- The starting cumulative score is 2000.
- Each trial requires one choice from A, B, C, or D.
- Decks may have different, initially unknown gain and loss patterns.
- Feedback reports reward, loss, net outcome, and cumulative score.
- Previous outcomes and the displayed history can inform later choices.
- Valid outputs are `CHOICE: A`, `B`, `C`, or `D`.

Hidden content:

- The canonical task name.
- The full payoff schedule.
- The labels advantageous/disadvantageous.
- The fact that C and D have positive long-run expected outcomes.
- Learning-curve or switching metrics.

## 6. BART Baseline

Participant-visible content:

- The run contains 40 balloons.
- Each balloon permits `PUMP` or `CASH_OUT`.
- Every successful pump adds 0.05 to temporary earnings.
- A pump can explode the balloon.
- Explosion loses the current balloon's temporary earnings and ends it.
- Cashing out banks the current temporary earnings and ends the balloon.
- Balloons may have unknown explosion outcomes; feedback and prior balloon
  outcomes are displayed.
- Valid outputs are `ACTION: PUMP` and `ACTION: CASH_OUT`.

Hidden content:

- The canonical task name.
- The explosion probability formula.
- The hidden explosion point.
- The certain-explosion pump.
- Risk-taking metrics or a recommended cash-out threshold.

## 7. Detailed-Condition Boundary

Each baseline must already contain all participant-facing task facts. The
future `detailed` variant may reorganise, clarify, and expand the explanation
of those same facts, but may not introduce additional task information.

This makes wording/detail the intended manipulation instead of confounding it
with information availability.

## 8. Files

Create:

- `prompts/bandit/baseline.md`
- `prompts/igt/baseline.md`
- `prompts/bart/baseline.md`
- `docs/baseline_prompt_source_map.md`

Modify:

- `src/tasks/horizon.py`
- `tests/test_horizon.py`
- `tests/test_prompt_dry_run.py`
- `configs/experiment_config_stage01.json`
- `prompts/generation/current_prompt_provenance.md`
- `README.md`
- `docs/research_log.md`

## 9. Acceptance Criteria

- All three baseline files contain exactly one `{observation}` placeholder.
- Prompt dry-run replaces every placeholder.
- Every configured legal output parses successfully.
- Horizon observations do not contain the four analysis labels.
- Horizon observations report remaining choices accurately.
- Baselines contain the approved task objective and unknown-pattern wording.
- Baselines contain no task name, metric name, hidden payoff, or hidden
  explosion information.
- Existing task and parser tests remain green.

