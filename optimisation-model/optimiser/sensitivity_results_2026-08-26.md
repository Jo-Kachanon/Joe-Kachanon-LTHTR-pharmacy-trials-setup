# Sensitivity sweeps: approval days and capacity budget

SYNTHETIC 30-Aug queue, floors world, Q4b 5-6 overlay, cap 3.

## Approval days E[S] (the gate weight)

| E[S] (d) | gate wait @3 | gate wait @6 | P1 | P2 | committed |
|---|---|---|---|---|---|
| 0.5 | 0.2 | 0.4 | 3 | 1891 | SYNTH-02, SYNTH-14, SYNTH-09 |
| 1.0 | 0.8 | 3.0 | 3 | 1901 | SYNTH-02, SYNTH-14, SYNTH-09 |
| 1.5 | 2.3 | 48.5 | 2 | 1908 | SYNTH-02, SYNTH-09 **(plan changed)** |
| 2.0 | 5.9 | 64.7 | 2 | 1960 | SYNTH-14, SYNTH-09 **(plan changed)** |
| 2.5 | 16.4 | 80.8 | 2 | 1998 | SYNTH-14, SYNTH-09 **(plan changed)** |
| 3.0 | 97.0 | 97.0 | 2 | 2068 | SYNTH-14, SYNTH-09 **(plan changed)** |

## Capacity budget (burden-weighted, routine-trial equivalents)

| budget | buys | trials committed | P1 | P2 | burden spent | committed |
|---|---|---|---|---|---|---|
| 2.61 | 1 heavy | 2 | 1 | 1884 | 2.00 | SYNTH-09, SYNTH-13 |
| 3.48 | 3.48 routine | 2 | 2 | 1925 | 2.74 | SYNTH-14, SYNTH-09 |
| 5.22 | 2 heavy | 4 | 2 | 1859 | 4.74 | SYNTH-14, SYNTH-09, SYNTH-13, SYNTH-08 |
| 6.96 | 6.96 routine | 4 | 3 | 1867 | 6.35 | SYNTH-02, SYNTH-14, SYNTH-09, SYNTH-13 |
| 7.83 | 3 heavy | 5 | 3 | 1840 | 7.35 | SYNTH-02, SYNTH-14, SYNTH-09, SYNTH-13, SYNTH-08 |
| 10.44 | 4 heavy | 5 | 3 | 1836 | 8.96 | SYNTH-02, SYNTH-14, SYNTH-09, SYNTH-03, SYNTH-13 |

## Score floor (eligibility threshold, out of the chapter since 27 Aug)

| floor | eligible | P1 | P2 | value committed | committed |
|---|---|---|---|---|---|
| 0 | 16/16 | 3 | 1901 | 60 | SYNTH-02, SYNTH-14, SYNTH-09 |
| 5 | 16/16 | 3 | 1901 | 60 | SYNTH-02, SYNTH-14, SYNTH-09 |
| 10 | 15/16 | 3 | 1729 | 60 | SYNTH-02, SYNTH-14, SYNTH-09 |
| 15 | 13/16 | 3 | 1270 | 60 | SYNTH-02, SYNTH-14, SYNTH-09 |
| 20 | 8/16 | 1 | 804 | 91 | SYNTH-02, SYNTH-13, SYNTH-10 |
| 25 | 7/16 | 1 | 755 | 91 | SYNTH-02, SYNTH-13, SYNTH-10 |
| 30 | 4/16 | 0 | 442 | 102 | SYNTH-13, SYNTH-06, SYNTH-16 |

Real-queue note: only 6 of the 20 returned trials carry a Stage 2 score and unscored trials pass the floor by design, so on today's real queue the floor excludes almost nothing. Its bite here is a property of a fully scored portfolio -- which is what the Prioritisation Tool intends to create.
