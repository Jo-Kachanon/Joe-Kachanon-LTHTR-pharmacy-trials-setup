"""Cases, and the Layer 1 arithmetic that turns dates into model inputs.

Nothing here is a judgement. Every derived field is subtraction from dates the Trust already
holds, which is what makes the later numbers auditable back to this module.

The field names mirror the planner prototype (`Experiments/ui_prototype/lthtr_planner.html`)
deliberately, so the JSON contract in `service.py` is a rename-free pass-through.
"""

from __future__ import annotations

import datetime
import logging
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from .config import BURDEN_WEIGHT_DEFAULT, BURDEN_WEIGHTS, Settings

logger = logging.getLogger(__name__)

__all__ = ["Case", "PlanningCase", "enrich", "plannable", "tier_of"]


@dataclass(frozen=True)
class Case:
    """A trial as it arrives from the tracker or the register, before any derivation.

    Attributes:
        name: Study short title. The join key across every source.
        prescription: Whether an electronic prescription must be built. This, with
            `aseptic`, fixes the set-up pathway. It replaced an oncology flag on
            2026-08-16: oncology was only ever a proxy, and it undercounts, because
            non-oncology studies need a prescription built too, through a different
            system but the same ePMA team and a similar timeline (6 August meeting).
        aseptic: Aseptic trial flag.
        hra_approval: HRA approval date, one of the two clock anchors.
        site_selected: Site selected date, the other clock anchor.
        notified: Date pharmacy first heard, tied to site selection. Diagnostic only, and
            never a start: it can precede queue entry by months (Chrissy, 5 August).
        setup_start: Date the trial entered the pharmacy work queue, triggered by R&I. The
            operational start, added by the August 2026 forms.
        sponsor_green_light: Date the sponsor confirmed the site. Until this lands the study
            may still not happen here, which is why Jaya rejected preparing on notification
            alone (6 August): a stretched team should not work on a study that is not picked.
        prep_override: Planner's own answer to "will pharmacy prepare this one before the
            clock starts", or None to let the complexity rule decide. This is a live input
            at planning time, not a field expected in the returned records: the person
            running the tool is looking at the study and can say. True forces the credit on
            for a study the rule would miss; False forces it off for one pharmacy has no
            capacity to prepare this cycle. See `_prep_credit`.
        prep_lead_days: Planned preparation lead, in days before the clock start that R&I
            will hand the trial to pharmacy. A planning input for trials R&I still holds,
            not a recorded field: positive means hand-over before the clock starts
            (preparation), negative a planned late hand-over, None means no plan and the
            median hand-over is assumed as before. Ignored when a recorded `setup_start`
            or `notified` date exists, because a reading beats a plan. Added 26 August
            2026 to carry the section 12 finding: preparation relieves the clock by
            exactly its lead and never shrinks the work, and it was the only observed
            route to the 60-day target (4 of 4 against 0 of 14). See `_work_start`.
        phase: Trial phase, 1 to 3, or None when not supplied. Known on day one from the
            protocol, before pharmacy has been told about the study or recorded anything,
            which is what makes it usable at the moment the planner is actually run. It is
            one of three day-one fields, with `aseptic` and `prescription`.
        value: Prioritisation Tool score, or None when the trial has not been scored.
        greenlight: Pharmacy greenlight date. Present means the set-up is finished, so the
            case is complete and drops out of planning.
    """

    name: str
    prescription: bool = False
    aseptic: bool = False
    hra_approval: datetime.date | None = None
    site_selected: datetime.date | None = None
    notified: datetime.date | None = None
    setup_start: datetime.date | None = None
    sponsor_green_light: datetime.date | None = None
    phase: int | None = None
    prep_override: bool | None = None
    prep_lead_days: int | None = None
    value: float | None = None
    burden_rank: int | None = None
    greenlight: datetime.date | None = None


