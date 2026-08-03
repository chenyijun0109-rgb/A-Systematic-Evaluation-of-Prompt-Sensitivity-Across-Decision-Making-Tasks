# Prompt Generation Protocol

**Protocol version:** 1.3  
**Adopted:** 2026-06-13  
**Revised:** 2026-06-14  
**Purpose:** Reproducible construction of the four prompt conditions used in each task

## 1. Methodological Position

The prompt-generation LLM is used as a **constrained rewriting tool**, not as
the designer of the cognitive tasks.

Task rules, available actions, trial structure, feedback, payoff rules,
stopping rules, and response format must first be fixed from the original task
paper, the open-data documentation, and the local task implementation. The
generator may vary only the intended linguistic factor.

Therefore:

- Task content is literature- and implementation-derived.
- The LLM generates candidate wording variants under explicit constraints.
- Human review checks rule equivalence and manipulation isolation.
- The final prompts actually used in the experiment are frozen and retained.

The generator must never infer or introduce a task rule that is absent from
the canonical task specification.

## 2. Source Hierarchy

Prompt content is checked against the following sources, in order:

1. Original task paper and participant-facing task description.
2. Documentation accompanying the human dataset.
3. Frozen project task parameters and implemented environment.
4. Canonical baseline prompt.

If these sources disagree, the discrepancy must be resolved and recorded
before prompt variants are generated.

The task literature supports the task design. Literature about prompting or
persona effects supports the decision to study linguistic manipulations, but
does not supply new task rules.

## 3. Baseline Construction

For each task, a researcher first constructs a neutral baseline containing
only information that a participant needs:

- Current task goal as presented to participants.
- Available actions.
- Feedback visible after an action.
- Trial, game, or balloon continuation rule.
- Stopping or completion rule.
- Required response format.
- The observation placeholder used by the runner.

The baseline must not:

- Reveal the canonical task name.
- Mention the original paper or dataset.
- Mention behavioural metrics or latent mechanisms.
- Describe an optimal strategy.
- Ask the model to imitate published human results.
- Add psychological interpretation.

The baseline is reviewed against the implemented environment before it is
used as input to prompt generation.

## 4. Prompt Conditions

The project uses four conditions per task:

| Condition | Permitted change | Prohibited change |
|---|---|---|
| `baseline` | Neutral, concise participant-facing wording | Added detail, role framing, emphasis, strategy |
| `detailed` | Clearer and more explicit explanation of rules already present | New rules, examples implying a strategy, extra feedback |
| `role_human` | Frame the model as a human participant completing the task | Claims that the LLM has human cognition, emotions, or preferences |
| Task-specific emphasis | Increase salience of information already present | New information, recommended actions, optimal-strategy hints |

The fourth condition is task-specific:

| Task | Condition | Intended manipulation |
|---|---|---|
| Horizon | `uncertainty_emphasis` | Make existing uncertainty and incomplete information more salient |
| IGT | `reward_loss_emphasis` | Make existing rewards and losses more salient |
| BART | `risk_emphasis` | Make existing risk and possible explosion more salient |

The fourth condition is not one interchangeable generic prompt. Its wording
must remain tied to the information already visible in the corresponding
task.

## 5. Exact Meta-Prompt

The exact reusable instruction is stored at:

```text
prompts/generation/controlled_prompt_variant_generation_protocol.md
```

The following inputs must be inserted without paraphrasing:

- Task identifier used by the project.
- Canonical task specification.
- Frozen baseline prompt.
- Name and definition of the task-specific emphasis.

The generator is asked for one candidate set containing three variants. The
baseline is a frozen researcher-constructed input and is not regenerated.
Across three tasks this produces nine generated prompts.

## 6. Generation Settings

Every generation event must record:

| Field | Required record |
|---|---|
| Provider | API or application used |
| Model | Exact model identifier if available |
| Model snapshot/version | Exact snapshot, or `not exposed by provider` |
| Generation date and time | ISO 8601 with time zone |
| System prompt | Full text, or `none` |
| Meta-prompt version | File path and version |
| Temperature | Exact value |
| Top-p | Exact value |
| Maximum output tokens | Exact value |
| Seed | Exact value if supported; otherwise `not supported` |
| Number of candidate sets | Count generated for each task |
| Selection rule | How the retained candidate was selected |
| Reviewer | Person who performed the manual check |
| Manual edits | Exact before/after record and reason |

The planned generator is the fixed GPT-4o snapshot below:

```text
model = gpt-4o-2024-11-20
reasoning.effort = not sent
text.verbosity = not sent
max_output_tokens = 6000
temperature = 0.0
top_p = 1.0
candidate sets per task = 1
```

