# Final Prompt Review

**Review date:** 2026-06-14  
**Protocol:** Prompt Generation Protocol 1.3  
**Generation model:** `gpt-4o-2024-11-20`  
**Review method:** Rule-equivalence and manipulation-isolation review performed
under the project owner's instruction, with raw AI outputs retained unchanged  
**Decision:** Pass after factual-equivalence and strict isolation reviews

## Scope and Outcome

| Task | Condition | Outcome |
|---|---|---|
| Horizon | `baseline` | Pass; frozen canonical input unchanged |
| Horizon | `detailed` | Pass; formatting extraction only |
| Horizon | `role_human` | Pass with edit |
| Horizon | `uncertainty_emphasis` | Pass; intended emphasis retained |
| IGT | `baseline` | Pass; frozen canonical input unchanged |
| IGT | `detailed` | Pass with edits |
| IGT | `role_human` | Pass with edits |
| IGT | `reward_loss_emphasis` | Pass with edits |
| BART | `baseline` | Pass; frozen canonical input unchanged |
| BART | `detailed` | Pass with edits |
| BART | `role_human` | Pass with edits |
| BART | `risk_emphasis` | Pass with edit |

## Edit Log

All outer response fences, condition labels, and the generator's constraint
audit were excluded from final prompt files. These are packaging changes, not
prompt-content edits.

| Task / condition | Generated wording | Final wording or action | Reason |
|---|---|---|---|
| Horizon `role_human` | Reward patterns "are different" | Reward patterns "may differ" | Restore the frozen baseline's uncertainty and isolate role framing |
| IGT `detailed` | Each deck "has its own pattern" | Each deck "may have a different pattern" | Avoid strengthening an uncertain task fact |
| IGT `detailed` | Defined net outcome and cumulative-score arithmetic | Retained only the four feedback fields | Detailed wording may organise existing facts but must not add explanations |
| IGT `role_human` | A "unique" reward/loss pattern | A pattern that "may" differ | Restore baseline uncertainty |
| IGT `role_human` | Defined net outcome and cumulative-score arithmetic | Retained only the four feedback fields | Isolate role framing |
| IGT `reward_loss_emphasis` | A "distinct" reward/loss pattern | A pattern that "may" differ | Restore baseline uncertainty while retaining emphasis |
| IGT `reward_loss_emphasis` | Defined net outcome and cumulative-score arithmetic | Retained only emphasised feedback-field names | Prevent new task explanation |
| BART `detailed` | "Be aware" that pumping carries risk | Neutral statement that a pump can cause explosion | Prevent risk emphasis in the detailed condition |
| BART `detailed` | Explosion likelihood may vary | Explosion outcomes are unknown and may differ | Restore the exact factual boundary of the frozen baseline |
| BART `role_human` | "Be aware" that pumping carries risk | Neutral statement that a pump can cause explosion | Isolate role framing |
| BART `role_human` | Explosion chance may differ | Explosion outcomes are unknown and may differ | Restore the exact factual boundary of the frozen baseline |
| BART `risk_emphasis` | Explosion likelihood may vary | Explosion outcomes are unknown and may differ | Retain risk emphasis without changing probability information |

No edit was selected using behavioural pilot results.

## Second Review: Strict Manipulation Isolation

A second review found that the first reviewed candidates still changed the
neutral objective and rewrote non-target text in the role and task-specific
conditions. These changes could confound the intended manipulation.

- Every variant now uses the exact baseline objective sentence.
- Each `role_human` prompt is the complete baseline plus only:
  `Take the role of a human participant completing this task.`
- Each task-specific emphasis prompt is the complete baseline with only one
  authorised paragraph replaced.
- Detailed prompts retain explanatory organisation but use the exact baseline
  objective.

The complete generation settings and both review rounds are documented in:

```text
docs/prompt_generation_and_review_record.md
```

## Final SHA-256 Hashes

| Prompt | SHA-256 |
|---|---|
| `prompts/bandit/baseline.md` | `D9EF2CAF1C1C2C75C6277A51E909BDCE0A3CF77D593E0F5F0FD64374F82BC116` |
| `prompts/bandit/detailed.md` | `1A1374B5AF26F83D9DCF55EA8BC182BA0E0FB85BF2866694A177B5940FC09D40` |
| `prompts/bandit/role_human.md` | `927AE942EFF1763A7D91F4E32FBBB6F72E5987E4BDA9B54D033C77DA02650815` |
| `prompts/bandit/uncertainty_emphasis.md` | `AC93F76FBEF89859B3B92AF3576F47B8474FB95EFDE7BE494EB622E3C0FC7830` |
| `prompts/igt/baseline.md` | `E09F035C448A21D6A0165F8A39D87056FA52AF63A4F59E5DEED833DD311859CE` |
| `prompts/igt/detailed.md` | `2FA981F9FDD93C07074284CC5FA83A76FA55660334F6D80B8CD2D1247745EAD2` |
| `prompts/igt/role_human.md` | `3A76E59C727CE00237940D68B1DCB6C1322F663C8EAADFA741E01EDC1EC6348F` |
| `prompts/igt/reward_loss_emphasis.md` | `08C8B7567BF3A7F398CEA6027AD46F3C3575874019778FEB1C9AC62F5C37D977` |
| `prompts/bart/baseline.md` | `7E78ABDC06504F2B1BDA6C1A7932BBDB88B1DBDC312CF5BE9EA11AB6CC6178EA` |
| `prompts/bart/detailed.md` | `2753C53DA506162626754DD2A92AEF9C129B5E2AAC35E9A5379857B49DC2C9FC` |
| `prompts/bart/role_human.md` | `47CF4DC5F7058FE8B038D19BD79FC012FDDCBC950B2391F101555EF4C6A868A6` |
| `prompts/bart/risk_emphasis.md` | `4CB602FCC67DEEABC5DDAA03DE9F4DC83B6855437230F34DE15083E8D19CE534` |

## Technical Verification

- All 12 experimental prompts contain exactly one `{observation}` placeholder.
- No prompt exposes the canonical task name or configured hidden information.
- Role prompts differ from baseline only by one explicit human-participant
  framing sentence.
- Task-specific prompts differ from baseline only in one authorised paragraph.
- All 12 prompts use the exact same neutral objective sentence.
- `python -m src.run_prompt_dry_run --all-conditions` passed for all 12 prompts.
- Parser checks passed for every configured legal response.

The raw generator outputs remain unchanged in each task's `raw_output.md`.
