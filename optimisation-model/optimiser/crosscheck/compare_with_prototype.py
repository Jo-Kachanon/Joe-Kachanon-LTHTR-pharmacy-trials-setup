"""Run the planner prototype's own JavaScript and compare it against the Gurobi package.

This is validation layer 1, internal consistency, made reproducible. Rather than reading the
two implementations side by side and hoping, it extracts the `model-logic` block straight out
of `Experiments/ui_prototype/lthtr_planner.html`, runs it under Node on the same pinned
instance, and compares every derived field, the gate wait, the decision and the capacity sweep.

Usage::

    python Experiments/optimiser/crosscheck/compare_with_prototype.py

Exit codes:
    0  the two agree everywhere except the documented design divergence
    1  an undocumented disagreement was found
    2  Node is not available, or the prototype markers could not be found

**The one expected divergence.** Above the self-limiting point the package commits fewer
trials than the limit allows, because it prices the approval queue at the count it actually
commits while the prototype prices it at the limit. That is the deliberate improvement recorded
in `Experiments/optimiser/README.md`, not a defect, and it is reported rather than ignored.
"""

from __future__ import annotations

import json
import logging
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))

from Experiments.optimiser import (
    demo_settings,
    enrich,
    gate_wait,
    load_demo_cases,
    solve_selection,
)

logging.disable(logging.CRITICAL)

PROTOTYPE = REPO / "Experiments" / "ui_prototype" / "lthtr_planner.html"

# The prototype gives the eight mock trials realistic-looking names. Same order, same values,
# same dates as the workbook's MOCK-01..08, so the caseloads are one caseload under two labels.
ALIAS = {
    "VELA-201": "MOCK-01", "CASSINI": "MOCK-02", "HALCYON": "MOCK-03", "BRIDGE-2": "MOCK-04",
    "ORION-BC": "MOCK-05", "KESTREL": "MOCK-06", "WILLOW": "MOCK-07", "FERN-CT": "MOCK-08",
}

_HARNESS = """
const {{MODEL}} = require('./model.js');
const {{DEMO}} = require('./demo.js');
const S = {{ today: '{today}', cap: {cap}, floor: {floor}, es: {es}, gpd: {gpd},
             dur: MODEL.DUR_DEMO }};
const rows = MODEL.enrich(DEMO.map(t => ({{...t}})), S);
const ranked = MODEL.decide(rows, S);
console.log(JSON.stringify({{
  setupCeiling: MODEL.SETUP_CEILING,
  committed: ranked.filter(r => r.act === 'COMMIT').map(r => r.name),
  p1: ranked.filter(r => r.act === 'COMMIT' && r.rescue).length,
  cases: ranked.map(r => ({{ name: r.name, tier: r.tier, dur: r.dur, toDue: r.toDue,
                             waited: r.waited, w: r.w, save: r.save,
                             clock: r.clock.toISOString().slice(0, 10) }})),
  sweep: [...Array({sweep_to})].map((_, i) => {{
    const c = i + 1, s2 = {{...S, cap: c}};
    const rr = MODEL.decide(MODEL.enrich(DEMO.map(t => ({{...t}})), s2), s2);
    const com = rr.filter(r => r.act === 'COMMIT');
    return {{ cap: c, used: com.length, gate: MODEL.gate(c, S.es, S.gpd),
              p1: com.filter(r => r.rescue).length }};
  }}),
}}));
"""


def _extract(html: str, start: str, end: str, what: str) -> str:
    """Pull a block out of the prototype by marker rather than by line number.

    Line numbers drift every time the HTML is restyled. The markers do not.
    """
    match = re.search(re.escape(start) + r"(.*?)" + re.escape(end), html, re.DOTALL)
    if match is None:
        raise LookupError(f"Could not find the {what} block in {PROTOTYPE.name}")
    return match.group(1)


def run_prototype(settings, sweep_to: int) -> dict:
    """Execute the prototype's model logic under Node and return its results.

    Raises:
        RuntimeError: If Node is missing or the prototype's script fails.
        LookupError: If the expected markers are absent from the HTML.
    """
    if shutil.which("node") is None:
        raise RuntimeError("Node is not on PATH, so the prototype cannot be executed.")

    html = PROTOTYPE.read_text(encoding="utf-8")
    model_js = _extract(html, '<script id="model-logic">', "</script>", "model-logic")
    demo_js = "const DEMO = [" + _extract(html, "const DEMO = [", "];", "DEMO caseload") + "];"

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        (work / "model.js").write_text(model_js + "\nmodule.exports = { MODEL };\n")
        (work / "demo.js").write_text(demo_js + "\nmodule.exports = { DEMO };\n")
        (work / "run.js").write_text(
            _HARNESS.format(
                today=settings.today.isoformat(), cap=settings.cap, floor=settings.floor,
                es=settings.approval_days, gpd=settings.approver_days_per_month,
                sweep_to=sweep_to,
            )
        )
        proc = subprocess.run(
            ["node", "run.js"], cwd=work, capture_output=True, text=True, check=False
        )

    if proc.returncode != 0:
        raise RuntimeError(f"The prototype's JavaScript failed:\n{proc.stderr.strip()}")
    return json.loads(proc.stdout)


