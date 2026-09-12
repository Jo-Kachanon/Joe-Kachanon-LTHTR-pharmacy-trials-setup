"""Checks that the Gurobi model agrees with what is already published.

The demonstration instance has an answer in `Sources/Data/Model_Demo_Workbook_2026-08.xlsx`
and in the planner prototype, both produced by a greedy rule. If the exact optimiser disagrees
with the greedy rule on that instance, one of them is wrong, and these tests are how that gets
caught rather than discovered in a meeting.

Run with:  python -m pytest Experiments/optimiser/tests -q
"""

from __future__ import annotations

import itertools
from collections.abc import Sequence

import pytest

from Experiments.optimiser import (
    Settings,
    demo_settings,
    enrich,
    gate_wait,
    load_demo_cases,
    plannable,
    pre_solve_check,
    settings_from_json,
    solve_json,
    solve_selection,
)
from Experiments.optimiser.data import PlanningCase


@pytest.fixture(scope="module")
def settings() -> Settings:
    return demo_settings()


@pytest.fixture(scope="module")
def cases(settings: Settings) -> list[PlanningCase]:
    return enrich(load_demo_cases(), settings)


def _greedy(cases: Sequence[PlanningCase], settings: Settings) -> list[str]:
    """The planner's rule: rescueable first, then largest weighted saving, take the top `cap`.

    Rescueability is evaluated at the commitment limit, which is what the JavaScript does.
    """
    wait = gate_wait(settings.cap, settings)
    eligible = plannable(cases, settings.floor)
    ranked = sorted(
        eligible,
        key=lambda c: (
            not (c.days_to_due >= c.duration + wait),
            -c.cycle_saving(settings.cycle_days),
        ),
    )
    return [c.name for c in ranked[: settings.cap]]


def _brute_force_best(cases: Sequence[PlanningCase], settings: Settings) -> tuple[int, float]:
    """Enumerate every plan and return the lexicographic optimum as (P1, P2).

    Slow by design. It is the independent answer the solver is checked against, and at 16
    cases and 3 slots there are only a few hundred plans.
    """
    eligible = plannable(cases, settings.floor)
    best: tuple[int, float] | None = None
    for size in range(settings.cap + 1):
        wait = gate_wait(size, settings)
        for combo in itertools.combinations(eligible, size):
            chosen = {c.name for c in combo}
            p1 = sum(1 for c in combo if c.days_to_due >= c.duration + wait)
            p2 = 0.0
            for c in eligible:
                base = c.duration - c.days_to_due
                deferral = 0 if c.name in chosen else settings.cycle_days
                p2 += c.claim_weight * max(0.0, base + wait + deferral)
            score = (p1, -round(p2, 6))
            if best is None or score > (best[0], -round(best[1], 6)):
                best = (p1, round(p2, 1))
    assert best is not None
    return best


def test_instance_loads_as_expected(cases: list[PlanningCase]) -> None:
    assert len(cases) == 16
    assert all(c.ready for c in cases), "every demonstration case carries a notified date"
    assert {c.tier for c in cases} == {"Routine", "Prescription only", "Aseptic only", "Both"}


def test_illustrative_durations_are_below_the_ceiling(settings: Settings) -> None:
    """The demonstration only shows the on-time mechanism because its durations fit.

    On measured durations every tier is above the ceiling, which is the real finding. This
    test guards the demo instance, not the service.
    """
    assert all(d <= settings.setup_ceiling for d in settings.durations.values())


def test_solution_matches_brute_force(cases: list[PlanningCase], settings: Settings) -> None:
    """The solver must reach the lexicographic optimum, checked by enumeration."""
    result = solve_selection(cases, settings)
    p1_best, p2_best = _brute_force_best(cases, settings)
    assert result.p1_on_time == p1_best
    assert result.p2_weighted_lateness == pytest.approx(p2_best, abs=0.15)


