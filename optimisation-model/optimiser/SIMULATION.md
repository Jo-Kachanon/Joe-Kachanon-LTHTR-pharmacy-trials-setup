# The plan simulation, explained

`plan_sim.py` answers a question the selection model (`model.py`) cannot: **how often does a
committed plan actually deliver what it promises?**

## Why it exists

`model.solve_selection` chooses which trials pharmacy commits to set up, and reports an
on-time count. That count is computed at one set-up duration per trial — the tier median —
so it reads as a fact: "two trials finish inside 60 days." It isn't one. Set-up durations
vary widely around their median, so the on-time count is really a random variable, and the
model's figure is only its value at the median case. Reporting that single number tells the
service nothing about how often the plan can actually miss.

`simulate_plan` runs the committed plan forward many times — 2,000 by default — drawing a
different set-up duration for each trial on each run, instead of fixing it at the median. It
turns "two on time" into "two on time in 61% of runs, one in 27%": a statement a service can
actually size capacity against.

## What varies, and what doesn't

- **Set-up duration varies.** Each trial's duration is drawn from a lognormal distribution
  on every replication.
- **The approval wait (the gate) does not vary.** It is held fixed at its expected value,
  computed by `gate.gate_wait` for the size of the committed plan. That queue is modelled in
  closed form (an M/G/1 approximation), not simulated, so the spread this module reports
  comes from duration alone. It is a **floor** on the true uncertainty in the on-time count,
  not an estimate of the whole of it — the real spread is wider once approval-wait
  variability is added back in.

## How a duration is drawn

Each draw uses a lognormal distribution, anchored on two figures from `config.py`:

- **Median** — the trial's tier duration (or its preparation-credited duration, if one
  applies): `case.effective_duration or case.duration`.
- **Spread** — `settings.setup_duration_cv`, the coefficient of variation of set-up duration,
  measured at 0.548 on the same 23 tracker sojourns behind the tier durations themselves.

The anchor is deliberately the **median**, not the mean, because that is what the tier
durations and the calibration measure. Anchoring a lognormal on a mean instead pulls the
whole distribution down — at a pooled median of 95 days it would return a generated median of
83, twelve days short of what is on record. Anchoring on the median instead reproduces the
calibration exactly: a generated median of 95 against a recorded 95, mean 108 against a
recorded 106.

**This is not `duration_cv`.** `duration_cv` (1.55) is a separate, much larger figure: a proxy
for the *approval time* that the gate-wait formula uses, borrowed from 51 iQemo template
builds because no direct measurement of approval-time variability exists. The two describe
different quantities and must not be swapped. Drawing set-up durations at `duration_cv`
instead of `setup_duration_cv` would put the generated median at 57 days — faster than any
set-up on record.

Lognormal was chosen because it is positive and right-skewed, which a set-up duration must
be, and because it is fully fixed by exactly the two moments (median, CV) the calibration
provides. No claim is made that set-up durations are lognormal in fact — it is simply the
least-committal shape consistent with what was measured.

## What one replication does

For each replication, and for every committed trial:

1. Draw a duration from the lognormal described above.
2. Compute slack: `days_available - (drawn_duration + gate_wait)`.
3. The trial is on time that run if `slack >= 0`.

The run's on-time count is the number of committed trials that cleared their own slack test
that replication. Two thousand replications later, that count has a full distribution rather
than a single value.

## What comes out: `PlanOutcome`

| Field | Meaning |
|---|---|
| `deterministic_count` | What `solve_selection` reported, at the tier median. The figure this module exists to qualify. |
| `distribution` | On-time count → share of runs producing it. |
| `mean_count` | Expected on-time count across all runs. |
| `p10_count` | The count met or exceeded in 90% of runs — the pessimistic end, and the figure a service planning capacity should actually look at, not the mean. |
| `probability_at_least_deterministic` | How often the plan achieves what it promised. A low figure means the reported count rests on durations that rarely occur in practice. |
| `gate_wait` | The (fixed) approval wait used in every replication. |
| `per_trial` | A `TrialRisk` for every committed trial, worst first (see below). |
| `replications` | How many runs the figures above are built from. |

### Per-trial risk (`TrialRisk`)

For each committed trial, the module also reports:

- `on_time_probability` — the share of runs in which that specific trial finished inside its
  window.
- `median_overrun` — median days past the window, treating an early finish as zero overrun.
- `deterministic_on_time` — what the plan claimed for this trial at the tier median. Where
  this disagrees with `on_time_probability` (e.g. claimed on-time, but only achieved in 40%
  of runs), the plan is relying on a duration it will not always get.

## How to run it

```python
from optimiser.config import demo_settings
from optimiser.data import enrich
from optimiser.loaders import load_demo_cases
from optimiser.model import solve_selection
from optimiser.plan_sim import simulate_plan

settings = demo_settings()
cases = enrich(load_demo_cases(), settings)
result = solve_selection(cases, settings)          # the deterministic plan
outcome = simulate_plan(result.committed, settings)  # its distribution of outcomes

print(outcome.deterministic_count, outcome.mean_count, outcome.p10_count)
print(outcome.probability_at_least_deterministic)
```

Pass `simulate_plan` the **committed plan**, not the whole candidate queue — a deferred trial
contributes no on-time count and carries no risk here. Always pass the same `Settings` object
the plan was solved with; mixing settings means the plan and the simulation no longer
describe the same world.

`seed` defaults to a fixed value (`20260818`) so that any reported figure regenerates exactly
on request. `replications` defaults to 2,000, which keeps the standard error on a probability
near 0.5 to about one percentage point — finer than the decision needs.

## How it's tested

`tests/test_plan_sim.py` checks two things:

1. **Consistency with the model it qualifies.** With `setup_duration_cv` set to 0, every
   replication draws exactly the tier median, so the whole distribution collapses to a spike
   on `deterministic_count`, `mean_count` equals it exactly, and
   `probability_at_least_deterministic` is 1.0. If this fails, the simulation and the
   selection model disagree about what the plan means, and every spread reported afterwards
   is measured from the wrong place.
2. **The properties a reader relies on**, including that real variability puts the
   deterministic count in doubt (`0 < probability_at_least_deterministic < 1`, and
   `mean_count < deterministic_count`), and that only `setup_duration_cv` — never
   `duration_cv`, the approval-time proxy — can add spread to the duration draw.

## The known limitation

The approval wait held fixed at its expected value is not just a simplification of
convenience — it is a **known, documented understatement**. The gate wait itself varies in
reality (it is a queue, not a constant), and that variability is not modelled here. So the
spread `simulate_plan` reports is the floor of the true uncertainty in the on-time count, from
duration alone, not the whole of it. Treat every probability and every `p10_count` this
module reports as optimistic in that specific, bounded sense.
