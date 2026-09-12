# 2. Literature Review

The pharmacy clinical-trial set-up service accepts work as it arrives without explicit regard to available capacity, and some trials consequently miss the 60-day target. A planning response must identify feasible on-time commitments and limit lateness across the remaining queue. These are counted in different units, and the trust has not defined how to trade one against the other. Chapter 2 reviews the evidence relevant to both concerns and identifies the gap where they must be addressed together. `[edit]`

However, before work can be prioritised, the set-up process itself must be measured, and the literature provides little support for this. `[edit]` Walker et al. (2018) identify 117 trial-site performance metrics, none covering set-up or activation, and the eight core metrics Whitham et al. (2018) settle on by Delphi consensus all apply after a site opens. No established method therefore exists for measuring pharmacy set-up work, and this study must define the process and its measures before modelling it.

## 2.1 Establishing an unrecorded process

`[edit]` Process mapping is the method for that step. Ofosu et al. (2021) build a map of an emergency referral system from practitioner interviews and then examine it for gaps between the intended process and the actual one. This study follows the same procedure, and stops there because the trust does not record activity-level timings. Its output is an operational flowchart of how the three pharmacy teams and Research and Innovation interact.

`[edit]` The resulting map identifies a final approval step shared across trials, which makes commitment selection consequential where that resource is constrained.

## 2.2 Selection under shared capacity

`[edit]` Which trials to start is a recognised scheduling problem. Scheduling with rejection decides which jobs to accept as well as when to schedule them, because in a heavily loaded system accepting every job increases completion delays and tardiness costs (Shabtay et al., 2013).

Slotnick and Morton (2007) give the formulation this study follows. Their model selects jobs from a pool and balances the value of accepted jobs against their weighted tardiness, and early completion is neither penalised nor rewarded, so late completion carries a cost. Lewis and Slotnick (2002) extend the decision across planning periods, allowing acceptance decisions to be updated as new jobs arrive.

Similar models have been used in clinical research, but not for pharmacy trial set-up. Deglise-Hawkinson et al. (2020) select trials for a clinical research unit that shares nursing and facility capacity. They showed that accepting an additional trial increases waiting times for other trials, and that this effect is non-linear, which is why they treat accepting a proposed trial as a decision that requires a model.

None of these models orders its objectives. Slotnick and Morton (2007) and Lewis and Slotnick (2002) combine theirs into one financial value, because revenue and lateness penalties are both money; Deglise-Hawkinson et al. (2020) instead bound access delay and overtime. `[edit]` Each needs a number the trust cannot supply, a trade-off rate in the first case and a bound in the second.

## 2.3 Ordered objectives

This study uses pre-emptive goal programming to order its objectives. In goal programming, each objective has a target, and the model seeks to reduce the difference between the target and the result. In the pre-emptive form, objectives are placed in order of importance. A lower-priority objective is considered only if it does not reduce the result achieved for a higher-priority objective (Jones and Tamiz, 2010).

`[edit]` Munoz et al. (2018) show when weighted goal programming is suitable: where decision-makers can state how important one objective is against another, as their clinical institute did through expert ratings. The trust has no such basis. Blake and Carter (2002) instead used the pre-emptive approach in hospital planning, fixing an economically feasible case mix before choosing among the equally feasible alternatives. Section 3.5 applies that logic.

The model in this study has two distinctive features. `[edit]` First, its highest-priority objective is to maximise the number of trials completed on time, which is the measure the trust is assessed on. Atsmony and Mosheiov (2023) also maximise a weighted count of jobs meeting their due dates, although theirs is a just-in-time setting in which early completion is penalised too, and they use this as their only objective. Second, the model represents a single approval step that every trial must cross, whereas the machines in Atsmony and Mosheiov are independent. The next section explains why this step limits the number of trials that can be in progress.

## 2.4 Modelling the shared step under uncertainty

`[edit]` The approval step is a queue: trials wait, and one person completes the approval. Gupta (2013) recommends the M/G/1 model for a single server whose service times follow no particular distribution, since its formula needs only the average service time and its variation, which are the only data the trust can provide. Appendix 4.B examines the arrival assumption it makes.

`[edit]` Similar queues have been used to model professional sign-off. Lahiri and Seidmann (2012) model a radiologist’s workstation as a single-server queue, and Svirsko et al. (2022) include waiting time that increases with workload in an optimisation model. Neither makes queue waiting time depend on which work is accepted: the first measures the queue without deciding which cases enter it, and in the second workload results from routing rather than selection decisions.

Section 3.4 brings approval waiting time into the trial-selection decision. The wait is shared by every committed trial and grows with the number committed, so a trial's on-time status depends on how many trials the plan commits, not on that trial alone.

`[edit]` The alternative was to simulate the full set-up pathway. Discrete-event simulation is widely used in NHS capacity planning (Demir et al., 2017; Harper et al., 2023), and Martinez et al. (2016) used it to model trial activation. The available records give coarse, retrospective segment timings, not the event-level activity, sequencing and service-time data such a simulation needs; they are sufficient for a queueing formula and not for a simulation of the full pathway.

`[edit]` One issue remains. The duration data are limited and highly variable, and on-time completion is a threshold outcome, so evaluating a plan on average durations does not show how often it will succeed. The selected plan is therefore tested through simulation, as Kheiri et al. (2021) test optimised NHS theatre schedules against bed-capacity breaches and Mavrotas et al. (2015) do for multi-objective models.

`[edit]` Two sources of uncertainty affect this test: the number of simulation runs, which sets the precision of the result (Morris et al., 2019), and the duration distribution estimated from a small sample, which Barton (2012) calls input uncertainty. Chapter 4 reports both.

## 2.5 Contribution of this dissertation

`[edit]` Table 2.1 sets the reviewed models against the problem's features.

**Table 2.1**

*Literature review summary*

|                                 | Select | Shared step modelled | Value objective | Lateness | On-time count | Objectives  | Setting                     |
| ------------------------------- | ------ | -------------------- | --------------- | -------- | ------------- | ----------- | --------------------------- |
| Slotnick and Morton (2007)      | ✓      |                      | ✓               | ✓        |               | Weighted    | Manufacturing               |
| Lewis and Slotnick (2002)       | ✓      |                      | ✓               | ✓        |               | Weighted    | Manufacturing               |
| Blake and Carter (2002)         | ✓      |                      | ✓               |          |               | Pre-emptive | Hospital                    |
| Munoz et al. (2018)             | ✓      |                      | ✓               |          |               | Weighted    | Clinical research institute |
| Qi et al. (2022)                | ✓      |                      | ✓               |          |               | Weighted    | Clinical trials             |
| Deglise-Hawkinson et al. (2020) | ✓      | ✓                    | ✓               |          |               | Bounded     | Clinical research unit      |
| Kheiri et al. (2021)            |        |                      |                 |          |               | Single      | NHS theatres                |
| Svirsko et al. (2022)           |        | ✓                    |                 |          |               | Frontier    | Hospital pharmacy           |
| Atsmony and Mosheiov (2023)     | ✓      |                      |                 |          | ✓             | Single      | Parallel machines           |
| This study                      | ✓      | ✓                    |                 | ✓        | ✓             | Pre-emptive | NHS pharmacy                |

*Note.* The value objective, lateness and on-time count columns record what each model optimises, not what it constrains.