def test_matches_the_published_greedy_answer(
    cases: list[PlanningCase], settings: Settings
) -> None:
    """The greedy rule is optimal for this constraint set, so the two must agree.

    This is not a redundant test. It is the claim that the published workbook and planner
    figures are correct, and it is the thing that will break first if a future constraint
    makes greedy wrong, which is exactly when the ILP starts earning its keep.
    """
    result = solve_selection(cases, settings)
    assert set(result.committed) == set(_greedy(cases, settings))


def test_capacity_is_respected_across_the_sweep(
    cases: list[PlanningCase], settings: Settings
) -> None:
    for cap in range(9):
        result = solve_selection(cases, settings.with_cap(cap))
        assert result.committed_count <= cap


def test_the_model_self_limits_rather_than_filling_every_slot(
    cases: list[PlanningCase], settings: Settings
) -> None:
    """The capacity ceiling is an output of the model, not a chart a reader must interpret.

    The workbook and the planner both evaluate rescueability at the commitment limit, so they
    assume every slot gets filled, and on that assumption the on-time count peaks at seven
    slots and then collapses. This model evaluates the signature queue at the count the plan
    actually commits, so raising the limit past seven changes nothing: it keeps committing
    seven, because an eighth trial would lengthen the queue enough to lose both rescues, and
    P1 outranks P2.

    The practical reading: a service that understands the trade would not fill the extra
    slots, so the ceiling does not need to be imposed from outside.
    """
    runs = {c: solve_selection(cases, settings.with_cap(c)) for c in range(1, 12)}
    on_time = [r.p1_on_time for r in runs.values()]
    used = [r.committed_count for r in runs.values()]

    assert max(on_time) > 0, "the demonstration instance must have a live on-time objective"
    assert on_time[-1] == max(on_time), "P1 must not collapse once the model can self-limit"
    assert used[-1] < 11, "the model must decline slots that would cost it a rescue"
    assert used == sorted(used), "committed count must never fall as the limit rises"
    assert max(used) == used[-1], "the plateau is the safe commitment limit"


def test_lateness_only_model_rescues_nothing(
    cases: list[PlanningCase], settings: Settings
) -> None:
    """The strongest argument for ranking on-time first.

    Rescueable trials are the newest, so they have waited least, so they carry the smallest
    claim weights, so they look like the cheapest trials to abandon under a lateness measure.
    Without P1 outranking P2 the optimiser abandons precisely the trials that could still meet
    the target.
    """
    for cap in range(1, 10):
        result = solve_selection(cases, settings.with_cap(cap), rank_on_time=False)
        assert result.p1_on_time == 0


def test_ranking_on_time_never_improves_lateness(
    cases: list[PlanningCase], settings: Settings
) -> None:
    """P1 first can only cost P2, never gain it. A negative price would mean a bug."""
    for cap in range(1, 6):
        capped = settings.with_cap(cap)
        ranked = solve_selection(cases, capped)
        lateness_only = solve_selection(cases, capped, rank_on_time=False)
        assert ranked.p2_weighted_lateness >= lateness_only.p2_weighted_lateness - 1e-6


def test_value_floor_closes_cases(cases: list[PlanningCase], settings: Settings) -> None:
    from dataclasses import replace

    result = solve_selection(cases, replace(settings, floor=30.0))
    assert result.closed, "a floor of 30 must close the low-scoring cases"
    assert all(
        d.value is None or d.value < 30.0 for d in result.decisions if d.action == "CLOSE"
    )


def test_empty_instance_returns_a_plan_not_an_error(settings: Settings) -> None:
    """A goal programme always answers. Committing nothing satisfies every hard constraint."""
    result = solve_selection([], settings)
    assert result.committed == ()
    assert result.p1_on_time == 0


def test_pre_solve_ceiling_bounds_the_solve(
    cases: list[PlanningCase], settings: Settings
) -> None:
    check = pre_solve_check(cases, settings)
    result = solve_selection(cases, settings)
    assert result.p1_on_time >= check.p1_ceiling, (
        "the ceiling is computed at the commitment limit, which is the pessimistic end, "
        "so the solver may beat it by committing fewer trials but must never fall short"
    )


