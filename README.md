# LTHTR Pharmacy Trials Set-Up

Final deliverables for the dissertation on pharmacy set-up capacity for clinical trials at
Lancashire Teaching Hospitals (LTHTR), supporting the UK Government's 150-day trial
set-up target.

Curated from the working research repository into four self-contained parts:

| Folder | Contents |
|---|---|
| `dissertation/` | The thesis chapters (Markdown source of truth), the Overleaf/LaTeX build, and figures |
| `optimisation-model/` | The Python selection model (Gurobi), its automated tests, and supporting analysis notes |
| `ui-prototype/` | Standalone HTML prototype of the pharmacy planner interface |
| `presentation/` | Results presentation slides |

## Dissertation

`dissertation/` holds the six chapters as Markdown (the source of truth) plus
`dissertation/latex/`, the Overleaf project they are rendered into for the final PDF.
See `dissertation/latex/README.md` for build instructions (pdfLaTeX) and the chapter/appendix
mapping.

## Optimisation model

`optimisation-model/optimiser/` is the Gurobi implementation of the selection model: which
trials pharmacy commits to set up in a given cycle. See
`optimisation-model/optimiser/README.md` for the formulation, module layout, and how to run
it and its test suite.

## UI prototype

`ui-prototype/lthtr_planner_standalone.html` is a self-contained (no build step) HTML
prototype of the planner interface — open it directly in a browser.

## Presentation

`presentation/LTHTR_Results_Presentation.pptx` is the results presentation deck.

## Provenance

This repository is curated from the working research repository
[`nhs-pharmacy-trials-setup`](https://github.com/Jo-Kachanon/nhs-pharmacy-trials-setup),
which also holds the underlying trust data requests, meeting notes, and exploratory
analysis that are out of scope here.
