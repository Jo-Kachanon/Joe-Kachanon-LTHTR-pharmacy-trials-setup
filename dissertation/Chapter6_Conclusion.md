# 6. Conclusion

## 6.1 Answers to the research questions

`[edit]` Table 6.1 answers the critical question and its three sub-questions, and cites the evidence behind each; their full wording is in §1.4 and Table 1.1.

**Table 6.1**

*Answers to the critical question and sub-questions SQ1 to SQ3* `[edit]`

|     | Answer                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| RQ  | Four distinct trials is the maximum achievable on time across the observed decision points. The constraint is time remaining when trials reach pharmacy, not nominal capacity: high-burden set-up can consume the full 60-day window before hand-over or approval delay is considered. Preparation is therefore the only tested lever that raises the on-time ceiling, because it creates time before the clock starts. Reducing hand-over and pharmacy-queue delay improves the position of trials near the threshold, while increasing nominal capacity reduces lateness but does not create further on-time completions (§§5.2, 5.4–5.6; Table 5.3).                            |
| SQ1 | Across the 25 observed decision points, only four distinct trials could be committed and completed on time within the cycle commitment limit; these trials are identified in Table 5.1 (§§5.1–5.2). `[edit]`                                                                                                                                                                                                                                                                                                                     |
| SQ2 `[edit]` | Neither the cycle commitment limit nor the approval queue is the primary constraint on the on-time count. Raising the cycle commitment limit increases the on-time count at none of the 25 decision points. The limit is a maximum, so the model leaves slots unused when additional commitments would create approval delay without improving on-time performance. The binding constraint is instead the time remaining when trials reach pharmacy: extra capacity reduces lateness but does not create further on-time completions. Approval time determines usable capacity, not the on-time ceiling (§§5.4–5.6; Appendix 5.C).                                                 |
| SQ3 | The rule improves on the arrival-order comparator only when capacity is tight: at one or two set-ups per month it can select a better committed portfolio, but from three onwards both approaches select the same trials. It therefore allocates scarce capacity rather than increasing overall performance (§5.1). Its on-time advantage is not robust across simulated portfolios. It appears only at pharmacy’s demonstrated duration floors, and within that regime is stronger for early arrivals and less aseptic pathway mixes. Across the demonstrated-floors regime, the rule is better in 36 per cent of runs and equal in the remainder by construction (Appendix 5.A). |

`[edit]` The observed ceiling is set by usable time, not by nominal commitment capacity.

## 6.2 Contribution and comparison with published work

The principal contribution is the translation of LTHTR’s pharmacy set-up process, existing capacity, pathways and shared approval queue into an optimisation model calibrated on the trust’s records. The repeatable model makes commitment decisions explicit, compares feasible portfolios and alternative scenarios before work is committed, and assesses portfolio-level on-time performance while distinguishing nominal from usable capacity. A companion user-interface mock-up makes the model operationally interpretable: users can progressively enter trial information, identify the 60-day clock start and pathway burden, consider preparation before the clock starts, and review transparent monthly commitment recommendations. `[edit]`

The findings refine the practical implication of the selection literature: selection can improve the allocation of commitments and reduce lateness across the queue, but it cannot recover time lost before pharmacy receives a trial. Earlier notification and preparation therefore create the conditions in which selection can improve on-time performance (Slotnick and Morton, 2007; Munoz et al., 2018; Qi et al., 2022; §§5.1, 5.4–5.6). Pharmacy is the first module of a wider trial set-up portfolio; comparable process, duration and capacity data from other departments would allow interdependent workstreams to be assessed jointly.

## 6.3 Limitations

The comparison with arrival order is limited by the comparator, not by the optimisation result. The comparator is a stated rule, not a record of routine practice, which already expedites some important studies. Any reported advantage is therefore an upper bound on the benefit over current practice and limits SQ3 alone. Similarly, agreement between the model and the four trials that achieved the target is retrospective consistency rather than prospective validation (§5.1; Appendix 5.A).

The four-trial ceiling is a conditional planning estimate, with its fourth on-time place particularly sensitive to the high-burden duration assumption (§5.3). The analysis rests on a small case-study base, estimated timing data, uncertain set-up durations and an assumed approval-time input. Sensitivity and simulation analyses test these uncertainties, but cannot independently validate the capacity ceiling or the reliability of the preparation result. In particular, holding approval delay at its expected value understates total operational uncertainty (§§4.2–4.3, 5.3–5.4; Appendices 5.A and 5.C).

