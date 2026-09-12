"""Immutable configuration for the pharmacy set-up selection model.

Every constant here traces to `Model/Merged_Model_Specification_EN.md` or to
`Experiments/build_demo_workbook.py`, and the two agree by construction: this module is the
single source and the workbook figures were checked against it.

Nothing in this file is a measurement unless the docstring says so. `es` and `gpd` in
particular are examples pending LTHTR form, Part 3, question 2.
"""

from __future__ import annotations

import datetime
from collections.abc import Mapping
from dataclasses import dataclass, field, replace

__all__ = [
    "DUR_ILLUSTRATIVE",
    "DUR_MEASURED",
    "DUR_MEASURED_N",
    "DUR_POOLED",
    "DUR_POOLED_N",
    "TIERS",
    "Settings",
    "demo_settings",
    "tracker_settings",
]

TIERS: tuple[str, ...] = ("Routine", "Prescription only", "Aseptic only", "Both")

# Set-up durations, pharmacy notified to greenlight, from the cleaned CTIMP tracker.
# Derived by `Experiments/tier_durations.py`. Three sets, and which is in play matters.
#
# DUR_MEASURED      measured tier medians. The ordering inverts the intuition: Both is the
#                   FASTEST, because the aseptic BMR path runs alongside set-up rather than
#                   gating the greenlight, in 6 of the 11 trials recording both dates.
# DUR_POOLED        the single defensible figure. The tiers are not statistically separable
#                   (Kruskal-Wallis H=2.41, df=3, critical 7.81), so one number carries the
#                   evidence. This is the default for any real uploaded caseload.
# DUR_ILLUSTRATIVE  the measured medians at 35%, for the demonstration instance only. Every
#                   measured duration exceeds the 52-day set-up ceiling, so on real figures no
#                   trial is ever rescueable and the on-time objective is dead. These keep the
#                   real ordering while leaving the mechanism visible.
DUR_MEASURED: Mapping[str, int] = {"Routine": 102, "Prescription only": 119, "Aseptic only": 107, "Both": 79}
DUR_MEASURED_N: Mapping[str, int] = {"Routine": 4, "Prescription only": 6, "Aseptic only": 1, "Both": 11}
DUR_POOLED: int = 95
DUR_POOLED_N: int = 22

# Service-time benchmarks from the August 2026 return, added 26 August. These are what the
# service has been SHOWN to do, from the lower tail, as opposed to DUR_POOLED, which is the
# median sojourn and carries ~42 days of congestion (recompute report, section 9).
# Pharmacy burden as a capacity weight, added 27 August 2026.
#
# The Prioritisation Tool's question 4b rank is recorded for all 20 case studies. It does not
# predict how long set-up takes: work medians by band are indistinguishable, Mann-Whitney
# p = 0.83. It does predict how short set-up can be, which is what a consumed resource looks
# like. The weights are the ratio of each band's fastest observed work interval to the
# lightest band's, from the 19 case studies carrying both a set-up start and a green light:
#
#     band 2, routine        floor 23 d    weight 1.00
#     band 3 to 4, moderate  floor 40 d    weight 1.74
#     band 5 to 6, high      floor 60 d    weight 2.61
#
# The budget they are spent against is a planning parameter, exactly as the slot count is.
# Neither is measured: Part 3 question 2 asked for hands-on days and returned a band. What
# the weights buy is the removal of the slot count's false assumption that every trial costs
# the service the same. Budgets are quoted in routine-trial equivalents.
BURDEN_WEIGHTS: dict[int, float] = {2: 1.00, 3: 1.74, 4: 1.74, 5: 2.61, 6: 2.61}
BURDEN_WEIGHT_DEFAULT = 1.74

