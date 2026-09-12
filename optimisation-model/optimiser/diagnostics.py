"""Checks run either side of the solve.

**The model can never return "infeasible", and that is deliberate.** Its only hard constraint
is the commitment limit, which committing nothing satisfies. The deadline and the value
preference sit in the objective as deviations rather than as restrictions. That is the
defining property of a goal programme: it always returns a plan, together with a statement of
how far short that plan fell.

So "is it feasible" is the wrong question. The question worth asking each cycle is whether the
60-day goal is attainable at all, and that is knowable **before** solving anything.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from dataclasses import dataclass

from .config import Settings
from .data import PlanningCase, plannable
from .gate import gate_wait
from .model import SelectionResult, solve_selection

logger = logging.getLogger(__name__)

__all__ = ["PostSolveReport", "PreSolveCheck", "post_solve_report", "pre_solve_check"]


@dataclass(frozen=True)
class PreSolveCheck:
    """What the instance allows, before any optimisation.

    Attributes:
        eligible: Cases clearing the value floor and ready to plan.
        rescueable: Names with enough slack to finish inside the target at the planned load.
        p1_ceiling: The largest on-time count any plan could achieve. `min(c, |rescueable|)`.
        nearest_miss_name: The case closest to becoming rescueable.
        nearest_miss_days: How many days short it is. This is the operational number: it says
            where a small process saving converts a breach into a success.
        breached: Names already past their 60-day due date.
        gate_wait: Expected signature wait at the commitment limit.
    """

    eligible: int
    rescueable: tuple[str, ...]
    p1_ceiling: int
    nearest_miss_name: str | None
    nearest_miss_days: int | None
    breached: tuple[str, ...]
    gate_wait: float

    @property
    def p1_is_flat(self) -> bool:
        """True when no selection can improve the on-time count, so P2 alone decides."""
        return self.p1_ceiling == 0

    def summary(self) -> str:
        if self.p1_is_flat:
            base = (
                f"P1 ceiling is 0 of {self.eligible} eligible cases. No selection can rescue "
                "anything, so weighted lateness alone determines the answer."
            )
            if self.nearest_miss_days is not None:
                return (
                    f"{base} Nearest miss is {self.nearest_miss_name}, short by "
                    f"{self.nearest_miss_days} days."
                )
            return base
        return (
            f"P1 ceiling is {self.p1_ceiling}: at most {self.p1_ceiling} of "
            f"{self.eligible} eligible cases can finish inside "
            f"{self.gate_wait:.1f} days of signature queue plus their set-up."
        )


@dataclass(frozen=True)
class PostSolveReport:
    """What the plan achieved, and what the priority order charged for it.

    Attributes:
        p1_achieved: On-time trials the plan captured.
        p1_ceiling: The most it could have captured.
        capacity_used: Slots filled, against the limit.
        capacity_limit: The commitment limit.
        binding: Which of the limit and the eligible set ran out first.
        price_of_on_time: Weighted late days given up to put on-time first. Zero has two very
            different meanings, and `price_is_meaningful` separates them.
        price_is_meaningful: False when the price is zero because no on-time trial existed to
            buy. Reading that as "on-time is free" is the misreading this flag prevents.
    """

    p1_achieved: int
    p1_ceiling: int
    capacity_used: int
    capacity_limit: int
    binding: str
    price_of_on_time: float
    price_is_meaningful: bool

    def summary(self) -> str:
        lines = [
            f"P1 achieved {self.p1_achieved} of a possible {self.p1_ceiling}.",
            (
                f"Capacity used {self.capacity_used} of {self.capacity_limit}, "
                f"{self.binding} binding."
            ),
        ]
        if self.price_is_meaningful:
            lines.append(
                f"Putting on-time first cost {self.price_of_on_time:.1f} weighted days."
            )
        else:
            lines.append(
                "On-time cost nothing, because no rescueable case existed to buy. "
                "This is not the same as on-time being free."
            )
        return " ".join(lines)


def pre_solve_check(cases: Sequence[PlanningCase], settings: Settings) -> PreSolveCheck:
    """Establish the P1 ceiling and the nearest miss without solving anything.

    Rescueability is evaluated at the commitment limit, which is the pessimistic end: a plan
    that commits fewer trials carries a shorter signature queue and may rescue more. The
    ceiling is therefore a floor on what the solver can do, never an over-claim.
    """
    eligible = plannable(cases, settings.floor)
    wait = gate_wait(settings.cap, settings)

    # Matches the solver's on-time test exactly, so this stays a real bound on P1: both
    # measure from the day work can begin, not from today.
    slack = {c.name: c.days_available - c.effective_duration - wait for c in eligible}
    rescueable = tuple(name for name, s in slack.items() if s >= 0)
    misses = {name: s for name, s in slack.items() if s < 0}

    nearest_name, nearest_days = None, None
    if misses:
        nearest_name = max(misses, key=lambda n: misses[n])
        nearest_days = round(-misses[nearest_name])

    check = PreSolveCheck(
        eligible=len(eligible),
        rescueable=rescueable,
        p1_ceiling=min(settings.cap, len(rescueable)),
        nearest_miss_name=nearest_name,
        nearest_miss_days=nearest_days,
        breached=tuple(c.name for c in eligible if c.days_to_due < 0),
        gate_wait=wait,
    )
    logger.info(check.summary())
    return check


def post_solve_report(
    result: SelectionResult,
    cases: Sequence[PlanningCase],
    settings: Settings,
    check: PreSolveCheck | None = None,
) -> PostSolveReport:
    """Price the priority order by solving the same instance again without P1.

    The second solve is the honest counterfactual: what would a lateness-only model have
    achieved, and how many weighted days did the service give up by refusing it? On the
    demonstration instance that lateness-only model rescues nothing at any capacity, which is
    the strongest available argument for ranking on-time first.

    Args:
        result: The solved plan.
        cases: The same cases the plan was solved on.
        settings: The same parameters.
        check: A pre-solve check already computed for this instance. Pass it to avoid running
            the check twice and logging its summary twice.
    """
    check = check or pre_solve_check(cases, settings)
    lateness_only = solve_selection(cases, settings, rank_on_time=False)

    # Ranking on-time first can only make weighted lateness worse or leave it unchanged, so
    # the price is the ranked plan's lateness less the lateness-only plan's.
    price = round(result.p2_weighted_lateness - lateness_only.p2_weighted_lateness, 1)
    meaningful = result.p1_on_time > lateness_only.p1_on_time

    eligible_total = check.eligible
    binding = "the commitment limit" if result.committed_count >= settings.cap else \
        "the eligible set" if result.committed_count >= eligible_total else "neither"

    report = PostSolveReport(
        p1_achieved=result.p1_on_time,
        p1_ceiling=check.p1_ceiling,
        capacity_used=result.committed_count,
        capacity_limit=settings.cap,
        binding=binding,
        price_of_on_time=abs(price),
        price_is_meaningful=meaningful,
    )
    logger.info(report.summary())
    return report