def test_unready_cases_are_blocked_not_dropped(settings: Settings) -> None:
    from Experiments.optimiser import Case

    raw = load_demo_cases() + [Case(name="NO-DATE-01", value=25.0)]
    enriched = enrich(raw, settings)
    result = solve_selection(enriched, settings)
    assert "NO-DATE-01" in result.blocked
    assert len(result.decisions) == 17


def test_json_round_trip_matches_a_direct_solve(settings: Settings) -> None:
    """The planner contract must return the same plan as calling the model directly."""
    payload = {
        "settings": {
            "today": settings.today.isoformat(),
            "cap": settings.cap,
            "floor": settings.floor,
            "es": settings.approval_days,
            "gpd": settings.approver_days_per_month,
            "dur": dict(settings.durations),
        },
        "cases": [
            {
                "name": c.name,
                "rx": c.prescription,
                "asep": c.aseptic,
                "hra": c.hra_approval.isoformat() if c.hra_approval else None,
                "siteSel": None,
                "notified": c.notified.isoformat() if c.notified else None,
                "value": c.value,
            }
            for c in load_demo_cases()
        ],
    }
    from_json = solve_json(payload, settings)
    direct = solve_selection(enrich(load_demo_cases(), settings), settings)

    assert from_json["committed"] == list(direct.committed)
    assert from_json["objectives"]["p1OnTime"] == direct.p1_on_time
    assert len(from_json["rows"]) == 16
    assert all(row["why"] for row in from_json["rows"]), "every row carries a sentence"


# --- The withdrawn trade budget -------------------------------------------------------
#
# `trade_budget` (`k` in the specification) was declared in `Settings` and accepted from the
# planner payload, but no solver code ever read it. A planner could set it and watch the plan
# not change. It was withdrawn on 19 August 2026 rather than implemented, because the trade it
# describes never pays: portfolio value is additive and near-linear in the number of trials
# committed, so giving up a trial to seat a more valuable one always loses more than it gains.
# These tests keep it withdrawn, and keep the property that made it pointless.


def test_settings_carries_no_trade_budget() -> None:
    """The dead parameter is gone from the configuration, not merely defaulted to zero."""
    assert not hasattr(Settings(today=demo_settings().today), "trade_budget")

    with pytest.raises(TypeError):
        Settings(today=demo_settings().today, trade_budget=1)  # type: ignore[call-arg]


def test_the_payload_refuses_a_trade_budget_rather_than_ignoring_it(
    settings: Settings,
) -> None:
    """A caller still sending the withdrawn key is told, not silently given an unchanged plan.

    Ignoring it would reproduce the exact failure the withdrawal was meant to end.
    """
    with pytest.raises(ValueError, match="tradeBudget"):
        settings_from_json({"cap": settings.cap, "tradeBudget": 1}, settings)


def test_value_never_buys_a_concession_from_on_time_or_lateness(
    cases: list[PlanningCase], settings: Settings
) -> None:
    """Switching P3 on must not cost a single on-time trial, or change who is committed.

    This is what a non-zero trade budget would have relaxed. With the objective tolerances
    pinned at zero the ranking stays strictly lexicographic, so there is no budget to spend.

    Weighted lateness is compared on a relative tolerance rather than exactly. Once P2 has
    been fixed and a lower-priority P3 is being solved, the `late` variables are only
    lower-bounded and nothing pushes them back down to that bound, so the *reported* P2 can
    sit up to Gurobi's default `MIPGap` above the true optimum. Measured at +0.2 on ~1615,
    which is 1.2e-4 relative, and it collapses to zero if `MIPGap` is set to 0. The selection
    is unaffected, which is what the committed-set assertion below pins.
    """
    from dataclasses import replace

    for cap in range(1, 7):
        paused = replace(settings, cap=cap, value_active=False)
        active = replace(settings, cap=cap, value_active=True)

        without = solve_selection(enrich(load_demo_cases(), paused), paused)
        with_value = solve_selection(enrich(load_demo_cases(), active), active)

        assert with_value.committed == without.committed, (
            f"at {cap} slots, activating value changed the committed set from "
            f"{without.committed} to {with_value.committed}"
        )
        assert with_value.p1_on_time == without.p1_on_time, (
            f"at {cap} slots, activating value changed the on-time count from "
            f"{without.p1_on_time} to {with_value.p1_on_time}"
        )
        assert with_value.p2_weighted_lateness == pytest.approx(
            without.p2_weighted_lateness, rel=1e-3
        ), f"at {cap} slots, activating value moved weighted lateness beyond solver tolerance"


