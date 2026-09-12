# The selection model, explained

`model.py` (with `data.py`, `gate.py` and `config.py` behind it) is the core of this
package: a Gurobi integer linear programme that decides **which** trials pharmacy commits
to set up this cycle. It does not build a timetable — that is deliberately a different
problem, left for a later module.

## The question it answers

Each planning cycle, pharmacy can open a limited number of trial set-ups. Given a queue of
candidate trials, each with its own clock, duration and value, which ones should be
committed now, and which deferred? The model answers that as an exact optimisation, not a
heuristic ranking: it guarantees the best plan under the constraints given, and it stays
correct even as more realistic constraints (a burden budget, a minimum-throughput floor) are
added — the kind of thing that breaks a simple greedy rule.

## From raw dates to model inputs: `data.py`

Nothing in `data.py` is a judgement call. Every field is arithmetic on dates the trust
already holds, which is what keeps the model's numbers traceable back to source records.

**A `Case`** is a trial exactly as it arrives from the tracker or the register: its
prescription/aseptic flags, its four possible dates (HRA approval, site selection,
pharmacy notification, queue entry), the sponsor's green light, and — if known — its phase
and Prioritisation Tool score.

**`enrich()`** turns each `Case` into a `PlanningCase` by deriving:

- **`tier`** — one of four set-up pathways (`Routine`, `Prescription only`, `Aseptic only`,
  `Both`), read off the prescription/aseptic flags.
- **`clock_start`** — the later of HRA approval and site selection, **not** the date
  pharmacy was told. The 60-day clock genuinely starts here; the gap before pharmacy
  notification is real time the model must account for.
- **`queue_entry`** — when the trial actually reached pharmacy's work queue
  (`setup_start`, or `notified` as a fallback while the newer field isn't universally
  populated).
- **`segment_b`** — `queue_entry - clock_start`: how many of the 60 days ran before
  pharmacy ever saw the trial. Negative means pharmacy started preparing *before* the clock
  began.
- **`work_start`** — the earliest day set-up work can actually begin: today, if the trial
  is already queued; a future hand-over date, if R&I has set one; or today plus the median
  8-day hand-over, flagged as assumed, if R&I holds the trial with no date yet.
- **`days_available`** — due date minus `work_start`. This, not days-to-due from today, is
  what the on-time test actually uses, because it nets out whatever hand-over time is still
  ahead.
- **`prep_credit`** — days taken off the tier duration when pharmacy prepared a study
  before its clock started. Zero unless *both* the sponsor has confirmed the site (so the
  work won't be wasted on a study that doesn't proceed) and the study is complex (aseptic or
  phase 1) — and zero for every study while `prep_credit_cap_days` sits at its default of 0,
  which makes the whole mechanism inert until LTHTR supplies a real figure.
- **`claim_weight`** — `1 + days_waited / weight_divisor`. A trial that has waited a year
  has roughly twice the claim of one just queued, so slow trials are never starved
  indefinitely by faster arrivals.

A case with neither a clock anchor nor a queue-entry date is kept, not dropped — it's marked
`ready = False` and surfaces as `BLOCKED`, so a missing date is a visible row a coordinator
can chase, not a silent omission.

## The approval-signature queue: `gate.py`

Every set-up crosses one approving signature. When several set-ups are committed in the same
cycle, they queue for that one signature, so the expected wait grows with how many trials are
committed — not with how demanding each individual trial is.

`gate_wait(n, settings)` is a standard **M/G/1 queueing approximation**: load is
`arrival_rate × n × approval_days`, utilisation is that load divided by the approver's
monthly capacity (capped at 95% so the formula never blows up as utilisation approaches 1),
and the expected wait scales with `utilisation / (1 - utilisation)` and the approval time's
coefficient of variation (`duration_cv`, a proxy figure — see below).

Because this formula is nonlinear in the committed count, it is **precomputed as a table**
(`gate_wait_table`) for every count the model could choose, and the resulting step function
is what keeps the whole selection problem a *linear* programme rather than a nonlinear one.
`rescue_matrix` then answers, for every trial at every possible committed count: is
`days_available >= duration + wait_at_that_count`? That table is a constant the solver reads,
not something it has to work out itself.

**The consequence this buys the model:** rescueability is a property of the *plan*, not of
the trial in isolation. A trial with 40 days to its due date and a 30-day set-up is inside
target in a three-trial month and outside it in an eight-trial month, purely because the
signature queue is longer. The workbook and the planner prototype instead evaluate
rescueability at the commitment *limit* — as if every slot were always filled — which
overstates the wait whenever the model would rather commit fewer trials than the cap allows.

## The formulation

```
decision      x_i in {0,1}                      commit trial i, or defer it
eligibility   i in E  iff  v_i >= t              below-floor trials are closed, not queued
capacity      sum_i x_i <= c                     a commitment limit, not a staffing wall
burden        sum_i b_i x_i <= B                 optional, weighted by pharmacy burden band
load selector sum_n z_n = 1,  sum_i x_i = sum_n n z_n
on time       onTime_i <= x_i
              onTime_i <= sum_n r_in z_n         r precomputed — gate.rescue_matrix
lateness      d+_i >= (p_i - avail_i) + sum_n g_n z_n + cycle*(1 - x_i),  d+_i >= 0

P1  max  sum_i onTime_i                          ranked first
P2  min  sum_i w_i d+_i                          ranked second
P3  max  sum_i v_i x_i                           paused since 1 August 2026
```