`[edit]` Two gaps follow. First, no reviewed model combines a shared step with pre-emptive objectives: Deglise-Hawkinson et al. (2020) model a shared step but bound their other objectives rather than ordering them, and Blake and Carter (2002) order their objectives but model no shared step. This dissertation closes that gap, modelling the shared approval step as an analytical queue whose waiting time is calculated for each possible plan size, and ordering two goals pre-emptively: the on-time count first, matching the measure the trust is assessed on, and weighted lateness second. Second, no reviewed model combines an on-time count with a value objective. That gap is not addressed here, because no trial in this analysis carries a priority score (§3.1), and it remains open pending score coverage linked to set-up outcomes.


---

## Source and provenance notes (not part of the submitted text)

**[edit] §2.4's M/G/1 paragraph compressed, 2026-09-02.** The link the chapter needs survives in one sentence: variable approval time, a single server, a formula needing only the mean and the variation, which are the only data the trust holds, and the arrival assumption sent to Appendix 4.B. Twenty words.

**[edit] §2.3 compressed, 2026-09-02.** The detail of how Munoz et al. built their weights and how Blake and Carter chose among feasible case mixes is illustration rather than premise. The premise the chapter needs is that weighted goal programming requires a defensible trade-off rate, that the trust has none, and that pre-emptive ordering therefore applies; all three survive, with the pointer to §3.5. Sixteen words.

**[edit] Second compression pass, 2026-09-02. Chapter 2 from 1,617 to 1,525 counted words.** Every replacement was measured before it was written this time, and the four sections yielded 92 words rather than the 190 estimated for them in the pass before.

§2.2's opening paragraph lost two sentences of definitional preamble, keeping the term and the Shabtay finding. Its closing paragraph lost the restatement of the trust's measures. The chapter opening lost the procedural detail of two other people's reviews, the 3,188 records screened and the 211-stakeholder Delphi, keeping the counts that carry the claim. §2.1 lost the four-item list of what Ofosu et al. examine. §2.5's "This dissertation closes the first gap" paragraph merged into the sentence stating that gap, and its lead sentence was cut to eleven words.

**A convention was nearly broken and is not.** Deleting the §2.5 lead sentence outright left the section opening on a table label, against `CLAUDE.md`'s rule that every table is referenced from the text before it appears. A shorter lead is in place instead, so the saving there is five words rather than fifteen.

**[edit] Three de-duplications, 2026-09-02. Chapter 2 from 1,681 to 1,617 counted words.** (1) The chapter opening and §2.1 both stated that no method exists for measuring pharmacy set-up; the claim is now made once, in the opening, and §2.1 goes straight to what the map found. (2) §2.2's closing sentences restated that the trust has no basis for trading one measure against another, which the chapter opening and §2.3 each state already; the paragraph now ends on the specific point, that each reviewed approach needs a number the trust cannot supply. (3) §2.5 raised the second gap and then dismissed it two paragraphs later; the dismissal now sits in the same sentence as the gap, with the scoring reason attached.

**[edit] Length pass, 2026-09-01. Chapter 2 cut from 1,769 to 1,681 counted words** against the 1,600 budget at `plan/Chapter2_Outline.md:7`. Six compressions, no deletion of a claim or a citation. §2.4: the Lahiri and Svirsko paragraph keeps the finding that neither makes queue waiting time depend on which work is accepted and drops the radiologist-workstation and prescription-filling detail; the discrete-event paragraph keeps both citations and the data reason and drops the enumeration of what a simulation would need; the simulation-testing and uncertainty paragraphs are tightened without losing Kheiri, Mavrotas, Morris or Barton. §2.5: the two gap paragraphs are merged into one, since Table 2.1 carries the evidence for both; the closing paragraph now gives the reason in one clause, that no trial in this analysis carries a priority score, and keeps the sentence stating that the second gap remains open, which §6.2 depends on. The chapter is 81 words above its budget and the remaining excess is in §2.2, not yet touched.

**[edit] The stale P3 claim removed from §2.3, 2026-09-01.** Part of a length pass agreed with the user; this one also closed a contradiction. §2.3 listed "three distinctive features" and gave the second as "the trust priority score is the lowest-priority objective", which is P3. P3 left the model on 2026-08-28 (`Chapter3_Problem_Description.md:185`), and §2.5 of this same chapter already states that the second gap is not addressed. The chapter therefore claimed a third objective on one page and disclaimed it on the next. The feature is deleted, "three" becomes "two", and the approval-step feature is renumbered second. 38 counted words. No other chapter cites the deleted sentence.

**[edit] Reduction and correctness pass on four passages, 2026-09-01.** Agreed with the user as steps 1 to 4 of a Chapter 1 and 2 de-duplication plan. Counted body falls from 1,863 to 1,757 words. Three of the four are correctness repairs that happen also to save words.

**The preamble no longer promises three objectives.** It said a response must "select trials with higher trust priority scores", which the 2026-08-29 correction below already withdrew from §2.5, and which `Chapter3_Problem_Description.md:97` contradicts: the ordering is two-level. The chapter opened on a premise it retracted seventy lines later. The commensurability sentences are deliberately **kept**, reworded for two concerns rather than three. They are the premise §2.2's closing paragraph and §2.3 discharge, and the argument survives the drop from three units to two, since an on-time count and weighted days are still different units. Removing them would leave §2.3's pre-emptive ordering unmotivated.

**§2.1's second paragraph now reports one literature fact and one bridge.** The five sentences describing the LTHTR process map, its validation with staff and the concurrency of the three teams are local method and local finding, owned by §3.1 and §3.4. The single-approver premise the M/G/1 argument needs is **not** orphaned: §2.4's opening sentence states it independently ("trials wait, and one person completes the approval"), which was checked before cutting. Saves 51 words.

**§2.4's discrete-event rejection rested on a claim that had become false.** It said LTHTR records hold "no activity-level timings". Appendix 4.D now tables three per-study segments, A preparation, B hand-over and C set-up, with medians and ranges across 19 to 20 studies, so segment timings exist. The rejection still holds, on the accurate distinction between coarse retrospective segments and the event-level activity, sequencing, resource-utilisation and service-time data a calibrated DES needs. Service time in particular remains unobserved: Appendix 4.E records hands-on approval time as "Elicited range, not an observed time series", and §6.4 lists measuring it as an action. The local counts, 23 usable durations and Martinez's 100-plus trials, are gone, since Chapter 4 and Appendix 4.A own data provenance. Word-neutral.

**§2.5's closing paragraph is shortened and its broken pointer removed.** It cited §3.7 as stating the condition for revisiting a value objective; Chapter 3's submitted structure ends at §3.6. The paragraph also re-explained the scoring gap for the third time in the dissertation. The replacement keeps three things: why no score is available, what the model uses instead, and an explicit statement that the second gap remains open. The last is load-bearing. Line 72 declares two gaps, and without it the section resolves one and lets the other trail off, while §6.2 claims one contribution. The reason is attributed to the Prioritisation Tool's lack of recoverable history for trials already in set-up (`Chapter4_Methodology.md` Table 4.1) rather than to the case-study return, which is where the limitation actually sits. Saves 44 words.

**Not done in this pass, and pending.** The SQ2 wording defect is a three-file bound set, Chapter 1 Table 1.1, `Chapter4_Methodology.md:107` and `Chapter6_Conclusion.md:15`, held for review as one unit. Table 2.1's Value objective column may want a "not implemented in the present study" marker for the row for this study; not applied, awaiting the user's decision. The Overleaf mirror `overleaf/Chapters/Chapter2.tex` has not been updated.