def test_more_slots_never_lower_portfolio_value(
    cases: list[PlanningCase], settings: Settings
) -> None:
    """The finding that makes the controlled trade pointless, pinned on the demo instance.

    Value rises monotonically with the number of trials committed, so the model is never
    offered a plan where dropping a trial raises value. `k` would have had nothing to buy.
    """
    from dataclasses import replace

    previous = None
    for cap in range(1, 7):
        active = replace(settings, cap=cap, value_active=True)
        result = solve_selection(enrich(load_demo_cases(), active), active)
        if previous is not None:
            assert result.p3_value >= previous - 1e-9, (
                f"portfolio value fell from {previous} to {result.p3_value} on the way to "
                f"{cap} slots, which would be the first case a trade budget could earn"
            )
        previous = result.p3_value


# --- Segment B: the clock running before the trial reaches pharmacy -------------------
#
# The 5-6 August meetings split the notified-to-start window at the clock start. The half
# after it, clock running but the trial not yet in the pharmacy queue, is a straight
# subtraction from the 60 days. These tests pin the three situations that differ.


def _anchored(name: str, *, today, clock_offset: int, queue_offset: int | None):
    """A case whose clock started `clock_offset` days ago, queued at `queue_offset`.

    `queue_offset` is measured from today: negative is already queued, positive is a hand-over
    R&I has scheduled, None is a trial R&I holds with no date set.
    """
    import datetime

    from Experiments.optimiser import Case

    clock = today - datetime.timedelta(days=clock_offset)
    entry = None if queue_offset is None else today + datetime.timedelta(days=queue_offset)
    return Case(name=name, hra_approval=clock, site_selected=clock,
                setup_start=entry, value=25.0)


def test_a_queued_trial_loses_nothing_twice(settings: Settings) -> None:
    """Segment B is already spent for a queued trial, so the window must not shrink again."""
    case = _anchored("QUEUED", today=settings.today, clock_offset=20, queue_offset=-12)
    pc = enrich([case], settings)[0]

    assert pc.segment_b == 8, "clock start to queue entry"
    assert pc.days_available == pc.days_to_due, "no hand-over is still ahead"
    assert not pc.queue_entry_assumed


def test_a_scheduled_hand_over_shrinks_the_window(settings: Settings) -> None:
    """Work cannot begin before R&I hands the trial over, so those days are not available."""
    case = _anchored("SCHEDULED", today=settings.today, clock_offset=10, queue_offset=9)
    pc = enrich([case], settings)[0]

    assert pc.days_available == pc.days_to_due - 9
    assert pc.days_waited == 0, "a trial not yet queued has waited no time in the queue"


def test_a_trial_r_and_i_still_holds_is_planned_on_the_median_hand_over(
    settings: Settings,
) -> None:
    """Jaya's day-one case: R&I fields only, no queue entry. Planned, and flagged as assumed."""
    case = _anchored("DAY-ONE", today=settings.today, clock_offset=10, queue_offset=None)
    pc = enrich([case], settings)[0]

    assert pc.ready, "R&I data alone is enough to plan a trial"
    assert pc.queue_entry_assumed
    assert pc.segment_b is None, "there is no measured segment B to report"
    assert pc.days_available == pc.days_to_due - settings.handover_days


