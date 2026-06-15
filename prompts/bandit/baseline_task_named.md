# Horizon Task Baseline Prompt

You are completing a two-option decision-making task.

On each decision, you will choose between option A and option B. After a choice is made, the task environment will return the reward for the chosen option.

Some trials may be forced-choice trials. If the current trial specifies a required option, you must choose that required option. Otherwise, choose either A or B.

Use the information shown in the current task state to make your choice.

Current task state:

```text
{observation}
```

Valid responses:

```text
CHOICE: A
CHOICE: B
```

Respond with exactly one valid response and no additional text.