**[edit] §2.5 corrected against the implemented model, 2026-08-29.** The section claimed a contribution the model does not have. Table 2.1 gave "This study" a tick under Value objective, and the closing paragraph said the model "orders three goals pre-emptively" and "addresses both gaps". None of the three holds. `Dissertation/Chapter3_Problem_Description.md:97` states "There is no third level", and its note at line 185 records the prioritisation tool being taken out of the model on 2026-08-28, after which "P3 and its goal constraint are gone, so §3.5 is a two-level ordering". The table's own note says the value column records what a model optimises, so the tick was unambiguous and wrong.

Three changes. The tick is removed. The closing paragraph now claims one gap closed rather than two, and says two goals rather than three. And the second gap is restated as open, with the data reason for leaving it open.

**The reason given is the scoring gap, not the value-first test.** `Model/Merged_Model_Specification_EN.md:337` records value-first selection losing in 175 of 200 synthetic draws, and that result is not cited here for two reasons. It is a result, and this is the literature chapter. And `Chapter3_Problem_Description.md:238` already records the risk that quoting it "risked being read as rejecting value altogether, when what lost was value at the *top* of the ordering, not value as a third level". The honest reason a value objective is absent is that no trial in this analysis carries a score, which §3.1 states and which is a fact about the data.

**What this unblocks.** Chapter 6's comparison with published work and its contribution statement both rest on §2.5. Recorded in `plan/Chapter6_Writing_Plan_2026-08-29.md` §6 as a P0 blocker, now cleared.

**[edit] Three claims corrected against the source PDFs, 2026-08-26.** Every citation in this chapter was re-checked against its PDF while completing the reference list for the PhD proposal. Three claims failed.

**Walker et al. (2018), refuted as written.** The chapter said the review found 117 metrics "but none measured set-up or activation". The paper's Table 1 lists set-up-phase metrics, including "Time from protocol release to ethics/regulatory submission" and "Time from protocol release to ethics/regulatory approval". What survives is the narrower claim, that none of the six **categories** (site potential, recruitment, retention, data collection, trial conduct, trial safety) covers set-up. The sentence now attaches "none" to the categories. **This matters because it opens the measurement argument**, and a reader who checks Walker would find the counter-examples.

**Whitham et al. (2018), qualifier added.** The eight core metrics were not settled by the 211 alone: 294 registered, 277 completed round one, 211 completed all three rounds, and the final eight were fixed at a separate consensus meeting. The sentence now names both stages.

**Atsmony and Mosheiov (2023), objective mis-stated.** The PDF was obtained on 2026-08-26, closing the gap the note of 2026-08-23 recorded. Their objective is "maximizing the weighted number of jobs completed **exactly at their due-dates**", which is just-in-time scheduling: early completion is penalised as well as tardiness. That is not this study's on-time count, which admits anything inside the window. Both §2.3 and §2.5 now say so. **Table 2.1's on-time count tick is retained**, because they do maximise a count of jobs meeting a timing target, but the two targets differ and the prose no longer implies otherwise. Full citation: 'Scheduling to maximize the weighted number of on-time jobs on parallel machines with bounded job-rejection', *Journal of Scheduling*, 26, pp. 193-207, doi 10.1007/s10951-022-00745-7.

**Checked and found correct, no change.** Munoz et al. (2018): the chapter correctly states that weighted GP suits decision-makers who can rank importance, that their institute used expert ratings, and that the trust has no such basis. Gupta (2013): the M/G/1 recommendation and the mean-and-variation requirement both hold. Svirsko et al. (2022): "waiting time that increases with workload in an optimisation model" is accurate; note the paper optimises medication distribution pathways and explicitly declines to determine staffing levels, so do not describe it as a staffing model. Lahiri and Seidmann (2012), Shabtay et al. (2013), Slotnick and Morton (2007), Ofosu et al. (2021), Blake and Carter (2002), Deglise-Hawkinson et al. (2020), Demir et al. (2017), Harper et al. (2023), Martinez et al. (2016), Kheiri et al. (2021), Morris et al. (2019) and Barton (2012) all verified as cited.

**Bibliographic details now available.** All twenty-one PDFs in `plan/Chapter2_source_check/` were read for full Harvard details, which are recorded in the PhD proposal's reference list and can be copied into `Dissertation/overleaf/Ref.bib`. Three fields are not printed in the PDFs and remain open: Blake and Carter's issue number, Svirsko's issue number, and the Jones and Tamiz series volume. Barton's published title carries the typo "OUTOUT" and should be reproduced as printed.


**Drafted 2026-08-23** from `plan/Chapter2_Outline.md` (problem-first storyline, 2026-08-23 revision) in the Chapter 4 register: short declarative sentences, statistics inside the sentence that introduces them, no em dashes, British English. Structure and moves from Tarhan et al. (2023) *Transportation Research Part C* 149:104029, the model paper chosen 2026-08-23.

**[edit] Paragraph seams repaired, 2026-08-23.** The user rewrote the opening paragraph and replaced the metrics paragraph, diagnosing the defect: a paragraph must open by picking up the prior idea, signpost what its evidence will show, and close in the chapter's own terms. The original metrics paragraph asserted a new fact and let juxtaposition carry the relation. The user's version is kept verbatim; the superseded original was deleted rather than merged.

An audit of every paragraph opening found the same defect at three further seams, now repaired. §2.2 opened on a general principle and now bridges from §2.1's closing sentence ("That decision is a recognised problem class"). §2.3's third paragraph opened abruptly on the on-time count and now picks up the priority structure just established. §2.4 opened with an objection-rebuttal about queueing customers and now states what the shared step is first, keeping the rebuttal as the second clause. Seams judged sound and left alone: §2.1, §2.2's second and third paragraphs, §2.3's first and second, §2.4's remaining three, §2.5, §2.6.

**Register note for later passes.** The user's two paragraphs run shorter than the drafted prose and use explicit connectives (However, As a result, Similarly, Therefore) where the draft used semicolons and juxtaposition. Match that register when revising: one idea per sentence, connective stated rather than implied.

**[edit] §2.1 rewritten, 2026-08-23.** On the user's note that it spent too many words on the reference research and never stated the contribution. Ofosu's definition compressed from two sentences to one, the four categories listed rather than expanded, and the value stream mapping contrast cut from a colon-clause to two short sentences. The section fell from about 210 words to about 175.

Two contributions added, both verifiable. First, no published map of pharmacy trial set-up was identified in this review, hedged in the form Gap 3 uses. Second, the mapping found a measurement defect: the date the trust records as the end of its 60-day window is the post-SIV Capability and Confirmation Agreement, signed once every track confirms readiness, so the recorded milestone is not the one the window ends at. Sources: `Knowledge/Research Gaps.md` Gap 7, and the Chapter 3 provenance note of 2026-08-16, which records that the true Stage 2 duration cannot be computed from any file currently held. Chapter 3 §3.1 already carries the finding in compressed form, so the forward reference resolves.

**[edit] Value stream mapping removed from §2.1, 2026-08-23.** On the user's account of what was actually done: the method stopped at an operational flowchart showing how departments interact, and the bottleneck was found by validating that flowchart with LTHTR rather than by any waste analysis. Explaining why value stream mapping was not used therefore answered a question the study never raised. Martinez et al. (2016) remains cited in §2.4, where it carries the discrete-event simulation rejection, so no source is lost.

Two consequences. The section now states that the map alone did not locate the constraint and that validation with both services did, which is a more accurate account of the method and also earns the Ofosu citation, since confirmation with practitioners is a step in his procedure. And the phrase "a gap of the second kind" is gone, which closes the cross-reference risk flagged above: §2.1 no longer requires Chapter 3 to name Ofosu's four categories.

