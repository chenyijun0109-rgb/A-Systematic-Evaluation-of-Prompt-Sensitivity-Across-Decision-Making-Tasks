# `final.tex` Overleaf figure manifest

Upload the seven figure files below while preserving the listed relative paths. The two design figures are high-resolution PNG files; the five Results figures remain vector PDFs. The paths are the ones used by `\includegraphics` in `final.tex`. All result figures are the current joint-analysis versions. In particular, the RQ3 figure treats English, Simplified Chinese, and Spanish symmetrically and contains no English-reference or pairwise-language analysis.

## Design and workflow figures

| Source file in this repository | Overleaf relative path | LaTeX label | Purpose/caption |
| --- | --- | --- | --- |
| `outputs/figures/design/study_design_scope.png` | `outputs/figures/design/study_design_scope.png` | `fig:study_design_scope` | Concise study design and deduplicated data structure. |
| `outputs/figures/design/experimental_workflow.png` | `outputs/figures/design/experimental_workflow.png` | `fig:experimental_workflow` | Concise workflow from frozen materials to formal analysis. |

## Main Results figures

| Source file in this repository | Overleaf relative path | LaTeX label | Purpose/caption |
| --- | --- | --- | --- |
| `outputs/figures/final_results_v01/figure_rq1_prompt_effects_overview.pdf` | `outputs/figures/final_results_v01/figure_rq1_prompt_effects_overview.pdf` | `fig:rq1` | Task-grouped forest plots of within-model prompt effects relative to Neutral; points are signed Hedges' \(g\), with percentile-bootstrap 95% confidence intervals. |
| `outputs/figures/final_results_v01/figure_rq2_model_interactions_overview.pdf` | `outputs/figures/final_results_v01/figure_rq2_model_interactions_overview.pdf` | `fig:rq2` | Model-by-prompt interaction overview; raw candidate-minus-GPT-5.4 interactions are printed in cells and colour encodes differences in signed Hedges' \(g\). |
| `outputs/figures/final_results_v01/figure_rq3_language_overview.pdf` | `outputs/figures/final_results_v01/figure_rq3_language_overview.pdf` | `fig:rq3` | Joint three-language centred comparison. No language is designated as the reference; deviations sum to zero within each comparison. |
| `outputs/figures/final_results_v01/figure_rq4_absolute_deviation_heatmap.pdf` | `outputs/figures/final_results_v01/figure_rq4_absolute_deviation_heatmap.pdf` | `fig:rq4a` | Descriptive prompt-associated changes in absolute human-SD-scaled mean deviation. |
| `outputs/figures/final_results_v01/figure_rq4_coverage_heatmap.pdf` | `outputs/figures/final_results_v01/figure_rq4_coverage_heatmap.pdf` | `fig:rq4b` | Descriptive prompt-associated changes in empirical human-reference coverage. |

## School-template files required before compilation

`final.tex` now uses the mandatory School format:

- `\documentclass[logo,msc]{infthesis}`
- `\usepackage{msccheck}`

Open or copy the files into the University's official dissertation Overleaf project, which must already contain `infthesis.cls`, `msccheck.sty`, and any logo assets required by the class. These template files are not present in this repository and should be obtained from the official School template rather than recreated or replaced. Do not add `geometry`, `fullpage`, `savetrees`, font-size overrides, line-spacing overrides, or compressed-list settings.

After compilation, confirm that Introduction begins on body page 1 and that Conclusion ends by page 40, before the bibliography and any appendices.

## Other files required by Overleaf

- `final.tex`
- `final_references.bib`

The tables are embedded directly in `final.tex`; no separate table files are required. Compile inside the official School template with pdfLaTeX, BibTeX, pdfLaTeX, and pdfLaTeX (or the corresponding Overleaf automatic sequence).
