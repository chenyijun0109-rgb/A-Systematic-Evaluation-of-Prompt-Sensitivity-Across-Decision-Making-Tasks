```text
## detailed
# Balloon Earnings Task

You will complete a total of 40 balloons. For each balloon, you will make a choice between two actions: either to pump the balloon or to cash out.

Each time you successfully pump the balloon, 0.05 will be added to the temporary earnings for that specific balloon. After each successful pump, you will again decide whether to pump the balloon further or to cash out. However, be aware that pumping the balloon carries a risk: it may cause the balloon to explode. If the balloon explodes, all temporary earnings for that balloon will be lost, and the task will proceed to the next balloon.

If you choose to cash out, the temporary earnings accumulated for the current balloon will be added to your total earnings, and the task will move on to the next balloon.

The likelihood of a balloon exploding is not known to you in advance and may vary between balloons. You can use the feedback and outcomes from earlier balloons to inform your decisions on subsequent balloons.

Your goal is to complete the task with the highest possible total reward.

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

## role_human
# Balloon Earnings Task

You are participating in a task involving 40 balloons. For each balloon, you will decide whether to pump the balloon or to cash out.

Each successful pump adds 0.05 to the temporary earnings for the current balloon. After each pump, you will decide again whether to pump further or to cash out. Be aware that pumping the balloon carries a risk: it may cause the balloon to explode. If the balloon explodes, all temporary earnings for that balloon will be lost, and you will move on to the next balloon.

If you choose to cash out, the temporary earnings for the current balloon will be added to your total earnings, and you will proceed to the next balloon.

The chance of a balloon exploding is unknown to you and may differ between balloons. You can use the feedback and outcomes from earlier balloons to guide your decisions as you progress through the task.

Your objective is to complete the task with as much total reward as possible.

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

## risk_emphasis
# Balloon Earnings Task

You will complete 40 balloons. For each balloon, you will choose whether to pump the balloon or to cash out.

Each successful pump increases the temporary earnings for the current balloon by 0.05. After each pump, you will decide whether to pump again or to cash out. However, pumping the balloon comes with a trade-off: while it increases temporary earnings, it also carries the risk of causing the balloon to explode. If the balloon explodes, all temporary earnings for that balloon will be lost, and the task will move to the next balloon.

If you cash out, the temporary earnings for the current balloon will be added to your total earnings, and the task will proceed to the next balloon.

The likelihood of a balloon exploding is not known to you in advance and may vary between balloons. You can use the feedback and outcomes from earlier balloons to inform your decisions on subsequent balloons.

Your goal is to complete the task with the highest possible total reward.

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

## Constraint audit
| Condition      | Intended linguistic change                                   | New task facts added | Rules changed | Strategy hints added | Placeholders preserved | Response format preserved |
|----------------|-------------------------------------------------------------|----------------------|---------------|-----------------------|------------------------|---------------------------|
| detailed       | More explicit and organized explanation of task facts       | none                 | none          | none                  | yes                    | yes                       |
| role_human     | Framed task as if the model is a human participant           | none                 | none          | none                  | yes                    | yes                       |
| risk_emphasis  | Emphasized the trade-off between pumping and explosion risk | none                 | none          | none                  | yes                    | yes                       |
```