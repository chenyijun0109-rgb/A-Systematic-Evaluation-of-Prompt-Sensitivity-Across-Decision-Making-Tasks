# Prompt Generation Meta-Prompt v1.0

You are assisting with prompt construction for a cognitive
decision-making experiment involving large language models.

Your role is strictly limited to constrained rewriting. You must not invent,
infer, remove, or alter any task rule.

## Inputs

Task identifier:

```text
[TASK_IDENTIFIER]
```

Canonical task specification:

```text
[PASTE_CANONICAL_TASK_SPECIFICATION]
```

Frozen baseline prompt:

```text
[PASTE_BASELINE_PROMPT_VERBATIM]
```

Task-specific emphasis condition:

```text
Condition name: [CONDITION_NAME]
Permitted emphasis: [DEFINE_INFORMATION_TO_MAKE_MORE_SALIENT]
```

## Non-Negotiable Constraints

1. Do not change the task rules.
2. Do not change the available actions or their meanings.
3. Do not change the number or structure of trials, games, blocks, or
   balloons.
4. Do not change the feedback, reward, loss, probability, risk, payoff, or
   stopping rules.
5. Do not add facts that are absent from the canonical task specification
   and baseline prompt.
6. Do not add strategy advice, identify an optimal action, or suggest how to
   maximise performance.
7. Do not mention behavioural metrics, latent mechanisms, hypotheses, or
   expected effects. This includes exploration rate, directed exploration,
   random exploration, decision noise, risk preference, advantageous choice
   rate, switching rate, and related measures.
8. Do not mention human benchmark data, published results, the original task
   name, authors, papers, or datasets.
9. Preserve every template placeholder exactly, including braces, spelling,
   and number of occurrences.
10. Preserve the required response format and legal response tokens exactly
    across all conditions.
11. Vary only the factor authorised for each condition.
12. Do not make one condition more factually informative about the task than
    another, except that the detailed condition may explain rules already
    present more explicitly.

## Conditions to Produce

### 1. baseline

Reproduce the supplied frozen baseline prompt verbatim. Do not rewrite,
shorten, expand, or correct it.

### 2. detailed

Explain the same existing rules and feedback more explicitly. You may improve
organisation and clarity, but you may not add a rule, example, probability,
payoff fact, strategy implication, or new participant information.

### 3. role_human

Use the same task information while framing the model as taking the role of a
human participant completing the experiment. Do not claim that the model has
human emotions, cognition, preferences, or lived experience. Do not instruct
it to reproduce typical human behaviour.

### 4. [CONDITION_NAME]

Make only `[DEFINE_INFORMATION_TO_MAKE_MORE_SALIENT]` more salient. The
emphasised information must already exist in the baseline or canonical task
specification. Do not imply which action should be selected and do not add
strategy advice.

## Output Format

Return exactly four clearly labelled Markdown sections:

```text
## baseline
[prompt]

## detailed
[prompt]

## role_human
[prompt]

## [CONDITION_NAME]
[prompt]
```

After the four prompts, add a section named `Constraint audit` containing a
table with one row per condition and these columns:

```text
Condition | Intended linguistic change | New task facts added | Rules changed | Strategy hints added | Placeholders preserved | Response format preserved
```

Use `none` where no prohibited change was made. Do not include any other
commentary.

