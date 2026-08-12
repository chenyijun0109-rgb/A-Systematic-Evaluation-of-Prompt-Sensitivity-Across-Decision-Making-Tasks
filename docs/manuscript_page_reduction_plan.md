# Dissertation page-reduction plan

The School limit applies to the body from Introduction through Conclusions. References and appendices follow the body.

## Baseline and target

The Overleaf baseline reported by the author was 48 body pages. Because a local TeX engine is unavailable, the baseline allocation below is estimated from chapter word counts, displayed equations, tables, and full-page landscape figures; final counts must be read from Overleaf after compilation.

| Chapter | Baseline estimate | Target | Main reduction rule |
| --- | ---: | ---: | --- |
| Introduction | 5 | 3 | Merge repeated motivation, definition, gap, and result statements while retaining objectives, RQs, achieved results, and document structure. |
| Background and Related Work | 8 | 4--5 | Retain the thematic chain and citations; remove repeated definitions and Method previews. |
| Methodology | 18--20 | 12--13 | Keep task parameters, prompt controls, analysis equations, uncertainty rules, and reproducibility boundaries; shorten repeated rationale and consolidate equations. |
| Results | 8--9 | 7--8 | Retain representative raw estimates and all four RQ answers; use four readable landscape figures rather than five and shorten repeated prose. |
| Discussion | 5 | 3 | Integrate findings and contribution; remove Results restatement and repeated literature review. |
| Conclusions | 2 | 1--2 | Preserve the direct answer, contribution, and prioritised future work. |
| **Total** | **48** | **34--35** | No font, margin, or line-spacing changes. |

## Implemented safeguards

- No task, metric, model, language, prompt condition, primary contrast, or RQ was removed.
- Core formulas and direction conventions remain in the main text.
- Detailed optimiser and provenance material remains assigned to the technical appendix.
- Results figures retain all plotted cells but encode prompt conditions through markers or columns, reducing repeated axis labels.
- RQ4 absolute deviation and coverage are combined in one two-row figure without combining their scales.
- `placeins` barriers keep figures in their RQ sections without the early page breaks caused by repeated `\clearpage` commands.

## Final Overleaf check

After uploading the revised source and figures, compile from scratch and record the start page of each chapter and the final page of Conclusions. If the body exceeds 35 pages, reduce only local repetition and float whitespace; do not alter the School format or remove analytical definitions.