def test_a_case_with_no_dates_at_all_is_still_blocked(settings: Settings) -> None:
    from Experiments.optimiser import Case

    pc = enrich([Case(name="NOTHING", value=25.0)], settings)[0]
    assert not pc.ready


def test_the_subtraction_can_cost_a_trial_its_rescue(settings: Settings) -> None:
    """The point of the change: a trial that looks on time from today, and is not.

    Its window is one day longer than the set-up plus the signature wait, so it is rescueable
    read from today. Once the hand-over R&I has not yet made is subtracted, it is not.
    """
    import datetime

    from Experiments.optimiser import Case

    duration = settings.durations["Routine"]
    wait = gate_wait(1, settings)
    # Clock start chosen so exactly `duration + wait + 1` days remain from today.
    remaining = duration + int(wait) + 1
    clock = settings.today - datetime.timedelta(days=settings.target_days - remaining)

    queued = Case(name="QUEUED", hra_approval=clock, site_selected=clock,
                  setup_start=settings.today - datetime.timedelta(days=1), value=25.0)
    held = Case(name="HELD-BY-RANDI", hra_approval=clock, site_selected=clock, value=25.0)

    one_slot = settings.with_cap(1)
    assert solve_selection(enrich([queued], one_slot), one_slot).p1_on_time == 1
    assert solve_selection(enrich([held], one_slot), one_slot).p1_on_time == 0, (
        "the median hand-over is longer than the single day of slack, so this trial "
        "cannot finish inside the target and the model must not claim it can"
    )


def test_the_reason_never_passes_an_assumption_off_as_a_reading(settings: Settings) -> None:
    case = _anchored("DAY-ONE", today=settings.today, clock_offset=10, queue_offset=None)
    result = solve_selection(enrich([case], settings), settings)
    reason = result.decisions[0].reason

    assert "assuming" in reason and str(settings.handover_days) in reason


# --- Segment A: the preparation credit -----------------------------------------------
#
# Two conditions, both required: the sponsor has confirmed the site, and the study is
# complex enough that pharmacy would prepare it, which is aseptic work or phase 1. The
# size comes from `prep_credit_cap_days`, which LTHTR form 3 section 4 asks for and which
# defaults to 0 until they answer. There is deliberately no per-study preparation flag:
# none was ever requested, so gating on one made the credit unreachable rather than inert.


def _flaggable(settings: Settings, *, flagged: bool, green_light: bool):
    """A case with a comfortable window, so only the credit moves the numbers.

    `flagged` now means "complex enough to be prepared", carried by the aseptic flag,
    since that is what `data._prep_credit` reads in place of the withdrawn per-study flag.
    """
    import datetime

    from Experiments.optimiser import Case

    clock = settings.today - datetime.timedelta(days=5)
    return Case(name="PREPPED", hra_approval=clock, site_selected=clock,
                setup_start=clock + datetime.timedelta(days=2),
                sponsor_green_light=clock if green_light else None,
                aseptic=flagged, phase=3, value=25.0)


def test_the_credit_is_inert_at_the_default_cap(settings: Settings) -> None:
    """Nothing changes until LTHTR supply a number. This is the guard on that promise."""
    assert settings.prep_credit_cap_days == 0
    pc = enrich([_flaggable(settings, flagged=True, green_light=True)], settings)[0]

    assert pc.prep_credit == 0
    assert pc.effective_duration == pc.duration


def test_a_flagged_and_confirmed_study_finishes_earlier(settings: Settings) -> None:
    from dataclasses import replace

    from dataclasses import replace

    generous = replace(settings, prep_credit_cap_days=10)
    pc = enrich([_flaggable(generous, flagged=True, green_light=True)], generous)[0]

    assert pc.prep_credit == 10
    assert pc.effective_duration == pc.duration - 10


