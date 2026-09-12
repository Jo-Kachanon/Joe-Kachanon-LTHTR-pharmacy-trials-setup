"""Tests for the signed preparation lead, added 26 August 2026.

Section 12 of the recompute report fixed the specification: preparation saves exactly its
own lead `L`, and only on the clock — `target met <=> work - L <= 60`, capacity unchanged.
The observed mechanism (4 of 4 early starters met the target, 0 of 14 others) was
unrepresentable while the day-one hand-over assumption was a single positive constant.

These tests pin the three properties the spec demands:
* a planned lead extends `days_available` by exactly the lead,
* it never touches `effective_duration` (the capacity side),
* recorded dates always beat a planned lead.
"""

from __future__ import annotations

import datetime

from Experiments.optimiser.config import Settings
from Experiments.optimiser.data import Case, enrich


TODAY = datetime.date(2026, 9, 1)


def settings(**overrides) -> Settings:
    return Settings(today=TODAY, **overrides)


def day_one_case(prep_lead_days: int | None = None, **overrides) -> Case:
    """A trial R&I still holds: anchors known, no queue entry, clock starts in 30 days."""
    base = dict(
        name="Q4B6-TEST",
        aseptic=True,
        prescription=True,
        hra_approval=datetime.date(2026, 8, 1),
        site_selected=TODAY + datetime.timedelta(days=30),
        prep_lead_days=prep_lead_days,
    )
    base.update(overrides)
    return Case(**base)


def one(case: Case, s: Settings):
    [planning_case] = enrich([case], s)
    return planning_case


# ── the lead reaches the clock ───────────────────────────────────────────────────

def test_planned_lead_extends_days_available_by_exactly_the_lead() -> None:
    s = settings()
    with_lead = one(day_one_case(prep_lead_days=19), s)
    # The contract: work can begin `prep_lead_days` before the clock starts, so the
    # window is the full target plus the lead.
    assert with_lead.days_available == s.target_days + 19
    assert with_lead.days_available == (
        with_lead.due - (with_lead.clock_start - datetime.timedelta(days=19))
    ).days


def test_zero_lead_means_handover_exactly_at_clock_start() -> None:
    planning_case = one(day_one_case(prep_lead_days=0), settings())
    assert planning_case.days_available == 60


def test_negative_lead_is_a_late_handover_and_shrinks_the_window() -> None:
    planning_case = one(day_one_case(prep_lead_days=-14), settings())
    assert planning_case.days_available == 60 - 14


def test_lead_in_the_past_cannot_bank_days_before_today() -> None:
    """A lead longer than the time until the clock starts is clipped at today."""
    planning_case = one(day_one_case(prep_lead_days=90), settings())  # clock starts in 30d
    assert planning_case.days_available == (planning_case.due - TODAY).days


# ── capacity untouched ───────────────────────────────────────────────────────────

def test_lead_never_changes_effective_duration() -> None:
    s = settings()
    without = one(day_one_case(), s)
    with_lead = one(day_one_case(prep_lead_days=19), s)
    assert with_lead.duration == without.duration
    assert with_lead.effective_duration == without.effective_duration


# ── precedence and bookkeeping ───────────────────────────────────────────────────

def test_recorded_queue_entry_beats_planned_lead() -> None:
    recorded = TODAY - datetime.timedelta(days=5)
    planning_case = one(day_one_case(prep_lead_days=19, setup_start=recorded), settings())
    assert planning_case.queue_entry == recorded
    assert not planning_case.queue_entry_assumed


def test_planned_lead_is_flagged_as_assumed_and_recorded() -> None:
    planning_case = one(day_one_case(prep_lead_days=19), settings())
    assert planning_case.queue_entry_assumed, "a planned hand-over is a forecast, not a reading"
    assert planning_case.prep_lead_days == 19


def test_observed_lead_is_derived_from_dates() -> None:
    """A trial that entered the queue 11 days before its clock started has L=+11."""
    entry = TODAY + datetime.timedelta(days=19)   # clock starts in 30
    planning_case = one(day_one_case(setup_start=entry), settings())
    assert planning_case.segment_b == -11
    assert planning_case.prep_lead_days == 11
