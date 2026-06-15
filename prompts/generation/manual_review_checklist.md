# Prompt Variant Manual Review Checklist

**Task:**  
**Generation record:**  
**Reviewer:**  
**Date:**  

Complete this checklist separately for each condition.

## Condition

```text
[baseline / detailed / role_human / task-specific condition]
```

## Rule Equivalence

- [ ] Available actions and their meanings are unchanged.
- [ ] Trial, game, block, or balloon structure is unchanged.
- [ ] Reward, loss, probability, feedback, and stopping rules are unchanged.
- [ ] No factual task information has been added or removed.
- [ ] The prompt agrees with the canonical specification and implementation.

## Manipulation Isolation

- [ ] Only the intended linguistic factor differs from baseline.
- [ ] No optimal strategy or preferred action is stated or implied.
- [ ] No behavioural metric or latent mechanism is named.
- [ ] No human benchmark or published result is revealed.
- [ ] No original task name, author, paper, or dataset is revealed.
- [ ] The prompt does not ask the model to reproduce human results.

## Technical Integrity

- [ ] All placeholders are preserved exactly.
- [ ] Required response syntax is unchanged.
- [ ] Legal response tokens match the parser.
- [ ] Formatting does not interfere with observation insertion or parsing.

## Decision

- [ ] PASS
- [ ] PASS WITH EDITS
- [ ] REJECT

**Reason and required edits:**

```text

```

