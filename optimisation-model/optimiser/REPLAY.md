# Retrospective replay — 2026-08-26

The Chapter 4 planning run needs a live queue; the August return holds finished trials.
The replay reconstructs the queue at historical dates from those trials' own dates and
runs the real solver on it. Script: `Experiments/run_replay_2026-08-26.py`. Results:
`replay_results_2026-08-26.csv` (48 rows), `frontier_<date>.csv` per date, and the
Kheiri-style figures in `Experiments/figures/` (fig A and B, from the 2025-02-01
frontier).

## Design

- **Queue at date T**: every trial pharmacy had been notified of by T and had not yet
  green-lit. Dates chosen on evidence: the three month-starts with the largest queues,
  2025-02-01 (5 trials), 2025-05-01 (7), 2025-06-01 (6).
- **Regimes**: `calibrated` (recompute §3 medians, current performance) and `standards`
  (§12 floor-top, demonstrated-achievable). Cap swept 1 to 8. Value floor 0, because
  only six trials carry a Stage 2 score.
- **Comparator**: arrival order (longest-waiting first), scored with the model's own
  lateness definition — base + gate wait + deferral cycle, claim-weighted. An earlier
  draft scored it with a simpler formula and made arrival order look better than the
  lexicographic optimum, which is impossible; the fix is in the script's docstring.
- **Anchor rule**: planning is permissive (either anchor anchors the clock), unlike the
  strict measurement rule, because a planner cannot drop a live trial for a missing
  date. BALLOON therefore plans on its HRA anchor alone.

## Findings

**1. At current performance the model can only tie arrival order.** Calibrated regime:
P1 = 0 at every date and every cap — nothing in any reconstructed queue was rescueable,
matching the robustness sweep and section 9. P2 ties exactly (saving +0.0) at every
cap: with every trial late, commitment choice barely reorders weighted lateness on
queues this small.

**2. Under standards, the model retrospectively picks the trial that actually won.**
At 2025-02-01, cap 1, it commits **BNT327-06** — the one trial in that queue which met
the 60-day target in reality, doing so through the 11-day preparation lead visible in
its recorded dates. Arrival order commits the longest-waiting instead and gets zero.
This is the lexicographic trade made concrete: the model pays +7.2 weighted days of P2
to buy the on-time trial (its P2 may exceed the comparator's only when its P1 is
higher). One case, on estimated start dates — an existence proof of the mechanism, not
a performance statistic.

**3. The frontier says slots buy lateness relief, not on-time trials.** P1 is flat in
cap at every date (1 at 2025-02-01 under standards, else 0); P2 falls with cap and
flattens at 5 to 6 slots (2025-02-01: 729 at cap 1 to 610 at cap 5, unchanged to 8).
On real queues, adding slots beyond ~5 does nothing — the binding constraints are
duration and arrival timing, which is the preparation finding again from the capacity
side.

## Limitations

- The reconstructed queue is a **subset**: the return holds 20 trials, the tracker 104,
  so the real queues at those dates were larger. Occupancy, P2 magnitudes and the
  cap-5-6 flattening point are all lower bounds on the real instance.
- `setup_start` values are pharmacy's estimates; BNT327-06's winning lead rests on one.
- n = 3 dates, queues of 5 to 7. The replay validates mechanisms; it does not power
  comparisons.