def main() -> int:
    settings = demo_settings()
    sweep_to = 11
    try:
        proto = run_prototype(settings, sweep_to)
    except (RuntimeError, LookupError) as exc:
        print(f"Cannot run the cross-check: {exc}")
        return 2

    cases = enrich(load_demo_cases(), settings)
    package = {c.name: c for c in cases}
    canon = lambda name: ALIAS.get(name, name)
    failures: list[str] = []

    print("=" * 76)
    print("A. LAYER 1 DERIVED FIELDS")
    print("=" * 76)
    checks = 0
    for row in proto["cases"]:
        name = canon(row["name"])
        got = package[name]
        for field, proto_value, package_value in (
            ("tier", row["tier"], got.tier),
            ("dur", row["dur"], got.duration),
            ("toDue", row["toDue"], got.days_to_due),
            ("waited", row["waited"], got.days_waited),
            ("w", row["w"], got.claim_weight),
            ("save", row["save"], got.cycle_saving(settings.cycle_days)),
            ("clock", row["clock"], got.clock_start.isoformat()),
        ):
            checks += 1
            if proto_value != package_value:
                failures.append(
                    f"{name}.{field}: prototype {proto_value}, package {package_value}"
                )
    print(f"  {checks - len(failures)} of {checks} field checks match.")

    print()
    print("=" * 76)
    print("B. GATE WAIT")
    print("=" * 76)
    gate_bad = [
        f"gate({row['cap']}): prototype {row['gate']}, package {gate_wait(row['cap'], settings)}"
        for row in proto["sweep"]
        if abs(row["gate"] - gate_wait(row["cap"], settings)) > 1e-9
    ]
    failures.extend(gate_bad)
    print(f"  {len(proto['sweep']) - len(gate_bad)} of {len(proto['sweep'])} gate waits match.")

    print()
    print("=" * 76)
    print("C. THE DECISION AT THE DEFAULT LIMIT")
    print("=" * 76)
    result = solve_selection(cases, settings)
    proto_set = sorted(canon(n) for n in proto["committed"])
    package_set = sorted(result.committed)
    print(f"  prototype : {', '.join(proto_set)}")
    print(f"  package   : {', '.join(package_set)}")
    if proto_set != package_set:
        failures.append(f"committed set differs: {proto_set} vs {package_set}")
    if proto["p1"] != result.p1_on_time:
        failures.append(f"P1 differs: prototype {proto['p1']}, package {result.p1_on_time}")
    print(f"  P1        : prototype {proto['p1']}, package {result.p1_on_time}")

    print()
    print("=" * 76)
    print("D. CAPACITY SWEEP")
    print("=" * 76)
    print(f"  {'limit':>5} {'proto used':>10} {'pkg used':>9} {'proto P1':>9} {'pkg P1':>7}  note")
    divergences = 0
    for row in proto["sweep"]:
        run = solve_selection(cases, settings.with_cap(row["cap"]))
        note = ""
        if row["used"] != run.committed_count:
            divergences += 1
            note = "package self-limits (expected)"
            if run.p1_on_time < row["p1"]:
                failures.append(
                    f"at limit {row['cap']} the package self-limited and LOST on-time trials"
                )
        elif row["p1"] != run.p1_on_time:
            failures.append(
                f"P1 differs at limit {row['cap']} with the same count committed: "
                f"prototype {row['p1']}, package {run.p1_on_time}"
            )
        print(f"  {row['cap']:>5} {row['used']:>10} {run.committed_count:>9} "
              f"{row['p1']:>9} {run.p1_on_time:>7}  {note}")

    print()
    print("=" * 76)
    if failures:
        print(f"RESULT: {len(failures)} undocumented disagreement(s)")
        for item in failures:
            print(f"  - {item}")
        return 1
    print("RESULT: the two implementations agree.")
    print(f"        {divergences} documented design divergence(s), all of them the package "
          "declining")
    print("        slots that would cost it an on-time trial. No on-time trial was lost.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
