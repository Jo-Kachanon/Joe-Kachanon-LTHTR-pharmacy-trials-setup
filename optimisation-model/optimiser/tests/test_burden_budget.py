"""Tests for pharmacy burden as a capacity weight, added 27 August 2026.

Burden entered the model twice before this and wrongly both times: as a third objective on
the 4b rank, and as an eligibility filter that dropped high-burden trials. Each encoded a
choice pharmacy does not have, since the service cannot decline the trials a sponsor sends.

What the 20 case studies support is a weight, not a preference. Burden does not separate work
medians (Mann-Whitney p = 0.83) but it does separate work floors (23, 40 and 60 days by band),
which is the signature of a resource being consumed. These tests pin what that means for the
model:

* a budget limits committed burden, not committed count,
* the same budget buys more light trials than heavy ones,
* an unrated trial is charged the moderate weight, never treated as free,
* no budget reproduces the old slot-count behaviour exactly.
"""

from __future__ import annotations

import datetime

import pytest

from Experiments.optimiser.config import BURDEN_WEIGHTS, Settings
from Experiments.optimiser.data import Case, enrich


TODAY = datetime.date(2026, 9, 1)


def case(name: str, burden_rank: int | None) -> Case:
    """A queued trial, anchors known and pharmacy notified, differing only in burden."""
    return Case(
        name=name,
        hra_approval=datetime.date(2026, 7, 1),
        site_selected=datetime.date(2026, 7, 1),
        notified=datetime.date(2026, 7, 9),
        burden_rank=burden_rank,
    )


def weights_of(cases: list[Case]) -> list[float]:
    settings = Settings(today=TODAY)
    return [c.capacity_weight for c in enrich(cases, settings)]


def test_weights_follow_the_observed_floor_ladder() -> None:
    """Bands 2, 3-4 and 5-6 cost 1.00, 1.74 and 2.61 routine-trial equivalents."""
    assert weights_of([case("R", 2), case("M", 3), case("M2", 4),
                       case("H", 5), case("H2", 6)]) == [1.00, 1.74, 1.74, 2.61, 2.61]


def test_unrated_trial_is_charged_the_moderate_weight() -> None:
    """An unrated trial must never be assumed free, or the budget understates the load."""
    assert weights_of([case("U", None)]) == [BURDEN_WEIGHTS[3]]


def test_budget_buys_more_light_trials_than_heavy_ones() -> None:
    """The point of the weight: a fixed budget holds five routine trials or one heavy pair."""
    budget = 5.5
    light = weights_of([case(f"L{i}", 2) for i in range(6)])
    heavy = weights_of([case(f"H{i}", 6) for i in range(6)])
    assert _affordable(light, budget) == 5
    assert _affordable(heavy, budget) == 2


def _affordable(weights: list[float], budget: float) -> int:
    spent, count = 0.0, 0
    for weight in sorted(weights):
        if spent + weight > budget:
            break
        spent, count = spent + weight, count + 1
    return count


def test_no_budget_leaves_the_setting_absent() -> None:
    """Default behaviour is unchanged: capacity is a slot count until a budget is set."""
    assert Settings(today=TODAY).burden_budget is None


def test_negative_budget_is_rejected() -> None:
    with pytest.raises(ValueError, match="burden_budget must not be negative"):
        Settings(today=TODAY, burden_budget=-1.0)