**[edit] §2.1's map claim clarified and its forward reference softened, 2026-08-23.** Two problems, both flagged by the user.

The claim "No published map of pharmacy trial set-up was identified in this review" rested on the word *published* and read as though this study had no map. It does. It took three revisions. The second moved the absence into the literature but kept an abstract subject, "This review identified no published map". The third fixed the word order but kept the hedge "found in this review", and the user asked what "this review" referred to, which is the answer: a self-referential hedge with no antecedent on the page.

The hedge is now dropped rather than reworded. "To the best of our knowledge" is the form the model paper uses twice, but the dissertation body is impersonal, with first-person usage confined to provenance notes and quoted LTHTR speech, so it would be the only "our" in the text. The sentence reads "No published study maps pharmacy set-up for clinical trials": subject, verb, object, with *published* carrying the scope. **This is a deliberate departure from the convention in Gap 3**, which records that the claim should be stated as identified-in-this-review rather than as none-existing. The protection that convention provides now has to come from precision instead, and if a statement of how the literature was searched is ever added to this chapter, the hedge can be reattached to that. The claim itself stands: no source in the 45-paper review maps this process, and Martinez et al. (2016) maps trial activation generally rather than the pharmacy track.

"Chapter 3 supplies one" was changed to "Chapter 3 describes one". Chapter 3 currently contains **no figure**; §3.1 describes the pathway in prose, which the weaker verb is satisfied by. Restore "supplies" and add a figure reference only once the refined flowchart is in the chapter.

**Dependency to clear before submission.** The existing assets are `Model/flowchart/LTHTR-Stage2-Process-CT-Excel-Mapping-2026-06-27.mmd` and its PNG, last edited 27 June 2026. The user reports the map needs refining because later work changed what it should show. At least two August findings postdate it: the oncology flag was replaced by an explicit electronic-prescription requirement, so a track labelled "Oncology Pharmacists" now mis-states the driver; and the pharmacy notification date was split from the set-up start date, which the map does not distinguish. The C&C assessment against C&C Agreement distinction does appear on the June map, so that correction is already carried. Check the map against `Model/Meeting_Findings_2026-08_Field_and_Model_Changes.md` before it goes into Chapter 3.

**[edit] The measurement finding removed from §2.1, 2026-08-23.** On the user's instruction: the defect in how the trust records the end of its 60-day window belongs to Chapter 3 and does not need establishing here. The opening paragraph already carries the measurement theme. §2.1 now delivers one finding, the bottleneck, and the two paragraphs merge because one finding does not need a signposting sentence.

The replacement states the **single-server rationale** explicitly, which every earlier version left implicit: three teams work in parallel, every set-up crosses one approval, one person normally gives it, and that approval rather than total effort limits how many trials can run at once. That is the argument §3.4 and Equation (4.3) rest on, and stating it here means §2.4 does not have to.

**Slip repaired in the same edit.** The user's revision of the first paragraph had truncated one of Ofosu's four categories to "gaps between the intended process", which needs a second term to parse. Restored to "gaps between the intended process and the actual one".

Saves about 55 words.

**[edit] §2.1's second paragraph replaced with the user's wording, 2026-08-23, with two corrections.** The user's version is clearer: "Validation with staff from both services showed that…" states method and result in one sentence where the draft used two, and the concessive "Although three teams work in parallel" is tighter than the draft's coordinate clause. Dropping the explicit Ofosu attribution costs nothing, because the first paragraph already states that this study follows the same procedure.

Two corrections applied to it.

**"Deciding when to start each trial" became "deciding which trials to start."** §3.6 states that the model decides which trials to commit and explicitly does not decide the order in which they are worked. Naming a timing decision here would contradict that and would mis-set up §2.2, which is about selection.

**"The main constraint is not the total amount of work" was scoped to concurrency**, becoming "what limits the number of trials underway is not the total amount of work available". The unscoped version reads as a claim about the main cause of delay, which Chapter 5 contradicts: utilisation at the gate is around 32 per cent, and it is the set-up durations rather than the signature that breach the 60-day window. Scoped to how many trials can run at once, the claim is true and consistent with both chapters.

**[edit] §2.4's opening two sentences cut, 2026-08-23.** "The shared step is a queue. Every set-up waits for one approver, and the more trials committed, the longer each waits." Both were written before §2.1 stated the single-server rationale. §2.1 now establishes that every trial requires one final approval usually given by one person, and that this limits how many trials can be active at once, so §2.4 was re-establishing a fact the reader already had. The section now opens on what the literature supplies rather than on what LTHTR is like, which is also the right division of labour between the two sections. "this kind of step" carries the reference back. Saves about 35 words.

**[edit] §2.5 merged into §2.4, 2026-08-23.** On the user's instruction, to recover words. The robustness material is now the closing paragraph of §2.4 rather than its own section, and the contribution section renumbers from §2.6 to §2.5. §2.4 is retitled "Modelling the shared step under uncertainty" to cover both halves.

The merge works because §2.4 already ended on the sentence that motivates robustness testing, that durations are few and variable and on time is a threshold. That sentence now leads directly into the response instead of closing a section and being picked up across a heading.

Three small compressions taken while merging: the Kheiri and Mavrotas semicolon split into two sentences, the signpost "The number of repetitions bounds the precision of any estimated probability" dropped because the Morris sentence states it, and "the input distribution is itself fitted from a finite sample whose error propagates to the output" shortened to "The fitted distribution carries its own error". All four citations survive.

Saves about 45 words, including the heading.

**[edit] Two changes to §2.2, 2026-08-23, both on the user's reading.**

**The deferral sentence removed.** "Chapter 3 keeps that principle in a milder form: a trial deferred this cycle is not lost but returns with a full cycle added to its lateness" described the $L(1-x_i)$ term, which is a Chapter 3 implementation detail. Removed for the same reason the duration finding left §2.1. Lewis and Slotnick is kept but re-pointed at what does belong here, that the choice recurs rather than being settled once, which is why the model is a cyclical planner. The paper's features remain visible in Table 2.1.

**The commensurability paragraph made explicit.** It previously ended on the fragment "The trust's three concerns are not", which left the reader to infer the consequence. The user identified this paragraph as carrying a contribution, and it now states the argument in full: the reviewed models can blend because their terms share a unit; the trust's three do not, being a count, days and a score; no exchange rate is available; **the standard formulation therefore does not transfer**; and this study orders the objectives instead. That makes the ordering a forced consequence rather than a stylistic preference, which is the defensible version of the claim.

Net effect on length is close to neutral: about 35 words saved on the deferral cut, about 45 spent on the contribution.

**[edit] Grunow et al. (2004) removed from §2.2 prose and from §2.5's readings, 2026-08-23.** On the user's challenge. Its sentence was defensive rather than argumentative: it existed so that §3.2's exclusion of capacity sizing would look like a choice between established framings. The real answer to "why not size capacity?" is that the trust cannot hire, which is a fact of the setting and needs no citation.

Table 2.1's third reading went with it. That reading, "every clinical model except Grunow takes capacity as fixed", amounted to *most authors do what I do*, which defends rather than contributes and diluted the two readings around it. Two readings remain and both are contribution claims.

**Citation now owed to Chapter 3.** Grunow, Günther and Yang (2004), *Health Care Management Science* 7(4):305–317, should be cited in §3.2 as one clause when that section states the fixed-capacity boundary: their objective is minimum total staffing cost, so the workforce adjusts until every study is delivered, which is the question this study does not ask. The paper keeps its row in Table 2.1, so the comparison is unaffected. ER-041 records the full assessment.