The fixed snapshot avoids future changes to the `gpt-4o` alias.
`temperature = 0.0` is the active sampling control used to minimise
stochastic variation; `top_p = 1.0` is retained as a neutral, non-truncating
setting. Both values are sent and recorded. Reproducibility also depends on
retaining the complete request, raw response, returned model identifier, and
final prompt files; exact byte-for-byte reproduction is not assumed.

Use:

```text
prompts/generation/generation_record_template.md
```

for each generation event.

## 7. Raw Output and Selection

For each task:

1. Generate the complete three-variant candidate set in one request.
2. Save the unedited request and raw response.
3. Do not repeatedly generate candidates until a preferred behavioural
   wording appears.
4. If multiple candidate sets were planned, state the number in advance.
5. Select using the rule-consistency checklist, not pilot performance.
6. Never select a prompt because it produces a larger or smaller desired
   behavioural effect.

Suggested directory structure:

```text
prompts/generation/records/
  YYYY-MM-DD_<task>_<model>/
    request.md
    raw_response.md
    review.md
    edit_log.md
```

## 8. Manual Review Protocol

Each candidate prompt is checked against the baseline and canonical
specification.

### Rule equivalence

- Same task rules.
- Same available actions.
- Same number and meaning of trials, games, or balloons.
- Same reward, loss, risk, feedback, and stopping rules.
- Same observation placeholder and dynamic information.
- Same required response syntax.

### Manipulation isolation

- Only the intended condition factor differs.
- No behavioural metric is named.
- No optimal action or strategy is implied.
- No human benchmark or published result is revealed.
- No canonical task name or citation is introduced.
- No condition receives additional factual task information.
- Detail is explanatory rather than strategically informative.

### Technical integrity

- Placeholders are preserved exactly.
- Legal response tokens match the parser.
- Markdown or punctuation does not alter parsing.
- No prompt contains unsupported payoff values or probabilities.

Review outcomes:

- `PASS`: usable without edits.
- `PASS WITH EDITS`: only minimal corrections needed; all edits recorded.
- `REJECT`: rule change, strategy leakage, or failed manipulation isolation.

The checklist is stored at:

```text
prompts/generation/manual_review_checklist.md
```

## 9. Manual Editing Rule

Manual edits are limited to:

- Correcting a task-rule inconsistency.
- Removing strategy leakage or behavioural metric names.
- Restoring required placeholders or response syntax.
- Restoring all non-target wording exactly to the frozen baseline when this
  is necessary to isolate the intended manipulation.
- Correcting grammar without changing meaning.

Every edit must record:

- Original text.
- Revised text.
- Reason.
- Reviewer and date.

Substantive rewriting without an edit record breaks the reproducibility chain
and is not permitted.

## 10. Prompt Freeze and Change Control

Before the formal experiment:

1. Complete manual review for all 12 final prompt files.
2. Record the generation metadata and edit history.
3. Freeze the exact prompt files used by the runner.
4. Record file hashes or a Git commit identifier.
5. Run prompt dry-run and parser tests.

After formal collection starts, a prompt change creates a new protocol
version. Results from different prompt versions must not be silently pooled.

## 11. Existing Prompt Provenance

The removed historical prompt files were created before this protocol was
formally adopted. Any historical generator model, date, sampling parameters,
raw outputs, or manual edits that were not recorded must be labelled:

```text
not recorded
```

They must not be reconstructed from memory and presented as exact historical
metadata. Before formal data collection, the researcher must choose one of
the following transparent approaches:

The project selected prospective reconstruction: three canonical baselines
were manually constructed from the task sources and implementation, and nine
manipulated variants were generated and reviewed under Protocol 1.3.

## 12. Dissertation Reporting

Suggested Methods wording:

> A fixed prompt-generation protocol was used to make prompt construction
> auditable and reproducible. For each task, a neutral baseline prompt was
> constructed from participant-facing information in the original task
> literature, open-data documentation, and the implemented task rules. A
> language model was then used only as a constrained rewriting tool to
> produce candidate prompt variants. The meta-prompt prohibited changes to
> the task rules, available actions, feedback, trial structure, stopping
> rules, and response format, and prohibited strategy hints, behavioural
> metrics, and human benchmark information. Each candidate was manually
> checked for rule equivalence and manipulation isolation. The complete
> meta-prompt, generation settings, raw outputs, edit records, and final
> prompts are retained in the project materials.

The dissertation appendix should include:

- Source papers and dataset documentation.
- Canonical task specifications.
- Full baseline prompts.
- Exact meta-prompt.
- Model and sampling settings.
- Raw candidate outputs.
- Manual review and edit records.
- Final prompt files and version identifier.

The complete generation event and two-stage review are recorded in:

```text
docs/prompt_generation_and_review_record.md
```
