"""Pharmacy set-up selection model for LTHTR, solved exactly with Gurobi.

It decides **which** trials pharmacy commits to set-up this planning cycle and reports what
that plan achieves against the 60-day target. It does not produce a timetable.

Quick start::

    from Experiments.optimiser import demo_settings, enrich, load_demo_cases, solve_selection

    settings = demo_settings()
    cases = enrich(load_demo_cases(), settings)
    result = solve_selection(cases, settings)
    print(result.headline())

Or from the command line::

    python -m Experiments.optimiser.cli --instance demo

Specification: `Model/Merged_Model_Specification_EN.md`, section 4 for the formulation and
section 6 for the outputs. Planner integration contract: `service.solve_json`.
"""

from __future__ import annotations

from .config import (
    DUR_ILLUSTRATIVE,
    DUR_MEASURED,
    DUR_POOLED,
    DUR_POOLED_CV,
    TIERS,
    Settings,
    demo_settings,
    tracker_settings,
)
from .data import Case, PlanningCase, enrich, plannable, tier_of
from .diagnostics import (
    PostSolveReport,
    PreSolveCheck,
    post_solve_report,
    pre_solve_check,
)
from .gate import gate_wait, gate_wait_table, rescue_matrix
from .loaders import load_demo_cases, load_tracker_cases
from .plan_sim import PlanOutcome, TrialRisk, simulate_plan
from .model import (
    Decision,
    GurobiUnavailableError,
    SelectionResult,
    solve_selection,
)
from .service import cases_from_json, result_to_json, settings_from_json, solve_json

__version__ = "0.1.0"

__all__ = [  # noqa: RUF022  grouped by role, which reads better than alphabetical here
    # configuration
    "Settings",
    "demo_settings",
    "tracker_settings",
    "TIERS",
    "DUR_MEASURED",
    "DUR_POOLED",
    "DUR_POOLED_CV",
    "DUR_ILLUSTRATIVE",
    # data
    "Case",
    "PlanningCase",
    "enrich",
    "plannable",
    "tier_of",
    # instances
    "load_demo_cases",
    "load_tracker_cases",
    # gate
    "gate_wait",
    "gate_wait_table",
    "rescue_matrix",
    # model
    "Decision",
    "SelectionResult",
    "solve_selection",
    # plan-level uncertainty
    "PlanOutcome",
    "TrialRisk",
    "simulate_plan",
    "GurobiUnavailableError",
    # diagnostics
    "PreSolveCheck",
    "PostSolveReport",
    "pre_solve_check",
    "post_solve_report",
    # planner integration
    "solve_json",
    "settings_from_json",
    "cases_from_json",
    "result_to_json",
]