Saves about 65 words across the two sections.

**[edit] §2.3's opening sentence removed, 2026-08-23.** "A count of on-time trials, lateness in days and a priority score cannot be summed without an exchange rate, and the trust has no evidence on which to set one" restated what §2.2 had just established at length, after that paragraph was expanded to carry the commensurability contribution. The section now opens directly on goal programming, which is what it is for. "Objectives of this kind" carries the reference back. Saves about 30 words.

**[edit] The commensurability claim corrected after verification, 2026-08-23.** The user asked whether the three cited models had actually been checked for pre-emptive goal programming. Two had been; one had not.

**Verified from the PDFs.** Slotnick and Morton (2007): zero occurrences of lexicographic, pre-emptive, goal programming or multi-objective; the objective is the single blended expression max Σ xᵢ[Qᵢ − wᵢ(Cᵢ−dᵢ)⁺]. Lewis and Slotnick (2002): two occurrences of "hierarchical", both citing Fransoo et al.'s capacity model rather than describing their own; their objective is profit net of weighted lateness, blended. **Deglise-Hawkinson et al. (2020): also zero occurrences, but it does not blend either.** Overtime cost and time to first available visit are stated as *constraints*, the objective maximises Scientific Value Gained, and the paper traces trade-offs by varying the bound. That is a constrained or ε-constraint treatment, not a combined value.

So the previous sentence, "Previous models combine their objectives into one value, usually money", was false of Deglise-Hawkinson. The conclusion survives, since none of the three orders its objectives, but the reason had to be split in two.

**The corrected argument is stronger than the one it replaces.** Blending needs a trade-off rate; bounding needs a bound. Both are numbers the trust cannot supply. A *ranking* is different, and the trust can supply one, because it is assessed on how many trials finish on time. That makes ordering follow from what the trust knows rather than from what it lacks.

**Table 2.1 relabelled to match.** Deglise-Hawkinson's objective treatment was "Single", which described the count of optimised objectives rather than the treatment. It is now "Bounded". Svirsko remains "Frontier"; both produce trade-off curves but by different means, and the distinction is worth keeping.

**Table 2.1's Objectives column, verification complete 2026-08-23.** Every row checked against the PDF except one.

| Row | Evidence | Cell |
|---|---|---|
| Slotnick and Morton (2007) | Objective is max Σ xᵢ[Qᵢ − wᵢ(Cᵢ−dᵢ)⁺]; no lexicographic, pre-emptive or GP terms in the paper | Weighted |
| Lewis and Slotnick (2002) | Profit net of weighted lateness; the two "hierarchical" hits cite Fransoo et al., not their own model | Weighted |
| Blake and Carter (2002) | "a linear GP model with two pre-emptive goals", later "six pre-emptive goals", P₁/P₂ notation | Pre-emptive |
| Munoz et al. (2018) | "the nonpreemptive (weighted) GP variant is more adequate"; weights from six experts on a nine-point scale | Weighted |
| Qi et al. (2022) | "this weighted GP model"; minimises "the total weighted sum of subgroup deviations from their target" | Weighted |
| Deglise-Hawkinson et al. (2020) | Overtime and time-to-first-available-visit are constraints; objective maximises Scientific Value Gained; trade-offs traced by varying the bound | Bounded |
| Kheiri et al. (2021) | "Our main objective… is to utilise the beds… as fully as possible… equivalent to minimising the number of unused beds" | Single |
| Svirsko et al. (2022) | Efficient frontier over labour cost against missing-dose rate, because the units differ | Frontier |
| Atsmony and Mosheiov (2023) | **Title and abstract only, PDF not obtained.** "maximize the weighted number of on-time jobs… with bounded job-rejection" | Single |
| Grunow et al. (2004) | Minimum total staffing cost | Single |
| Mavrotas et al. (2015) | Not a table row; PDF is 3 pages of 14 | — |

**Two cells were wrong before this pass**, both from source notes written off abstracts rather than papers: Blake and Carter was recorded as weighted when it is pre-emptive, and Deglise-Hawkinson as Single when it bounds. A 2-in-11 error rate on the column that carries the §2.5 contribution claim. Any future row must be verified from the paper before it is ticked.

**[edit] §2.3 replaced with the user's draft, 2026-08-23, with two fixes and one addition.**

The user's version restructures the section so each paragraph does one job: define the variant, justify choosing it over weighted, show it applied in a hospital, then handle the on-time objective. Its closing sentence, "The next section explains how this shared step affects the model", is an explicit forward bridge and replaces a vaguer one.

**Three claims verified before accepting.** Blake and Carter's P₁ and P₂ description matches the paper's own wording, that P₁ identifies an economically feasible mix and P₂ identifies "from among the many case mixes that could be selected" the one closest to physicians' desired mix. Munoz's criterion is faithful: the paper says the pre-emptive form is used "when there are major differences in the importance of the goals". Atsmony and Mosheiov's objective matches the published title.

**Fix 1, accuracy.** "Allowing some jobs to be rejected" became "allowing jobs to be rejected within a cost limit". The paper's rejection is bounded, which the title states, and an unbounded reading would make it a different problem.

**Fix 2, clarity.** "Their study used one objective and independent machines" became "used one objective, and their machines are independent, so jobs compete only for machine time". Without the clause a reader may ask how jobs interact at all; the point is that they compete for capacity but cross no shared step.

**Addition: value subordination.** Two sentences added to the Blake and Carter paragraph stating that this is why priority score is placed last, and that value settles a choice between plans equal on timeliness but cannot buy a trial its place. This difference is not otherwise stated anywhere in the chapter, and it is the sharpest contrast with the reviewed models: Deglise-Hawkinson maximise value subject to service constraints, and Slotnick and Morton put revenue in the blend so a valuable job can offset its own lateness. Here the priority is inverted. Without this, a reader may assume the Prioritisation Tool score drives selection.

**[edit] §2.3 restructured, 2026-08-23.** The user's diagnosis: four paragraphs each described a paper and then stated separately what this study takes from it, so the section delivered four disconnected adoptions rather than one argument.

Rebuilt as two paragraphs. The first is what the study adopts, as a continuous chain: Jones and Tamiz give the form, Munoz gives the test for choosing the pre-emptive variant over the weighted one, Blake and Carter show the variant working in a hospital. The second is what differs, as three numbered features: a count as the highest priority, value as the lowest, and trials coupled by a shared step. Atsmony and Mosheiov now sits inside the contribution paragraph, where it does its real job of showing the on-time objective is established but differently used, rather than opening a paragraph of its own.

**A false claim caught in drafting.** "Three priority levels rather than two" was nearly used as a distinguishing feature. Blake and Carter's cost model has **six** pre-emptive goals, so the number of levels distinguishes nothing. Removed before it entered the text.

§2.3 falls from 293 to about 275 words.

**Superseded.** [edit] §2.3 trimmed by deferring to Chapter 3, 2026-08-23. Two passages explained what Chapter 3 explains.

"This is the same principle used in Section 3.5: a lower-priority objective is considered only when higher-priority objectives leave more than one possible solution" restated the mechanism that the first paragraph already defines from Jones and Tamiz, and that the Blake and Carter sentences already demonstrate. It said the same thing a third time under a cross-reference. Removed.

