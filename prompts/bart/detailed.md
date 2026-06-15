# Balloon Earnings Task

You will complete a total of 40 balloons. For each balloon, you will make a
choice between two actions: either to pump the balloon or to cash out.

Each time you successfully pump the balloon, 0.05 will be added to the
temporary earnings for that specific balloon. After each successful pump, you
will again decide whether to pump the balloon further or to cash out. A pump
can also cause the balloon to explode. If the balloon explodes, all temporary
earnings for that balloon will be lost, and the task will proceed to the next
balloon.

If you choose to cash out, the temporary earnings accumulated for the current
balloon will be added to your total earnings, and the task will move on to the
next balloon.

Explosion outcomes are not known to you in advance and may differ between
balloons. You can use the feedback and outcomes from earlier balloons to
inform your decisions on subsequent balloons.

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