def test_the_flag_alone_earns_nothing_without_the_sponsor(settings: Settings) -> None:
    """Jaya's objection: preparing before the site is confirmed wastes a stretched team."""
    from dataclasses import replace

    from dataclasses import replace

    generous = replace(settings, prep_credit_cap_days=10)
    pc = enrich([_flaggable(generous, flagged=True, green_light=False)], generous)[0]

    assert pc.prep_credit == 0


def test_the_sponsor_alone_earns_nothing_without_the_flag(settings: Settings) -> None:
    """The credit is never inferred from dates. Pharmacy has to say they did the work."""
    from dataclasses import replace

    from dataclasses import replace

    generous = replace(settings, prep_credit_cap_days=10)
    pc = enrich([_flaggable(generous, flagged=False, green_light=True)], generous)[0]

    assert pc.prep_credit == 0


def test_phase_one_earns_the_credit_without_aseptic_work(settings: Settings) -> None:
    """The day-one route. Phase is known from the protocol before pharmacy hears anything.

    This is what makes the credit reachable by the person who actually runs the planner.
    Aseptic and prescription are recorded late; the withdrawn preparation flag was never
    requested at all; phase is on the protocol from the start.
    """
    import datetime

    from Experiments.optimiser import Case

    from dataclasses import replace

    generous = replace(settings, prep_credit_cap_days=10)
    clock = generous.today - datetime.timedelta(days=5)
    base = dict(name="EARLY", hra_approval=clock, site_selected=clock,
                setup_start=clock + datetime.timedelta(days=2),
                sponsor_green_light=clock, aseptic=False, value=25.0)

    phase1 = enrich([Case(**base, phase=1)], generous)[0]
    phase3 = enrich([Case(**base, phase=3)], generous)[0]

    assert phase1.prep_credit == 10, "phase 1 is complex enough to be prepared"
    assert phase3.prep_credit == 0, "a routine phase 3 study earns nothing"
    assert phase1.effective_duration == phase3.effective_duration - 10


def test_the_credit_needs_no_field_pharmacy_alone_could_supply(settings: Settings) -> None:
    """Guard on the 2026-08-16 correction: every input to the credit is on the request.

    The credit previously required a per-study preparation flag that no LTHTR form asks
    for, so it could never fire on the returned data. `Case` no longer carries one.
    """
    from Experiments.optimiser import Case

    assert not hasattr(Case(name="X"), "prep_flagged"), (
        "a preparation flag would be unobtainable: form 1 asks per study only for "
        "prescription, prescribing system, specialist input, aseptic, phase and delay reason")


def test_the_planner_can_carry_a_study_the_rule_would_miss(settings: Settings) -> None:
    """Jaya marks a new trial for preparation, and the credit follows her, not the rule.

    The rule is a default for studies nobody has judged. A routine phase 3 study earns
    nothing by default; if the planner says pharmacy will prepare it, the credit applies.
    """
    import datetime
    from dataclasses import replace

    from Experiments.optimiser import Case

    generous = replace(settings, prep_credit_cap_days=10)
    clock = generous.today - datetime.timedelta(days=5)
    base = dict(name="MARKED", hra_approval=clock, site_selected=clock,
                setup_start=clock + datetime.timedelta(days=2),
                sponsor_green_light=clock, aseptic=False, phase=3, value=25.0)

    by_rule = enrich([Case(**base)], generous)[0]
    marked = enrich([Case(**base, prep_override=True)], generous)[0]

    assert by_rule.prep_credit == 0, "the rule alone gives a routine phase 3 study nothing"
    assert marked.prep_credit == 10, "the planner's own answer carries it"


