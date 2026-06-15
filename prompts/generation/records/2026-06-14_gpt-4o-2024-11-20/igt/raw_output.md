```markdown
## detailed
# Four-Deck Reward Task

You will make a total of 100 choices during this task. Your cumulative score begins at 2000 points.

On each trial, you will select one of four decks: A, B, C, or D. Each deck has its own pattern of rewards and losses, but these patterns are not known to you at the start of the task. After making a choice, you will receive feedback that includes the following information:
- The reward you received from the chosen deck.
- Any loss associated with the chosen deck.
- The net outcome, which is the reward minus the loss.
- Your updated cumulative score, which reflects the net outcome added to or subtracted from your previous score.

You can use the feedback provided after each choice, as well as the history of your previous choices and outcomes, to inform your decisions in subsequent trials.

Your goal is to complete all 100 trials with the highest cumulative score possible.

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

## role_human
# Four-Deck Reward Task

You are participating in a task where you will make 100 choices. Your cumulative score starts at 2000 points.

On each trial, you will choose one of four decks: A, B, C, or D. Each deck has a unique but initially unknown pattern of rewards and losses. After each choice, you will receive feedback that includes:
- The reward you earned from the deck you selected.
- Any loss associated with that deck.
- The net outcome, which is the reward minus the loss.
- Your updated cumulative score, which reflects the net outcome added to or subtracted from your previous score.

You can use the feedback and the history of your choices to guide your decisions as you progress through the task.

Your objective is to finish all 100 trials with the highest cumulative score you can achieve.

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

## reward_loss_emphasis
# Four-Deck Reward Task

You will make 100 choices in this task. Your cumulative score starts at 2000 points.

On each trial, you will select one of four decks: A, B, C, or D. Each deck has a distinct but initially unknown pattern of rewards and losses. After every choice, you will receive detailed feedback, including:
- **The reward** you earned from the deck you selected.
- **Any loss** associated with that deck.
- **The net outcome**, which is the reward minus the loss.
- **Your updated cumulative score**, which reflects the net outcome added to or subtracted from your previous score.

This feedback, along with the history of your previous choices and outcomes, is available for you to consider when making future decisions.

Your goal is to complete all 100 trials with the highest cumulative score possible.

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

## Constraint audit
| Condition            | Intended linguistic change                     | New task facts added | Rules changed | Strategy hints added | Placeholders preserved | Response format preserved |
|-----------------------|-----------------------------------------------|----------------------|---------------|-----------------------|------------------------|---------------------------|
| detailed             | More explicit and organized explanation       | none                | none          | none                 | yes                    | yes                       |
| role_human           | Framed task as if model is a human participant | none                | none          | none                 | yes                    | yes                       |
| reward_loss_emphasis | Emphasized rewards, losses, net outcomes, and cumulative consequences | none                | none          | none                 | yes                    | yes                       |
```