Preparation is not capacity-free: the base model does not charge pre-window work against the commitment limit, so it may overstate its benefit. The sensitivity analysis in Appendix 5.E shows that preparation still increases the number of decision points achieving at least one on-time completion across the tested capacity range, although the three-trial result disappears at two set-ups. Preparation is therefore a capacity-consuming intervention, not a free source of additional time.

Finally, the model selects trials for commitment but does not sequence work after commitment. The evidence therefore concerns portfolio selection only and does not establish whether a sequencing intervention could improve performance (§3.6).

## 6.4 Implications for practice and for further research

The results imply four immediate actions for LTHTR: record hands-on approval time to calibrate the approval queue; flag aseptic studies at notification for targeted early preparation; plan to a reliable lower outcome rather than the deterministic maximum; and use selection to support, rather than substitute for, earlier preparation and hand-over (§§5.1, 5.3–5.5). `[edit]`

`[edit]` Four research directions follow from the limitations above:

- Extend the model to integrated selection and sequencing, which the present analysis cannot address.
- Measure pathway-specific work, approval service times and rework, so that resource use can be modelled in staff time rather than commitment counts.
- Optimise early preparation under finite capacity, including the activity it displaces.
- Prospectively evaluate the model's recommendations against observed practice, under demand growth, changing pathway mix and interdependent cross-service workflows.

---

## Source and provenance notes (not part of the submitted text)

**[edit] Table 6.1's Question column removed, 2026-09-02.** On the user's choice between two options put to them. The column repeated wording that Chapter 1 Table 1.1 and §1.4 already carry in full, and the lead sentence now says so, at a cost of nine words against the seventy-two the column held. The table title changed to name what it contains. Sixty-three words net.

**The answer cells were measured and left alone.** They run to 314 words against the 340 budgeted in `plan/Chapter6_skeleton_2026-08-30.md`, so there was nothing to compress there; the earlier plan to trim them was dropped once measured.

**A proposed short-label alternative was rejected for one of its labels.** The label offered for SQ2, "what binds, and when capacity stops helping", reintroduces the presupposition removed on 2026-09-01, that raising the limit helps somewhere, which the adjoining answer contradicts at all 25 decision points. Since the column is gone, the question does not arise; if a label column is ever restored, use the §1.4 wording.

**[edit] §6.4's future-research paragraph became four bullets, 2026-09-02.** Each direction answers a limitation in §6.3 one for one, and in prose the reader had to reconstruct that mapping. No agenda was dropped: integrated selection and sequencing, pathway-level measurement, finite-capacity preparation including displaced activity, and prospective evaluation under demand growth and cross-service dependency. Thirteen words. The four immediate actions above them are unchanged.

**[edit] Duplicate pointer removed from Table 6.1, 2026-09-02.** The SQ1 cell named Table 5.1 twice in consecutive sentences: the second was added on 2026-09-01 when the "limit is a maximum" sentence was cut, without noticing that the first sentence already carried the pointer. The section reference is now attached to the first. Eleven words.

**[edit] Three de-duplication cuts and a dead appendix reference, 2026-09-01.** Length pass agreed with the user. (1) **Appendix 6.A does not exist**: it was deleted at the skeleton stage (`plan/Chapter6_skeleton_2026-08-30.md:13`) but §6.2 and §6.4 both still cited it. §6.4's mock-up sentence is deleted as a duplicate of §6.2's fuller description, and §6.2 keeps the description without the citation. The chapter now contains no reference to Appendix 6.A. (2) §6.1's closing paragraph restated the RQ cell of Table 6.1 in prose and is replaced by a one-sentence bridge, on the user's choice of the two options offered. (3) The SQ1 cell's "the limit is a maximum rather than a requirement" sentence is deleted because the SQ2 cell answers that question directly and at greater length; SQ1 keeps its Table 5.1 pointer so it still answers "which trials". 55 counted words. The chapter is now 1,080 counted words against its own 850 budget.

**[edit] Table 6.1's SQ2 label corrected, 2026-09-01.** It read "What binds, and at what point does raising the limit stop helping?", which presupposes that raising the limit helps somewhere, while the answer in the adjoining cell states that it "increases the on-time count at none of the 25 decision points" and that neither the limit nor the approval queue is the primary constraint. The question and its answer sat side by side contradicting each other. The label now matches the reworded SQ2 in `Chapter1_Introduction.md` Table 1.1 verbatim. **One of three bound edits**, the third being Table 4.3's commitment-limit row in `Chapter4_Methodology.md`; the Chapter 1 note carries the full reasoning.

