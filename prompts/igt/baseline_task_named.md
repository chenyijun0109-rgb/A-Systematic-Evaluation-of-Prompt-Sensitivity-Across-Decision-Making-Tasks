# Iowa Gambling Task Baseline Prompt

You are completing a card-selection task.

On each trial, you will choose one deck from four available decks: A, B, C, and D. After each choice, the task environment will return the reward, any loss, and the updated cumulative score.

Use the information shown in the current task state to make your choice.

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

