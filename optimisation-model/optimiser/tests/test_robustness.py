"""Checks for the SQ3 robustness experiment.

Three layers: the enumerator reproduces the appendix instance by hand, the generator
is deterministic under its seed, and where a Gurobi licence is present the enumerator
is cross-checked against the real selection model on the same instance.
"""

from __future__ import annotations

import datetime
import random

import pytest

from optimiser.config import Settings
from optimiser.gate import gate_wait_table
from optimiser.robustness import (SynthTrial, Scenario, arrival_order_plan,
                                  evaluate_plan, generate_portfolio, solve_exact)

SETTINGS = Settings(today=datetime.date(2026, 8, 13))
WAITS = gate_wait_table(SETTINGS, max_committed=14)


def _trial(name: str, dur: int, dtd: int, waited: int = 0) -> SynthTrial:
    return SynthTrial(name=name, duration=dur, days_to_due=dtd, days_waited=waited,
                      claim_weight=1.0 + waited / 365.0)


def test_appendix_instance_rescueability() -> None:
    """A(50) B(44) C(38) D(12), duration 36: at n=3 A, B, C are on time and D never is."""
    trials = [_trial("A", 36, 50), _trial("B", 36, 44), _trial("C", 36, 38), _trial("D", 36, 12)]
    committed, p1, _ = solve_exact(trials, WAITS, cap=3, cycle_days=30)
    assert p1 == 3
    assert committed == frozenset({"A", "B", "C"})
    # D is not rescueable even alone: 12 < 36 + 0.2
    _, p1_d = 0, evaluate_plan(trials, frozenset({"D"}), WAITS, 30)[0]
    assert p1_d == 0


def test_lateness_matches_hand_calculation() -> None:
    """One committed, one deferred: d+ follows eq 3.5 exactly."""
    trials = [_trial("A", 36, 50, waited=0), _trial("B", 36, 10, waited=365)]
    p1, p2 = evaluate_plan(trials, frozenset({"A"}), WAITS, 30)
    # A: base = 36 - 50 + 0.2 < 0 -> 0. B deferred: base = 36 - 10 + 0.2 + 30 = 56.2, w = 2.
    assert p1 == 1
    assert p2 == pytest.approx(112.4)


def test_generator_deterministic_under_seed() -> None:
    scenario = Scenario("typical", 0.6, 0.2, "illustrative")
    a = generate_portfolio(scenario, random.Random(7), SETTINGS)
    b = generate_portfolio(scenario, random.Random(7), SETTINGS)
    assert a == b


def test_arrival_order_takes_longest_waiting() -> None:
    trials = [_trial("A", 36, 50, waited=10), _trial("B", 36, 50, waited=200),
              _trial("C", 36, 50, waited=90), _trial("D", 36, 50, waited=5)]
    assert arrival_order_plan(trials, cap=3) == frozenset({"B", "C", "A"})


def test_enumerator_matches_gurobi_when_licensed() -> None:
    """Cross-check the exact enumerator against the real selection model."""
    gp = pytest.importorskip("gurobipy")
    from optimiser.model import solve_selection, GurobiUnavailableError
    from optimiser.data import Case, enrich, plannable

    today = SETTINGS.today
    cases = []
    for name, dtd, waited in [("A", 50, 40), ("B", 44, 120), ("C", 38, 10), ("D", 12, 300)]:
        cases.append(Case(
            name=name, prescription=False, aseptic=True,
            hra_approval=today - datetime.timedelta(days=60 - dtd),
            site_selected=today - datetime.timedelta(days=60 - dtd),
            notified=today - datetime.timedelta(days=waited), value=30.0,
        ))
    try:
        result = solve_selection(plannable(enrich(cases, SETTINGS), SETTINGS.floor), SETTINGS)
    except (GurobiUnavailableError, gp.GurobiError) as exc:  # licence-limited machines
        pytest.skip(f"Gurobi unavailable: {exc}")
    duration = SETTINGS.durations["Aseptic only"]
    trials = [_trial(n, duration, dtd, waited)
              for n, dtd, waited in [("A", 50, 40), ("B", 44, 120), ("C", 38, 10), ("D", 12, 300)]]
    _, p1, _ = solve_exact(trials, WAITS, SETTINGS.cap, SETTINGS.cycle_days)
    assert result.p1_on_time == p1
