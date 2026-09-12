# Verification record: Gurobi package against the specification and the prototype

**Date:** 5 August 2026
**Instance:** the 16-trial demonstration caseload, planning date 2026-08-03, `c`=3, floor 20,
`E[S]`=1.0, approver days 9.45, illustrative durations.
**Reproduce:** `python Experiments/optimiser/crosscheck/compare_with_prototype.py`

## Verdict

The package agrees with the prototype everywhere the two are comparable. Every disagreement
found is between the **specification's published numbers** and **both implementations**, or is
a documented design difference in the package. No defect was found in the package.

| Check | Result |
|---|---|
| Layer 1 derived fields, 16 cases x 7 fields | 112 of 112 match |
| Gate wait, 11 commitment levels | 11 of 11 match |
| Committed set at 3 slots | Identical |
| P1 at 3 slots | Identical |
| Frontier at 3 slots, all three points and their plan compositions | Match the specification |
| Eligible count and plan count | 11 and 165, match the specification |
| Price-of-on-time table, 33 cells | 30 match, 3 disagree (all in the 8-slot row) |
| Tests | 13 passed |
| Lint | ruff clean |

## Method

The cross-check does not read the two implementations side by side. It extracts the
`model-logic` block directly from `Experiments/ui_prototype/lthtr_planner.html` by marker,
runs it under Node on the same pinned instance, and compares field by field. Extraction is by
marker rather than line number so it survives restyling of the HTML.

## Finding 1: the caseloads are one caseload under two names

The prototype renames the eight mock trials. Same order, same values, same dates.

| Workbook and package | Prototype |
|---|---|
| MOCK-01 | VELA-201 |
| MOCK-02 | CASSINI |
| MOCK-03 | HALCYON |
| MOCK-04 | BRIDGE-2 |
| MOCK-05 | ORION-BC |
| MOCK-06 | KESTREL |
| MOCK-07 | WILLOW |
| MOCK-08 | FERN-CT |

The documentation states that the workbook, the upload file and the prototype "all describe one
caseload". The data confirm it; the labels do not. Anyone comparing a workbook tab against a
prototype screenshot will think they are looking at different studies. Worth settling on one
scheme before any of this reaches the dissertation.

## Finding 2: the specification's 8-slot row is wrong

Section 6C reports zero on-time trials at eight slots. Both implementations report one.

At eight committed the gate wait is 9.39 days. MOCK-07 has 50 days to its due date against a
36-day set-up, needing 45.39, so it survives. TiPE has 44 days and misses by 1.39.

| Slots | Spec `P2` | Spec `P1` | Prototype `P2` | Prototype `P1` | Package `P1` |
|---|---|---|---|---|---|
| 7 | 261.9 | 2 | 261.9 | 2 | 2 |
| **8** | **301.2** | **0** | **299.4** | **1** | **2** |
| 9 | 333.3 | 0 | 333.3 | 0 | 2 |

Every other row of that table matches. The narrative built on it, that on-time peaks at seven
and then collapses, still holds directionally: the collapse is to one trial at eight and to
zero at nine, not to zero at eight.

## Finding 3: the specification's formulation and its numbers disagree with each other

Section 4 defines the goal constraint with `d+_i >= 0`, so lateness is clipped and a trial
earns nothing for finishing early. Section 6C's numbers were computed with a shortcut that
credits every committed trial with the full `w_i x cycle`, which is only correct once a trial
has already breached.

The difference falls entirely on trials that still have slack, and those are exactly the
rescueable ones. So the shortcut overstates the P2 contribution of the trials P1 wants to
rescue, and understates what ranking on-time first costs.

| Quantity | Section 6C | Deviation form, as section 4 defines it |
|---|---|---|
| Price of putting on-time first, 3 slots | 20.4 weighted days | 41.3 weighted days |

The committed set is unaffected, because P1 outranks P2 either way.

## Finding 4: the live-queue savings in section 4 round differently

Section 4's table multiplies an unrounded claim weight; both implementations round the weight
to two decimals first, which is what the prototype's `r2()` does.

| Trial | Days waited | `w_i` | Spec saving | Implementations |
|---|---|---|---|---|
| LIBREXIA-STROKE | 637 | 2.75 | 82.4 | 82.5 |
| STOP'EM | 411 | 2.13 | 63.8 | 63.9 |
| STARshiP | 374 | 2.02 | 60.7 | 60.6 |

Days waited and the weights match exactly. This is presentational, not a defect, but the
published figures should be regenerated rather than retyped.

## The one design divergence, and why it is not a defect

Above seven slots the package commits seven and declines the rest. The prototype fills every
slot.

| Limit | Prototype commits | Prototype `P1` | Package commits | Package `P1` |
|---|---|---|---|---|
| 7 | 7 | 2 | 7 | 2 |
| 8 | 8 | 1 | 7 | 2 |
| 11 | 11 | 0 | 7 | 2 |

The prototype evaluates rescueability at the commitment limit, so it assumes every slot gets
filled. The package prices the approval queue at the count it actually commits, so an eighth
trial has to justify the longer queue it imposes on the other seven. It cannot, and P1 outranks
P2, so the model declines it.

The cross-check asserts that the package never loses an on-time trial by self-limiting, and it
does not. The practical consequence is that the seven-slot ceiling is now derived by the model
rather than read off a chart by a person.

## What this does not verify

Internal consistency only, which is validation layer 1 of specification section 9. It shows the
implementations agree with each other and identifies where the published figures do not. It says
nothing about whether the model's decisions are better than LTHTR's, which is layer 2 and needs
the 14 recovered decision months replayed.