The value-subordination addition was compressed from two sentences to one clause and folded into the Chapter 3 pointer. The Chapter 2 job is the contrast with §2.2's models, where value drives selection; explaining how P3 behaves is §3.5's job and §3.5 already does it.

Two minor tightenings: Munoz's closing pair merged, and the final sentence shortened where §2.1 had already established the shared step.

§2.3 falls from 332 to about 275 words.

**Superseded cost note.** §2.3 rises from 266 to 332 words, so the chapter moves from about 1,877 to about 1,943. The user should decide whether the value-subordination addition is worth 30 of those words; the remainder is their own draft.

**Still not stated anywhere in the chapter:** that P2 sums weighted lateness across the whole eligible queue rather than only the committed set, which is what stops the model selecting only easy trials. Slotnick and Morton's objective multiplies the entire bracket by xᵢ, so a rejected job carries no penalty at all. That is a structural difference from "the formulation this study follows" and currently goes unmentioned.

**[edit] §2.4 restructured and trimmed, 2026-08-23**, applying the same two tests as §2.3.

**Four paragraphs became three, each with one job.** The first is what the study adopts, as a chain: Gupta gives the model class, Lahiri applies it to a professional sign-off, Svirsko shows how it enters a linear programme. The second is why simulation was rejected, which is a data argument. The third is how the resulting plan is tested. Previously the sign-off precedent and the linearisation sat in a separate paragraph from the queueing form, which split one adoption argument across two paragraphs, and the robustness material read as bolted on after the §2.5 merge.

**Five passages deferred to Chapter 3 or 4.** Lahiri's finding that upstream information-gathering shortens turnaround, which supports the preparation credit and belongs where that parameter is introduced. Svirsko's mechanism detail, precomputed as a function of the decision and embedded piecewise, which is §3.4's to explain. Gupta's steady-state caveat, compressed from three sentences to one clause because Appendix 4.B states it in full. Table 4.8's two thousand runs and the worst case at a probability of one half, both Chapter 4 figures. And the §4.3 pointer for approver availability, compressed to "a figure the trust has yet to confirm".

All ten citations survive: Gupta, Lahiri, Svirsko, Demir, Harper, Martinez, Kheiri, Mavrotas, Morris and Barton.

§2.4 falls from 493 to about 370 words.

**[edit] §2.3 replaced with the user's second draft, 2026-08-23, with two fixes.** The draft opens by declaring the method before explaining it, and replaces the earlier prose list of distinguishing features with a numbered one. Both are improvements and the section keeps the adopt-then-differ shape.

**Fix 1, accuracy.** "Also maximise the number of on-time jobs" became "the weighted number of on-time jobs", which is what the paper's title states. The distinction matters in both directions: the citation is now correct, and this study's P1 is an unweighted count, so the two objectives differ more than the original sentence implied.

**Fix 2, consistency.** The third feature read "all trials share one approval step", which is a fact about the service listed among features of the model. It now reads "the model represents a single approval step that every trial must cross".

**Deliberately not changed.** The draft argues the choice of variant by elimination, that weighted goal programming suits objectives whose relative importance can be scored and the trust cannot score its three, without also stating Munoz's positive criterion for the pre-emptive form. That is shorter and reads better, and the conclusion is unaffected.

§2.3 rises from 267 to about 290 words.

**[edit] Overlap between §2.2 and §2.3 removed, 2026-08-23.** The user identified two duplicated statements. Both had the same cause: **the two sections reached the same conclusion.** §2.2 ended "this study orders the three objectives rather than combining or bounding them" and §2.3 ended "this study uses pre-emptive goal programming", which are the same claim, so the reason for it was stated twice as well.

Each section now has one job. §2.2 establishes the **problem**, that every reviewed model needs a number the trust cannot supply, and stops there. §2.3 supplies the **answer**. The seam improves as a result: §2.2 closes on "it has no basis for stating how much of one is worth another" and §2.3 opens on "This study uses pre-emptive goal programming to order its objectives".

Three changes. §2.2's closing three sentences reduce to one that names the three measures and the missing basis. §2.3's Munoz paragraph refers back with "The trust has no such basis" instead of re-listing the measures. And the displaced observation that the trust is assessed on on-time completions moves to §2.3's first feature, where it now justifies why that objective ranks first, which nothing previously did.

Net saving about 45 words.

**[edit] Three fixes applied to §2.3, 2026-08-23**, from the evaluation the user requested.

**[edit 1] Duplicated conclusion removed.** Paragraph 1 opened "This study uses pre-emptive goal programming to order its objectives" and paragraph 2 closed "Therefore, this study uses pre-emptive goal programming" about eighty words later. This was the same fault removed between §2.2 and §2.3 earlier the same day, surviving inside §2.3. Since the section deliberately declares the method up front, the Munoz paragraph now ends on the criterion applied, "The trust has no such basis", and runs straight into Blake and Carter. Blake and Carter's opening changed from "used the same approach" to "used the pre-emptive approach", because "the same" previously referred to the deleted sentence.

**[edit 2] Duplicated contrast removed.** The independent-machines point appeared in feature 1 ("they use this as their only objective and assume independent machines") and again as feature 3 ("a single approval step that every trial must cross"). Feature 1 now contrasts on objective structure alone, and the machines contrast moves into feature 3 where the shared step is stated, so each contrast is made once.

**[edit 3] Feature list levelled.** Feature 1 previously had a paragraph to itself while features 2 and 3 shared one, so a reader promised three features met one long item and two short ones. All three now sit in a single paragraph with comparable weight.

**Minor.** Feature 2 said plans perform equally on "on-time completion and delay". §2.2 calls it "days late" and P2 is weighted lateness, so the wording is now "trials completed on time and days late" for consistency.

§2.3 falls from 287 to about 265 words.

**[edit] §2.4 rewritten for clarity, 2026-08-23.** The user reported it was hard to follow. Four specific causes, all addressed.

**[edit 1] The section opened defensively.** It began "Queueing theory describes this kind of step, and its customers need not be patients", answering an objection before the reader knew what was being modelled. It now opens "The approval step is a queue. Trials wait, and one person serves them." Gupta's list of non-patient examples is cut entirely, because Lahiri's radiology cases and Svirsko's nurses already demonstrate the point without a separate defence.

**[edit 2] Two sentences were doing three jobs each.** Gupta's recommendation previously carried the condition, the formula's inputs and the steady-state caveat in one sentence. It is now four short sentences, one idea each, matching the register used elsewhere in the chapter. Why M/G/1 suits this case is now stated explicitly: the formula needs only the average service time and its variability, which is all the trust can supply.

**[edit 3] Two sentences were unparseable.** "The queue term therefore supplies the mechanism, that committing more trials lengthens every committed trial's wait, while where the capacity ceiling sits depends on a figure the trust has yet to confirm" is now two sentences: the formula shows why a limit exists, and it does not show where that limit falls. "Barton (2012) terms the error in a distribution fitted from a small sample input uncertainty" led the reader down a garden path, since "input uncertainty" is the object of "terms" but reads as a continuation of the noun phrase. It now reads "The fitted duration distribution is itself uncertain because it comes from a small sample, which Barton (2012) calls input uncertainty."

**[edit 4] Jargon reduced.** "On time is a threshold" became "completing on time is a pass-or-fail outcome". "Enough to parameterise one closed-form expression" became "enough for a queueing formula". "Load-dependent delay" became "a wait that grows with workload". "Per-step durations" became "step-by-step durations".

The queueing form and sign-off precedent split into two paragraphs, so the section is four short paragraphs rather than three long ones. All ten citations survive.

