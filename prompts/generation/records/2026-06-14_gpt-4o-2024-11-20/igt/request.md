# Prompt Generation Meta-Prompt v2.0

You are assisting with prompt construction for a cognitive
decision-making experiment involving large language models.

Your role is strictly limited to constrained rewriting. The supplied baseline
is frozen and must not be rewritten. You must produce exactly three variants
that preserve all task facts and technical requirements in that baseline.

## Inputs

Task identifier:

```text
four_deck_reward_task
```

Canonical task specification:

```text
The frozen baseline is the complete participant-facing specification. It describes 100 choices, a starting score of 2000, four decks with initially unknown reward and loss patterns, outcome feedback, and the exact response format. Do not identify advantageous decks, reveal the payoff schedule, introduce behavioural metrics, or recommend a deck.
```

Frozen baseline prompt:

```text
# Four-Deck Reward Task

You will make 100 choices. Your cumulative score starts at 2000.

On each trial, choose one of four decks: A, B, C, or D. Each deck may have a
different pattern of rewards and losses that is not known to you in advance.
After every choice, you are shown the reward, any loss, the net outcome, and
your updated cumulative score. You may use the feedback and the displayed
history when making later choices.

Your aim is to finish the full task with as much total reward as possible.

Current task state:

```text
{observation}
```

Valid responses:

```text
CHOICE: A
CHOICE: B
CHOICE: C
CHOICE: D
```

Respond with exactly one valid response and no additional text.

```

Task-specific emphasis condition:

```text
Condition name: reward_loss_emphasis
Permitted emphasis: the rewards, losses, net outcomes, and cumulative consequences already described in the frozen baseline
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

### 3. reward_loss_emphasis

Make only `the rewards, losses, net outcomes, and cumulative consequences already described in the frozen baseline` more salient. The
emphasised information must already appear in the frozen baseline. Do not
imply which action should be selected.

## Output Format

Return exactly three clearly labelled Markdown sections:

```text
## detailed
[prompt]

## role_human
[prompt]

## reward_loss_emphasis
[prompt]
```

After the three prompts, add a section named `Constraint audit` containing a
table with one row per condition and these columns:

```text
Condition | Intended linguistic change | New task facts added | Rules changed | Strategy hints added | Placeholders preserved | Response format preserved
```

Use `none` where no prohibited change was made. Do not include any other
commentary.

