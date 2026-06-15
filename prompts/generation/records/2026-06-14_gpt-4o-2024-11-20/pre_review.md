# Prompt Generation Pre-Review

**Generation date:** 2026-06-14  
**Model requested:** `gpt-4o-2024-11-20`  
**Model returned:** `gpt-4o-2024-11-20`  
**Protocol:** Prompt Generation Protocol 1.2  
**Status:** Generated successfully; manual review and minimal edits required

## Completeness

- Three API calls completed: Horizon, IGT, and BART.
- Each task produced `detailed`, `role_human`, and its task-specific emphasis
  condition.
- Each generated prompt contains exactly one `{observation}` placeholder.
- Legal response tokens are present in all nine candidates.
- The complete requests, raw responses, extracted outputs, response IDs,
  model identifiers, baseline hashes, and sampling settings were retained.
- No candidate has been installed as a final experimental prompt.

## Initial Findings

### Horizon

- `detailed` is close to the frozen baseline.
- `role_human` changes "may differ" to "are different". Restore the weaker
  baseline wording so the role condition changes only role framing.
- `uncertainty_emphasis` appropriately increases the salience of incomplete
  information, but should be checked against the final manipulation-isolation
  criterion before freezing.

### IGT

- `detailed` explicitly defines net outcome as reward minus loss. Verify that
  this is treated as clarification of displayed feedback rather than an added
  task fact.
- `role_human` changes "may have a different pattern" to "has a unique
  pattern". Restore the baseline uncertainty wording.
- `reward_loss_emphasis` uses "distinct" rather than "may have a different
  pattern". Restore the baseline wording while retaining typographic and
  linguistic emphasis on reward, loss, net outcome, and cumulative score.

### BART

- The candidates say that explosion likelihood or chance may vary between
  balloons. The frozen baseline states that explosion outcomes are unknown
  and may differ between balloons. Restore the exact baseline claim to avoid
  changing the probability description.
- `risk_emphasis` otherwise isolates the intended pump-versus-explosion
  trade-off.

## Formatting Finding

Each raw response wraps the complete answer in an outer Markdown code fence.
The final prompt files must contain only the prompt body for the relevant
condition, without the outer fence, section label, or constraint-audit table.

## Decision

Do not regenerate candidates based on desired behavioural effects. Perform
only documented, minimal edits needed to restore rule equivalence and isolate
the intended manipulation. Then run prompt dry-run and parser tests before
installing and freezing the nine prompt files.
