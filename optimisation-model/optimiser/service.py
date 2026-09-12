"""The JSON boundary between the solver and the LTHTR planner.

The planner (`Experiments/ui_prototype/lthtr_planner.html`) currently ranks cases with a greedy
rule written in JavaScript. This module lets it call the exact optimiser instead, without
renaming a single field: the keys below are the planner's own (`onc`, `asep`, `siteSel`,
`toDue`, `act`, `why`, `rescue`, `save`, `w`), so the integration is one `fetch` in place of
one function call.

Two properties the planner depends on are preserved deliberately:

- **Nothing is silently dropped.** A case with no usable date comes back as `BLOCKED` with a
  reason, so the register can keep showing it and a chasing action has somewhere to live.
- **Every row carries a sentence.** `why` is meant to be read out to a sponsor unchanged.

The planner is offline by design and holds no patient-identifiable data, so a service built on
this must stay on the local machine. Do not deploy it to a shared host without a separate
information-governance decision.
"""

from __future__ import annotations

import datetime
import logging
from collections.abc import Mapping, Sequence
from typing import Any

from .config import TIERS, Settings
from .data import Case, PlanningCase, enrich
from .diagnostics import post_solve_report, pre_solve_check
from .model import SelectionResult, solve_selection

logger = logging.getLogger(__name__)

__all__ = ["cases_from_json", "result_to_json", "settings_from_json", "solve_json"]

# 1.1 adds `setupStart` on input and `avail`, `segB` and `queueAssumed` on output.
# 1.2 adds `sponsorGreenLight`, `phase` and the optional `prep` on input, `prepCredit`
# and `effDur` on output. Additive only: a 1.0 register still solves, and an older front
# end can ignore the new keys.
_SCHEMA_VERSION = "1.2"


def _date(raw: Any) -> datetime.date | None:
    """Accept an ISO string, a date, or nothing. Anything else is an error worth raising."""
    if raw in (None, ""):
        return None
    if isinstance(raw, datetime.date):
        return raw
    if isinstance(raw, str):
        try:
            return datetime.date.fromisoformat(raw.strip()[:10])
        except ValueError as exc:
            raise ValueError(f"Date {raw!r} is not ISO format (YYYY-MM-DD)") from exc
    raise TypeError(f"Cannot read {raw!r} as a date")


def settings_from_json(payload: Mapping[str, Any], base: Settings) -> Settings:
    """Overlay the planner's Layer 2 and Layer 3 settings onto a base configuration.

    Only the keys present are applied, so a partial payload leaves the rest at their defaults.

    Args:
        payload: The planner's settings object. Recognised keys are `today`, `cap`, `floor`,
            `es`, `gpd`, `dur` and `valueActive`.
        base: Configuration supplying anything the payload omits.

    Returns:
        A new frozen `Settings`.

    Raises:
        ValueError: If `dur` is present but does not name every tier, or if the withdrawn
            `tradeBudget` key is sent. That key is refused rather than ignored so a caller
            still sending it is told, instead of watching a control do nothing.
    """
    from dataclasses import replace

    changes: dict[str, Any] = {}
    if "today" in payload:
        today = _date(payload["today"])
        if today is not None:
            changes["today"] = today
    if "cap" in payload:
        changes["cap"] = int(payload["cap"])
    if "floor" in payload:
        changes["floor"] = float(payload["floor"])
    if "es" in payload:
        changes["approval_days"] = float(payload["es"])
    if "gpd" in payload:
        changes["approver_days_per_month"] = float(payload["gpd"])
    if "valueActive" in payload:
        changes["value_active"] = bool(payload["valueActive"])
    if "tradeBudget" in payload:
        # Withdrawn 19 August 2026. It was accepted here and never read by the solver, so
        # setting it changed no plan. Refused loudly rather than dropped quietly.
        raise ValueError(
            "`tradeBudget` was withdrawn: the controlled trade is not implemented and the "
            "key never changed a plan. Portfolio value is additive in the number of trials "
            "committed, so giving up a trial to seat a more valuable one never pays. Sweep "
            "`cap` instead to read value against count."
        )
    if "dur" in payload:
        durations = {str(k): int(v) for k, v in dict(payload["dur"]).items()}
        missing = [t for t in TIERS if t not in durations]
        if missing:
            raise ValueError(f"`dur` is missing tiers: {missing}")
        changes["durations"] = durations

    return replace(base, **changes)


