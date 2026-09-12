# Sensitivity and trade-off on the returned case studies

Rolling replay over 25 decision points, 2024-04-01 to 2026-04-01. Strict anchor rule, standard times, high-burden overlay. No synthetic data.

The 25 are month-starts, not trials: 19 trials generate them because a trial stays in the queue for several months. Consecutive queues therefore share studies, so the counts below are months in which the service could have acted, not independent observations.

## What each lever changes

| Lever | Controlled by | Basis | Range | Dates reaching 1 on time | Dates reaching 2 | Best count | Lateness saved |
|---|---|---|---|---|---|---|---|
| Preparation lead, committed trials | R&I | measured | 0 to 60 d | 20 of 25 | 12 | 3 | 394 |
| Hand-over gap, clock to notification | R&I | measured | 0 to 112 d | 11 of 25 | 1 | 2 | 498 |
| Pharmacy queue, notification to start | Pharmacy | measured | 0 to 23 d | 14 of 25 | 3 | 2 | 76 |
| Slots opened per month | Pharmacy | decision | 1 to 6 | 9 of 25 | 0 | 1 | 154 |
| Hands-on days per approval | Approver | assumed | 0.5 to 3.0 d | 9 of 25 | 0 | 1 | 20 |
| Target window | Governance | policy | 55 to 70 d | 11 of 25 | 1 | 2 | 77 |

Best value of each lever across every decision point. Lateness saved is the largest reduction at any one date, measured against that lever's own baseline setting rather than a global one.