- **`x_i`** — the binary commit/defer decision for trial `i`.
- **`z_n`** — a "load selector": exactly one `z_n` is 1, and it marks how many trials the
  plan commits in total. It exists purely to let the gate wait and the rescue matrix — both
  precomputed by count — enter the model as ordinary linear terms.
- **`onTime_i`** — 1 only if the trial is committed *and* the rescue table says it's still
  achievable at the count the plan actually lands on.
- **`d+_i`** (lateness) — written in **deviation form**: how many days late the trial runs
  past its target, measured from `work_start`, with a deferred trial charged a full
  `cycle_days` penalty. Writing it this way means the *cost* of deferral is derived from the
  trial's own slack, not assumed. For a trial already past its due date this collapses
  exactly to the workbook's flat `weight × cycle_days` saving — the regression test in
  `tests/test_selection.py` fixes that equivalence. For a trial that still has slack left,
  only part of the deferral actually costs anything, so this correctly reports a *smaller*
  saving than the workbook does. Because the trials with slack are exactly the ones P1 wants
  to rescue, the workbook systematically overstates P2's saving on them and therefore
  **understates the true price of ranking on-time first**.

### The three objectives, ranked lexicographically

1. **P1 — maximise the on-time count.** Ranked first: getting more trials in under target
   always outranks minimising lateness.
2. **P2 — minimise weighted lateness**, summed across the *whole* eligible queue (committed
   and deferred together), weighted by each trial's `claim_weight`.
3. **P3 — maximise portfolio value** (Prioritisation Tool score). Currently paused
   (`value_active = False`), because no trial in the available data carries both a value
   score and pharmacy timings together.

These are solved with Gurobi's hierarchical multi-objective machinery, **both tolerances set
to zero**: strict lexicographic ordering, so a lower-priority objective can never buy a
concession from a higher one. There is deliberately no "trade budget" allowing P3 to bid
committed slots away from P1 — the evidence says that trade never pays, because portfolio
value is additive and roughly linear in trial count, so committing more trials is (almost)
always worth more, full stop.

### Why burden is a constraint, not an objective

Pharmacy doesn't choose which trials a sponsor sends it — so rewarding the model for
*declining* burdensome work in the objective would encode a refusal the service cannot
actually make. As a capacity constraint instead, burden says something the service *does*
control: a heavy trial (aseptic, high-burden band) consumes more of the cycle's capacity than
a light one, so committing it leaves less room for others. `capacity_weight` — from
`config.BURDEN_WEIGHTS` — expresses this in "routine-trial equivalents": a band 5–6 trial
costs 2.61 of the budget a routine trial costs 1.00. A version of this that instead used
burden as a third objective, or as an eligibility filter dropping high-burden trials
entirely, was tried and withdrawn on 27 August 2026 for exactly that reason.

## Reading the output: `SelectionResult`

`solve_selection()` returns a `SelectionResult` holding one `Decision` per input trial, in
the order the meeting actually wants to read them (committed first — on-time before rescued
by weight — then deferred, then closed, then blocked). Each `Decision` carries an action
(`COMMIT` / `DEFER` / `CLOSE` / `BLOCKED`) and a plain-English `reason` — a sentence
generated to be read aloud to a sponsor unchanged, e.g. *"Can still finish within 60 days"*
or *"No slot left; waiting costs 32 weighted days this month"*.

`SelectionResult.headline()` produces the one-line summary the meeting asks for:
`"Commit 3 of 5 slots: TiPE, MOCK-07, MOCK-12. 2 still inside 60 days."`

## Two things worth remembering when reading a result

1. **The gate wait moves with the plan's own size**, via `z_n` — raising the commitment cap
   doesn't necessarily change what gets committed, because an extra trial can lengthen the
   signature queue enough to cost the plan a rescue elsewhere, and P1 always outranks the
   extra count.
2. **Lateness savings quoted here will be smaller** than the workbook's for any trial that
   still has slack left, because of the deviation-form lateness above — and that's the
   correct direction of the error, not a discrepancy to chase.

## Limitations, by design

- It selects a set of trials for one cycle; it does not sequence or schedule the work within
  it (a separate, not-yet-built module).
- The rolling multi-cycle queue, the capacity-versus-outcomes sweep, the epsilon-constraint
  frontier, and a formal ablation of the gate-wait mechanism are all deliberately out of
  scope for this build (see the optimiser `README.md`, "What this does not yet cover").
- Several inputs — `approval_days`, `approver_days_per_month`, `prep_credit_cap_days`,
  `duration_cv` — are explicitly *placeholders* pending specific answers from LTHTR's own
  forms, not measurements. `config.py`'s docstrings name exactly which question each is
  waiting on, and each defaults to a value (often zero) that leaves the mechanism it feeds
  inert until a real figure is supplied.

## See also

- `SIMULATION.md` — `plan_sim.py` runs a *committed* plan from this model forward under
  duration uncertainty, turning its single on-time count into a distribution.
- `README.md` — installation, running the CLI, and the test suite.
