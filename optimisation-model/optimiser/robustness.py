"""SQ3 robustness experiment: does the selection rule beat arrival order, and does
the advantage survive when arrival timing, trial mix and set-up duration vary?

Method: a Monte Carlo sensitivity analysis. Portfolios are generated across a grid of
scenarios, the selection model is solved on each, and the plan is compared with the
arrival order used today. Generating portfolios is the point — it is how the ranking is
tested outside the single queue the trust happens to hold. Grounding:

  * aseptic share is centred on the trust's own figure of roughly 60 per cent of open
    trials (LTHTR answer Q6) and varied around it;
  * the electronic-prescription share has no trust figure at all (oncology was a proxy
    that undercounts it), so it is varied rather than assumed;
  * the approval wait g_n comes from `gate.gate_wait_table` at default settings, the
    same table the selection model uses;
  * durations are SEEDED FROM THE CALIBRATION when one is supplied, and varied around
    it (0.8x, 1.0x, 1.2x), so robustness is tested around the measured point rather
    than around a guess. Without a calibration the module falls back to two standing
    regimes, illustrative and measured-like (95 days, the pooled tracker median).

The comparator is arrival order: commit the earliest arrivals up to the limit. LTHTR
answer Q4-2 records that real practice sometimes accelerates studies judged important,
so this comparator FLATTERS the model; any advantage reported here is an upper bound.

The solver is exact enumeration of every plan of size 0..c, applying the Chapter 3
formulation directly: on-time needs commitment and rescueability at the chosen size
(eq 3.4), lateness is d+_i = max(0, (p_i - delta_i) + g_n + L(1 - x_i)) over the whole
eligible queue (eq 3.5), objectives ordered P1 max on-time then P2 min weighted
lateness (eq 3.6). With c = 3 the enumeration is a few hundred subsets per draw, and
`tests/test_robustness.py` cross-checks it against the Gurobi model where licensed.
"""

from __future__ import annotations

import csv
import datetime
import itertools
import logging
import random
from collections.abc import Sequence
from dataclasses import dataclass

from .config import Settings
from .gate import gate_wait_table

logger = logging.getLogger(__name__)

__all__ = ["SynthTrial", "Scenario", "generate_portfolio", "solve_exact",
           "regimes_from_calibration",
           "arrival_order_plan", "evaluate_plan", "run_experiment", "SCENARIOS"]

SEED = 42

# Duration regimes, days per pathway (aseptic flag, rx flag).
DURATIONS = {
    "illustrative": {(False, False): 25, (True, False): 36, (False, True): 36, (True, True): 45},
    "measured95":   {(False, False): 95, (True, False): 95, (False, True): 95, (True, True): 95},
}

# Days remaining to the due day at the planning date, by arrival-timing scenario.
# "typical" reflects the cleaned tracker, where the median trial enters the queue about
# a week after the window opens; "late" reflects the long right tail of pre-queue delay.
TIMING = {
    "early":   (30, 60),
    "typical": (5, 50),
    "late":    (-30, 25),
}

@dataclass(frozen=True)
class SynthTrial:
    """One synthetic trial: everything the selection rule needs and nothing else."""

    name: str
    duration: int          # p_i, days, set by the pathway
    # delta_i, negative once breached. Synthetic trials are drawn already in the pharmacy
    # queue, so this is both days-to-due and the available window: there is no hand-over
    # still ahead to subtract. See `data.PlanningCase.days_available` for the real split.
    days_to_due: int
    days_waited: int       # a_i, days since queue entry
    claim_weight: float    # w_i = 1 + a_i / 365


@dataclass(frozen=True)
class Scenario:
    """One cell of the experiment grid."""

    timing: str
    aseptic_share: float
    rx_share: float
    regime: str

    @property
    def label(self) -> str:
        return (f"{self.timing}|asep{self.aseptic_share:.1f}|rx{self.rx_share:.1f}"
                f"|{self.regime}")


TIER_TO_FLAGS = {"Routine": (False, False), "Aseptic only": (True, False),
                 "Prescription only": (False, True), "Both": (True, True)}


def regimes_from_calibration(calibrated: dict[str, int]) -> dict[str, dict]:
    """Build duration regimes centred on the measured durations.

    `calibrated` is the per-pathway median from the finished cases in the return, as
    produced by the planning pipeline. Robustness then varies +/-20 per cent around
    that point, which is the question the trust actually faces: does the ranking hold
    if set-up runs faster or slower than the cases we measured?

    Note the pathway keys follow the current implementation, where the second flag is
    the electronic-prescription build, which replaced the oncology proxy on 2026-08-16.
    """
    out = {}
    for label, factor in (("calibrated-20pct", 0.8), ("calibrated", 1.0),
                          ("calibrated+20pct", 1.2)):
        out[label] = {TIER_TO_FLAGS[tier]: max(1, round(days * factor))
                      for tier, days in calibrated.items()}
    return out


