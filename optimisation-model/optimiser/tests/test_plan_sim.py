"""The on-time count as a distribution, and the guarantees that make it readable.

Two groups. The first fixes that the simulation agrees with the model it qualifies: run it
with no duration variability and it must reproduce `solve_selection` exactly, because at
the tier median there is nothing left to vary. The second fixes the properties a reader
relies on when interpreting the spread.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from ..config import Settings, demo_settings
from ..data import PlanningCase, enrich
from ..loaders import load_demo_cases
from ..plan_sim import simulate_plan


@pytest.fixture(scope="module")
def settings() -> Settings:
    return demo_settings()


@pytest.fixture(scope="module")
def cases(settings: Settings) -> list[PlanningCase]:
    return enrich(load_demo_cases(), settings)


@pytest.fixture(scope="module")
def plan(cases: list[PlanningCase]) -> list[PlanningCase]:
    """Three trials that between them span on-time, marginal and hopeless."""
    return [c for c in cases if c.name in {"TiPE", "MOCK-07", "MOCK-01"}]


# --- Does it agree with the model it qualifies? --------------------------------------


def test_without_variability_it_reproduces_the_deterministic_plan(
    plan: list[PlanningCase], settings: Settings
) -> None:
    """At a coefficient of variation of zero every run draws the tier median.

    The distribution must then be a spike on the count the model reported. If it is not,
    the simulation and the model disagree about what the plan says, and every spread the
    module reports afterwards is measured from the wrong place.
    """
    outcome = simulate_plan(plan, replace(settings, setup_duration_cv=0.0), replications=200)
    assert outcome.distribution[outcome.deterministic_count] == 1.0
    assert outcome.mean_count == float(outcome.deterministic_count)
    assert outcome.probability_at_least_deterministic == 1.0


def test_variability_puts_the_reported_count_in_doubt(
    plan: list[PlanningCase], settings: Settings
) -> None:
    """The point of the module: the reported count is not always achieved.

    A plan carrying a trial whose median duration only just fits will miss it whenever the
    draw runs long, so the promised count must be delivered less than always.
    """
    outcome = simulate_plan(plan, settings, replications=2000)
    assert 0.0 < outcome.probability_at_least_deterministic < 1.0
    assert outcome.mean_count < outcome.deterministic_count


def test_it_draws_on_the_set_up_cv_and_not_the_approval_proxy(
    plan: list[PlanningCase], settings: Settings
) -> None:
    """The two coefficients of variation are not interchangeable, and this fixes which is used.

    `duration_cv` is the approval-time proxy borrowed from iQemo builds, nearly three times
    the measured set-up spread. Reading it for the duration draws put set-up medians at 57
    days against a recorded 95 and generated set-ups faster than any on record.

    It does legitimately reach this module through `gate_wait`, so the test is not that it
    changes nothing. It is that it cannot add *duration* variability: with the set-up
    coefficient at zero the distribution must stay a spike however large `duration_cv` is,
    and only `setup_duration_cv` may spread it.
    """
    flat = replace(settings, setup_duration_cv=0.0)
    for cv in (settings.duration_cv, settings.duration_cv * 3):
        outcome = simulate_plan(plan, replace(flat, duration_cv=cv), replications=400)
        spike = max(outcome.distribution.values())
        assert spike == 1.0, (
            f"duration_cv={cv} spread the duration draws; it must only move the wait"
        )

    spread = simulate_plan(plan, settings, replications=400)
    assert max(spread.distribution.values()) < 1.0


# --- Properties a reader relies on ---------------------------------------------------


def test_the_distribution_is_a_distribution(
    plan: list[PlanningCase], settings: Settings
) -> None:
    """Sums to one, covers every attainable count, and never exceeds the plan size."""
    outcome = simulate_plan(plan, settings, replications=1000)
    assert set(outcome.distribution) == set(range(len(plan) + 1))
    assert abs(sum(outcome.distribution.values()) - 1.0) < 1e-6
    assert all(0.0 <= share <= 1.0 for share in outcome.distribution.values())


def test_the_pessimistic_end_is_no_better_than_the_average(
    plan: list[PlanningCase], settings: Settings
) -> None:
    """`p10_count` is what the service should size against, so it must not read high."""
    outcome = simulate_plan(plan, settings, replications=2000)
    assert outcome.p10_count <= outcome.mean_count <= outcome.committed


def test_per_trial_risk_is_reported_worst_first(
    plan: list[PlanningCase], settings: Settings
) -> None:
    """A reader looking for the trial about to fail should find it in the first row."""
    outcome = simulate_plan(plan, settings, replications=500)
    probabilities = [t.on_time_probability for t in outcome.per_trial]
    assert probabilities == sorted(probabilities)
    assert {t.name for t in outcome.per_trial} == {c.name for c in plan}


def test_a_trial_the_plan_never_rescues_is_never_rescued(
    plan: list[PlanningCase], settings: Settings
) -> None:
    """Consistency in the other direction, on the hopeless case.

    MOCK-01 is committed for its lateness contribution, not because it can finish in time.
    Drawing a shorter duration must not turn it into a rescue, or the module would report
    an optimism the plan never claimed.
    """
    outcome = simulate_plan(plan, settings, replications=2000)
    hopeless = next(t for t in outcome.per_trial if not t.deterministic_on_time)
    assert hopeless.on_time_probability < 0.05
    assert hopeless.median_overrun > 0.0


def test_a_larger_plan_carries_a_longer_wait_and_more_risk(
    cases: list[PlanningCase], settings: Settings
) -> None:
    """The approval wait is applied at the committed count, not at a fixed one.

    Widening the plan lengthens the signature queue for every trial in it, so the same
    trial must be at least as likely to miss in the larger plan. This fixes that the
    module reads the wait from the plan rather than from the settings.
    """
    ready = [c for c in cases if c.days_available > 0][:6]
    small = simulate_plan(ready[:2], settings, replications=1000)
    large = simulate_plan(ready, settings, replications=1000)
    assert large.gate_wait > small.gate_wait


# --- Reproducibility and guards ------------------------------------------------------


def test_a_run_regenerates_exactly(plan: list[PlanningCase], settings: Settings) -> None:
    """Without this no figure quoted in the write-up can be reproduced."""
    assert simulate_plan(plan, settings, replications=300) == simulate_plan(
        plan, settings, replications=300
    )


def test_a_different_seed_gives_a_different_draw(
    plan: list[PlanningCase], settings: Settings
) -> None:
    """The converse, so the previous test cannot pass by the seed being ignored."""
    first = simulate_plan(plan, settings, replications=300, seed=1)
    second = simulate_plan(plan, settings, replications=300, seed=2)
    assert first.mean_count != second.mean_count


def test_an_empty_plan_is_refused(settings: Settings) -> None:
    """There is no distribution to report, and a zero-length plan is a caller error."""
    with pytest.raises(ValueError, match="at least one committed trial"):
        simulate_plan([], settings)


def test_a_non_positive_replication_count_is_refused(
    plan: list[PlanningCase], settings: Settings
) -> None:
    with pytest.raises(ValueError, match="replications"):
        simulate_plan(plan, settings, replications=0)
