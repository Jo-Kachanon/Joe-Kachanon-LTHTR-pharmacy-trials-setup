# Pharmacy set-up selection model, solved with Gurobi

Exact implementation of the selection model described in the dissertation's methodology
chapter (`../../dissertation/Chapter4_Methodology.md`, section 4). It decides **which** trials
pharmacy commits to set-up this cycle. It does not produce a timetable.

## Run it

Install dependencies from `requirements.txt`, then run from the `optimisation-model/`
directory:

```bash
pip install -r requirements.txt
python -m optimiser.cli --instance demo
```

```bash
python -m optimiser.cli --instance tracker --cap 5
```

```bash
python -m pytest optimiser/tests -q
```

The demonstration instance is the one to run first: it is the only one whose answer can be
checked against published figures.

## Licence

The pip-installed `gurobipy` ships a restricted licence that already runs this model. A
100-trial instance uses about 300 variables against a 2,000 limit, so **the full licence is
not blocking anything**. It matters once the rolling queue plan and the frontier sweep are
added, because those solve the model many times over and a size-limited licence would start to
bind on a larger caseload.

## Layout

| File | Holds |
|---|---|
| `config.py` | `Settings`, frozen. Every constant, with its provenance in the docstring |
| `data.py` | `Case`, `PlanningCase`, and the Layer 1 date arithmetic |
| `loaders.py` | The 16-trial demonstration instance and the cleaned tracker CSV |
| `gate.py` | The approval-signature queue, and the rescue table it produces |
| `model.py` | The Gurobi build and the lexicographic solve |
| `diagnostics.py` | The pre-solve P1 ceiling and the post-solve report |
| `service.py` | JSON in, JSON out, in the planner's own field names |
| `cli.py` | Command line entry point |

## Formulation

```
decision      x_i in {0,1}                      commit trial i, or defer it
eligibility   i in E  iff  v_i >= t             below-floor trials are closed, not queued
capacity      sum_i x_i <= c
load selector sum_n z_n = 1,  sum_i x_i = sum_n n z_n
on time       onTime_i <= x_i
              onTime_i <= sum_n r_in z_n
lateness      d+_i >= (p_i - avail_i) + sum_n g_n z_n + cycle (1 - x_i),  d+_i >= 0

P1  max  sum_i onTime_i                         ranked first
P2  min  sum_i w_i d+_i                         ranked second
P3  max  sum_i v_i x_i                          paused since 1 August 2026
```

`avail_i` is days from the day work can begin to the due day, which is days-to-due less any
hand-over still ahead. The 60-day clock starts at the later of HRA approval and site
selection, but the trial does not reach pharmacy until R&I hands it over, and the tracker
puts a median 8 days between the two. Three cases:

| Trial state | Window used |
|---|---|
| Already in the pharmacy queue | Days to due. That hand-over is spent and must not be charged twice |
| Hand-over date set for the future | Days to due, less the days still to wait |
| Held by R&I, no date | Days to due, less the median 8-day hand-over, and the row says so |

The third case is what lets a trial be planned on R&I's fields alone, before pharmacy has
been told anything. `data._work_start` holds the rule; the meeting record is
`Model/Meeting_Findings_2026-08_Field_and_Model_Changes.md`.

`p_i` is the tier duration less a preparation credit, which is `prep_credit_cap_days` when
**both** the sponsor has confirmed the site and the study is complex, meaning aseptic or
phase 1, and zero otherwise. That is a service-level rule, matching what form 3 asks
pharmacy to answer once for the whole service, and the credit is never inferred from how
early they heard. `Case.prep_override` overrides the rule in either direction when the
planner running the tool has an answer of their own. The cap defaults to 0, which makes the
whole mechanism inert until LTHTR answer form 3, section 4. `data._prep_credit` holds the
rule.

Lexicographic ordering uses Gurobi's hierarchical objectives with both tolerances at zero, so
a lower level can never buy a concession from a higher one.

## Two places this is stronger than the workbook

**The gate wait is evaluated at the count the plan actually commits.** The workbook and the
planner both evaluate rescueability at the commitment limit, which assumes every slot is
filled. Through the `z_n` selector this model prices the signature queue at the plan's real
size, so raising the limit above seven changes nothing on the demonstration instance: it keeps
committing seven, because an eighth trial would lengthen the queue enough to lose both rescues
and P1 outranks P2. **The capacity ceiling becomes an output rather than a chart a reader has
to interpret.**

**Lateness is written in deviation form.** The workbook credits a committed trial with
`w_i x cycle` weighted days saved. That is only right for a trial already past its due date.
For a trial with slack left, part of the deferral is absorbed by that slack, so the true saving
is smaller. The trials with slack are exactly the rescueable ones, so the workbook overstates
the P2 saving of the trials P1 wants to rescue, and therefore **understates the price of
putting on-time first**: 41.3 weighted days on the demonstration instance, against 20.4 as
published. The committed set is unchanged, because P1 outranks P2 either way.

## Planner integration

`service.solve_json` takes and returns the planner's own field names, so
`Experiments/ui_prototype/lthtr_planner.html` swaps one function call for one `fetch`:

```python
from Experiments.optimiser import demo_settings, solve_json

payload = {
    "settings": {"today": "2026-08-03", "cap": 3, "floor": 20,
                 "es": 1.0, "gpd": 9.45, "dur": {...}},
    "cases": [{"name": "TiPE", "onc": False, "asep": False,
               "hra": "2026-07-18", "siteSel": None,
               "notified": "2026-07-22", "setupStart": "2026-07-30",
               "value": 21.0}],
}
result = solve_json(payload, demo_settings())
```

`notified` is first contact and `setupStart` is queue entry. A register carrying only
`notified` still solves, because queue entry falls back to it, which is what the tracker's
column measures in practice.

The returned `rows` array carries `act`, `why`, `rescue`, `save`, `w`, `toDue` and `dur`
exactly as the front end already reads them, in the model's ranked order, so nothing needs
sorting client-side. Schema 1.1 adds `avail`, `segB` and `queueAssumed`; the addition is
backwards compatible in both directions.

Two properties the planner depends on are preserved deliberately. **Nothing is silently
dropped**: a case with no usable date returns as `BLOCKED` with a reason, so the register
keeps showing it and a chasing action has somewhere to live. **Every row carries a sentence**
in `why`, meant to be read out to a sponsor unchanged.

The planner is offline by design. Any service built on this must stay on the local machine
unless information governance says otherwise.

## What this does not yet cover

Deliberately out of scope for the first build, and each is a new module rather than a rewrite:
the rolling multi-cycle queue plan (output 2b), the capacity sweep (outputs 8 to 11), the
epsilon-constraint frontier (output 9), and the gate ablation (output 21).

## An honest note on what the ILP buys

For the current constraint set the planner's greedy rule is already optimal, and
`tests/test_selection.py::test_matches_the_published_greedy_answer` asserts exactly that. The
exact model earns its keep in three other ways: it guarantees optimality rather than assuming
it, it stays correct when constraints are added that break greedy (per-team effort pools, a
minimum-throughput floor, must-start-by backstops, the controlled trade `k`), and it builds the
frontier by epsilon-constraint rather than enumeration, which removes the planner's 14-case
limit on the "Why these cases" tab.
