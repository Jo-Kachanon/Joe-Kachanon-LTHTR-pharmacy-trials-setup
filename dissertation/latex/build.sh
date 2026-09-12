#!/usr/bin/env bash
# Build the dissertation locally with Tectonic.
#
# Overleaf's free plan compiles this project past its timeout. Tectonic has no timeout,
# takes about 5 seconds once its package cache is warm, and needs no TeX Live install.
#
#   ./build.sh          compile to build/main.pdf
#   ./build.sh --open   compile, then open the PDF
#
# Tectonic has no shell-escape, so nothing here may call out to an external program.
# That is why the two SVG figures are pre-converted to PDF rather than included with
# \includesvg. Regenerate them after editing either SVG:
#
#   rsvg-convert -f pdf -o Figures/fig1_timeline.pdf Figures/fig1_timeline.svg
#   rsvg-convert -f pdf -o Figures/fig2_pharmacy.pdf Figures/fig2_pharmacy.svg
#
# And after regenerating any raster figure, re-run the down-sampler rather than copying
# a master into Figures/ by hand:
#
#   python3 ../../Experiments/prepare_overleaf_figures.py

set -euo pipefail
cd "$(dirname "$0")"

command -v tectonic >/dev/null || { echo "tectonic not found: brew install tectonic" >&2; exit 1; }

mkdir -p build
tectonic -X compile main.tex --keep-logs --outdir build

echo
echo "build/main.pdf"
grep -c "Overfull" build/main.log 2>/dev/null | xargs echo "overfull boxes:"
grep "Reference .* undefined" build/main.log 2>/dev/null || echo "no undefined references"

[[ "${1:-}" == "--open" ]] && open build/main.pdf
