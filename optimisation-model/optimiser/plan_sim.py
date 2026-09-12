"""What a committed plan is actually likely to deliver, rather than what it promises.

`model.solve_selection` returns an on-time count. That count is computed at one set-up
duration per trial, the tier median, so it reads as a fact: *two trials finish inside 60
days*. It is not a fact. Set-up durations vary widely around their median, and the count is
a random variable over the plans a service could end up with. Reporting its expected value
alone tells the service nothing about how often the plan misses.

This module runs a committed plan forward many times, drawing a duration for each trial
instead of fixing it, and reports the distribution of the on-time count. "Two on time in 61
per cent of runs, one in 27 per cent" is a different and far more useful statement than
"two on time", and it is the statement a service sizing its capacity needs.

**What varies here and what does not.** Durations are drawn. The approval wait is held at
`gate.gate_wait`, its expected value at the committed count, because this project models
that queue in closed form and does not simulate it. The wait itself varies in reality, so
the spread reported here comes from duration alone and **understates** the total
uncertainty in the on-time count. That is a floor on the spread, not an estimate of it, and
it should be reported as such.

Durations are drawn lognormal, anchored on the tier duration as its **median** and spread by
`setup_duration_cv`, both measured on the same 23 tracker sojourns. The tier durations are
medians, so anchoring the draw on the median is what makes the generated distribution match
the recorded one: median 95 against a recorded 95, mean 108 against a recorded 106.
Note that this is **not** `duration_cv`: that field is the approval-time proxy the gate
formula uses, and it is nearly three times larger. Drawing set-ups at it puts their median
at 57 days against a recorded 95 and generates set-ups faster than any on record.

Lognormal is positive and right-skewed, which a set-up duration must be, and it is fixed by
those two moments. No claim is made that set-up is lognormal; the shape is the least
committal one consistent with what the calibration measures.
"""

from __future__ import annotations

import logging
import math
import random
import statistics as st
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass

from .config import Settings
from .data import PlanningCase
from .gate import gate_wait

logger = logging.getLogger(__name__)

__all__ = [
    "PlanOutcome",
    "TrialRisk",
    "simulate_plan",
]


@dataclass(frozen=True)
class TrialRisk:
    """How one committed trial fared across the runs.

    Attributes:
        name: The trial.
        on_time_probability: Share of runs in which it finished inside its window.
        median_overrun: Median days past the window, counting a run that finished early as
            zero. A trial that usually makes it still has an overrun of zero here.
        deterministic_on_time: What the plan claimed for this trial at the tier median.
            Where this disagrees with `on_time_probability` the plan is relying on a
            duration it will not always get.
    """

    name: str
    on_time_probability: float
    median_overrun: float
    deterministic_on_time: bool


@dataclass(frozen=True)
class PlanOutcome:
    """The on-time count as a distribution rather than a number.

    Attributes:
        committed: Trials in the plan.
        deterministic_count: The on-time count `solve_selection` reported, computed at the
            tier median duration. The figure this module exists to qualify.
        distribution: On-time count mapped to the share of runs producing it. Keys run from
            zero to `committed`.
        mean_count: Expected on-time count across the runs.
        p10_count: The count met or exceeded in 90 per cent of runs. The pessimistic end,
            and the one a service planning capacity should look at.
        probability_at_least_deterministic: How often the plan achieves what it promised. A
            low figure means the reported count rests on durations that rarely occur.
        gate_wait: The approval wait applied, held fixed at its expected value.
        per_trial: Risk for each committed trial, worst first.
        replications: Runs behind every figure above.
    """

    committed: int
    deterministic_count: int
    distribution: dict[int, float]
    mean_count: float
    p10_count: int
    probability_at_least_deterministic: float
    gate_wait: float
    per_trial: tuple[TrialRisk, ...]
    replications: int