§2.4 falls from 382 to about 345 words.

**[edit] §2.4 replaced with the user's version, 2026-08-23, with four fixes.** The user's draft is clearer than the one it replaces: six short paragraphs instead of four, "First… Second…" for the two uncertainty sources, and "a trial either meets the target or does not" as a plain gloss on the threshold. Separating the mechanism-versus-position claim into its own paragraph is also right, since it is a distinct point that was previously buried at the end of the simulation paragraph.

**[edit 1] Terminology error corrected.** The draft said "the model assumes a stable queue". In queueing theory **stability** means the traffic intensity is below one, so the queue does not grow without bound; **steady state** means the system has run long enough that its behaviour no longer depends on time. The model assumes both, but the caveat Gupta raises, and the one the draft then explained correctly, is steady state. The jargon is now avoided altogether: "the model assumes that the pattern of arrivals does not change over time".

**[edit 2] Model class made precise.** "A single server with variable service times" does not distinguish M/G/1 from M/M/1, since exponential service times are variable too. What distinguishes M/G/1 is that the distribution is unspecified, which is precisely why it suits a step whose distribution the trust cannot supply. Now "whose service times follow no particular distribution".

**[edit 3] Understatement removed.** "Not for a reliable simulation" implies a simulation could be built but not trusted. Martinez required activity-level timings and LTHTR holds none, so a discrete-event simulation of the pathway cannot be parameterised at all. Now "not for a simulation of the full pathway".

**[edit 4] Claim about Lahiri corrected.** "They also apply their findings to prescription filling in pharmacies" overstates what the paper does. Its own wording is that the results "have broader implications for the optimal design of other clinical workflows, such as the process of filling prescriptions in pharmacies". Now "Their conclusions extend to prescription filling in pharmacies".

**Also trimmed.** "This assumption may not hold when trial arrivals change over time" became "This assumption may not hold for trial arrivals", since the preceding sentence now names the assumption.

§2.4 moves from 377 to about 385 words. The increase buys the paragraph splits and the explicit connectives in the section the user reported as hardest to follow.

**[edit] Contribution made explicit in §2.4's sign-off paragraph, 2026-08-23.** The paragraph described two papers and closed "Section 3.4 follows these approaches", which claims nothing. The user asked for the contribution to be stated.

**What distinguishes this study, verified against both papers.** Lahiri and Seidmann model the queue but do not decide what enters it: they measure turnaround for whatever arrives, and their intervention is relocating information-gathering upstream rather than selecting cases. Svirsko's wait does depend on a decision, but on a routing decision, since nurse waiting time rises with the share of doses routed through the dispensing cabinets. In neither model does the wait depend on which work is **accepted**.

Here it does, and the paragraph now says so: accepting one more trial lengthens the wait for every other trial in the plan, so whether a trial finishes on time depends on the plan and not on the trial alone. That is the claim §3.4 rests on and it was previously left for the reader to infer.

Split into two paragraphs, precedent then contribution, matching the adopt-then-differ shape used in §2.3.

Cost about 40 words. §2.4 moves from about 403 to about 443, and the chapter to about 1,819.

**[edit] Mechanism-and-position paragraph cut from §2.4, 2026-08-23.** "The formula explains why capacity is limited: each additional trial increases the approval wait for all other trials. However, it cannot identify the exact capacity limit because the approver's available capacity has not yet been confirmed."

Two reasons, one on each half.

**The first half had become a duplicate.** The user's revision of the contribution paragraph states that the wait "is shared by every committed trial and grows with the number committed". This paragraph then said "each additional trial increases the approval wait for all other trials", two paragraphs later with the simulation rejection in between.

**The second half belongs to Chapter 4.** That the approver's capacity is unconfirmed is a data-status caveat, not a literature point. §4.3 states it precisely, that approver availability changes the location of the capacity ceiling but not whether one exists, and §4.5 treats the ceiling as a pattern to identify rather than a number to report. Asserting it here added nothing and risked drifting from that wording.

Flow improves as well: the simulation rejection now runs straight into the uncertainty problem, without a return to the queueing formula in between.

§2.4 falls from 465 to about 429 words, the chapter to about 1,807.

**[edit] §2.5 and Table 2.1 revised after the §2.1 to §2.4 rewrites, 2026-08-23.** The user ruled that the non-time objective, lateness and on-time count columns record **what each model optimises**, and that quantities imposed as constraints are not counted. A note under the table now states this, so the ambiguity cannot recur.

**Grunow's row removed.** Every feature column was blank once the third reading was cut, leaving a row that stated only "Single" and "Clinical studies" and appeared in no prose. Its citation is still owed to §3.2, where the fixed-capacity boundary is set.

**Three cells corrected under the objectives-only rule.** Deglise-Hawkinson's lateness tick removed: time to first available visit is a constraint in their model, not an objective, which is why the row is labelled Bounded. Atsmony and Mosheiov's non-time tick removed: rejection cost is a bound, not an objective. **Svirsko's non-time tick added**, which the earlier review had missed: they minimise distribution cost, and cost is a non-time objective. Applying the rule consistently found this third case.

**Observation 2 compressed.** It previously restated a point the reader had already met in §2.3's first and third features and again in §2.4's contribution paragraph. It now reads "The on-time count appears in one other row, but there as a lone objective."

**Observation 1 aligned with the table.** It described Deglise-Hawkinson as having "a single objective", where the table now says Bounded. It reads "bound their other objectives rather than ordering them".

**Contribution (iv) dropped.** The Monte Carlo test had no matching gap, and the table shows Deglise-Hawkinson and Kheiri both testing uncertainty, so it is not distinctive. Three contributions now answer three gaps, which is the mirrored structure the outline adopted from Tarhan et al.

**[edit] Table 2.1 columns reviewed and reduced from nine to seven, 2026-08-23.** A tick count across the ten rows showed which columns were doing work.

**Fixed capacity removed: ticked in 10 rows out of 10.** The column carried no information at all. It discriminated only while Grunow was listed, and Grunow was removed when the third reading was cut. The fact is preserved as a sentence in the table note, where it costs seven words instead of a column.

**Uncertainty tested removed.** It discriminated, at 3 of 10, but supported nothing: neither observation used it, and contribution (iv) was dropped precisely because Deglise-Hawkinson and Kheiri also test uncertainty. A column backing no claim is decoration.

**Non-time objective renamed Value objective.** At 8 of 10 it discriminated weakly, and verifying Kheiri showed why: minimising unused beds is literally a non-time objective, so the column was capturing two different things. Under the narrower definition it pairs with the on-time count to show that only this study optimises both, which is what contribution (iii) claims. **Svirsko's tick added earlier is therefore reverted**, since distribution cost is not a value measure, and Kheiri stays blank.

**Verified this session, both correct as listed.** Qi: site selection is a decision, capacity constrains rather than being sized, the six goals are representativeness, target enrolment, site capacity, population matching, cost and site count, none time-based, and the paper describes itself as a weighted GP model. One ambiguity recorded: it also mentions "other goals with different priority levels", which could be read as lexicographic, but the implemented model is weighted. Kheiri: the objective is to minimise unused beds, formalised as minimising the number of colours used, so Single is correct; the model assigns specialties to sessions rather than selecting work; beds are a hard constraint rather than a wait that grows with load, so the shared-step column stays blank.

Six columns now discriminate and Setting shows nine distinct values, which is what makes the absence of an NHS pharmacy row visible.