def test_the_planner_can_withhold_the_credit_from_a_complex_study(settings: Settings) -> None:
    """The override runs both ways. Aseptic work earns the credit by rule, but not when
    pharmacy has no capacity to prepare this cycle and the planner says so."""
    import datetime
    from dataclasses import replace

    from Experiments.optimiser import Case

    generous = replace(settings, prep_credit_cap_days=10)
    clock = generous.today - datetime.timedelta(days=5)
    base = dict(name="BUSY", hra_approval=clock, site_selected=clock,
                setup_start=clock + datetime.timedelta(days=2),
                sponsor_green_light=clock, aseptic=True, phase=3, value=25.0)

    assert enrich([Case(**base)], generous)[0].prep_credit == 10
    assert enrich([Case(**base, prep_override=False)], generous)[0].prep_credit == 0


def test_the_override_cannot_bypass_the_sponsor_condition(settings: Settings) -> None:
    """Both conditions still hold. Without the sponsor green light the study may not run
    here at all, and no planner judgement changes that."""
    import datetime
    from dataclasses import replace

    from Experiments.optimiser import Case

    generous = replace(settings, prep_credit_cap_days=10)
    clock = generous.today - datetime.timedelta(days=5)
    case = Case(name="UNCONFIRMED", hra_approval=clock, site_selected=clock,
                setup_start=clock + datetime.timedelta(days=2),
                sponsor_green_light=None, aseptic=True, phase=1,
                prep_override=True, value=25.0)

    assert enrich([case], generous)[0].prep_credit == 0


def test_the_credit_cannot_shorten_a_study_below_a_day(settings: Settings) -> None:
    from dataclasses import replace

    absurd = replace(settings, prep_credit_cap_days=500)
    pc = enrich([_flaggable(absurd, flagged=True, green_light=True)], absurd)[0]

    assert pc.effective_duration == 1
    assert pc.prep_credit == pc.duration - 1


def test_a_negative_cap_is_refused(settings: Settings) -> None:
    from dataclasses import replace

    with pytest.raises(ValueError, match="prep_credit_cap_days"):
        replace(settings, prep_credit_cap_days=-1)


def test_the_credit_can_turn_a_miss_into_a_rescue(settings: Settings) -> None:
    """The point of the mechanism, end to end through the solver."""
    import datetime
    from dataclasses import replace

    from Experiments.optimiser import Case

    duration = settings.durations["Routine"]
    wait = gate_wait(1, settings)
    # One day short of rescueable, so only a credit can save it.
    remaining = duration + int(wait) - 1
    clock = settings.today - datetime.timedelta(days=settings.target_days - remaining)
    case = Case(name="NEARLY", hra_approval=clock, site_selected=clock,
                setup_start=settings.today - datetime.timedelta(days=1),
                sponsor_green_light=clock, aseptic=True, value=25.0)

    one_slot = settings.with_cap(1)
    assert solve_selection(enrich([case], one_slot), one_slot).p1_on_time == 0

    with_credit = replace(one_slot, prep_credit_cap_days=5)
    result = solve_selection(enrich([case], with_credit), with_credit)
    assert result.p1_on_time == 1
    assert "preparation done before the clock started" in result.decisions[0].reason


# ── planning buffer ──────────────────────────────────────────────────────────────
# Added 26 August 2026. The buffer is a separate policy setting so the published
# target stays LTHTR's own 60 days. Default zero must leave every figure untouched.

def test_planning_buffer_defaults_to_zero_and_changes_nothing() -> None:
    s = demo_settings()
    assert s.planning_buffer_days == 0
    assert s.planning_deadline_days == s.target_days
    assert s.setup_ceiling == s.target_days - s.handover_days


def test_planning_buffer_tightens_deadline_and_ceiling_but_not_target() -> None:
    s = demo_settings().with_planning_buffer(10)
    assert s.target_days == 60, "the published target must not move"
    assert s.planning_deadline_days == 50
    assert s.setup_ceiling == 50 - s.handover_days


def test_planning_buffer_rejects_negative_and_oversized_values() -> None:
    with pytest.raises(ValueError, match="must not be negative"):
        demo_settings().with_planning_buffer(-1)
    with pytest.raises(ValueError, match="must be less than"):
        demo_settings().with_planning_buffer(60)
