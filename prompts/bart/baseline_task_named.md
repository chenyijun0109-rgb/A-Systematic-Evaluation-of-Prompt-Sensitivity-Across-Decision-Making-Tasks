# Balloon Analogue Risk Task Baseline Prompt

You are completing a balloon decision-making task.

For each balloon, you can choose to pump the balloon or cash out.

If you choose PUMP and the balloon does not explode, the temporary earning for the current balloon increases and you continue with the same balloon.

If you choose PUMP and the balloon explodes, the temporary earning for the current balloon is lost and the task moves to the next balloon.

If you choose CASH_OUT, the temporary earning for the current balloon is added to the total earning and the task moves to the next balloon.

Use the information shown in the current task state to make your action.

Current task state:

```text
{observation}
```

Valid responses:

```text
ACTION: PUMP
ACTION: CASH_OUT
```

Respond with exactly one valid response and no additional text.

