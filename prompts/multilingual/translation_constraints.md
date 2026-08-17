# Multilingual Prompt Translation and Variant Constraints

Status: frozen before multilingual prompt creation  
Source language: English (`en`)  
Target languages: Simplified Chinese (`zh-CN`) and Spanish (`es`)  
Scope: the 12 active experimental prompts for Horizon, IGT, and BART

## Purpose

The multilingual prompts must vary participant-facing language without changing
the task, information available to the model, response parser, or intended
prompt manipulation. English remains the canonical source. Target-language
baselines are created first; every target-language variant is then derived from
its reviewed target-language baseline rather than translated independently.

## Required derivation order

1. Freeze and hash the active English baseline for each task.
2. Translate that baseline into `zh-CN` and `es` under the baseline constraints
   below.
3. Review each translated baseline against the English source clause by clause.
4. Freeze and hash the reviewed translated baseline.
5. Derive `role_human` by adding only the authorised role sentence.
6. Derive the task-specific emphasis condition by replacing only the authorised
   paragraph.
7. Derive `detailed` by expanding and reorganising only facts already present in
   that language's baseline.
8. Run structural, parser-token, hidden-information, and source-equivalence
   audits before making a prompt available to the runner.

Independent translation of the English variants is prohibited because it can
introduce uncontrolled wording differences between conditions.

## Invariants for every language and condition

- Preserve all task facts, quantities, option labels, trial counts, reward
  values, and uncertainty statements.
- Preserve exactly one `{observation}` placeholder, including its ASCII braces
  and spelling.
- Preserve the valid output strings byte-for-byte:
  - Horizon: `CHOICE: A`, `CHOICE: B`
  - IGT: `CHOICE: A`, `CHOICE: B`, `CHOICE: C`, `CHOICE: D`
  - BART: `ACTION: PUMP`, `ACTION: CASH_OUT`
- Tell the model to return exactly one valid response with no additional text.
- Preserve the neutral objective: finish the complete task with as much total
  reward as possible.
- Do not translate option/deck labels `A`, `B`, `C`, or `D`.
- Do not translate the parser tokens `CHOICE`, `ACTION`, `PUMP`, or `CASH_OUT`.
- Do not add examples of decisions, recommended strategies, explanations of
  optimal behaviour, behavioural metrics, hypotheses, or human benchmarks.
- Do not name the classic task in active experimental prompts.
- Do not reveal implementation-only condition labels, payoff schedules, true
  reward means, probability formulas, explosion thresholds, advantageous decks,
  or latent cognitive mechanisms.
- Use neutral, standard written language. Avoid regional slang, idioms, gendered
  participant assumptions, honorifics, or persuasive language absent from the
  English source.
- Keep Markdown structure and code fences functionally equivalent.

## Baseline translation constraints

The translated baseline must be clause-level meaning-equivalent to the frozen
English baseline. Natural target-language syntax is allowed, but compression,
elaboration, interpretation, and emphasis are not. In particular:

- modal strength must be preserved (`may`, `can`, and mandatory instructions
  must not be strengthened or weakened);
- statements about unknown information must remain unknown rather than becoming
  probabilistic advice;
- feedback availability must not become a recommendation for how to use it;
- the objective must not become an instruction to maximise a disclosed metric.

## Condition-specific authorised changes

### `role_human`

Add exactly one sentence after the title and before the baseline body:

- `zh-CN`: the role instruction is translated as "You will answer as a human
  participant completing this task." (canonical Chinese wording is retained in
  the frozen zh-CN prompt files)
- `es`: `Asume el papel de un participante humano que está completando esta tarea.`

After removing this sentence and its following blank line, the file must be
byte-identical to the reviewed baseline in the same language.

### Horizon `uncertainty_emphasis`

Only the baseline paragraph describing unknown reward patterns and observed
rewards may change. The replacement may state that each observation supplies
only partial information and may call the available information incomplete. It
must not mention exploration, uncertainty bonuses, reward distributions, true
means, or a recommended choice rule.

### IGT `reward_loss_emphasis`

Only the baseline paragraph describing deck selection and feedback may change.
The replacement may direct particular attention to the already-displayed
reward, loss, net outcome, and cumulative score. It must not identify good or
bad decks, disclose the payoff schedule, or define a learning strategy.

### BART `risk_emphasis`

Only the baseline paragraph describing pumping consequences may change. The
replacement may explicitly call pumping a trade-off between increased temporary
earnings and possible explosion. It must not disclose explosion probabilities,
thresholds, expected values, or a cash-out strategy.

### `detailed`

The detailed condition may split, reorder, and restate baseline facts for
clarity. Every factual proposition must be traceable to the reviewed baseline in
the same language. It may not add salience instructions such as "pay particular
attention", human-role framing, strategic advice, or task-specific emphasis
language reserved for another condition.

## Language-specific quality rules

### Simplified Chinese (`zh-CN`)

- Use simplified characters and standard Mainland written Chinese.
- Translate `reward`, `loss`, `net outcome`, `cumulative score`, `temporary
  earnings`, and `total earnings` consistently within a task.
- Keep Arabic numerals and decimal `0.05` unchanged.

### Spanish (`es`)

- Use neutral international Spanish and `usted`-neutral imperative phrasing
  without regional vocabulary.
- Keep terminology for reward, loss, net outcome, cumulative score, temporary
  earnings, and total earnings consistent within a task.
- Keep Arabic numerals and decimal point `0.05` unchanged.

## Required audit record

For every generated file, record:

- target language, task, and condition;
- canonical English source path and SHA-256;
- target-language baseline parent path and SHA-256 for variants;
- generation date and method;
- placeholder count;
- parser-token preservation result;
- condition-isolation result;
- hidden-information review result;
- reviewer/status field.

No multilingual prompt is considered frozen merely because it exists on disk.
It becomes eligible for an experiment only after all automated checks pass and
its audit status is recorded as reviewed.
