# Balloon Earnings Task

You will complete 40 balloons. For each balloon, choose either to pump the
balloon or to cash out.

Every successful pump adds 0.05 to the temporary earnings for the current
balloon, and you may then choose again. Pumping therefore involves a
trade-off: it can increase the temporary earnings, but it can also cause the
balloon to explode. If it explodes, the temporary earnings for that balloon
are lost and the task moves to the next balloon.

If you cash out, the current temporary earnings are added to your total
earnings and the task moves to the next balloon.

Explosion outcomes are not known to you in advance and may differ between
balloons. You may use the feedback and displayed outcomes from earlier
balloons when making later choices.

Your aim is to finish the full task with as much total reward as possible.

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