#
# SERVICE_P25_CLOCK   p25 of anchor -> pharmacy greenlight, the interval the 60-day target
#                     is scored on. Strict anchor, both HRA and site selected required, so
#                     BALLOON drops and n=19. 95% CI 46 to 111 by exact binomial order
#                     statistics. Sits 2 days above the 60-day target: a quarter of trials
#                     land within a whisker of it under current congestion.
# SERVICE_P25_TOTAL   p25 of notified -> greenlight, n=20, 95% CI 62 to 97. The same idea on
#                     the pharmacy-held interval; use when no clock anchor exists.
# Neither is a minimum: the fastest observed (34 on the clock, 61 on the total) is an
# existence proof and gets no interval, because the bootstrap is inconsistent for extreme
# order statistics. Pathways are not separable (Kruskal-Wallis p=0.577), so both figures
# are pooled. Source: `Experiments/benchmark_pathways.py` and recompute report section 10.
SERVICE_P25_CLOCK: int = 62
SERVICE_P25_CLOCK_N: int = 19
SERVICE_P25_TOTAL: int = 74
SERVICE_P25_TOTAL_N: int = 20

# The August-return calibration, settled 26 August 2026 (three supervisor decisions).
# Two worlds, each with the CV measured on ITS OWN duration basis -- pairing decided
# because a spread must match its duration's measurement scale:
#   DUR_RETURN_MEDIANS  per-path medians of notified->greenlight (recompute SS3);
#                       current performance. Draw at CV_RETURN_TOTAL = 0.467.
#   DUR_RETURN_FLOORS   per-path work floors (SS12); demonstrated-achievable, replacing
#                       the invented DUR_ILLUSTRATIVE. Draw at CV_RETURN_WORK = 0.575.
# High-burden overlay under the Q4b 5-6 definition: work floor band 60-63, so the
# floors world plans such trials at HB_FLOOR_TOP = 63 (L_required ~4 d at standard,
# ~46 d planning on the observed median -- report both). Hand-over assumption stays
# 8 days; the return's 14 is bimodal (4 negative leads, tail to +210) and is reported
# alongside, never substituted.
DUR_RETURN_MEDIANS: Mapping[str, int] = {
    "Routine": 142, "Prescription only": 102, "Aseptic only": 102, "Both": 79}
DUR_RETURN_FLOORS: Mapping[str, int] = {
    "Routine": 50, "Prescription only": 30, "Aseptic only": 72, "Both": 60}
HB_FLOOR_TOP: int = 63
CV_RETURN_TOTAL: float = 0.467
CV_RETURN_WORK: float = 0.575
DUR_ILLUSTRATIVE: Mapping[str, int] = {"Routine": 36, "Prescription only": 42, "Aseptic only": 37, "Both": 28}

# Coefficient of variation of the set-up duration itself, measured on the same 23 tracker
# sojourns that give DUR_POOLED: mean 105.9 days, standard deviation 58.0. This is a
# measurement, unlike `duration_cv`, which is a proxy for a quantity nobody has recorded.
# The two are easily confused and must not be interchanged: a 95-day multi-stage set-up and
# a single signature have no reason to vary alike, and on these figures they do not.
DUR_POOLED_CV: float = 0.548


def _pooled_durations() -> dict[str, int]:
    """One figure for every tier, which is what the evidence supports."""
    return {tier: DUR_POOLED for tier in TIERS}