@dataclass(frozen=True)
class PlanningCase:
    """A case with Layer 1 derived. Immutable, so a sweep rebuilds rather than mutates.

    Attributes:
        case: The raw case this was derived from.
        tier: Which set-up duration applies.
        duration: Set-up days for that tier, before any preparation credit.
        prep_credit: Days taken off `duration` because pharmacy prepared this study before
            the clock started. Zero unless both the sponsor has confirmed the site and the
            study is complex, meaning aseptic or phase 1, and zero for everyone while
            `prep_credit_cap_days` stays at its default of 0.
        effective_duration: `duration - prep_credit`, floored at one day. This is the length
            the on-time test and the lateness goal actually use.
        ready: Whether the case can enter the model. False only when the case carries
            neither a clock anchor nor a queue-entry date, so nothing can be derived.
        clock_start: The later of HRA approval and site selection. The 60-day clock starts
            here, not at pharmacy notification.
        clock_anchored: True when at least one real anchor date was available. False means
            `clock_start` fell back to queue entry minus the median handover, which is
            optimistic.
        queue_entry: When the trial entered, or is assumed to enter, the pharmacy work queue.
        queue_entry_assumed: True when no queue-entry date exists and the median handover was
            assumed instead. The plan is then a forecast for that case, not a reading.
        segment_b: Queue entry minus clock start. Days the 60-day clock ran before the trial
            reached pharmacy at all. None when either date is missing. **Negative when the
            trial entered the queue before its clock started**, which is preparation.
        prep_lead_days: The signed preparation lead L. For a trial with recorded dates this
            is `-segment_b`; for a day-one trial it is the planned lead from
            `Case.prep_lead_days`. Positive L relieves the clock by exactly L days and
            never changes `effective_duration`: the job is the same size, relocated before
            the window (recompute report section 12).
        due: Clock start plus the 60-day target.
        days_waited: Planning date minus queue entry, floored at zero.
        days_to_due: Due date minus the planning date. Negative means already past 60 days.
        days_available: Due date minus the day work can actually begin. This is `days_to_due`
            less whatever of segment B is still ahead, and it is what the on-time test uses.
        claim_weight: `1 + days_waited / weight_divisor`. A trial waiting a year has twice the
            claim of one that has just been queued. This stops slow trials being starved.
        value: The score, or None when unscored.
    """

    case: Case
    tier: str
    duration: int
    ready: bool
    prep_credit: int = 0
    effective_duration: int = 0
    clock_start: datetime.date | None = None
    clock_anchored: bool = False
    queue_entry: datetime.date | None = None
    queue_entry_assumed: bool = False
    segment_b: int | None = None
    prep_lead_days: int | None = None
    due: datetime.date | None = None
    days_waited: int = 0
    days_to_due: int = 0
    days_available: int = 0
    claim_weight: float = 1.0
    value: float | None = None
    burden_rank: int | None = None

    @property
    def capacity_weight(self) -> float:
        """What this trial spends from the burden budget, in routine-trial equivalents.

        A trial pharmacy has not rated falls back to the moderate band rather than to the
        lightest, so an unrated trial is never assumed to be free.
        """
        if self.burden_rank is None:
            return BURDEN_WEIGHT_DEFAULT
        return BURDEN_WEIGHTS.get(self.burden_rank, BURDEN_WEIGHT_DEFAULT)

    @property
    def name(self) -> str:
        return self.case.name

    @property
    def scored(self) -> bool:
        return self.value is not None

    def cycle_saving(self, cycle_days: int) -> float:
        """Weighted days avoided by committing this case rather than deferring it one cycle.

        A ranking quantity for comparing plans, not a calendar forecast. Say that whenever the
        number is quoted.
        """
        return round(self.claim_weight * cycle_days, 1)

    def clears_floor(self, floor: float) -> bool:
        """Unscored cases pass through flagged rather than being dropped."""
        return self.value is None or self.value >= floor


def tier_of(case: Case) -> str:
    """Which set-up pathway a case follows, from its two flags."""
    if case.prescription and case.aseptic:
        return "Both"
    if case.prescription:
        return "Prescription only"
    if case.aseptic:
        return "Aseptic only"
    return "Routine"


def _queue_entry(case: Case) -> datetime.date | None:
    """When the trial entered the pharmacy work queue.

    `setup_start` is the field the August 2026 forms add. Until a return carries it, the
    tracker's "Pharmacy notified by RSG- start review" column stands in, because that is what
    it measures in practice. Chrissy, 6 August: "it's not really the pharmacy notification
    date, it's more the pharmacy start date for set up." A return carrying both fields uses
    `setup_start` and leaves `notified` as the diagnostic it is.
    """
    return case.setup_start or case.notified