def _lognormal_draw(median: float, cv: float, rng: random.Random) -> float:
    """A positive right-skewed duration with the given median and coefficient of variation.

    **The anchor is the median, not the mean, because that is what the calibration measures.**
    `DUR_POOLED` and the tier durations are medians of the tracker sojourns. Feeding a median
    to a mean-anchored draw pulls the whole distribution down: at the pooled 95 days and a
    coefficient of variation of 0.548 it returns a median of 83, twelve days short of the
    figure the calibration recorded. Anchoring on the median returns 95 exactly, and a mean
    of 108 against the 106 the same 23 sojourns show.
    """
    if cv <= 0.0:
        return median
    sigma = math.sqrt(math.log1p(cv * cv))
    return rng.lognormvariate(math.log(median), sigma)


def simulate_plan(
    committed: Sequence[PlanningCase],
    settings: Settings,
    replications: int = 2000,
    seed: int = 20260818,
) -> PlanOutcome:
    """Run a committed plan forward under duration uncertainty.

    Args:
        committed: The trials the model chose. Pass the plan, not the whole queue: a
            deferred trial contributes no on-time count and is not at risk here.
        settings: Supplies the coefficient of variation and the approval wait. The same
            object the selection model was solved with, or the plan and the simulation
            will not describe the same world.
        replications: Runs. Two thousand puts the standard error on a probability near a
            half at about one percentage point, which is finer than the decision needs.
        seed: Stream seed, so any figure regenerates exactly.

    Returns:
        The on-time count as a distribution, with per-trial risk behind it.

    Raises:
        ValueError: If no trials are supplied or `replications` is not positive.
    """
    if not committed:
        raise ValueError("simulate_plan needs at least one committed trial")
    if replications < 1:
        raise ValueError(f"replications must be at least 1, got {replications}")

    rng = random.Random(seed)
    wait = gate_wait(len(committed), settings)
    cv = settings.setup_duration_cv

    counts: list[int] = []
    successes = {c.name: 0 for c in committed}
    overruns: dict[str, list[float]] = {c.name: [] for c in committed}

    for _ in range(replications):
        on_time = 0
        for case in committed:
            median = float(case.effective_duration or case.duration)
            drawn = _lognormal_draw(median, cv, rng)
            slack = case.days_available - (drawn + wait)
            if slack >= 0.0:
                on_time += 1
            overruns[case.name].append(max(0.0, -slack))
            successes[case.name] += 1 if slack >= 0.0 else 0
        counts.append(on_time)

    tally = Counter(counts)
    distribution = {
        k: round(tally.get(k, 0) / replications, 4) for k in range(len(committed) + 1)
    }
    deterministic = sum(
        1
        for c in committed
        if c.days_available >= (c.effective_duration or c.duration) + wait
    )
    ordered = sorted(counts)
    at_least = sum(1 for n in counts if n >= deterministic) / replications

    per_trial = tuple(
        sorted(
            (
                TrialRisk(
                    name=c.name,
                    on_time_probability=round(successes[c.name] / replications, 4),
                    median_overrun=round(st.median(overruns[c.name]), 1),
                    deterministic_on_time=(
                        c.days_available >= (c.effective_duration or c.duration) + wait
                    ),
                )
                for c in committed
            ),
            key=lambda r: r.on_time_probability,
        )
    )

    outcome = PlanOutcome(
        committed=len(committed),
        deterministic_count=deterministic,
        distribution=distribution,
        mean_count=round(st.fmean(counts), 3),
        p10_count=ordered[int(0.10 * len(ordered))],
        probability_at_least_deterministic=round(at_least, 4),
        gate_wait=wait,
        per_trial=per_trial,
        replications=replications,
    )
    logger.info(
        "plan of %d: reported %d on time, achieved in %.0f%% of runs, mean %.2f",
        outcome.committed, outcome.deterministic_count,
        100.0 * outcome.probability_at_least_deterministic, outcome.mean_count,
    )
    return outcome
