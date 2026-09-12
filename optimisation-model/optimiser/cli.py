"""Command line entry point.

    python -m Experiments.optimiser.cli --instance demo
    python -m Experiments.optimiser.cli --instance tracker --cap 5
    python -m Experiments.optimiser.cli --instance demo --json out/plan.json

Run from the project root. The demonstration instance is the one to run first: it is the only
one whose answer can be checked against published figures.
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import sys
from pathlib import Path

from .config import Settings, demo_settings, tracker_settings
from .data import enrich
from .diagnostics import post_solve_report, pre_solve_check
from .loaders import load_demo_cases, load_tracker_cases
from .model import GurobiUnavailableError, SelectionResult, solve_selection
from .service import result_to_json

logger = logging.getLogger(__name__)

__all__ = ["build_parser", "main"]

_ACTION_MARK = {"COMMIT": "+", "DEFER": ".", "CLOSE": "x", "BLOCKED": "?"}

# A real tracker carries dozens of cases with no notified date. They are reported, but the
# console lists a few and then counts the rest.
_MAX_BLOCKED_ROWS = 5


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lthtr-optimiser",
        description="Solve one pharmacy set-up planning cycle with Gurobi.",
    )
    parser.add_argument("--instance", choices=("demo", "tracker"), default="demo",
                        help="Which caseload to run. Default: demo.")
    parser.add_argument("--tracker-csv", type=Path, default=None,
                        help="Override the tracker CSV path.")
    parser.add_argument("--today", type=datetime.date.fromisoformat, default=None,
                        help="Planning date, ISO format. Default: the instance default.")
    parser.add_argument("--cap", type=int, default=None, help="Commitment limit c.")
    parser.add_argument("--floor", type=float, default=None, help="Value floor t.")
    parser.add_argument("--es", type=float, default=None,
                        help="Hands-on days per approval, E[S]. Pending Part 3, question 2.")
    parser.add_argument("--gpd", type=float, default=None,
                        help="Approver days available per month.")
    parser.add_argument("--value", action="store_true",
                        help="Activate P3, portfolio value. Paused by default.")
    parser.add_argument("--json", type=Path, default=None,
                        help="Write the full result as JSON to this path.")
    parser.add_argument("--solver-log", action="store_true", help="Show the Gurobi log.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Debug logging.")
    return parser


def _settings_from_args(args: argparse.Namespace) -> Settings:
    from dataclasses import replace

    base = demo_settings(args.today) if args.instance == "demo" else tracker_settings(args.today)
    changes = {}
    if args.cap is not None:
        changes["cap"] = args.cap
    if args.floor is not None:
        changes["floor"] = args.floor
    if args.es is not None:
        changes["approval_days"] = args.es
    if args.gpd is not None:
        changes["approver_days_per_month"] = args.gpd
    if args.value:
        changes["value_active"] = True
    return replace(base, **changes) if changes else base


def _report(result: SelectionResult, cases, settings: Settings) -> None:
    """Write the plan to the log in the order the meeting reads it."""
    check = pre_solve_check(cases, settings)
    report = post_solve_report(result, cases, settings, check=check)

    logger.info("")
    logger.info("=" * 78)
    logger.info(result.headline())
    logger.info("=" * 78)
    logger.info("")
    # AVAIL, not days to due: it is the window the on-time test actually reads, so a row
    # showing more days than its duration but no rescue would otherwise look like a bug.
    logger.info("  %-16s %-8s %-10s %6s %6s %6s  %s",
                "CASE", "ACTION", "TIER", "AVAIL", "DUR", "SAVE", "WHY")
    logger.info("  %s", "-" * 74)

    # Blocked cases are listed rather than dropped, but a real tracker holds dozens of them
    # and printing every one buries the decision. The count is what matters here; the register
    # in the planner is where each one gets chased.
    blocked_shown = 0
    for d in result.decisions:
        if d.action == "BLOCKED":
            blocked_shown += 1
            if blocked_shown > _MAX_BLOCKED_ROWS:
                continue
            logger.info("%s %-16s %-8s %-10s %6s %6s %6s  %s",
                        _ACTION_MARK[d.action], d.name[:16], d.action, d.tier[:10],
                        "-", "-", "-", d.reason)
            continue
        logger.info("%s %-16s %-8s %-10s %6d %6d %6.1f  %s",
                    _ACTION_MARK.get(d.action, " "), d.name[:16], d.action, d.tier[:10],
                    d.days_available, d.effective_duration, d.saving, d.reason)

    if blocked_shown > _MAX_BLOCKED_ROWS:
        logger.info("  ... and %d more blocked for the same reason, %d blocked in total.",
                    blocked_shown - _MAX_BLOCKED_ROWS, blocked_shown)

    logger.info("")
    logger.info("OBJECTIVES")
    logger.info("  P1 on time             %d", result.p1_on_time)
    logger.info("  P2 weighted lateness   %.1f", result.p2_weighted_lateness)
    if settings.value_active:
        logger.info("  P3 value committed     %.1f", result.p3_value)
    else:
        logger.info("  P3 value committed     %.1f  (not ranked, P3 is paused)",
                    result.p3_value)
    logger.info("  Gate wait at %d slots   %.2f days", result.committed_count, result.gate_wait)

    logger.info("")
    logger.info("DIAGNOSTICS")
    logger.info("  %s", check.summary())
    logger.info("  %s", report.summary())
    if any(c.duration > settings.setup_ceiling for c in cases):
        logger.info("")
        logger.info("  CEILING WARNING. A duration in use exceeds the %d-day set-up ceiling. "
                    "A trial handed to pharmacy today has %d days before the %d-day target "
                    "expires, so "
                    "any pathway longer than that cannot reach the target however many slots "
                    "are opened. Length is the constraint, not capacity.",
                    settings.setup_ceiling, settings.setup_ceiling, settings.target_days)
    logger.info("")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(message)s",
        stream=sys.stdout,
    )

    try:
        cases_raw = (load_demo_cases() if args.instance == "demo"
                     else load_tracker_cases(args.tracker_csv))
    except (FileNotFoundError, ValueError) as exc:
        logger.error("Could not load the %s instance: %s", args.instance, exc)
        return 2

    settings = _settings_from_args(args)
    cases = enrich(cases_raw, settings)

    try:
        result = solve_selection(cases, settings, log_to_console=args.solver_log)
    except GurobiUnavailableError as exc:
        logger.error("%s", exc)
        return 3
    except RuntimeError as exc:
        logger.error("Solve failed: %s", exc)
        return 4

    _report(result, cases, settings)

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(
            json.dumps(result_to_json(result, cases), indent=2), encoding="utf-8"
        )
        logger.info("JSON written to %s", args.json)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
