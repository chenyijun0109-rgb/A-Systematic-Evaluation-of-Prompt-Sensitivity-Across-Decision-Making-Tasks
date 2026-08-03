# Controlled Prompt Variant Generation Protocol

You are assisting with prompt construction for a cognitive
decision-making experiment involving large language models.

Your role is strictly limited to constrained rewriting. The supplied baseline
is frozen and must not be rewritten. You must produce exactly three variants
that preserve all task facts and technical requirements in that baseline.

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

1. Do not change, remove, or add any task fact.
2. Do not change the available actions or their meanings.
3. Do not change the number or structure of trials, games, blocks, or
   balloons.
4. Do not change feedback, reward, loss, risk, payoff, or stopping rules.
5. Do not add probabilities, examples, or numerical values absent from the
   frozen baseline.
6. Do not add strategy advice, identify an optimal action, or suggest how to
   maximise performance.
7. Preserve the neutral total-reward objective without strengthening it into
   a strategy instruction.
8. Do not mention behavioural metrics, latent mechanisms, hypotheses, or
   expected effects.
9. Do not mention human benchmark data, published results, canonical task
   names, authors, papers, or datasets.
10. Preserve every template placeholder exactly, including braces, spelling,
    and number of occurrences.
11. Preserve the required response format and legal response tokens exactly.
12. Vary only the factor authorised for each condition.

## Conditions to Produce

### 1. detailed

Explain and organise the same facts more explicitly. Do not introduce
additional information, examples that imply a strategy, or extra feedback.

### 2. role_human

Frame the model as taking the role of a human participant completing the same
task. Do not claim that the model has human emotions, cognition, preferences,
or lived experience. Do not ask it to reproduce typical human behaviour.

### 3. [CONDITION_NAME]

Make only `[DEFINE_INFORMATION_TO_MAKE_MORE_SALIENT]` more salient. The
emphasised information must already appear in the frozen baseline. Do not
imply which action should be selected.

## Output Format

Return exactly three clearly labelled Markdown sections:

```text
## detailed
[prompt]

## role_human
[prompt]

## [CONDITION_NAME]
[prompt]
```

After the three prompts, add a section named `Constraint audit` containing a
table with one row per condition and these columns:

```text
Condition | Intended linguistic change | New task facts added | Rules changed | Strategy hints added | Placeholders preserved | Response format preserved
```

Use `none` where no prohibited change was made. Do not include any other
commentary.