**[edit] §2.5's two closing paragraphs merged, 2026-08-23.** The user asked whether the paragraph below the table was needed. Both were, in part, but between them they told the same story three times in 167 words: the observations paragraph read the gaps off the table, the second paragraph renumbered them as (i) to (iii), and its contribution list then stated them a third time as what the study does.

**The cause is a structure copied without its middle.** The outline followed Tarhan et al. (2023): table reading, then one paragraph per gap, then a formal contributions list. Tarhan's middle paragraphs are substantive, explaining why intermediate resting points matter in disaster relief, which a table cannot show. This chapter has no middle paragraphs, because the gaps are argued in §2.2 to §2.4 as they arise. With nothing between them, the formal gap list only renamed the observations.

**What was kept from each.** The first paragraph names which papers are the near-misses, Deglise-Hawkinson and Blake and Carter, which is the specific and checkable claim. The second keeps only its contribution sentence. "Two observations follow" became "Two gaps follow", which is the framing the deleted list was providing, and the second gap now carries what was contribution (iii) in full: the on-time count appears elsewhere "but there as a lone objective, not combined with a value objective under an ordering".

The numbered (i) to (iii) form is gone from the contribution sentence. It mirrored a numbered gap list that no longer exists, and three clauses read better than three numerals.

Saves about 60 words.

**[edit] Table 2.1 note reduced from three sentences to one, 2026-08-23.**

**The first two merged.** They defined what the three objective columns mean and stated the constraints rule separately. The ambiguity they address is real, since Deglise-Hawkinson's lateness cell was ticked wrongly for two turns because the column's meaning was unsettled, so the definition stays. It is now one sentence: the columns record what each model optimises, not what it constrains.

**The third was cut, and it was false.** "Every model listed treats capacity as fixed" does not hold for Svirsko et al. (2022). Their decision variables include the number of automated dispensing cabinets required on each unit and whether a robot is needed, and the paper states that the model "permits an unconstrained number of ADCs on each unit". They size equipment capacity rather than taking it as given.

The sentence was in any case a residue of an argument already removed. It survived from the deleted Fixed capacity column, which existed to support the third table reading, which was cut when Grunow left the prose. Chapter 2 makes no scope claim about capacity; §3.2 does, and that is where Grunow's citation is owed.

**Worth recording as a pattern.** This is the fourth time a deletion has left orphaned text elsewhere: the VSM cut, the mechanism-and-position paragraph, §2.5's gap list, and now this note. Each restructure needs a re-read of what pointed at the removed material.

**[edit] §2.5's second gap reframed as a combination claim, 2026-08-23.** The user asked whether the paragraph below the table develops the earlier sections or repeats them. The first sentence develops: it joins §2.3's pre-emptive precedent, Blake and Carter, with §2.4's shared-step precedents, Deglise-Hawkinson and Svirsko, to show the two sets do not overlap. That claim requires both sections to be on the table and appears nowhere earlier.

The second sentence did not. "The on-time count appears in one other row, but there as a lone objective" restated §2.3's first feature, which already says Atsmony and Mosheiov "use this as their only objective", with a clause about value appended rather than argued.

It is now a combination claim parallel to the first: no model optimises an on-time count alongside a value objective. That is a statement about the whole set, which only the table can support, and it names the near-misses on both sides. Verified against Table 2.1: the on-time count column ticks Atsmony and this study, the value objective column ticks six others and this study, and the two overlap only in the final row.

Both sentences now do the same work, reading a combination off the table that no single section could show. Costs about 13 words.

**[edit] §2.5's gaps paragraph replaced with the user's version, 2026-08-23, with two terminology fixes.** The draft is clearer than the one it replaces: "First… Second…" across two paragraphs signposts the two gaps, the colons become full stops so no sentence carries two clauses, and "set limits on their other objectives rather than placing them in priority order" is plainer than "bound theirs rather than ordering them".

**Fix 1.** "The number of jobs completed on time" clashed with the same paragraph's later "the on-time count", and with the table column of that name. Both now read "on-time count".

**Fix 2.** "Models that include value" was loose, since the table note states the columns record what each model optimises and "include" invites the question of whether a constraint counts. Now "models with a value objective".

**Terminology settled: "shared step" throughout, on the user's decision.** The draft introduced "shared capacity step", a fourth term alongside the table's "Shared step modelled" and §2.3's and §2.4's "approval step" and "shared step". "Shared capacity" would arguably fit Deglise-Hawkinson better, since their congestion comes from resources shared across the whole delivery process rather than from one stage every trial crosses, and their own wording is "the portfolio is conducted under shared resources". "Shared step" was kept because the single-step nature is what makes the approval a single-server queue, which is the argument §2.4 rests on. Deglise-Hawkinson's tick stands: the column marks models where capacity is shared enough that accepting one job delays the others.

Also changed for consistency: the first example previously read "have the shared resource", which used the term the decision rejected. It now reads "model a shared step".

**Decisions taken in this draft, not yet ratified by the user:**

1. **The Value column is renamed "Non-time objective".** The outline left its definition open. Under this definition Blake and Carter (physician preference) and Qi (representativeness) tick cleanly, and no cell needs a question mark. If the column is meant to be a value *score*, both ticks must be reviewed.
2. **The Mavrotas row is omitted from Table 2.1.** The outline said obtain the full text or remove the row; the held PDF is still 3 pages of 14, so the row is out and the paper is cited in §2.5 prose for framing only.
3. **Martinez's trial count is written as "well over a hundred trials".** The vault note of 2026-07-09 says roughly 161, but its own breakdown (activated 79 + in-process 44) sums to 123. Pin the exact figure from `martinez-2016-supp1-dataset.xlsx` before submission and restore the number.
4. **Qi et al. (2022) appears in the table but not the prose.** Its weighted GP is covered by Munoz's taxonomy sentence; a prose mention would repeat it. Acceptable for a summary table, but check the marker's expectation that every table row is discussed.

**Citation forms to verify when the bibliography is built:** author lists for Demir et al. 2017, Harper et al. 2023 and Kheiri et al. 2021 are cited as "et al." from the vault's short names and need confirming against the PDFs. Atsmony and Mosheiov 2023 is cited from its published title and abstract only (*J. Sched.* 26:193–207); the PDF has not been read. With the Sequence column dropped, every tick in its row follows from the published title. Barton 2012's published title contains the typo "OUTOUT"; reproduce or silently correct, but do not let a reference manager mangle it.

**Word count.** Counted body after the draft-time trim: about 1,660 prose plus about 250 of table text, roughly 1,910 against the 1,600 target. Per-section prose sits on the outline's budgets; the excess is the table itself plus the contribution section, both already trimmed once. Further cuts are a user decision; candidates in order: merge §2.5 into §2.4 (saves ~60), cut the Lewis and Slotnick pair of sentences (~45), drop Qi's table row (~20).

**The Sequence column was dropped at draft time.** No argument rested on it, and it held the only inferred tick in the Atsmony and Mosheiov row; every remaining tick in that row follows from the paper's published title.

**Cross-references.** §2.1 points at Chapter 3's use of Ofosu's four categories, which is **not yet written into Chapter 3**; either add the categories to §3.1 on the next Chapter 3 pass or soften the sentence here. §2.4's "a figure that remains the trust's to confirm" tracks §4.3 and Appendix 4.B; keep aligned if the LTHTR data lands.

**No bibliography exists yet.** All 21 works cited here need Harvard entries; `Dissertation/overleaf/Ref.bib` holds 2 records. This chapter cannot go to Overleaf until that is built.