**§6.2 checked and left unchanged in the same pass.** `Chapter2_Literature_Review.md` §2.5 now states explicitly that the dissertation does not address the second literature gap, the combination of an on-time count with a value objective. §6.2 was re-read against that: it claims the translation of the process into a calibrated optimisation model and makes no claim about value or priority scoring, so no correction is owed. The contribution sentence remains quoted from §1.3, which was not edited in this pass. The Overleaf mirror has not been updated.

**Drafted 2026-08-30** against `plan/Chapter6_skeleton_2026-08-30.md`, which holds the section budgets, the evidence map and the reasoning behind each design choice. Four sections, matching the handbook's definition of Conclusions as summary of findings, comparison with published research, and implications, with the rubric's contribution and achievement folded into §6.1 and §6.2, and limitations kept in the counted body following the exemplar's §6.1.1.

**No new evidence, and one new run.** Every figure has a home in Chapters 4 or 5. The duration-error challenge is answered from Table 5.A.2's 0.8 and 1.2 rows rather than by argument, and the triangulation in §6.1 is stated verbatim in Appendix 5.A rather than argued here.

**Alternative explanations are folded into §6.3 rather than given their own section.** At this length there is no room for both, and each limitation reads better carrying the evidence that bounds it. The one alternative that cannot be answered, that no sequencing model was built, is conceded in the final paragraph and becomes the first research direction.

**The contribution sentence is quoted verbatim from `Chapter1_Introduction.md` §1.3.** If either copy is edited, edit both in the same pass. Chapter 1's provenance note records the same rule and the reason: criterion 1 scores Problem, Motivation, Contribution and Achievement as one bundle whose name is alignment.

**Two economies worth recording.** The sub-questions are given in brief in Table 6.1 rather than quoted in full, which saves about 100 words against a body target of 850; the full wording is in Chapter 1 Table 1 and the table's question column preserves both halves of each. And the on-time-objective comparison with Atsmony and Mosheiov (2023) was dropped from §6.2 as the least load-bearing of the three, Chapter 2 already carrying the ground for it.

**[edit] Preparation charged against capacity, 2026-08-30.** §6.3 had no limitation covering the capacity cost of preparation, and §5.4's claim that "what preparation does not cost is pharmacy capacity" rests on Figure 5.C.4, which measures the burden a plan commits rather than the effort the preparation itself consumes. Pharmacy's own answer to Part 3 Q4 on 2026-08-20 is that preparation happens "when capacity allows" and that effort is deliberately balanced, so the omission needed addressing rather than defending.

**It was resolved by measurement rather than by argument.** `Experiments/run_prep_capacity_charge_2026-08-30.py` sweeps the preparation lead against the number of concurrent set-ups over the same twenty-five decision points, adding no new modelling assumption and touching no existing script or result. Its six-slot column reproduces §5.4 exactly, at 9, 11, 17 and 20 dates, which is what makes the rest of the grid readable. The three-trial result survives to three concurrent set-ups and fails at two, against 3.51 observed in progress and 3.48 predicted by Little's Law (Appendix 4.A) `[edit]`. **No figure in Chapter 5 changes.** This is the one place where Chapter 6 rests on a run of its own, and it is reported in Appendix 5.E rather than in the counted body.

**Open item.** No prototype reference is included. `Experiments/ui_prototype/lthtr_planner.html` predates the optimiser contract change of 16 August 2026 and sends the Oncology column as the prescription flag, moving 2 of 20 demonstration studies between pathways, so no computed plan from it may be shown. If an appendix is added, one clause in §6.4 cites it; nothing here depends on that.

**Not yet done.** `overleaf/Chapters/Chapter6.tex` is still the template's red `\todo` scaffold and must be generated from this file.

**[edit] Provenance references reconciled, 2026-08-31.** The preparation-capacity sensitivity run is reported in Appendix 5.E, not Appendix 6.B; the earlier reference was stale following the appendix restructuring. The open item concerning Chapter 1 §1.5 is closed: §1.5 now describes Chapter 6 through the four functions delivered by §§6.1–6.4, so no further structural alignment edit is required.
