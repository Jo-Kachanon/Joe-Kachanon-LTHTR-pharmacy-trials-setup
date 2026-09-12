# V2-B plan-level uncertainty, August-return calibration

10,000 replications per cell, seed 20260818. Spread comes from duration alone (gate wait held at its expectation), so every interval here understates total uncertainty — a floor on the spread.

### real queue 2025-02-01, medians world (CV 0.467)

- committed: DyNAMIc, BNT327-06, BALLOON
- promised on-time count: **0**
- distribution over 10,000 runs: 0: 71.2%, 1: 28.8%, 2: 0.0%, 3: 0.0%
- delivers the promise in **100%** of runs; count met in 90% of runs: **0**

### real queue 2025-02-01, floors world (CV 0.575)

- committed: DyNAMIc, BNT327-06, BALLOON
- promised on-time count: **0**
- distribution over 10,000 runs: 0: 51.6%, 1: 48.4%, 2: 0.0%, 3: 0.0%
- delivers the promise in **100%** of runs; count met in 90% of runs: **0**

### synthetic queue 30 Aug, medians world (CV 0.467)

- committed: SYNTH-03, SYNTH-13, SYNTH-10
- promised on-time count: **0**
- distribution over 10,000 runs: 0: 100.0%, 1: 0.0%, 2: 0.0%, 3: 0.0%
- delivers the promise in **100%** of runs; count met in 90% of runs: **0**

### synthetic queue 30 Aug, floors world (CV 0.575)

- committed: SYNTH-02, SYNTH-14, SYNTH-09
- promised on-time count: **3**
- distribution over 10,000 runs: 0: 0.9%, 1: 18.0%, 2: 48.5%, 3: 32.6%
- delivers the promise in **33%** of runs; count met in 90% of runs: **1**
