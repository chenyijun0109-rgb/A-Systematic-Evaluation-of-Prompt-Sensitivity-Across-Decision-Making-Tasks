# Multilingual Prompt Generation and Audit Record

Date: 2026-07-20  
Method: constrained human-readable translation and controlled derivation  
Constraint file: `prompts/multilingual/translation_constraints.md`  
Languages: Simplified Chinese (`zh-CN`) and neutral Spanish (`es`)

## Derivation history

The six target-language baselines were produced first from the three frozen
English baselines. Role, task-emphasis, and detailed variants were produced only
after their target-language baseline existed. No English variant was translated
independently.

| Task | English baseline SHA-256 | `zh-CN` baseline SHA-256 | `es` baseline SHA-256 |
|---|---|---|---|
| Horizon | `d9ef2caf1c1c2c75c6277a51e909bdce0a3cf77d593e0f5f0fd64374f82bc116` | `8b720bd1d4d4cf047c7b3407a248a4d74f1010e67084b975b2ccfd4411c09d51` | `2557096cbdcf34e58d69e1d30c061cb06edc9189bdd5539736bbbd26dd33030f` |
| IGT | `e09f035c448a21d6a0165f8a39d87056fa52af63a4f59e5deed833dd311859ce` | `def248b8555ff187988d5cdf59e788a8e0aba84015b1cce7d1c429a38d87cfe5` | `65ee2a263c41e5dfd36850d4238e20a628106d56d9c6f649d987681a0a13a92e` |
| BART | `7e78abdc06504f2b1bda6c1a7932bbdb88b1dbdc312cf5be9ea11ab6cc6178ea` | `39d8372bfabaf8cc8501b9715d004d51e533d1bc88a5dd3e0821ff918e979a37` | `99db05d7ab43255f4b929ad37611de7cc1868e608df971d2188e9949e937eb4b` |

Every variant below has the baseline in the same language as its parent.

| Language | Task | Condition | SHA-256 |
|---|---|---|---|
| `zh-CN` | Horizon | `detailed` | `a696db83005fede322780a72a7920ba713823ee63ebcecf078b24390c28405af` |
| `zh-CN` | Horizon | `role_human` | `109c538a79bad503e999bc9fd900aef0def9a1235d2168f535b0ff269ef06d04` |
| `zh-CN` | Horizon | `uncertainty_emphasis` | `f5670c6834546035e27101b3396733746c495776bd93ac51a00499bdca038a87` |
| `zh-CN` | IGT | `detailed` | `abe60a7a2f7323ac3ec94d6e16348a4098ff1c3a7aa3b12eb0c1faa3c8db0989` |
| `zh-CN` | IGT | `role_human` | `be4771191d7af24d10156e43171ccfc880883137070bd5decc37c6ea48d513ed` |
| `zh-CN` | IGT | `reward_loss_emphasis` | `7e89d30340c1d25f05cc7df85515a9aeb759fa9d6c4898490a5b89fc210daaf5` |
| `zh-CN` | BART | `detailed` | `05791325b04ec53d7926acec0b71aabd4c8b3d254bfabb50d3f4d3244b87adc8` |
| `zh-CN` | BART | `role_human` | `a2b04188f2f8397506dab9b811ea26a5b73812d207f304fb333f7ef73c33b002` |
| `zh-CN` | BART | `risk_emphasis` | `5bcacb5fdce08ea1a67b68f08974819fa675d88c460991a9b2e7ad3d4a4cdb10` |
| `es` | Horizon | `detailed` | `347a3077272348a020fb2a79db18e003a34a47224f1d4c6b60eb939ba3f67941` |
| `es` | Horizon | `role_human` | `22801bce0b27d1be525e1038e43b0e275aececbd626607a2cf3b279eac2a96a3` |
| `es` | Horizon | `uncertainty_emphasis` | `8aa2bb9f6d1b14b88165f2c2c401651e6225939cd5e3f7de220ce09cf8f901e9` |
| `es` | IGT | `detailed` | `3778ac5bfa39e8ea6153f28a1fb868d63c66d229e82c65b15bd4bd67c1688f09` |
| `es` | IGT | `role_human` | `6a04c4c31a4987cf0a4a1324aee327bfd7cf5732241ad6aee5890a4aee9f59ad` |
| `es` | IGT | `reward_loss_emphasis` | `54b7f462889aee8590f3273b756b70d40d35b616e4b426a66b7943b28594bad8` |
| `es` | BART | `detailed` | `3359ce414d7ac6eb3896cd869d6d870212f0e57bee884b127b01c08343f3aca0` |
| `es` | BART | `role_human` | `4cbf60d3974b322022a825c237d213420d4bf75e217df913d36cdb2ecf99d80d` |
| `es` | BART | `risk_emphasis` | `24609ffc478b36d6b888d3df69229e221026f90c15836e0b18a79bab06622e80` |

## Audit status

Automated checks cover all 24 target-language files and confirm:

- exactly one `{observation}` placeholder;
- byte-preserved parser outputs;
- all configured files load and render;
- all valid response strings pass the existing parser;
- each role prompt becomes byte-identical to its same-language baseline after
  removing the single authorised role sentence.

## Final bilingual semantic review

Review date: 2026-07-25  \
Reviewer: Codex, acting as a fluent Simplified Chinese and Spanish reviewer at
the user's explicit request  \
Decision: `semantic_review_complete`

The review compared every target-language baseline clause by clause with its
English source, then compared every variant with its parent baseline. It checked:

- quantities, option labels, reward values, task sequence, and uncertainty;
- modal strength and whether optional information use remained optional;
- consistent Chinese terminology for reward, loss, net outcome, cumulative
  score, temporary earnings, and total earnings (canonical Chinese terms are in
  `src/observation_renderer.py` and the frozen zh-CN prompts);
- consistent Spanish terminology for recompensa, pérdida, resultado neto,
  puntuación acumulada, ganancia temporal, and ganancia total;
- neutral international Spanish without regional strategy cues;
- the absence of advantageous-deck, payoff-schedule, explosion-probability,
  reward-distribution, metric, hypothesis, or recommended-strategy disclosures;
- preservation of the neutral objective and exact parser outputs;
- condition isolation: role adds one sentence, task emphasis changes only its
  authorised concept, and detailed variants only restate source facts.

No meaning-changing defect requiring a prompt edit was found. The wording is
natural and sufficiently equivalent for the planned cross-language pilot.
Because no prompt text changed during final review, the SHA-256 values above
remain current.

The static prompt set is now `reviewed_and_frozen_for_multilingual_pilot`.
Dynamic observations are reviewed separately in
`src/observation_renderer.py`; they use the selected language while leaving
ASCII actions and hidden task state unchanged. The machine-readable freeze is
`configs/multilingual_experiment_freeze_v01.json`.