def cases_from_json(rows: Sequence[Mapping[str, Any]]) -> list[Case]:
    """Read the planner's case register.

    Args:
        rows: One object per case, using the planner's keys: `name`, `onc`, `asep`, `hra`,
            `siteSel`, `notified`, `setupStart`, `sponsorGreenLight`, `phase`, `prep`,
            `value`, `greenlight`. `notified` is first contact and `setupStart` is queue
            entry; a register carrying only `notified` still works, because queue entry falls
            back to it. The preparation credit is decided by rule from `sponsorGreenLight`
            plus `asep` or `phase`, so no per-study preparation field is expected in the
            return. `prep` is optional and overrides that rule in either direction when the
            planner running the tool has an answer of their own. See `data._prep_credit`.

    Returns:
        Raw cases, ready for `data.enrich`.

    Raises:
        ValueError: If a row has no name, since the name is the join key across every source.
    """
    cases: list[Case] = []
    for index, row in enumerate(rows):
        name = str(row.get("name", "")).strip()
        if not name:
            raise ValueError(f"Case at position {index} has no name")
        raw_value = row.get("value")
        cases.append(
            Case(
                name=name,
                # "rx" is the current key. "onc" is accepted only so the planner
                # prototype keeps running; it makes that prototype send ONCOLOGY data
                # into the PRESCRIPTION field, which is wrong and silent. Remove the
                # fallback once the prototype sends "rx".
                # See Experiments/ui_prototype/CONTRACT_CHANGES_TODO.md, item 1.
                prescription=bool(row.get("rx", row.get("onc", False))),
                aseptic=bool(row.get("asep", False)),
                hra_approval=_date(row.get("hra")),
                site_selected=_date(row.get("siteSel")),
                notified=_date(row.get("notified")),
                setup_start=_date(row.get("setupStart")),
                sponsor_green_light=_date(row.get("sponsorGreenLight")),
                phase=row.get("phase"),
                # Optional. Omit to let the complexity rule decide.
                prep_override=row.get("prep"),
                value=None if raw_value in (None, "") else float(raw_value),
                greenlight=_date(row.get("greenlight")),
            )
        )
    return cases


def result_to_json(
    result: SelectionResult,
    cases: Sequence[PlanningCase],
) -> dict[str, Any]:
    """Serialise a solved plan into the shape the planner renders.

    The `rows` array is already in the model's ranked order, so the front end can draw it
    without sorting and the order shown always matches the order solved.
    """
    settings = result.settings
    by_name = {c.name: c for c in cases}

    rows: list[dict[str, Any]] = []
    for decision in result.decisions:
        case = by_name.get(decision.name)
        rows.append(
            {
                "name": decision.name,
                "act": decision.action,
                "why": decision.reason,
                "tier": decision.tier,
                "dur": decision.duration,
                "prepCredit": decision.prep_credit,
                "effDur": decision.effective_duration,
                "toDue": decision.days_to_due,
                "avail": decision.days_available,
                "segB": decision.segment_b,
                "queueAssumed": bool(case and case.queue_entry_assumed),
                "w": decision.claim_weight,
                "save": decision.saving,
                "rescue": decision.on_time,
                "value": decision.value,
                "lateness": decision.lateness,
                "ready": bool(case and case.ready),
                "clockAnchored": bool(case and case.clock_anchored),
                "clockStart": case.clock_start.isoformat() if case and case.clock_start else None,
                "due": case.due.isoformat() if case and case.due else None,
            }
        )

    check = pre_solve_check(cases, settings)
    report = post_solve_report(result, cases, settings, check=check)

    return {
        "schemaVersion": _SCHEMA_VERSION,
        "solver": "gurobi",
        "headline": result.headline(),
        "committed": list(result.committed),
        "deferred": list(result.deferred),
        "closed": list(result.closed),
        "blocked": list(result.blocked),
        "objectives": {
            "p1OnTime": result.p1_on_time,
            "p2WeightedLateness": result.p2_weighted_lateness,
            "p3Value": result.p3_value,
            "valueActive": settings.value_active,
        },
        "gateWait": result.gate_wait,
        "committedCount": result.committed_count,
        "rows": rows,
        "diagnostics": {
            "p1Ceiling": check.p1_ceiling,
            "p1IsFlat": check.p1_is_flat,
            "p1Achieved": report.p1_achieved,
            "rescueable": list(check.rescueable),
            "breachedCount": len(check.breached),
            "nearestMiss": (
                {"name": check.nearest_miss_name, "days": check.nearest_miss_days}
                if check.nearest_miss_name else None
            ),
            "capacityUsed": report.capacity_used,
            "capacityLimit": report.capacity_limit,
            "binding": report.binding,
            "priceOfOnTime": report.price_of_on_time,
            "priceIsMeaningful": report.price_is_meaningful,
            "presolveSummary": check.summary(),
            "postsolveSummary": report.summary(),
        },
        "settings": {
            "today": settings.today.isoformat(),
            "cap": settings.cap,
            "floor": settings.floor,
            "es": settings.approval_days,
            "gpd": settings.approver_days_per_month,
            "dur": dict(settings.durations),
            "setupCeiling": settings.setup_ceiling,
        },
        "caveat": (
            "Weighted-day figures rank options, they do not forecast calendars. Durations are "
            "fitted from the tracker, so levels are indicative and shapes are reliable."
        ),
    }


def solve_json(payload: Mapping[str, Any], base: Settings) -> dict[str, Any]:
    """One call, end to end: planner JSON in, planner JSON out.

    Args:
        payload: `{"settings": {...}, "cases": [...]}`. Both keys are optional; an absent
            `settings` leaves `base` untouched.
        base: Default configuration, usually `config.demo_settings()` or
            `config.tracker_settings()`.

    Returns:
        The serialised plan.

    Raises:
        GurobiUnavailableError: If gurobipy is missing or unlicensed.
        ValueError: If the payload is malformed.
    """
    settings = settings_from_json(payload.get("settings", {}), base)
    cases = enrich(cases_from_json(payload.get("cases", [])), settings)
    result = solve_selection(cases, settings)
    return result_to_json(result, cases)
