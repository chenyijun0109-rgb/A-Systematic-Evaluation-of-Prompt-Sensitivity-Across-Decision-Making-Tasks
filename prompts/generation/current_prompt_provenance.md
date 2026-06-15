# Current Prompt Provenance Record

**Record status:** Twelve-prompt matrix reviewed, installed, and frozen  
**Protocol version:** 1.3  
**Protocol adopted:** 2026-06-13  
**Protocol revised:** 2026-06-14  
**Applies to:** Reconstructed canonical baselines and generated candidate variants

## Historical Generation Metadata

| Field | Recorded value |
|---|---|
| Provider/application | `not recorded` |
| Exact generator model | `not recorded` |
| Model snapshot/version | `not recorded` |
| Generation date | `not recorded` |
| Temperature | `not recorded` |
| Top-p | `not recorded` |
| Maximum output tokens | `not recorded` |
| Seed | `not recorded` |
| Exact historical meta-prompt | `not recorded` |
| Number of candidate sets | `not recorded` |
| Historical selection rule | `not recorded` |
| Historical raw responses | `not recorded` |
| Historical manual edits | `not recorded` |

`prompts/generation/meta_prompt_v2.md` was adopted prospectively on
2026-06-13 to generate three variants from each frozen baseline. It must not
be described as the exact historical instruction used to create the removed
prompt files.

## Current Experimental Prompt Inventory

| Task | Condition | Final prompt file | Protocol 1.3 status |
|---|---|---|---|
| Horizon | `baseline` | `prompts/bandit/baseline.md` | Verified and frozen input |
| Horizon | `detailed` | `prompts/bandit/detailed.md` | Generated, reviewed, frozen |
| Horizon | `role_human` | `prompts/bandit/role_human.md` | Generated, minimally edited, frozen |
| Horizon | `uncertainty_emphasis` | `prompts/bandit/uncertainty_emphasis.md` | Generated, reviewed, frozen |
| IGT | `baseline` | `prompts/igt/baseline.md` | Verified and frozen input |
| IGT | `detailed` | `prompts/igt/detailed.md` | Generated, minimally edited, frozen |
| IGT | `role_human` | `prompts/igt/role_human.md` | Generated, minimally edited, frozen |
| IGT | `reward_loss_emphasis` | `prompts/igt/reward_loss_emphasis.md` | Generated, minimally edited, frozen |
| BART | `baseline` | `prompts/bart/baseline.md` | Verified and frozen input |
| BART | `detailed` | `prompts/bart/detailed.md` | Generated, minimally edited, frozen |
| BART | `role_human` | `prompts/bart/role_human.md` | Generated, minimally edited, frozen |
| BART | `risk_emphasis` | `prompts/bart/risk_emphasis.md` | Generated, minimally edited, frozen |

The `baseline_task_named.md` files are retained for a possible future
task-name exposure condition and are not part of the current four-condition
experimental matrix.

## Required Decision Before Formal Data Collection

Choose and record one approach:

- [ ] **Retain and audit:** Keep the historical wording, complete Protocol 1.3
      manual review, disclose the missing historical generation metadata,
      and freeze the final files.
- [x] **Prospective regeneration:** Manually reconstruct and freeze the three
      canonical baselines, then generate nine variants using
      `meta_prompt_v2.md`. Save exact requests and raw outputs, complete
      review records, freeze the generated files, and rerun affected pilots.

**Decision:** Remove the historical prompts, reconstruct the three canonical
baselines from task sources, and generate only the nine manipulated variants
prospectively.  
**Decision date:** 2026-06-13  
**Rationale:** Ensure that the exact generation instruction, model settings,
raw outputs, review decisions, and edits are retained for reproducibility.  
**Researcher:** Project owner  

## Current Operational Status

All four experimental conditions are available for each task. The nine
generated variants were minimally edited where required, installed, tested,
and frozen. Existing historical pilot outputs may be retained as development
records, but they must not be pooled with results from this replacement prompt
version.

The exact baseline hashes and verification results are stored in:

```text
prompts/generation/records/2026-06-13_canonical_baselines/review.md
```

The completed generator configuration was:

```text
requested model: gpt-4o-2024-11-20
reasoning effort: not sent
text verbosity: not sent
temperature: 0.0
top-p: 1.0
candidate sets per task: 1
```

All three API responses returned `gpt-4o-2024-11-20`. The exact requests,
responses, response IDs, and generation records are retained under:

```text
prompts/generation/records/2026-06-14_gpt-4o-2024-11-20/
```

The initial review is recorded in `pre_review.md`. The completed two-stage
review, exact generation settings, task-specific inputs, editing rationale,
technical checks, and final SHA-256 hashes are recorded in:

```text
docs/prompt_generation_and_review_record.md
prompts/generation/records/2026-06-14_gpt-4o-2024-11-20/final_review.md
```

Raw outputs remain unchanged. Under Protocol 1.3, role prompts differ from
baseline only by one role sentence, and task-specific prompts differ only in
one authorised paragraph.