@dataclass(frozen=True)
class Settings:
    """All model parameters. Frozen, so a sweep builds new instances rather than mutating one.

    Attributes:
        today: The date the model treats as now. Every wait and every claim weight is measured
            from it.
        cap: `c`, the commitment limit. How many set-ups the service chooses to open this
            cycle. A decision, not a physical wall.
        burden_budget: The capacity the service spends this cycle, in routine-trial
            equivalents. When set, a plan must satisfy sum of BURDEN_WEIGHTS over its
            committed trials <= this budget, and `cap` still bounds the count. When None
            the model falls back to counting trials, which assumes every trial costs the
            same. See BURDEN_WEIGHTS for why that assumption is false.
        floor: `t`, the per-trial value floor. Scored trials below it are closed rather than
            queued. Unscored trials always pass, flagged.
        approval_days: `E[S]`, hands-on days one approval consumes. Pending Part 3, question 2; 1.0 is an
            example and the whole gate correction scales with it.
        approver_days_per_month: Approver days available per month. Pending form A3c.
        durations: Set-up days by tier, notified to greenlight.
        arrival_rate: `lambda`, trials per month. Measured at 0.97, carried as 1.0.
        duration_cv: Coefficient of variation of the **approval time**, the `kappa` of the
            gate formula. No measurement of it exists, so 1.55 is carried as a proxy,
            measured on 51 iQemo template builds. See Chapter 4 Appendix 4.B, which records
            at length that this parameter is not identified by the available records.
        setup_duration_cv: Coefficient of variation of the **set-up duration**, used to draw
            durations in `plan_sim`. Measured 0.548 on the 23 tracker sojourns behind
            `DUR_POOLED`. A separate field from `duration_cv` because the two describe
            different quantities: sharing one field made the plan-level run draw set-ups at
            nearly three times their real spread.
        cycle_days: One planning cycle. A deferred trial is assumed to complete this many days
            later than if committed now, which is what makes deferral costly.
        handover_days: Median days from clock start to pharmacy queue entry, which is
            segment B. Tracker median, 8 days. Used twice: to assume a hand-over date for a
            trial R&I has not yet passed to pharmacy, and as the last-resort clock estimate
            when a trial has neither anchor date.
        target_days: The 60-day set-up target. LTHTR's own figure, stated in
            `Model/150_Day_Summary.md` as "set-up within 60 days from regulatory approval".
            Do not change it to buy schedule safety: use `planning_buffer_days` for that, so
            the published target stays the trust's number and the buffer stays visible.
        planning_buffer_days: Days held back from `target_days` when planning, so a trial is
            scheduled to finish early and variance does not eat the target. **Zero by
            default**, which leaves planning identical to the target. A policy choice, not a
            measurement, and it belongs to whoever runs the queue. Decided 26 August 2026:
            reported separately rather than folded into the target, because on the 20-trial
            return no trial finishes between 50 and 61 days, so a buffer anywhere in that band
            changes no verdict, and a target that is not the trust's own number costs
            credibility for nothing. See `Sources/Data/Digest_LTHTR-4-return-SE_2026-08-24.md`.
        prep_credit_cap_days: Days a study saves when pharmacy prepares before the clock
            starts, which the rule allows once the sponsor has confirmed the site and the
            study is complex. Pending LTHTR form 3, section 4, question 2, "on a complex
            study where that preparation did happen, roughly how many days does it take off
            the eventual set-up", which returns a band rather than a figure. **Zero by
            default, which makes the mechanism inert**: the credit is discretionary and
            unresourced, so a positive value must come from LTHTR rather than from a figure
            fitted here. See `data._prep_credit` for the two conditions.
        weight_divisor: Days for a trial's claim to double. A policy choice, not a measurement,
            and it should be put to LTHTR.
        value_active: Whether P3, portfolio value, participates in the ranking. Paused since
            1 August 2026 because no trial holds both a value score and pharmacy timings.
            The three levels are strictly lexicographic: P3 can order plans that P1 and P2
            leave tied, and can never buy a concession from either. There is deliberately no
            trade-budget parameter. See `model.solve_selection`.
    """

    today: datetime.date
    cap: int = 3
    floor: float = 20.0
    approval_days: float = 1.0
    approver_days_per_month: float = 9.45
    durations: Mapping[str, int] = field(default_factory=_pooled_durations)
    arrival_rate: float = 1.0
    duration_cv: float = 1.55
    setup_duration_cv: float = DUR_POOLED_CV
    cycle_days: int = 30
    handover_days: int = 8
    target_days: int = 60
    planning_buffer_days: int = 0
    prep_credit_cap_days: int = 0
    weight_divisor: float = 365.0
    value_active: bool = False
    burden_budget: float | None = None

    def __post_init__(self) -> None:
        if self.burden_budget is not None and self.burden_budget < 0:
            raise ValueError(
                f"burden_budget must not be negative, got {self.burden_budget}"
            )
        if self.cap < 0:
            raise ValueError(f"cap must not be negative, got {self.cap}")
        if self.approval_days <= 0:
            raise ValueError(f"approval_days must be positive, got {self.approval_days}")
        if self.approver_days_per_month <= 0:
            raise ValueError(
                f"approver_days_per_month must be positive, got {self.approver_days_per_month}"
            )
        if self.weight_divisor <= 0:
            raise ValueError(f"weight_divisor must be positive, got {self.weight_divisor}")
        if self.setup_duration_cv < 0:
            raise ValueError(
                f"setup_duration_cv must not be negative, got {self.setup_duration_cv}"
            )
        if self.planning_buffer_days < 0:
            raise ValueError(
                f"planning_buffer_days must not be negative, got {self.planning_buffer_days}"
            )
        if self.planning_buffer_days >= self.target_days:
            raise ValueError(
                f"planning_buffer_days ({self.planning_buffer_days}) must be less than "
                f"target_days ({self.target_days})"
            )
        if self.prep_credit_cap_days < 0:
            raise ValueError(
                f"prep_credit_cap_days must not be negative, got {self.prep_credit_cap_days}"
            )
        missing = [tier for tier in TIERS if tier not in self.durations]
        if missing:
            raise ValueError(f"durations missing tiers: {missing}")

    @property
    def planning_deadline_days(self) -> int:
        """The date planning aims at: the target less any buffer held back.

        Equals `target_days` at the default zero buffer, so nothing moves unless someone
        deliberately sets one. Report performance against `target_days`, plan against this.
        """
        return self.target_days - self.planning_buffer_days

    @property
    def setup_ceiling(self) -> int:
        """Set-up days the planning deadline can accommodate, once the median handover is spent.

        Any tier duration above this cannot reach the deadline however many slots are opened.
        On the measured figures every tier is above it, which is the binding finding.
        """
        return self.planning_deadline_days - self.handover_days

    def with_planning_buffer(self, planning_buffer_days: int) -> Settings:
        """A copy at a different buffer, for showing the planner's sensitivity to it."""
        return replace(self, planning_buffer_days=planning_buffer_days)

    def with_cap(self, cap: int) -> Settings:
        """A copy at a different commitment limit, for sweeping outputs 8 to 11."""
        return replace(self, cap=cap)

    def with_approval_days(self, approval_days: float) -> Settings:
        """A copy at a different `E[S]`, for the Part 3, question 2 sensitivity."""
        return replace(self, approval_days=approval_days)


def demo_settings(today: datetime.date | None = None) -> Settings:
    """Settings for the 16-trial demonstration instance.

    Matches `Experiments/build_demo_workbook.py` and the planner prototype exactly, so all
    three describe one caseload and their figures can be compared.
    """
    return Settings(
        today=today or datetime.date(2026, 8, 3),
        cap=3,
        floor=20.0,
        approval_days=1.0,
        approver_days_per_month=9.45,
        durations=dict(DUR_ILLUSTRATIVE),
        value_active=False,
    )


def tracker_settings(today: datetime.date | None = None) -> Settings:
    """Settings for a real caseload: pooled durations, value layer off.

    The value floor is inert here because no tracker trial carries a score. That is the empty
    join of specification section 2c, not a configuration choice.
    """
    return Settings(
        today=today or datetime.date(2026, 8, 3),
        cap=3,
        floor=20.0,
        approval_days=1.0,
        approver_days_per_month=9.45,
        durations=_pooled_durations(),
        value_active=False,
    )