def _clock_start(
    case: Case, settings: Settings, queue_entry: datetime.date | None
) -> tuple[datetime.date | None, bool]:
    """The later of the two anchors, with the handover fallback and whether it was used.

    Settled 3 August 2026: pharmacy notification is **not** the clock start. It is a
    downstream event, and the gap between the two is uncounted. Roughly 80% of tracker trials
    carry at least one anchor, so the fallback is a last resort rather than a norm.
    """
    anchors = [d for d in (case.hra_approval, case.site_selected) if d is not None]
    if anchors:
        return max(anchors), True
    if queue_entry is None:
        return None, False
    return queue_entry - datetime.timedelta(days=settings.handover_days), False


def _prep_credit(case: Case, settings: Settings) -> int:
    """Days off the set-up because pharmacy prepared before the clock started.

    Two conditions, both required.

    * **the sponsor has confirmed the site.** Jaya, 6 August, rejecting preparation on
      notification alone: "if we are not going to be site selected, then it's a small team,
      stretched team, and then they start looking at it only to be told that the study didn't
      get picked." The sponsor green light is what removes that risk;
    * **the study is complex enough that pharmacy would prepare it.** This is a service-level
      rule, not a per-study answer, and it is what LTHTR form 3 actually asks for: "how often
      does real preparation happen", answered once with "only on complex studies, aseptics or
      unusual handling" among the options.

    **A per-study preparation flag was used here until 2026-08-16 and has been removed.** No
    such field was ever requested: form 1 asks per study for the prescription, prescribing
    system, specialist input, aseptic, phase and delay reason, and nothing else. Gating the
    credit on a field that will never arrive made it permanently unreachable rather than
    merely inert, and it made the demonstration depend on a column invented for the mock.

    The rule below is a default, and `Case.prep_override` overrides it in either direction
    when the planner has an answer of their own. That is not the withdrawn field returning:
    this one is supplied live by the person running the tool, not expected in the records.

    Complexity is read from what the return does carry. Aseptic work is the trust's own
    example of a complex study; phase 1 is included because early-phase medicines are the
    other case the service names, and phase is the only complexity signal available on day
    one. Whether phase belongs here is a question the returned data is meant to inform, and
    16 to 20 studies will not settle it, so it is recorded as an assumption rather than a
    finding.

    Returns:
        Days to subtract from the tier duration. Zero unless both conditions hold, and zero
        for every study while `prep_credit_cap_days` is at its default of 0.
    """
    if case.sponsor_green_light is None:
        return 0
    # The rule is a default for studies nobody has judged. Where the planner has judged
    # one, that answer wins in both directions: it can carry a study the rule would miss,
    # and it can withhold the credit from a study pharmacy has no capacity to prepare.
    prepared = case.prep_override
    if prepared is None:
        prepared = case.aseptic or case.phase == 1
    if not prepared:
        return 0
    return settings.prep_credit_cap_days


def _work_start(
    queue_entry: datetime.date | None, settings: Settings
) -> tuple[datetime.date, bool]:
    """The earliest day set-up work can begin, and whether the date had to be assumed.

    This is where segment B is subtracted. Three situations, one rule:

    * the trial is already in the queue, so work can begin today and the whole of segment B
      is behind it, already spent out of the 60 days;
    * R&I has set a future hand-over date, so the rest of segment B is still ahead and the
      window shrinks by exactly that much;
    * R&I holds the trial and has named no date, which is the day-one case where only the
      R&I fields exist. The median handover is assumed and the case is flagged, because a
      forecast presented as a reading is the thing that gets a model distrusted.
    """
    if queue_entry is None:
        return settings.today + datetime.timedelta(days=settings.handover_days), True
    return max(settings.today, queue_entry), False


def _planned_work_start(
    clock_start: datetime.date, prep_lead_days: int, settings: Settings
) -> tuple[datetime.date, bool]:
    """Work start for a day-one trial whose hand-over is planned relative to its clock.

    The section 12 mechanism: hand-over `prep_lead_days` before the clock start gives the
    trial exactly that many extra days of window, because the on-time test reads
    `days_available = due - work_start`. Clipped at today, since a plan cannot bank days
    that have already passed. Always flagged assumed: a planned hand-over is a forecast.
    """
    planned_entry = clock_start - datetime.timedelta(days=prep_lead_days)
    return max(settings.today, planned_entry), True


