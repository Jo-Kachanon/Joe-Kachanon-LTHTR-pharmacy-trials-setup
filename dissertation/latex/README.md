# Dissertation

LaTeX source for my dissertation. `main.tex` is the root document.

## Building

Build locally with [Tectonic](https://tectonic-typesetting.github.io). Overleaf's free
plan compiles this project past its timeout; Tectonic has no timeout, takes about five
seconds once its package cache is warm, and installs nothing into the system.

```bash
brew install tectonic     # once
./build.sh                # writes build/main.pdf
./build.sh --open         # and opens it
```

`build.sh` reports the overfull-box count and any undefined references, so a regression
in the layout is visible without reading the log.

**Tectonic has no shell-escape.** Nothing in the source may call an external program
during the build. That is why the two SVG figures are pre-converted to PDF instead of
being included with `\includesvg`, and why the `svg` package is no longer loaded.
Regenerate them after editing either SVG:

```bash
rsvg-convert -f pdf -o Figures/fig1_timeline.pdf Figures/fig1_timeline.svg
rsvg-convert -f pdf -o Figures/fig2_pharmacy.pdf Figures/fig2_pharmacy.svg
```

Overleaf still works as an editor and reviewer view if you want it; the source is
plain LaTeX and nothing here is Tectonic-specific.

## Start here

All of your personal details live in one block at the top of [`main.tex`](main.tex) —
title, name, student ID, supervisor, degree, university, department, faculty, subject,
keywords, submission date. Nothing is hardcoded anywhere else: the title page, the
declaration, and the PDF metadata all read from that block.

Every value still in `[SQUARE BRACKETS]` is a placeholder that must be replaced before
submission. None are left: `\keywords{}` is filled in and feeds the PDF metadata only.

Drop your university logo into `Figures/` as `logo.png` or `logo.jpg` and the title page
picks it up automatically. It compiles fine with no logo present.

## Layout

```
main.tex            Root document: your details block, package setup, \input list
Thesis.cls          Document class (book-based): margins, spacing, front-matter macros
First_Pages/        Title page, declaration, abstract, acknowledgements, abbreviations, dedication
Chapters/           Chapter1.tex ... Chapter6.tex
Appendices/         AppendixA.tex ... AppendixE.tex
Figures/            Images; \graphicspath and \svgpath point here, so no path prefix is needed
Ref.bib             Bibliography database (natbib, unsrtnat style)
lstpatch.sty        Patch for the listings package
vector.sty          Vector notation macros
```

## What is written

| File | State |
|---|---|
| `Chapters/Chapter1.tex` | Introduction, complete draft |
| `Chapters/Chapter2.tex` | Literature Review, `\todo` scaffold only |
| `Chapters/Chapter3.tex` | Problem Description, complete draft |
| `Chapters/Chapter4.tex` | Methodology, complete draft |
| `Chapters/Chapter5.tex` | Results, complete draft |
| `Chapters/Chapter6.tex` | Conclusion, `\todo` scaffold only |

Chapters 1, 3, 4 and 5 are generated from the Markdown working sources in the project
repository (`Dissertation/Chapter1_Introduction.md`, `Chapter3_Problem_Description.md`,
`Chapter4_Methodology.md`, `Chapter5_Results.md`). Keep editing the Markdown and
regenerate, or switch to editing the `.tex` here — but not both.

**Figures are down-sampled for this build.** The masters in
`Dissertation/figures/` are 2200-3600 px wide; every figure is placed at
`width=\textwidth`, which is 14.65 cm, so anything above 1730 px is resolution the page
cannot print. Carrying the masters put the build over Overleaf's free-plan compile
timeout. `Experiments/prepare_overleaf_figures.py` resizes each figure to 300 dpi at
`\textwidth` and re-encodes it with a 256-colour palette, taking `Figures/` from 5.5 MB
to 1.8 MB. Re-run it after regenerating any figure; never copy a master in by hand.

**If the build still times out,** the next cost is the two `\includesvg` calls in
`Chapter1.tex`. Each shells out to Inkscape on every compile. Converting
`fig1_timeline.svg` and `fig2_pharmacy.svg` to PDF once and switching to the
`\includegraphics` lines already commented in place beside them removes that cost.

**Known gap in Chapter 5.** It refers in plain text to Appendix 4.F, 4.G, 4.H, 4.I and
Table 4.H.3. Those Chapter 4 appendices have not been migrated into `Appendices/` yet, so
those names resolve to nothing a reader can turn to. They compile without error. Convert
them to `\ref` once the Chapter 4 appendices are added.

`AppendixF` and `AppendixG` set their running head with `\thechapter` rather than a
hardcoded letter, because `AppendixE` is commented out and the printed letters therefore
shift. Appendices A to D still hardcode theirs.

The appendices carry the chapter appendices from those Markdown sources:

| File | Was | Contents |
|---|---|---|
| `AppendixA.tex` | Appendix 3.A | Notation and worked instance |
| `AppendixB.tex` | Appendix 4.A | The tracker, its structure and its cleaning |
| `AppendixC.tex` | Appendix 4.B | Assumptions behind the approval wait |
| `AppendixD.tex` | Appendix 4.C | What the 52 automated tests check |
| `AppendixE.tex` | — | Code listings stub, commented out in `main.tex` |
| `AppendixF.tex` | Appendix 5.A | The robustness sweep |
| `AppendixG.tex` | Appendix 5.B | Targeted against untargeted preparation |

In-text references such as "Appendix 3.A" are now `\ref{app:notation}` and typeset as
"Appendix A". Chapters 2 and 6 are still `\todo` scaffolds; they typeset in red on
purpose so nothing is forgotten.

## Figures

`Figures/` holds five images, two SVG and three PNG:

| File | Used in |
|---|---|
| `fig1_timeline.svg` | Chapter 1, the 150-day metric |
| `fig2_pharmacy.svg` | Chapter 1, the pharmacy set-up track |
| `fig4_1_data_sources.png` | Chapter 4, the three data sources |
| `fig4_2_segments.png` | Chapter 4, where the 60 days go |
| `fig4_A1_tracker_completeness.png` | Appendix B, field completeness |

The two SVGs go through the `svg` package, which calls Inkscape. Overleaf runs this
automatically. **The `inkscapelatex=false` option is required, not optional**: without
it the package strips the text out of the SVG and re-typesets it in the document font,
using coordinates computed for 9–13 px sans-serif text, so every label overlaps. If
`\includesvg` ever fails, convert each SVG to PDF, upload it to `Figures/`, and swap to
the commented `\includegraphics` line inside each figure environment.

## Compiling

**Overleaf** — New Project → Upload Project → the zip. In Menu, set Compiler to
**pdfLaTeX** and Main document to **main.tex**.

Regenerate the zip after local edits:

```bash
zip -r dissertation-overleaf.zip . -x '.git/*' '*.DS_Store' 'dissertation-overleaf.zip'
```

**Locally**, if you install a TeX distribution — the bibliography needs the full four-pass
run:

```bash
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

## Credit and licence

Built on the [Masters/Doctoral Thesis template](http://www.latextemplates.com/template/masters-doctoral-thesis)
from LaTeX Templates, via [github.com/ahmedkheiri/thesis](https://github.com/ahmedkheiri/thesis).
The original template is licensed **CC BY-NC-SA 3.0** — see the
[licence explanation](http://www.latextemplates.com/license-explanation).