def generate_portfolio(scenario: Scenario, rng: random.Random, settings: Settings,
                       regimes: dict[str, dict] | None = None) -> list[SynthTrial]:
    """Draw one eligible-queue portfolio for a scenario."""
    lo, hi = TIMING[scenario.timing]
    durations = (regimes or DURATIONS)[scenario.regime]
    trials = []
    for k in range(rng.randint(8, 14)):
        aseptic = rng.random() < scenario.aseptic_share
        rx = rng.random() < scenario.rx_share
        waited = rng.randint(0, 180)
        trials.append(SynthTrial(
            name=f"T{k:02d}",
            duration=durations[(aseptic, rx)],
            days_to_due=rng.randint(lo, hi),
            days_waited=waited,
            claim_weight=round(1.0 + waited / settings.weight_divisor, 4),
        ))
    return trials


def evaluate_plan(trials: Sequence[SynthTrial], committed: frozenset[str],
                  waits: dict[int, float], cycle_days: int) -> tuple[int, float]:
    """P1 and P2 for a given committed set, per equations 3.4 to 3.6."""
    n = len(committed)
    g_n = waits[n]
    p1 = 0
    p2 = 0.0
    for t in trials:
        in_plan = t.name in committed
        if in_plan and t.days_to_due >= t.duration + g_n:
            p1 += 1
        base = (t.duration - t.days_to_due) + g_n + (0 if in_plan else cycle_days)
        p2 += t.claim_weight * max(0.0, base)
    return p1, round(p2, 2)


def solve_exact(trials: Sequence[SynthTrial], waits: dict[int, float],
                cap: int, cycle_days: int) -> tuple[frozenset[str], int, float]:
    """Best plan by exhaustive enumeration: max P1, then min P2. Exact for small c."""
    names = [t.name for t in trials]
    best: tuple[int, float, frozenset[str]] | None = None
    for n in range(0, min(cap, len(names)) + 1):
        for combo in itertools.combinations(names, n):
            committed = frozenset(combo)
            p1, p2 = evaluate_plan(trials, committed, waits, cycle_days)
            key = (-p1, p2)
            if best is None or key < (-best[0], best[1]):
                best = (p1, p2, committed)
    assert best is not None
    return best[2], best[0], best[1]


def arrival_order_plan(trials: Sequence[SynthTrial], cap: int) -> frozenset[str]:
    """The comparator: commit the longest-waiting (earliest-arrived) trials up to cap."""
    ordered = sorted(trials, key=lambda t: -t.days_waited)
    return frozenset(t.name for t in ordered[:cap])


def run_experiment(draws: int = 100, out_csv: str | None = None,
                   calibrated: dict[str, int] | None = None,
                   regimes: dict[str, dict] | None = None) -> list[dict]:
    """Run every scenario cell, `draws` portfolios each.

    Args:
        draws: portfolios per scenario cell.
        out_csv: optional path for the per-cell summary.
        calibrated: per-pathway measured durations from the return. When supplied the
            duration axis becomes 0.8x / 1.0x / 1.2x around it, so the sweep tests
            robustness around what the data actually shows.
        regimes: explicit duration regimes, `{label: {(aseptic, rx): days}}`. Overrides
            both `calibrated` and the module defaults. Added 26 August 2026 so the
            section 12 standards and the pooled service p25 can run in the same seeded
            sweep as the calibration multipliers.
    """
    settings = Settings(today=datetime.date(2026, 8, 13))
    waits = gate_wait_table(settings, max_committed=14)
    if regimes is None:
        regimes = regimes_from_calibration(calibrated) if calibrated else DURATIONS
    scenarios = [Scenario(t_, a, r_, g_) for t_ in TIMING
                 for a in (0.4, 0.6, 0.8) for r_ in (0.2, 0.4)
                 for g_ in regimes]
    rows = []
    for cell_index, scenario in enumerate(scenarios):
        rng = random.Random(SEED + cell_index)  # reproducible per cell
        wins = ties = losses = 0
        p2_saving_total = 0.0
        for _ in range(draws):
            trials = generate_portfolio(scenario, rng, settings, regimes)
            if not trials:
                ties += 1
                continue
            _, m_p1, m_p2 = solve_exact(trials, waits, settings.cap, settings.cycle_days)
            fcfs = arrival_order_plan(trials, settings.cap)
            f_p1, f_p2 = evaluate_plan(trials, fcfs, waits, settings.cycle_days)
            if m_p1 > f_p1:
                wins += 1
            elif m_p1 < f_p1:
                losses += 1
            else:
                ties += 1
            p2_saving_total += f_p2 - m_p2
        rows.append({
            "timing": scenario.timing, "aseptic_share": scenario.aseptic_share,
            "rx_share": scenario.rx_share,
            "regime": scenario.regime, "draws": draws,
            "p1_wins": wins, "p1_ties": ties, "p1_losses": losses,
            "mean_p2_saving_weighted_days": round(p2_saving_total / draws, 1),
        })
        logger.info("%s: wins=%d ties=%d losses=%d", scenario.label, wins, ties, losses)
    if out_csv:
        with open(out_csv, "w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        logger.info("wrote %s", out_csv)
    return rows


SCENARIOS = [
    Scenario(timing, asep, rx, regime)
    for timing in TIMING
    for asep in (0.4, 0.6, 0.8)
    for rx in (0.2, 0.4)
    for regime in DURATIONS
]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    run_experiment(draws=100,
                   out_csv="Experiments/optimiser/robustness_results_2026-08-13.csv")