def enrich(cases: Iterable[Case], settings: Settings) -> list[PlanningCase]:
    """Derive Layer 1 for every case.

    Cases with a greenlight date are dropped as complete, so the whole tracker can be passed
    in without filtering it first. A case carrying neither a clock anchor nor a queue-entry
    date is kept but marked not ready, so a missing date is a visible row rather than a
    silent omission.

    Args:
        cases: Raw cases.
        settings: Model parameters supplying the planning date and the durations.

    Returns:
        One `PlanningCase` per incomplete case, in input order.
    """
    derived: list[PlanningCase] = []
    for case in cases:
        if case.greenlight is not None:
            continue

        tier = tier_of(case)
        duration = settings.durations[tier]
        # A study cannot take less than a day, however generous the credit is set.
        prep_credit = min(_prep_credit(case, settings), duration - 1)
        effective_duration = duration - prep_credit
        queue_entry = _queue_entry(case)
        clock_start, anchored = _clock_start(case, settings, queue_entry)

        if clock_start is None:
            derived.append(PlanningCase(case=case, tier=tier, duration=duration, ready=False,
                                        prep_credit=prep_credit,
                                        effective_duration=effective_duration,
                                        value=case.value))
            continue

        due = clock_start + datetime.timedelta(days=settings.target_days)
        if queue_entry is None and case.prep_lead_days is not None and anchored:
            work_start, assumed = _planned_work_start(clock_start, case.prep_lead_days, settings)
        else:
            work_start, assumed = _work_start(queue_entry, settings)
            # The default day-one assumption is hand-over `handover_days` after TODAY. For
            # a trial whose clock starts in the future that implies an unplanned lead, and
            # an implicit lead should never pass silently now that an explicit one exists.
            if queue_entry is None and (implicit := (clock_start - work_start).days) > 0:
                logger.info(
                    "%s: no hand-over plan; the default assumption implies a %d-day lead "
                    "before the clock. Pass prep_lead_days to make the plan explicit.",
                    case.name, implicit)
        # A trial not yet queued has waited no time in the queue, so the floor is zero
        # rather than a negative wait that would give it less claim than a fresh arrival.
        days_waited = max(0, (settings.today - queue_entry).days) if queue_entry else 0

        derived.append(
            PlanningCase(
                case=case,
                tier=tier,
                duration=duration,
                ready=True,
                prep_credit=prep_credit,
                effective_duration=effective_duration,
                clock_start=clock_start,
                clock_anchored=anchored,
                queue_entry=queue_entry,
                queue_entry_assumed=assumed,
                segment_b=(queue_entry - clock_start).days if queue_entry else None,
                prep_lead_days=((clock_start - queue_entry).days if queue_entry
                                else case.prep_lead_days),
                due=due,
                days_waited=days_waited,
                days_to_due=(due - settings.today).days,
                days_available=(due - work_start).days,
                claim_weight=round(1.0 + days_waited / settings.weight_divisor, 2),
                value=case.value,
                burden_rank=case.burden_rank,
            )
        )

    unready = sum(1 for c in derived if not c.ready)
    if unready:
        logger.info("%d of %d cases carry neither a clock anchor nor a queue-entry date "
                    "and cannot be planned.", unready, len(derived))
    credited = [c for c in derived if c.prep_credit > 0]
    if credited:
        logger.info("%d of %d cases carry a preparation credit of %d days, on pharmacy's own "
                    "flag rather than on any date.", len(credited), len(derived),
                    settings.prep_credit_cap_days)
    assumed_count = sum(1 for c in derived if c.queue_entry_assumed)
    if assumed_count:
        logger.info("%d of %d cases have no queue-entry date, so hand-over was assumed at "
                    "the median of %d days.", assumed_count, len(derived),
                    settings.handover_days)
    return derived


def plannable(cases: Sequence[PlanningCase], floor: float) -> list[PlanningCase]:
    """The eligible set `E`: ready to plan, and clearing the value floor.

    Cases below the floor are closed rather than queued forever. Unscored cases pass through.
    """
    return [c for c in cases if c.ready and c.clears_floor(floor)]
