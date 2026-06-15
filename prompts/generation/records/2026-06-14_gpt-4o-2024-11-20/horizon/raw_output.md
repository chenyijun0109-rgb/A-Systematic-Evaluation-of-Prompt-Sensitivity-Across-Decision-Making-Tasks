```markdown
## detailed
# Two-Option Reward Task

You will complete 40 separate games. Each game consists of a series of choices between two options: option A and option B.

At the start of each game, you will make four forced choices. During these forced-choice trials, the current task state will specify which option you must select. After completing these four forced choices, you will proceed to make either one or six free choices, where you can freely choose between option A and option B.

Within each game, the reward patterns for options A and B may differ, and these patterns are not revealed to you beforehand. After every choice you make, you will receive feedback showing the reward associated with the option you selected. You can use the rewards you observe, along with the number of remaining choices in the current game, to inform your subsequent decisions.

Your objective is to complete all 40 games and achieve the highest total reward possible.

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

## role_human
# Two-Option Reward Task

You are participating in a task that involves completing 40 separate games. In each game, you will make a series of decisions between two options: option A and option B.

At the beginning of each game, you will make four forced choices. During these forced-choice trials, the task will specify which option you must select. After these four forced choices, you will make either one or six free choices, where you can decide freely between option A and option B.

The reward patterns for options A and B in each game are different and are not known to you in advance. After each choice, you will see the reward associated with the option you selected. You can use the rewards you observe and the number of remaining choices in the current game to guide your decisions.

Your goal is to complete all 40 games and maximize the total reward you earn.

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

## uncertainty_emphasis
# Two-Option Reward Task

You will complete 40 separate games. In each game, you will make a series of choices between two options: option A and option B.

Each game begins with four forced-choice trials. During these trials, the task will specify which option you must select. After completing these four forced choices, you will make either one or six free choices, where you can freely choose between option A and option B.

The reward patterns for options A and B in each game are initially unknown to you. After each choice, you will see the reward associated with the option you selected. However, the observed rewards provide only partial information about the underlying reward patterns for A and B. You can use this incomplete information, along with the number of remaining choices in the current game, to guide your decisions.

Your objective is to complete all 40 games and achieve the highest total reward possible.

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

## Constraint audit

| Condition           | Intended linguistic change                                      | New task facts added | Rules changed | Strategy hints added | Placeholders preserved | Response format preserved |
|----------------------|---------------------------------------------------------------|----------------------|---------------|----------------------|------------------------|---------------------------|
| detailed            | Explained and organized the same facts more explicitly         | none                | none          | none                 | yes                    | yes                       |
| role_human          | Framed the task as if the model were a human participant       | none                | none          | none                 | yes                    | yes                       |
| uncertainty_emphasis | Highlighted the initially unknown reward patterns and incomplete information | none                | none          | none                 | yes                    | yes                       |
```