"""The single approval signature, and the wait it imposes.

Every pharmacy set-up crosses one approving person. When several set-ups run at once they
queue for that signature, so the expected wait grows with the number of trials committed.

The consequence the model depends on: **rescueability is a property of the plan, not of the
trial.** A trial with 40 days to its due date and a 30-day set-up is inside the target in a
three-trial month and outside it in an eight-trial month, because the gate wait differs.

The wait is a standard M/G/1 approximation. It is precomputed for each plausible committed
count and embedded as a step function, which is what keeps the selection model an integer
*linear* programme rather than a nonlinear one.

**Known overlap with the duration, recorded 26 August 2026.** The rescue test is
``days_available >= duration + gate_wait``, and the duration in play is a tracker *sojourn*
from notification to green light, so it already contains whatever wait that trial spent at
the signature. Adding `gate_wait` therefore counts that wait twice. Left in place because
the size is negligible at the loads this service runs: 0.46 days at two committed, 0.79 at
three, against a 95-day duration. It passes 10% only above eight committed, which is beyond
anything LTHTR does. Fix it by supplying a service-time duration rather than a sojourn, not
by removing the term. See section 9 of
`Experiments/eda_output/real_run/CH4_RECOMPUTE_2026-08-26.md`.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping

from .config import Settings

logger = logging.getLogger(__name__)

__all__ = [
    "MAX_UTILISATION",
    "describe_ceiling",
    "gate_wait",
    "gate_wait_table",
    "rescue_matrix",
    "rescueable_counts",
]

# The queueing formula diverges as utilisation approaches 1. Capping at 0.95 keeps the model
# solvable and makes the saturation visible as a plateau rather than an overflow. At the
# example approval time this binds from about 2.99 hands-on days per approval, at which point
# output 21 stops being an ablation and becomes a capacity finding about the signature itself.
MAX_UTILISATION: float = 0.95


def gate_wait(committed: int, settings: Settings) -> float:
    """Expected wait in days at the approval signature when `committed` trials are taken on.

    `committed` is the number of set-ups opened in a cycle, not a count of set-ups running
    concurrently at some instant. The formula treats that monthly commitment as the load on
    the approver.

    Args:
        committed: Number of trials committed this cycle.
        settings: Model parameters supplying `E[S]`, approver availability and the duration CV.

    Returns:
        Expected wait in days, rounded to two decimals. Zero when nothing is committed.

    Raises:
        ValueError: If `committed` is negative.
    """
    if committed < 0:
        raise ValueError(f"committed must not be negative, got {committed}")
    if committed == 0:
        return 0.0

    load = settings.arrival_rate * committed * settings.approval_days
    utilisation = min(MAX_UTILISATION, load / settings.approver_days_per_month)
    cv = settings.duration_cv
    wait = (
        utilisation / (1.0 - utilisation)
        * (1.0 + cv * cv) / 2.0
        * settings.approval_days
    )
    return round(wait, 2)


def gate_wait_table(settings: Settings, max_committed: int | None = None) -> dict[int, float]:
    """The step function `W_gate(n)`, precomputed for every count the model can choose.

    Args:
        settings: Model parameters.
        max_committed: Highest count to tabulate. Defaults to the commitment limit.

    Returns:
        Mapping from committed count to expected gate wait in days, for 0 to `max_committed`.
    """
    top = settings.cap if max_committed is None else max_committed
    table = {n: gate_wait(n, settings) for n in range(top + 1)}
    if table and table[top] >= settings.target_days:
        logger.warning(
            "Gate wait at %d committed is %.1f days, at or beyond the %d-day target. "
            "The signature, not capacity, is the constraint at this load.",
            top, table[top], settings.target_days,
        )
    return table


def rescue_matrix(
    days_available: Mapping[str, int],
    durations: Mapping[str, int],
    wait_table: Mapping[int, float],
) -> dict[str, dict[int, bool]]:
    """Which trials can still finish inside 60 days, evaluated at each committed count.

    This is the constant table the selection model reads. It is precomputed rather than
    derived inside the solver because the queueing formula is nonlinear in the committed
    count, and tabulating it is what keeps the model linear.

    Args:
        days_available: Days from the day work can begin to the 60-day due date, per trial
            name, from `data.PlanningCase.days_available`. This is days-to-due net of any
            hand-over still ahead, so passing days-to-due instead would credit a trial with
            time it will spend waiting for R&I. Negative means the trial has already breached.
        durations: Set-up duration in days, per trial name.
        wait_table: Expected gate wait by committed count, from `gate_wait_table`.

    Returns:
        `matrix[name][n]` is True when trial `name` still finishes inside its target given
        `n` trials share the signature.
    """
    return {
        name: {
            n: days_available[name] >= durations[name] + wait
            for n, wait in wait_table.items()
        }
        for name in days_available
    }


def rescueable_counts(matrix: Mapping[str, Mapping[int, bool]]) -> dict[int, int]:
    """How many trials are rescueable at each committed count.

    Reading this down the counts shows the ceiling directly: it falls as the count rises,
    because a fuller month makes every approval wait longer.
    """
    counts: dict[int, int] = {}
    for per_trial in matrix.values():
        for n, ok in per_trial.items():
            counts[n] = counts.get(n, 0) + int(ok)
    return counts


def describe_ceiling(settings: Settings, matrix: Mapping[str, Mapping[int, bool]]) -> str:
    """One sentence on where the on-time objective peaks, for logs and reports."""
    counts = rescueable_counts(matrix)
    if not counts or max(counts.values()) == 0:
        return (
            "No trial is rescueable at any committed count. On these durations the on-time "
            "objective is identically zero and capacity cannot change it."
        )
    achievable = {n: min(n, c) for n, c in counts.items()}
    best = max(achievable, key=lambda n: (achievable[n], -n))
    return (
        f"On-time count peaks at {achievable[best]} trials with {best} committed. "
        f"Gate wait there is {gate_wait(best, settings):.1f} days."
    )
