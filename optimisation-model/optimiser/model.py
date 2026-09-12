"""The selection model, as a Gurobi integer linear programme.

It decides **which** trials pharmacy commits to set-up this cycle. It does not produce a
timetable, which is what keeps it distinct from a scheduling model.

Formulation, matching `Model/Merged_Model_Specification_EN.md` section 4:

    decision      x_i in {0,1}                      commit trial i, or defer it
    eligibility   i in E  iff  v_i >= t             below-floor trials are closed, not queued
    capacity      sum_i x_i <= c                    a commitment limit, not a staffing wall
    burden        sum_i b_i x_i <= B                 optional, b from config.BURDEN_WEIGHTS
    load selector sum_n z_n = 1,  sum_i x_i = sum_n n z_n
    on time       onTime_i <= x_i
                  onTime_i <= sum_n r_in z_n        r precomputed, see gate.rescue_matrix
    lateness      d+_i >= (p_i - avail_i) + sum_n g_n z_n + cycle (1 - x_i),  d+_i >= 0

`avail_i` is days from the day work can begin to the due day, not days from today. The two
differ only for a trial R&I has not yet handed to pharmacy, where the rest of that hand-over
is still ahead. See `data._work_start`.

`p_i` is the tier duration less any preparation credit, which is non-zero only for a study
the sponsor has confirmed and which is complex, meaning aseptic or phase 1, and only once
LTHTR set `prep_credit_cap_days` above its default of 0. See `data._prep_credit`.

    P1  max  sum_i onTime_i
    P2  min  sum_i w_i d+_i
    P3  max  sum_i v_i x_i                          paused since 1 August 2026

Pharmacy burden enters as the capacity constraint, never as an objective. The service does
not choose which trials the sponsor sends it, so a burden term in the objective would reward
declining work the trust has already accepted. As a weight it says something the service does
control: a heavy trial consumes more of the cycle than a light one, so fewer of them fit.
Withdrawn on 27 August 2026: a third objective on the 4b rank, and an eligibility filter that
dropped high-burden trials from the plannable set. Both encoded a refusal pharmacy cannot make.

Two things here are stronger than the spreadsheet and the planner prototype, and both matter.

**The gate wait is evaluated at the count the plan actually commits**, through the `z_n`
selector, rather than assumed to sit at the commitment limit. A plan of two carries a shorter
signature queue than a plan of three, so the same trial can be rescueable in one and not the
other. The workbook evaluates rescueability at `c` throughout, which over-states the wait
whenever the model would rather commit fewer trials.

**Lateness is written in deviation form**, so a trial's cost of deferral is derived rather
than assumed. For a trial already past its due date this reduces exactly to the workbook's
`w_i x cycle` saving, which is the regression test in `tests/`.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from .config import Settings
from .data import PlanningCase, plannable
from .gate import gate_wait_table, rescue_matrix

logger = logging.getLogger(__name__)

__all__ = ["Decision", "GurobiUnavailableError", "SelectionResult", "solve_selection"]

COMMIT, DEFER, CLOSE, BLOCKED = "COMMIT", "DEFER", "CLOSE", "BLOCKED"


class GurobiUnavailableError(RuntimeError):
    """Raised when gurobipy cannot be imported or no usable licence is present."""


def _import_gurobi():
    """Import gurobipy with a message that names the fix rather than the traceback."""
    try:
        import gurobipy as gp
        from gurobipy import GRB
    except ImportError as exc:
        raise GurobiUnavailableError(
            "gurobipy is not installed. Install it with `uv pip install gurobipy`. "
            "The pip package ships a restricted licence that is large enough for this model "
            "(a 100-trial instance uses about 300 variables against a 2,000 limit)."
        ) from exc
    return gp, GRB


@dataclass(frozen=True)
class Decision:
    """What the model decided about one case, and the sentence explaining it."""

    name: str
    action: str
    reason: str
    tier: str
    duration: int
    prep_credit: int
    effective_duration: int
    days_to_due: int
    days_available: int
    segment_b: int | None
    claim_weight: float
    saving: float
    on_time: bool
    value: float | None
    lateness: float


@dataclass(frozen=True)
class SelectionResult:
    """The solved plan, its objective values, and enough context to defend it.

    Attributes:
        decisions: Every case, in the order the model ranks them.
        committed: Names committed this cycle.
        p1_on_time: Committed trials that can still finish inside 60 days.
        p2_weighted_lateness: Weighted late days across the eligible queue, committed and
            deferred together. Lower is better.
        p3_value: Portfolio value committed. Reported whether or not P3 ranked.
        committed_count: How many slots the plan used.
        gate_wait: Expected wait at the approval signature at that count, in days.
        settings: The parameters that produced this result.
    """

    decisions: tuple[Decision, ...]
    committed: tuple[str, ...]
    p1_on_time: int
    p2_weighted_lateness: float
    p3_value: float
    committed_count: int
    gate_wait: float
    settings: Settings

    @property
    def deferred(self) -> tuple[str, ...]:
        return tuple(d.name for d in self.decisions if d.action == DEFER)

    @property
    def closed(self) -> tuple[str, ...]:
        return tuple(d.name for d in self.decisions if d.action == CLOSE)

    @property
    def blocked(self) -> tuple[str, ...]:
        """Cases that could not enter the model, for want of any usable date."""
        return tuple(d.name for d in self.decisions if d.action == BLOCKED)

    def headline(self) -> str:
        """The sentence the meeting actually asked for."""
        if not self.committed:
            return "No case is ready to commit this cycle."
        names = ", ".join(self.committed)
        return (
            f"Commit {len(self.committed)} of {self.settings.cap} slots: {names}. "
            f"{self.p1_on_time} still inside {self.settings.target_days} days."
        )


def _reason(
    action: str,
    case: PlanningCase,
    on_time: bool,
    settings: Settings,
) -> str:
    """A sentence per case that could be read out to a sponsor."""
    if action == BLOCKED:
        return ("No clock anchor and no pharmacy queue-entry date, so the case cannot be "
                "planned yet")
    if action == CLOSE:
        return f"Below the worth-doing floor of {settings.floor:g}"

    if action == COMMIT:
        sentence = (f"Can still finish within {settings.target_days} days" if on_time
                    else "Largest weighted saving among the rest")
    else:
        saving = case.cycle_saving(settings.cycle_days)
        sentence = f"No slot left; waiting costs {saving:.0f} weighted days this month"

    if case.queue_entry_assumed:
        # Never let an assumed hand-over pass as a measured one on a row someone will act on.
        sentence += (f", assuming R&I hands it over in {settings.handover_days} days")
    elif case.segment_b is not None and case.segment_b > 0:
        sentence += f" ({case.segment_b}d of the clock spent before pharmacy had it)"
    if case.prep_credit:
        sentence += (f", {case.prep_credit}d off for preparation done before the clock "
                     "started")
    return sentence


def solve_selection(
    cases: Sequence[PlanningCase],
    settings: Settings,
    rank_on_time: bool = True,
    log_to_console: bool = False,
) -> SelectionResult:
    """Solve one planning cycle.

    Args:
        cases: Enriched cases, from `data.enrich`.
        settings: Model parameters.
        rank_on_time: Whether P1 participates. Setting it False drops to lateness-only, which
            is the comparison the frontier and the price-of-on-time diagnostic need. It is not
            a mode to run the service on: on the demonstration instance a lateness-only model
            rescues nothing at any capacity from 1 to 9 slots.
        log_to_console: Pass through to the Gurobi log.

    Returns:
        The solved plan.

    Raises:
        GurobiUnavailableError: If gurobipy is missing or unlicensed.
        RuntimeError: If the solve does not reach optimality, which should not happen: the
            model always admits the empty plan, so it can never be infeasible.
    """
    gp, GRB = _import_gurobi()

    eligible = plannable(cases, settings.floor)
    names = [c.name for c in eligible]
    by_name = {c.name: c for c in eligible}

    if not eligible:
        logger.warning("No case clears the value floor of %g, so nothing can be committed.",
                       settings.floor)
        return _empty_result(cases, settings)

    cap = min(settings.cap, len(eligible))
    if settings.burden_budget is not None:
        # No plan can hold more trials than the budget buys at the cheapest weight, so the
        # load selector need not carry levels the burden constraint would reject anyway.
        affordable = 0
        spent = 0.0
        for weight in sorted(c.capacity_weight for c in eligible):
            if spent + weight > settings.burden_budget:
                break
            spent += weight
            affordable += 1
        cap = min(cap, affordable)
    counts = range(cap + 1)

    waits = gate_wait_table(settings, max_committed=cap)
    rescue = rescue_matrix(
        days_available={c.name: c.days_available for c in eligible},
        durations={c.name: c.effective_duration for c in eligible},
        wait_table=waits,
    )

    model = gp.Model("lthtr_pharmacy_selection")
    model.Params.OutputFlag = 1 if log_to_console else 0
    model.ModelSense = GRB.MINIMIZE

    commit = model.addVars(names, vtype=GRB.BINARY, name="x")
    load = model.addVars(counts, vtype=GRB.BINARY, name="z")
    on_time = model.addVars(names, vtype=GRB.BINARY, name="onTime")
    late = model.addVars(names, lb=0.0, vtype=GRB.CONTINUOUS, name="dplus")

    # Capacity, expressed through the load selector so the gate wait knows the plan's size.
    # The count still drives the gate: the approval signature queue lengthens with the number
    # of trials awaiting a signature, not with how demanding each one is.
    model.addConstr(load.sum() == 1, name="one_load_level")
    model.addConstr(commit.sum() == gp.quicksum(n * load[n] for n in counts), name="capacity")

    # Burden budget, when the service has set one. Spent in routine-trial equivalents, so a
    # band 5 to 6 trial costs 2.61 of the budget and a band 2 trial costs 1.
    if settings.burden_budget is not None:
        model.addConstr(
            gp.quicksum(by_name[n].capacity_weight * commit[n] for n in names)
            <= settings.burden_budget,
            name="burden_budget",
        )

    gate_expr = gp.quicksum(waits[n] * load[n] for n in counts)

    for name in names:
        case = by_name[name]
        # On time only if committed, and only if rescueable at the load actually chosen.
        model.addConstr(on_time[name] <= commit[name], name=f"ontime_needs_commit[{name}]")
        model.addConstr(
            on_time[name] <= gp.quicksum(int(rescue[name][n]) * load[n] for n in counts),
            name=f"ontime_needs_slack[{name}]",
        )
        # Goal constraint: days late against the target, with deferral costing one cycle.
        # Measured from when work can begin, so a trial R&I has not yet handed over carries
        # the rest of that hand-over as lateness rather than being credited with it.
        base = case.effective_duration - case.days_available
        model.addConstr(
            late[name] >= base + gate_expr + settings.cycle_days * (1 - commit[name]),
            name=f"lateness[{name}]",
        )

    p1 = gp.quicksum(on_time[n] for n in names)
    p2 = gp.quicksum(by_name[n].claim_weight * late[n] for n in names)
    p3 = gp.quicksum((by_name[n].value or 0.0) * commit[n] for n in names)

    # Hierarchical objectives. Higher priority is optimised first and then fixed, which is
    # strict lexicographic ordering rather than a weighted blend. Both tolerances stay at
    # zero so a lower level can never buy a concession from a higher one.
    #
    # There is deliberately no trade budget `k`. Loosening these tolerances would let P3 buy
    # on-time trials from P1, and the evidence says that trade never pays: portfolio value is
    # additive and near-linear in the number of trials committed, so more trials always means
    # more value. A `trade_budget` setting existed until 19 August 2026, was never read here,
    # and has been withdrawn. See the specification, section 6C, frontier 3.
    priority = 3
    if rank_on_time:
        model.setObjectiveN(-p1, index=0, priority=priority, name="P1_on_time")
        priority -= 1
    model.setObjectiveN(p2, index=1 if rank_on_time else 0, priority=priority,
                        name="P2_weighted_lateness")
    priority -= 1
    if settings.value_active:
        model.setObjectiveN(-p3, index=2 if rank_on_time else 1, priority=priority,
                            name="P3_value")

    model.optimize()

    if model.Status != GRB.OPTIMAL:
        raise RuntimeError(
            f"Solve ended at status {model.Status}, which should not be reachable: the empty "
            "plan is always feasible. Check the instance for NaN dates or durations."
        )

    return _read_solution(cases, eligible, settings, commit, on_time, late, waits)


def _read_solution(
    all_cases: Sequence[PlanningCase],
    eligible: Sequence[PlanningCase],
    settings: Settings,
    commit,
    on_time,
    late,
    waits: Mapping[int, float],
) -> SelectionResult:
    """Turn solver variables into decisions, ranked the way the meeting reads them."""
    eligible_names = {c.name for c in eligible}
    chosen = {c.name for c in eligible if commit[c.name].X > 0.5}
    rescued = {c.name for c in eligible if on_time[c.name].X > 0.5}
    wait = waits[len(chosen)]

    decisions: list[Decision] = []
    for case in all_cases:
        if not case.ready:
            action, is_on_time, lateness = BLOCKED, False, 0.0
        elif case.name not in eligible_names:
            action, is_on_time, lateness = CLOSE, False, 0.0
        elif case.name in chosen:
            action = COMMIT
            is_on_time = case.name in rescued
            lateness = round(late[case.name].X, 1)
        else:
            action, is_on_time = DEFER, False
            lateness = round(late[case.name].X, 1)

        decisions.append(
            Decision(
                name=case.name,
                action=action,
                reason=_reason(action, case, is_on_time, settings),
                tier=case.tier,
                duration=case.duration,
                prep_credit=case.prep_credit,
                effective_duration=case.effective_duration,
                days_to_due=case.days_to_due,
                days_available=case.days_available,
                segment_b=case.segment_b,
                claim_weight=case.claim_weight,
                saving=case.cycle_saving(settings.cycle_days),
                on_time=is_on_time,
                value=case.value,
                lateness=lateness,
            )
        )

    rank = {COMMIT: 0, DEFER: 1, CLOSE: 2, BLOCKED: 3}
    decisions.sort(key=lambda d: (rank[d.action], not d.on_time, -d.saving))

    committed = tuple(d.name for d in decisions if d.action == COMMIT)
    return SelectionResult(
        decisions=tuple(decisions),
        committed=committed,
        p1_on_time=len(rescued),
        p2_weighted_lateness=round(
            sum(c.claim_weight * late[c.name].X for c in eligible), 1
        ),
        p3_value=round(sum(c.value or 0.0 for c in eligible if c.name in chosen), 1),
        committed_count=len(chosen),
        gate_wait=wait,
        settings=settings,
    )


def _empty_result(cases: Sequence[PlanningCase], settings: Settings) -> SelectionResult:
    """The plan when nothing is eligible. Still a plan, with a reason on every row."""
    decisions = tuple(
        Decision(
            name=c.name,
            action=BLOCKED if not c.ready else CLOSE,
            reason=_reason(BLOCKED if not c.ready else CLOSE, c, False, settings),
            tier=c.tier,
            duration=c.duration,
            prep_credit=c.prep_credit,
            effective_duration=c.effective_duration,
            days_to_due=c.days_to_due,
            days_available=c.days_available,
            segment_b=c.segment_b,
            claim_weight=c.claim_weight,
            saving=c.cycle_saving(settings.cycle_days),
            on_time=False,
            value=c.value,
            lateness=0.0,
        )
        for c in cases
    )
    return SelectionResult(
        decisions=decisions, committed=(), p1_on_time=0, p2_weighted_lateness=0.0,
        p3_value=0.0, committed_count=0, gate_wait=0.0, settings=settings,
    )
