# Next Steps Plan

Updated 2026-08-18. The formal experiment is complete (1,200 deduplicated
valid task runs). The items below are ordered by the evidence they would add.

## 1. Higher-powered replication of the largest effects

The largest sign reversals (especially the BART adjusted-pump interactions and
the Horizon Random-exploration contrasts) should be replicated with larger
cells and independent collection dates to distinguish persistent response
structure from snapshot-specific behaviour.

## 2. Factorial prompt designs

The current formulations are information-matched but not feature-orthogonal.
Future designs should manipulate semantic emphasis, prompt length, information
position, and keyword salience separately.

## 3. Independent translation validation and concurrent collection

Multilingual prompts should be validated by independent bilingual reviewers
(including back-translation) and collected concurrently across languages so
that language implementation is not confounded with temporal drift.

## 4. Full propagation of human-reference uncertainty

Run-level resampling intervals for the RQ4 prompt-associated changes are now
reported for the seven directly computed metrics
(`model_human_distance_changes_bootstrap.csv`). The remaining item is to
propagate reference-sample bootstrap uncertainty through the cell-level
deviation and coverage changes, and to align task implementations more closely
(task length, familiarisation, information presentation).

## 5. Repository and submission hygiene

- Table 3.1 collection dates are aligned with the run records in the source
  (English GPT-4.1 08–13 July; GPT-5.4 30–31 July; GPT-5.4 Mini 01 August;
  zh-CN 03–05 August; es 05–07 August); recompile the dissertation PDF so the
  rendered table matches.
- The appendix now reproduces all 36 frozen prompts verbatim with a
  terminology mapping table; confirm the rendered appendix (CJK fonts, table
  widths) inside the official Overleaf template.
- Keep the public GitHub repository English-only and free of local absolute
  paths; raw run JSONs and human datasets remain local audit materials.
- Package the `PROJECT/` archive (with `PROJECT/README.md`) for the School's
  electronic submission, including the full processed analysis package and
  provenance records for the human datasets.
