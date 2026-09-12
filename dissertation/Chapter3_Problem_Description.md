# 3. Problem Description

**Draft status.** First draft, 2026-07-27. Counted body is §§3.1–3.6; Appendix 3.A and the provenance notes do not count towards the dissertation word limit.
## 3.1 The problem in practice

From 2024 to 2026, only 3 of 24 trials met the 60-day window on the available C&C Agreement proxy measure; the median interval was 144 days. Pharmacy completed review within 60 days in 2 of 23 trials with usable pharmacy data.

Volume alone does not explain this. LTHTR typically brings 12–15 CTIMPs into set-up each year, counting non-commercial trials because they draw on the same teams even though only commercial ones fall under the target. The clinical trials team’s service-level agreement allows two commercial trials a month, or about 24 annually. This suggests that its capacity is not fully used.

The specialist units have no agreed capacity. Around 60% of open trials require aseptic work and therefore queue for the same small unit, which must operate below 80% utilisation under its manufacturing licence. Oncology prefers to handle one trial at a time and slows when several run concurrently. These limits do not mean that work is refused: clinical trials account for only about 2% of Aseptic Services’ weekly workload. However, the trust has not measured how many trials either unit can manage concurrently. Progress therefore depends on when the relevant team reaches a trial, rather than on whether it has overall capacity.

No formal rule allocates this scarce team time. Trials are generally taken in arrival order. Pharmacy may expedite a study it considers important outside the usual review timeline, but these decisions are informal and unrecorded. Consequently, a trial’s completion date depends partly on the work that arrived before it, rather than solely on its own requirements. The model does not assign trials a value score or exclude them on perceived importance. All trials within scope are therefore treated as equally worthwhile; the decision is which trials can be committed while maximising on-time completion and then minimising weighted lateness.

Two linked decisions are therefore made without a supporting method. The first is which waiting trials pharmacy starts. The second is the order in which the teams complete the work once it has started. Neither decision is recorded or reviewed, although together they shape whether pharmacy completes work within its 60-day target.

## 3.2 Scope and boundaries

The exclusions in §1.3 apply throughout, but for different reasons. Capacity is fixed: the model asks what existing staff can achieve, rather than how many staff each team should have.

Clinical site set-up is not modelled. This work, undertaken by the research delivery team, includes activities such as staff training and site initiation and is separate from the pharmacy clinical trials function modelled here. The trust records neither its start nor end date, so its duration cannot be estimated from the available data.

`[edit]` Governance is also excluded. The tracker shows when governance finished but not when it started, so its length cannot be worked out, and governance committees impose fixed calendar delays rather than claims on pharmacy capacity: they may block completion but do not alter the pharmacy effort a trial requires. Committee requirements are therefore recorded outside the optimisation model.

## 3.3 Sets, parameters and variables

`[edit]` Let $i \in I$ denote a trial waiting for set-up and $E$ the eligible queue, the trials in $I$ falling inside the scope of §3.2. Appendix 3.A tabulates every symbol.

`[edit]` Each trial follows one of four set-up pathways, fixed by whether it needs sterile preparation and whether an electronic prescription must be built. The pathway sets the trial's set-up duration $p_i$ in days, and records what a trial requires rather than which team supplies it.

The 60-day window is fixed by the 150-day Stage 2 definition. It opens on the later of regulatory approval and site selection, and the site must be confirmed before it closes, so trial $i$ carries a due day:

$$due_i = \max(\mathrm{approval}_i, \mathrm{selection}_i) + G, \qquad G = 60 \tag{3.1}$$

`[edit]` Against a planning date, $\delta_i$ is the days remaining to $due_i$, negative once the due day has passed.


$$w_i = 1 + a_i / D, \qquad D = 365 \tag{3.2}$$

A trial waiting a year is twice as expensive to defer as one that has just arrived. This is what stops slow trials being starved by faster ones.

`[edit]` Two decision variables carry the plan: $x_i = 1$ if trial $i$ is committed this cycle and $0$ if deferred, and $d^+_i \ge 0$ records the days by which it finishes past its due day, with a binary $\mathrm{onTime}_i$ marking a committed trial that still lands inside the window.

## 3.4 The approval queue

Final approval is represented as a shared, load-dependent single-server queue. This is a conservative approximation of a process normally centred on one lead approver: delegation can shorten, but not increase, the modelled delay. Let $g_n$ denote the expected approval delay when 
 $n$ trials are committed.

`[edit]` On-time performance is a property of the plan, not of an individual trial: approval delay depends on how many trials are committed, so the same trial may be feasible in a smaller plan and late in a larger one. A trial meets its deadline only when its set-up duration and the approval delay together fit inside its remaining time, and whether they do cannot be assessed until the plan is chosen.

The formulation represents the number of trials committed by the plan explicitly. Let $z_n = 1$ if the plan commits exactly $n$ trials and $0$ otherwise:

$$\sum_n z_n = 1, \qquad \sum_{i \in E} x_i = \sum_n n\, z_n, \qquad \sum_{i \in E} x_i \le c \tag{3.3}$$

`[edit]` Here $c$ is the maximum number of trials the service may commit in one cycle, so the constraints select one plan size, equate it to the number committed, and cap that number.

Let $r_{in} = 1$ if trial $i$ would finish inside its window when $n$ trials are committed, that is if $p_i + g_n \le \delta_i$. A trial counts as on time only when it is selected and can meet its deadline at the chosen plan size:

$$\mathrm{onTime}_i \le x_i, \qquad \mathrm{onTime}_i \le \sum_n r_{in}\, z_n \tag{3.4}$$

## 3.5 The selection model

`[edit]` **The model is a pre-emptive goal programme.** Two goals are stated in strict priority order, and a lower priority is optimised only within the value already fixed above it, because the trust has no basis for an exchange rate between them. A deferred trial receives a further planning cycle of lateness, so deferral cannot remove it from consideration, and weighted lateness is summed across the whole eligible queue rather than the committed trials alone, which prevents the model from improving its result by selecting only easy cases. Appendix 3.A gives the goal-programming notation, the equivalence between minimising $n_1^-$ and maximising the on-time count, and a worked instance.

**The order is on-time completion first, then lateness.** The second is used only to separate plans that tie on the first. Lateness is set out below because both goals are written against it, but it is the lower of the two.

**The lateness measure.** It is written as a goal rather than measured after a plan is chosen, so that deferring a trial carries an explicit cost. A committed trial finishes late by its set-up duration and queue wait, less its remaining time; a deferred trial waits a further planning cycle of $L$ days:

$$d^+_i \;\ge\; (p_i - \delta_i) + \sum_n g_n z_n + L\,(1 - x_i), \qquad d^+_i \ge 0 \tag{3.5}$$


**The other goal is on-time completion.** Its target is that every eligible trial finishes inside its window, and it carries an under-achievement:

$$\sum_{i \in E} \mathrm{onTime}_i + n_1^- = |E|, \qquad n_1^- \ge 0 \tag{3.6}$$


**The two deviations are then minimised lexicographically:**

$$\text{Lex min}\;\left\{\; \underbrace{n_1^-}_{\text{P1}},\;\; \underbrace{\sum_{i \in E} w_i\, d^+_i}_{\text{P2}} \;\right\} \tag{3.7}$$

`[edit]` **P1 is the measure the trust is assessed on**, the number of trials completed on time; **P2 separates plans achieving the same P1**, and because it sums weighted lateness across the whole eligible queue it selects the plan leaving the least weighted lateness behind.


## 3.6 What the model does not decide

The model decides which trials to commit in a cycle. It does not decide the order in which those trials are worked, or which team handles each trial on a given day. It commits a set and reports what that set achieves. Ordering is handled through the queue wait $g_n$: the model represents the congestion that a detailed schedule would otherwise resolve, which keeps the problem linear and avoids per-team timings the trust does not record.


---

## Appendix 3.A: Notation and worked instance

*(Appendix material does not count towards the word limit.)*

### A.1 Notation

| Symbol | Meaning | Units |
|---|---|---|
| $i \in I$, $E$ | Trial awaiting pharmacy set-up; the eligible queue | n/a |
| $G$, $due_i$ | Set-up goal (60), due day $\max(\mathrm{approval}_i, \mathrm{selection}_i) + G$ | days |
| $p_i$ | Set-up duration of trial $i$, from its pathway | days |
| $\delta_i$ | Days remaining to $due_i$ at the planning date, negative once breached | days |
| $a_i$, $D$ | Days trial $i$ has waited; weight divisor (365) | days |
| $w_i$ | Claim weight, $1 + a_i / D$ | dimensionless |
| $c$ | Set-ups the service can commit in a cycle | trials |
| $L$ | Planning cycle length (30) | days |
| $g_n$ | Expected approval wait when $n$ trials are committed | days |
| $r_{in}$ | 1 if trial $i$ finishes inside its window at committed count $n$ | binary |
| $x_i$ | 1 if trial $i$ is committed | binary |
| $z_n$ | 1 if the plan commits exactly $n$ trials | binary |
| $\mathrm{onTime}_i$ | 1 if trial $i$ is committed and lands inside its window | binary |
| $d^+_i$ | Days by which trial $i$ finishes past $due_i$ | days |

### A.2 The goal-programming detail behind §3.5

`[edit]` The lateness target is zero days. Only the over-deviation appears in equation (3.5) because early completion earns no reward, so the under-deviation would be zero in every optimal solution; writing the constraint as an inequality lets the objective drive $d^+_i$ down to the overrun itself. The on-time target of equation (3.6), that every eligible trial finishes inside its window, is not expected to be met: a goal states what the service would achieve without constraint, and the size of the shortfall $n_1^-$ is the result the model reports. Because $|E|$ is a constant, minimising $n_1^-$ is equivalent to maximising the on-time count directly; it is written as a goal for consistency with the priority structure. The ordering still discriminates when every trial has already breached its window, since P1 is then equal for any plan of a given size and P2 decides, because lateness in days still varies.

### A.3 Worked instance: why on-time is a property of the plan

<!-- [edit] 2026-08-13: rebuilt against the implemented model. Waits computed with Experiments/optimiser/gate.py at default settings. -->
This instance shows the mechanism §3.4 describes: the same trial can finish inside its window in a small plan and outside it in a large one, so committing more trials can leave fewer of them on time.

**Durations here are illustrative, at 36 days.** The measured durations cannot be used for this purpose. Pooled across the tracker they run to about 95 days against a 60-day window, which puts every trial outside the target whatever the plan, and removes the question the instance is meant to show. The distinction the instance makes is therefore about the model's behaviour, not about LTHTR's current position.

The expected approval wait, computed at the model's default settings, rises slowly and then sharply:

| Committed count $n$ | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|
| Wait $g_n$, days | 0.20 | 0.46 | 0.79 | 1.25 | 1.91 | 2.96 | 4.86 | 9.39 | 32.32 |

Four trials from the eligible queue, each needing 36 days of set-up, differ only in how much of their window remains:

| Trial | Days remaining $\delta_i$ | Slack over the 36-day set-up |
|---|---|---|
| A | 50 | 14.0 |
| B | 44 | 8.0 |
| C | 38 | 2.0 |
| D | 12 | none, already short |

A trial finishes inside its window when $\delta_i \ge p_i + g_n$. Applying that at each plan size gives the rescue matrix $r_{in}$ the model reads:

| Plan size $n$ | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|
| A rescueable | yes | yes | yes | yes | yes | yes | yes | yes | no |
| B rescueable | yes | yes | yes | yes | yes | yes | yes | no | no |
| C rescueable | yes | yes | yes | yes | yes | no | no | no | no |
| D rescueable | no | no | no | no | no | no | no | no | no |

Three things follow, and each answers something the chapter asserts.

**Rescueability is not a property of the trial.** C survives at five committed and fails at six. Nothing about C changed; the queue it joined grew. This is why the model cannot decide trial by trial before the plan is chosen, and why the load selector $z_n$ of equation (3.3) exists.

**Raising the commitment limit eventually makes performance worse.** Counting trials on time as the plan grows gives three at five committed, two at six and seven, one at eight, and none at nine. The on-time count peaks and then falls, because past the peak the queue costs more days than the tightest rescueable trial has left. That is the answer SQ2 asks for, and it is why "take every slot you can get" is the wrong reading of a capacity case.

**A trial can be beyond help.** D has 12 days against a 36-day set-up and is outside its window at every plan size. It contributes nothing to P1 whatever the model does, which is why P2 exists: deferring D still lets its lateness grow, so the model is not free to ignore it.

Trial labels here are illustrative. The waits are computed from Experiments/optimiser/gate.py at default settings; the durations and remaining days are chosen to make the mechanism visible.

## Source and provenance notes (not part of the submitted text)

**[edit] First substantive pass on Chapter 3, 2026-09-02. From 1,637 to 1,438 counted words.** Every equation stays: (3.1) to (3.7) are untouched, as are §3.6 and the exclusions of §3.2.

**§3.3 was defining twice what Appendix 3.A already tabulates.** Table A.1 carries all seventeen symbols with meaning and unit, so the body now names $E$, the pathway that sets $p_i$, $\delta_i$ and the three decision quantities, and points to the table. The pathway paragraph keeps the boundary sentence that a pathway records what a trial requires rather than which team supplies it, because §3.6 depends on the model having no per-team assignment.

**§3.4's rescueability paragraph was compressed around its core sentence**, which is kept verbatim: on-time performance is a property of the plan, not of an individual trial, because approval delay depends on how many trials are committed. The paragraph is the bridge between the operational problem, the approval queue and the $z_n$ and $r_{in}$ formulation, so it was shortened rather than moved.

**§3.5's technical detail moved to a new Appendix 3.A.2.** What moved is derivation: why the under-deviation is zero at the optimum, the equivalence between minimising $n_1^-$ and maximising the on-time count, that the target is not expected to be met, and that P2 still discriminates once every trial has breached. What stays is the reasoning a marker needs to accept the formulation: the strict priority order and why the trust has no exchange rate, the deferred-cycle penalty, and weighted lateness summed across the whole eligible queue rather than the committed trials alone. §3.5 is 322 words including its three equations. **It was deliberately not compressed to the 120 to 160 words considered earlier**, on the user's judgement that the objective-function rationale is what Criterion 3 scores and is worth more than the word economy. The former A.2 worked instance is now A.3.

**[edit] Two de-duplication cuts, 2026-09-01.** Length pass agreed with the user. (1) The closing paragraph of §3.6 was deleted: it stated only that the formulation abstracts operational features and pointed to §4.4 and §6.3, both of which carry that material at length. §3.6's first paragraph already fixes the selection-not-sequencing boundary, which is the load-bearing claim. (2) The two governance paragraphs of §3.2 were merged into one. They record two different exclusions, the governance stage whose start is not dated and the committees that spend calendar rather than pharmacy capacity, but read as repetition when split. Both reasons are preserved verbatim in the merged paragraph. 33 counted words.

**[edit] The prioritisation tool taken out of the model, 2026-08-28.** On the user's instruction. The tool is new and scores a study as it arrives, so it cannot be applied backwards to a study already in set-up, and no trial in this analysis carries a score. Three things follow. §3.3 no longer gates eligibility on $v_i \ge t$, and $E$ is now the trials in scope. P3 and its goal constraint are gone, so §3.5 is a two-level ordering and (3.6) carries one deviation rather than two. The fourth assumption in §3.7 was the eligibility threshold and is now the flat statement that every eligible trial is treated as equally worth doing, with the condition for revisiting it. The notation table loses $v_i$ and $t$.

**Two consequences outside this chapter.** SQ3 in §1.4 asked whether the advantage survives when arrival timing, trial mix and *the eligibility threshold* are varied; the threshold no longer exists. **Resolved 2026-08-29:** the third factor is now set-up duration, and the Appendix 5.A sweep was rerun with the score axis removed. Chapter 4 still discusses P3's placement and quotes the 13.5 to 36.5 score range, and its Overleaf mirror carries a `\ref{eq:value}` that now resolves to nothing.

**[edit] §3.5 wording: the priority order stated before the goals, 2026-08-28.** The section opened "The first goal is lateness" and then labelled lateness P2 four lines later, which reads as a contradiction in a pre-emptive goal programme. The order is now stated in its own paragraph before any goal appears, and the lateness paragraph says plainly that it comes first on the page but ranks second. No equation changed for this.

**[edit] §3.5 restated as a pre-emptive goal programme, 2026-08-23.** On the user's instruction, after the model's own classification was checked against `Experiments/optimiser/model.py:230-277` rather than against the source notes. Only P2 was a goal: `late` is declared as `addVars(names, lb=0.0, ..., name="dplus")`, a one-sided over-deviation, while P1 and P3 were direct objectives with no aspiration level. Chapter 4's claim that deadlines, throughput targets and value preferences are all "expressed as deviations in the goal-programming formulation of §3.5" therefore overstated what §3.5 contained. P1 and P3 now carry explicit targets and under-achievement variables $n_1^-$ and $n_3^-$, so all three levels are goals.

**Nothing changes mathematically.** $|E|$ and $V$ are constants, so minimising $n_1^-$ and $n_3^-$ is identical to maximising the on-time count and the committed value. Solutions, optimal values and every reported figure are unchanged, and `model.py` needs no edit. The closing paragraph of §3.5 states that equivalence in the text rather than leaving it to be found.

**Why the GP label rather than the alternative.** A framing was considered that declined the label and described the model as a lexicographic selection model carrying one goal constraint, citing order acceptance for the problem and goal programming only for the lateness term. The user chose pre-emptive GP because it is the recognised framework in healthcare OR, where the reader is. Slotnick and Morton 2007 (ER-038) is retained for the selection formulation, whose Equation (1) matches this one term for term, and for the one-sided deviation.

**A correction that made this possible.** `Knowledge/Method Taxonomy.md` had classified Blake and Carter 2002 (ER-030) as a weighted-GP paper. It is pre-emptive: "a linear GP model with two pre-emptive goals", later "six pre-emptive goals", with P₁ and P₂ notation and the same discriminate-among-ties logic. It becomes the lead method citation for §3.5's opening sentence. The misclassification is what made this look like a four-paper literature gap when it was a one-book gap.

**Numbering.** The old (3.6) held P1 and P2 and the old (3.7) held P3; both are absorbed. (3.6) is now the two new goal constraints and (3.7) the lexicographic objective. Two references were corrected in Chapter 4, at the strict-priorities sentence in §4.4 and the comparator sentence in §4.6. Equation (3.5) keeps its number, so the three references to it are untouched.

**Word count.** The body rose from 2,576 to 2,742 words, 166 more rather than the 70 estimated when this was drafted. The plan file `plan/Chapter3_5_GP_Reframe_2026-08-23.md` holds the full decision record and the apply checklist.

**Still outstanding.** The Overleaf mirror in `Dissertation/overleaf/Chapters/` has not been updated and no longer matches. Jones and Tamiz (2010), *Practical Goal Programming*, is not yet obtained; with the GP label now claimed in the chapter, that citation is required rather than optional.

**[edit] Committees confirmed as blocking, 2026-08-20.** JS's Part 2 return answers the question §3.2 left open: a committee "holds it up. Pharmacy cannot finish set-up until the committee has cleared the study." §3.1's closing clause previously said pharmacy may meet its target while the site misses confirmation, which a blocking gate rules out, and it now states the opposite consequence: committee wait lands inside pharmacy's own recorded set-up without being pharmacy work. The exclusion in §3.2 is unaffected, since a gate still consumes no pharmacy capacity, but **one consequence is not yet acted on**: any set-up duration measured on a committee study includes the committee wait, so the durations calibrated in Chapter 4 §4.2 are contaminated for those studies and the committee-flagged cases should be checked separately before the final run.

**[edit] Two corrections from the August questionnaire returns, 2026-08-20.** Source: `Sources/Interviews/2026-08-20_questionnaire-returns-digest.md`, from JS's Part 2 return (19 Aug), the returned Part 1 study table, and SE's Part 3 return (20 Aug). (1) §3.1's committee paragraph corrected: GMO meets every three months, not monthly, so a missed slot can cost up to a quarter; S&Q added to the committee list because it gated MOLI in the returned data; "meeting dates are fixed a year ahead" dropped because JS does not hold the calendar and has asked what period we need. IDEAS monthly is implied rather than ticked in the return and should be confirmed when the calendar arrives. (2) §3.4's opening corrected: the sign-off normally rests with one approver but can be delegated to the Operational Manager when most processes are approved, so the single-server queue is now stated as a conservative approximation rather than a fact. The formula and the ceiling argument are unchanged; a second signer can only shorten the wait, so $g_n$ is an upper bound.

**§3.1 took the operational detail from Chapter 1, 2026-08-12.** Supervisor feedback that the Introduction's operational problem should be elaborated here. §3.1 now runs eight paragraphs. The old combined paragraph on capacity and selection practice split into three: a new paragraph on demand and who controls it, carrying the R&I release role, 29 trials open to recruitment, five in set-up, the 10 to 20 per cent growth projection and the two-per-month service level agreement, all moved from §1.2; the existing capacity limits; and how work is picked today, which gained the prioritisation tool sentence. The opening paragraph was cut from the full three-stage 150-day breakdown to a back-reference, since Chapter 1 §1.1 states it. Chapter 1 §1.2 is now one paragraph of 111 words. Plan: `plan/Chapter1_Revision_Plan.md`.

**[edit] Chapter rewritten for the six-chapter template and de-duplicated against Chapter 1, 2026-08-12.** Six changes.

1. **§3.1 opening compressed.** The 150-day stage breakdown and the re-explanation of pharmacy's position on the critical path are stated in §1.1 and are now a single back-reference. The three teams are still named, because §3.3 needs them as model entities.
2. **The R&I demand sentence de-duplicated.** §1.2 already says R&I sets the volume, mix and timing. §3.1 keeps only the quantities: 29 open to recruitment, five in set-up, the growth projection, the two-per-month agreement.
3. **§3.2 compressed to a pointer.** The two exclusions were stated almost word for word in §1.3. §3.2 now refers to them and adds only the reason each cannot be measured.
4. **Kearney cut by a third.** It is retained because it justifies studying the pharmacy track at all, but it is a literature claim and should move to Chapter 2 when that chapter is drafted.
5. **§3.6 loses the solution method.** The six-iteration cap is a solution detail and moves to Chapter 4 under the template's structure. The coupling argument itself stays here.
6. **§3.7 cut to the four assumptions.** Their consequences for the results move to Chapter 6, and the complexity-mix discrepancy to Chapter 4 where the portfolios are generated. The sentence reporting 24 of 24 against 2 of 24 was dropped: it belongs with the results, and its comparator has been superseded by the 2 of 23 recomputation below.

**[edit] Unscored trials pass the eligibility gate, 2026-08-13/15.** Found while checking the chapters against the implementation after the mock-pipeline run. §3.3 defined $E = \{i : v_i \ge t\}$, which with eight scored studies would leave the eligible queue nearly empty. `optimiser/data.py plannable()` is explicit: "Cases below the floor are closed rather than queued forever. Unscored cases pass through." §3.3, the notation table and §1.3 now say scored trials face the floor and unscored trials pass. Minor item also noted: §3.4 says $g_n$ increases with $n$, while the implementation caps utilisation, so the wait flattens at roughly 32 days past nine committed; harmless at current limits, one clause if it ever matters.

**[edit] The 20/80 complexity split removed from §3.7, 2026-08-13.** User decision. The figure never belonged in the chapter, though not for the reason given at the time: it was not built from 20 complete cases. `Sources/Interviews/lthtr-project-brief.md:17` reads "65 CTIMPs (60% aseptic, 20% early phase)", so the 20 per cent is the early-phase share of the portfolio and was misread as a complexity share. The ER-033 note records that finding. There was therefore never a contest between 20/80 and 60 per cent aseptic; there was one figure and a misreading of another.

The assumption is kept in slimmed form, because something real survives: the roughly 60 per cent aseptic share comes from the trust's answer about its open portfolio, not from the cases studied here, and any simulated portfolio inherits it.

**`CLAUDE.md` still carries the misreading** and should be corrected. It instructs that synthetic datasets follow a "20% high-complexity / 80% routine" split, which would misdirect any generation run from it. This is now the second document to be corrected for the same error.

**§3.6 merged into §3.2 and then rolled back, 2026-08-13.** The merge was made and reversed on the user's decision within the same session. §3.6 "What the model does not decide" stays a separate section and Assumptions stays §3.7, so the chapter remains seven sections.

The reason for keeping them apart, recorded so the question does not have to be reopened: §3.2 bounds the *study* before any model has been presented, excluding capacity sizing, clinical site set-up, governance and the committees. §3.6 bounds the *model*, and "it does not order trials" is not meaningful to a reader until equations 3.3 to 3.7 have been read. They are the same kind of statement made at two different points in the argument.

**The limitation version goes to Chapter 6**, recorded in `plan/Model_Reconciliation_2026-08-13.md` section 6b: because the model does not order trials, it cannot tell the service which to work first, and the approval wait is an expected value at a plan size rather than a real sequence, so a plan feasible on average may not be feasible in the order the teams actually take the work.

**[edit] P3's active status removed from §3.5, 2026-08-13.** The paragraph said P3 "is currently inactive" and explained why. Whether a switch is on for a particular run is an implementation setting, not part of the problem statement, so it belongs in Chapter 4 where the model is configured and run.

**For Chapter 4 to record.** `value_active = False` in `Experiments/optimiser/config.py`, set on 1 August 2026, so P3 is not evaluated in the runs reported here. Two reasons to state there: the ordering was replaced on 3 August after value-first selection performed badly, recorded at `Model/Merged_Model_Specification_EN.md:273`; and the score has no spread to work with, since `LTHTR_2_Research_and_Innovation_2026-08.md:70` records all eight scored studies coming out HIGH. Reactivation would need scoring coverage wide enough for value to separate trials, which is worth checking against the 16 to 20 cases when they arrive.

**[edit] P3 defined rather than justified by a result, 2026-08-13.** The paragraph read "Value-first selection was tested and rejected: with every trial past its due day it made on-time performance worse in 175 of 200 trials." That is a result, and Chapter 3 describes the problem. It also risked being read as rejecting value altogether, when what lost was value at the *top* of the ordering, not value as a third level.

P3 is now given its own numbered equation (3.7) and defined by where it sits: below the other two, acting only where a choice remains once on-time count and weighted lateness are settled. Its inactive status is explained by scoring coverage rather than by the test, and the condition for reactivating it is stated.

**The 175-of-200 finding belongs in Chapter 5**, as evidence for SQ3. Source: `Model/Merged_Model_Specification_EN.md:273`. Across 200 synthetic value draws, value-first selection matched LTHTR's on-time result in 16 runs, beat it in 9 and lost in 175, which is why the ordering was replaced on 3 August. State it there with the qualifier that it tested value at the top of the ordering.

**Why P3 is inert in practice, for Chapter 5 to check.** `LTHTR_2_Research_and_Innovation_2026-08.md:70` records that all eight scored studies come out HIGH, so the score currently has no spread. P2 is a continuous weighted sum, so exact ties are close to impossible and a third level would rarely be reached in any case. When the 16 to 20 cases arrive, check the spread of scores before deciding whether to switch it on.

**[edit] The one-sided goal constraint explained, 2026-08-13.** §3.5 writes the lateness goal with only $d^+_i$, and as an inequality rather than the equality a goal programme conventionally uses. A reader who knows goal programming expects the deviation pair $d^+_i$ and $d^-_i$ either side of an equality, and will read the single variable as an omission.

It is a deliberate simplification and the two forms are equivalent here. Only overrun is penalised, so at any optimum the under-deviation is zero and carries no information; dropping it removes one continuous variable per trial for nothing lost. The inequality with $d^+_i \ge 0$ lets the objective push $d^+_i$ to $\max(0, \cdot)$ on its own. This follows `Experiments/optimiser/model.py`, which builds the constraint the same way.

The earlier draft of this chapter did carry the pair, in the superseded sequencing formulation, written as $C_i - d^+_i + d^-_i = due_i$. That equality was correct for a model that also rewarded early completion through the schedule. The present model does not, so the pair is no longer justified.

**[edit] Why prescribing system and specialty are not model inputs, 2026-08-13.** The August meetings added two fields, `Prescribing system` (chemo ePMA, inpatient ePMA, none) and `Specialist pharmacy input` (specialty). Neither enters the model, and §3.3 now says why in one sentence: the pathway records what a trial requires rather than which team supplies it.

The reasoning, kept here rather than in the chapter.

**The model uses trial attributes for one purpose only**, setting $p_i$. A field belongs in the model only if it changes that duration.

**Prescribing system does not change it.** Chrissy's own statement is that the chemotherapy and inpatient routes run on comparable timelines, so splitting the pathway by system would create two groups that behave identically.

**Specialty has no fixed value set.** It is free text or an open picklist, so there is nothing to key a duration on.

**And the sample cannot carry more groups.** Two flags give four pathways against 16 to 20 real cases, roughly four per group. Adding prescribing system takes it to twelve groups, and specialty multiplies again. The four that exist are already not separable: pooled durations across the tracker sit near 95 days regardless of pathway, which is why `config.py` carries the same 95 for all four and why Appendix A.2 has to use illustrative durations.

**Where the two fields do work instead.** Chapter 4 uses prescribing system to test whether the two routes really do take comparable time, which turns Chrissy's claim into a checked finding rather than an assumption, and uses specialist input to show how far set-up work spreads beyond oncology, which is what she asked the field for. Chapter 6 names both as the route to a better pathway definition once more cases exist.

**[edit] Four fixes from checking the chapter against the meetings, the forms and the code, 2026-08-13.**

1. **$a_i$ is now defined, and follows the August meetings.** §3.3 said "the days it has already waited" without saying from when. It is now the days since the trial entered the pharmacy set-up queue, explicitly not the days since pharmacy was notified. This matters because $a_i$ drives the claim weight and therefore P2. **The code does not yet do this:** `data.py` computes `days_waited` from `notified`, and gates entry on it. That change is blocked on the set-up start dates in `LTHTR_1` Block 1 and must be made before the final run, or Chapter 4 must state which date was used.
2. **$c$ is a commercial ceiling.** §3.4 introduced it as the number of set-ups the service can take on, while §3.1 counts non-commercial trials as load. `LTHTR_3_Pharmacy_Clinical_Trials_2026-08.md:130` records the intention to label the figure as commercial wherever it appears, because non-commercial set-ups use the same hours and the same approver. §3.4 now says so.
3. **The eligibility threshold currently separates nothing.** §3.3 defines $E$ as though every trial carries a score. `LTHTR_2_Research_and_Innovation_2026-08.md:70` records that eight studies have been scored and every one comes out HIGH. §3.7 now says the eligible queue is the whole queue by default rather than by rule, which is a stronger caveat than "a working figure".
4. **Chapter attribution corrected.** §3.2 said Chapter 4 would establish how often committees delayed set-up. Under the six-chapter template Chapter 4 is Methodology and describes how; Chapter 5 reports the finding.

**One thing checked and left alone.** §3.1 and §3.3 describe the pathway as set by whether an electronic prescription must be built, which is correct after the 6 August meeting. `data.py:104` still derives it from the oncology flag, so the chapter is ahead of the code. Fix `tier_of()` before the final run, or Chapter 4 must record that oncology was the available proxy.

**[edit] §3.3 to §3.6 rewritten against the implementation, 2026-08-13.** Evidence: `Experiments/optimiser/model.py`, `data.py`, `gate.py`, `config.py`; reconciliation recorded in `plan/Model_Reconciliation_2026-08-13.md`. The previous text described a formulation the project does not use. The old §3.3 to §3.6 are preserved at `scratchpad/ch3_old_33_36.md` in case any of it is wanted back.

**What was removed, and why.** Per-team effort budgets $A_m$, concurrency caps $cap_m$, per-team effort $a_{im}$ and processing time $p_{im}$, the routing set $R_i$ over teams $M$, and the throughput goal $T_N$ with its deviation pair. None appears in the code. The model has one commitment limit and one duration per trial. The throughput goal was dropped on 3 August because, with every trial past its due date, throughput shortfall is identical for any selection of the same size and therefore discriminates nothing.

**What replaced it.** §3.3 defines the eligible queue, the four pathways that set $p_i$, the due day, the days remaining $\delta_i$, and the claim weight $w_i = 1 + a_i/365$. §3.4 is new and covers the approval queue: a single approving signature whose expected wait $g_n$ grows with the committed count, the load selector $z_n$ that lets the model evaluate that wait at the size it actually chooses, and the rescue matrix $r_{in}$. §3.5 gives the lateness goal constraint and the two ordered objectives, P1 maximise on-time count and P2 minimise weighted lateness across the whole eligible queue.

**§3.5 and §3.6 no longer describe a sequencing model, and this reverses the decision of 2026-08-12.** Sequencing was confirmed as staying on the assumption that it existed. It does not: `model.py` states "It does not produce a timetable, which is what keeps it distinct from a scheduling model." The disjunctive precedence constraints, the completion variables $C_i$, the order variables $y_{ijm}$ and the coupling loop were never implemented and cannot be built and validated before 7 September. §3.6 now states the boundary positively: the model prices the congestion that sequencing would resolve, through $g_n$, rather than ordering trials explicitly.

**Three things now in the dissertation for the first time.** The approval queue and its consequence that rescueability is a property of the plan rather than of the trial. The age weight and its purpose, which is to stop slow trials being starved. And the whole-queue lateness sum, which is what stops the model cherry-picking easy trials.

**Consequences not yet acted on.** §3.1 still describes two decisions being taken in practice, which remains true of the trust even though the model addresses only the first; check on the next read whether that reads as a promise the chapter does not keep. §1.4 has three sub-questions and none asks about the approval queue, although SQ2 now points at it. ~~Appendix 3.A's worked instance still illustrates queueing for the aseptic team under the old formulation and needs rebuilding or removing.~~ **Closed 2026-08-13.** The instance was rebuilt against the implemented model, and its four trials, illustrative 36-day durations and gate-wait row now match `Experiments/optimiser/gate.py` at default settings. `tests/test_robustness.py::test_appendix_instance_rescueability` reproduces it, and Chapter 4 §4.7 cites it as one of the two hand-worked checks.

**[edit] Exclusions in §3.2 separated and named, 2026-08-13.** Three problems in one sentence.

1. **"Clinical set-up" was undefined and collided with a term in scope.** §3.1 names a "pharmacy clinical trials team", which is modelled and has dates in the tracker, three paragraphs before §3.2 excluded "clinical set-up". Both begin with "clinical", one is in scope and one is out, and nothing distinguished them. The exclusion now names it "clinical site set-up", says it is the research delivery team's work such as staff training and site initiation, and says explicitly that it is not the pharmacy team.
2. **"Runs in parallel" was not a reason and argued the other way.** Aseptic Services and the prescription build also run in parallel and are modelled, and §3.1 says the site waits for whichever track finishes last, so a parallel track is precisely one that can determine the site date. The clause is removed. What it pointed at is a limitation, not a boundary: a trial held up by clinical site set-up rather than by pharmacy is invisible to this study, and the model would attribute the whole window to pharmacy. That belongs in Chapter 6.
**[edit] Notification removed from §3.3, 2026-08-13.** User decision: the reader does not need the notification date, and the paragraph should emphasise the 60-day window instead. Three sentences went, explaining that release is not notification, that notification is tied to site selection, and that it can precede release by months without committing resource. The paragraph now opens on the window definition and treats the release day as secondary to it.

Nothing load-bearing is lost. The correction those sentences carried, that $r_i$ is queue entry and not the day pharmacy first hears, survives in the definition of $r_i$ itself and in the note of 2026-08-12 below. The point that the window is already running when a trial reaches the queue also survives, in "any days between the window opening and that release are already spent", which is the operational consequence rather than the field definition.

The distinction between notified and set-up start still matters for the data, since the August request splits them into two fields. It belongs in Chapter 4 where those fields are described, not in the model's notation.

**The one-day interpretation moved out of §3.2, 2026-08-13.** It was written into the scope section and then removed at the user's decision: scope states what is in and out and why, and does not argue about what a figure means. The material is kept here and belongs in Chapter 4, where the tracker fields are described.

What to write there. C&C to green light has a median of exactly 1 day across the 23 trials holding both dates, with six same-day and five at one day, computed 2026-08-13 from `Sources/Data/CTIMP_tracker_cleaned_2026-08-02.xlsx`. That is not a measure of governance speed. LTHTR's answer at `Sources/Interviews/question-list-1402-lthtr-qa.md:186` is that the green light is not a piece of work but an announcement made once everything else is complete, and the note closes "We should stop treating that number as a measure of anything." Chapter 4 should say so when it introduces the field, so that no reader treats the one day as evidence that governance is fast.

3. **Governance needed its own reason, and a warning.** `Sources/Interviews/question-list-1402-lthtr-qa.md:186` records LTHTR's answer to the question of why governance shows one day: "The green light is not a piece of work. It is an announcement made once everything else is complete. So measuring 1 day tells us nothing about governance speed", closing "We should stop treating that number as a measure of anything." Q4 on the same page adds that the governance start date sits with the research support team and pharmacy does not hold it. So governance has an end without a beginning, and the one-day figure in the data is an artefact. §3.2 now says both, which pre-empts a marker who finds a one-day governance figure and asks why something that takes a day was excluded.

The same source contradicts any impression that this work is quick: staff training and competence sign-off add time, and a trial using genetically modified material can wait weeks for a committee meeting held every two months.

**[edit] Aseptic capacity is a queue, not an unknown ceiling, 2026-08-13.** §3.1 said the trust "does not know how many trials Aseptic Services can absorb", which read as a flat unknown. `Sources/Interviews/question-list-3006-lthtr-qa.md:14` says three things and the chapter used only one of them. The unit does work to a capacity model mapping activity units within its MHRA licence, within 80 per cent usage. Clinical trials are only about 2 per cent of its weekly workload. And the specific unknown is concurrency: "I don't actually know what capacity they can absorb", meaning how many trials it can hold at once.

Taken together the unit absorbs the work; trial work queues behind routine production and each trial takes longer. That is the same shape as the Oncology correction of 2026-08-12, so both specialist limits now read as slowing rather than stopping. The 2 per cent figure enters the dissertation here for the first time and is what makes the point concrete.

Consequence for the model, not yet acted on. If the aseptic limit is elapsed time rather than a hard ceiling, $cap_{\mathrm{Asep}}$ as a hard concurrency cap in §3.5 misrepresents it in the same way the single-server assumption misrepresents Oncology, and the honest treatment for both is a processing time that rises with load. This is now the second finding pointing at that change.

**Open question on whose capacity the two-per-month figure is.** The two sources disagree. `Sources/Interviews/lthtr-project-brief.md:17` says "CT service capacity SLA 2 commercial CTIMPs/ATIMPs per calendar month", which makes it the clinical trials team's. `Model/Meeting_Findings_2026-08_Field_and_Model_Changes.md:171` records "Pharmacy can currently absorb about two commercial trials a month", which reads as a whole-service ceiling.

§3.1 follows the brief, because it is the more specific statement. If the meeting's reading is right, the argument in §3.1 weakens sharply: the surplus in paragraph 3 would already account for the specialist units, and paragraph 4's pivot from adequate totals to unmeasured specialist capacity would lose its force. One question to LTHTR settles it, and it should be asked before Chapter 4 fixes the effort budgets $A_m$, which rest on the same figure.

Note also that Oncology is not wholly without a capacity statement. LTHTR answer Q3-2 gives a preference of one trial at a time. That is a working preference, not an agreed capacity, which is why §3.1 now says the specialist units have "no agreed capacity of their own" rather than no figure at all.

**[edit] Why the intake figure counts non-commercial trials, 2026-08-13.** The dissertation's scope is commercial: §1.3, the research question and the 150-day target itself all exclude non-commercial studies. §3.1's intake figure of 12–15 a year counts both kinds, and the paragraph did not say why, so a reader carrying the commercial scope from Chapter 1 met a mixed count with no explanation.

The mixed figure is the right one. Non-commercial trials consume the same three teams whether or not they count towards the target, so excluding them would understate the load against which capacity is judged. This follows the decision recorded at `Model/Meeting_Findings_2026-08_Field_and_Model_Changes.md:39`: Chrissy argued non-commercial trials can be as complex to set up while pharmacy is steered towards commercial work for financial reasons; Jaya argued the metric covers only commercial; the resolution was to carry the field, "use it for capacity reporting, do not use it in the on-time calculation". Counting non-commercial trials as load while judging on-time only for commercial trials is that decision applied.

Two things follow for later chapters. The tracker holds no commercial or non-commercial flag, confirmed by inspecting the cleaned workbook's columns, so the split cannot be computed from it and the new field requested in the August data ask is what supplies it. And the comparison in this paragraph is conservative: it sets mixed demand against a commercial-only allowance. Commercial arrivals alone would be roughly eight a year against 24 slots, a larger surplus than the paragraph claims.

**[edit] §3.1 paragraph 4 now states a problem rather than listing limits, 2026-08-13.** The paragraph reported that 60 per cent of trials need aseptics, that Aseptic Services runs below 80 per cent, and that Oncology prefers one trial at a time, then concluded that progress depends on the needed team being free. It never said whether the team is free, so the limits read as background and no problem appeared.

It cannot say, and that is the finding. `Sources/Interviews/question-list-3006-lthtr-qa.md:14` records LTHTR's own answer to Q3-1: "I don't actually know what capacity they can absorb." The paragraph now closes on that: neither specialist unit has a stated capacity, the trust does not know the aseptic figure, and nobody can say in advance how many trials the specialist route allows. The problem is not demonstrated overload, it is that feasibility is unknowable from what the trust holds, which is what SQ2 asks and what the planning model exists to make visible.

The paragraph before it also lost its closing sentence, "even counting other routine works, arrivals do not fill that", which widened the comparison to work that is not trials and left paragraph 4 referring back to a scope that had shifted. The point it carried, that the 12–15 already covers both kinds of trial, is now a clause inside the fact itself.

**[edit] Duplicate paragraph removed and the capacity claim shown, 2026-08-13.** §3.1 carried the same "neither target was met" paragraph twice, in two drafts, one of which also had a double full stop. The later draft is kept and the earlier deleted.

The retained paragraph asserted that the team has more slots than trials without ever stating the number the claim depends on. Two a month is about 24 a year, now written down. A second gap sat behind it: the 12 to 15 counts all CTIMPs while the two-a-month agreement covers commercial trials only, so the two figures are not like for like. The added sentence, "even counting non-commercial work, arrivals do not fill that", disposes of the mismatch by pointing out that it only widens the gap, since commercial arrivals are a subset of the 12 to 15.

The user also acted on the fourth review point independently: the governance-gates paragraph has moved to the end of §3.1 and now closes by saying the delay is excluded from the analysis. That resolves the flow objection recorded below, since the gates no longer interrupt the chain from specialist scarcity to the two decisions.

**[edit] Three logic fixes in §3.1, 2026-08-13.** From a review of the section's flow.

1. **The surplus and the constraint were measured on different teams.** The paragraph conceded that arrivals fit inside capacity, citing the two-per-month agreement, which covers the clinical trials team only. The next paragraph then located the constraint in Aseptic Services and the prescription build, for which no equivalent agreement exists. The concession now names the team it applies to, and the following paragraph opens by saying the specialist units carry no equivalent, which turns a rhetorical transition into an argued one.
2. **"Finite shared capacity" contradicted the paragraph that preceded it.** §3.1 argues capacity is not one shared pool; the closing sentence then called it shared, meaning shared between trials. Now "finite specialist capacity".
3. **"only few studies"** corrected to "only a few studies".

A fourth issue was raised and not acted on, at the user's decision. The governance-gates paragraph is the only one in §3.1 that does not feed the closing argument, since gates are excluded in §3.2 and never enter the model. The section therefore describes one cause it does not go on to address. Keeping it is a deliberate choice to show the whole problem before narrowing to the modelled part. If a marker queries the join, the fix is either to move the paragraph after the two-decisions paragraph or to have the closing paragraph acknowledge the exclusion.

**[edit] Kearney removed from §3.1, 2026-08-13.** User decision. The paragraph was doing a literature-review job inside a chapter that describes the problem, and §3.1 now establishes the problem from LTHTR's own tracker, which is better evidence for this trust than a 2014 multi-site study. Nothing else in the chapter depended on it.

Where it goes. Kearney et al. (2014), ER-008, covered by Claim A3 in `Knowledge/Claim Map.md`, belongs in Chapter 2 with the rest of the delay literature. Its specific value there is the finding that the dominant delay in opening NHS research sites falls in documentation preparation rather than in formal review, which took 16 days once a valid application arrived. That is the published support for studying a preparation activity such as the pharmacy track, and it should appear in the section of Chapter 2 that closes on this dissertation's intended contribution, not in Chapter 3.

**[edit] Governance gates added to §3.1, and excluded in §3.2, 2026-08-12.** The section argued that a yearly surplus of slots coexists with missed deadlines and explained it by specialist scarcity alone. Timing was the missing half. Source: `Model/Meeting_Findings_2026-08_Field_and_Model_Changes.md:49-51`, Jaya on 6 August, IDEAS for radiology and GMO for genetically modified organisms, dates fixed a year ahead, "it adds plus 30 days and immediately it will go from your green to your amber", with Chrissy confirming it is outside the trust's control once missed. The chapter states the 30 days as half the 60-day window, which is the fact that matters here.

**How the gates connect to a pharmacy chapter.** The paragraph now states the bridge explicitly, because IDEAS and GMO are radiology and biosafety committees and their relevance is not self-evident to a pharmacy reader. The link is the shared deadline, not shared staff: a gate takes no pharmacy time but spends the same 60 days, so pharmacy can meet its own goal while the site misses confirmation.

A second and more direct link is likely but not evidenced. The GMO gate governs genetically modified organisms, which in trial terms usually means advanced therapy products, and those are the trials most likely to need aseptic preparation. If that holds, the gate and the scarcest pharmacy route fall on the same trials and compound. Nothing held states it. The resolving document is the written description of how each committee affects the pathway that Jaya agreed to supply on 6 August, recorded at `Model/Meeting_Findings_2026-08_Field_and_Model_Changes.md:225` and still outstanding. Ask for the gate-to-route overlap explicitly when chasing it.

§3.2 records why they are not modelled: a gate changes when a trial can start, not how much team time it consumes, so it does not enter a capacity model. This is the same reasoning that kept them out of §1.2, where they would have promised a reader something Chapter 3 does not deliver. Note that no claim is made about gates batching arrivals into pharmacy, because the source does not establish whether a gate sits before or after release to pharmacy.

**[edit] "No explicit rule" corrected against LTHTR answer Q4-2, 2026-08-12.** §3.1 said trials are picked up in arrival order "with no explicit rule for deciding which goes first". `Sources/Interviews/question-list-3006-lthtr-qa.md:17` records the opposite in part: "if there is a higher priority studies … we usually accelerate the review outside of the meeting timelines." A practice exists; it is informal and unrecorded, which is not the same as absent. The sentence now says so.

This matters beyond accuracy. SQ3 compares the model against current practice, and if current practice already accelerates important studies, a comparator built on pure arrival order would overstate the model's advantage. That is the same warning the briefing gave about a first-come-first-served baseline, and it should be settled with LTHTR before Chapter 4 fixes the experimental design.

**[edit] The volume paragraph rebuilt on the arrival rate, 2026-08-12.** It previously offered 29 trials open to recruitment, five in set-up and a growth projection, then concluded that the service can absorb what arrives. None of those three is an arrival rate: 29 counts trials that finished set-up long ago, five is a snapshot, and the projection is a percentage of an unstated base. The claim is true but the evidence did not show it. The paragraph now uses the intake computed from the tracker, 12 to 15 CTIMPs a year against roughly two commercial slots a month, which is the comparison the claim needs.

Three side effects. The undated 29 and five leave the chapter, which removes two figures the source note flags as lacking an "as at" date. "Decides when each trial is passed on" leaves too, a third restatement of §1.2. And "counted as totals, the service can absorb roughly what arrives" is replaced by "over a year, pharmacy has more set-up slots than trials to fill them", after the user asked what the original meant.

The concession is safe in the direction that matters. The two-per-month agreement covers commercial trials only, while the 12 to 15 mixes commercial and non-commercial, so commercial arrivals are fewer still and the surplus is larger than the sentence claims, not smaller.

**[edit] Oncology concurrency corrected from a hard limit to a preference, 2026-08-12.** §3.1 stated that Oncology "handles one trial at a time". The source does not support that as a capacity ceiling. LTHTR answer Q3-2, recorded at `Sources/Interviews/question-list-3006-lthtr-qa.md:15`, reads: "preference is 1 at a time and it takes 1-2 weeks to complete and then review." A preference with a duration attached is a soft constraint. The team can hold more work; each trial then takes longer.

Two consequences. §3.7 now records that $cap_m$ approximates a soft limit with a hard one, which affects both specialist teams and not only Aseptic Services. And §3.5 models contention at these teams disjunctively, one trial strictly before another, which is the single-server assumption the correction undermines. The faithful alternative is a processing time $p_{im}$ that rises with concurrent load, which is a change to the formulation rather than to the prose, and it has not been made. Decide before Chapter 4 fixes the experimental design.

Note also from the same answer, not yet used anywhere: the 6-day working pilot supported "1 in a week" at peak, on an overtime rate that "doesn't mirror business as usual". That is the same warning Chrissy gave in August about durations fitted to pump-primed overtime, and it belongs with the duration calibration in Chapter 4.

**[edit] Release day redefined, 2026-08-12.** §3.3 defined $r_i$ as the day pharmacy is notified. `Model/Meeting_Findings_2026-08_Field_and_Model_Changes.md:91` records Chrissy correcting this: work enters the queue when RSG says so, and notification is tied to site selection and can precede release by months without committing resource. Jaya rejected notification as a trigger at `:89`. $r_i$ is now queue entry. Two knock-on corrections: §3.5's precedence gloss now reads "enters the pharmacy queue", and the per-trial goal constraint is written against $due_i$ rather than $r_i$, since the 60 days run from the start of the window and not from queue entry. The previous form measured a 60-day allowance from release, which would have granted every trial a fresh 60 days however late it entered the queue.

**[edit] "Site confirmed" renamed to the C&C Agreement throughout this note, 2026-08-16. Numbers unchanged.** The note below closed by saying "site confirmed is `Date of C&C`". That mapping is wrong and it propagated into §3.1 and into `Chapter1_Introduction.md:17`. `Sources/Data/CT-Excel-README.md:236-237` separates two events that share a name: the C&C **assessment**, Governance Track Step 3, which is stamped in EDGE as `Date site confirmed` and ends the 60-day window, and the C&C **Agreement**, column 16, a post-SIV sponsor document signed once all tracks confirm readiness. Only the second is in the tracker. Every interval labelled "site confirmed" here therefore ends inside the uncounted Gap described at `Knowledge/Research Gaps.md:83`, not at the end of Stage 2, and the table rows and the text now say so. The medians and counts are unaffected. Two consequences to carry forward: the true Stage 2 duration cannot be computed from any file currently held, and `Date site confirmed` should be added to the outstanding EDGE data request, which would turn Gap 7 from an observation into a measurement.

**[edit] Headline changed to clock-to-site-confirmed, and the 77-day claim removed, 2026-08-12.** User decision to lead on the site-level measure. Computed 2026-08-12 on `Sources/Data/CTIMP_tracker_cleaned_2026-08-02.xlsx`, which the cleaning log derives from `CTIMP Trials 150 Day Metric Tracker- 2026-07-30 SE.xlsx`, the latest tracker.

| Interval | n | Median | Within 60 |
|---|---|---|---|
| Clock start to C&C Agreement signed, all years | 25 | 153 | 3, 12% |
| **Clock start to C&C Agreement signed, clock start 2024 onward** | **24** | **144** | **3, 13%** |
| Clock start to pharmacy green light, 2024 onward | 23 | 134 | 4 |
| Clock start to open to recruitment, 2024 onward | 29 | 140 | 4 |

The 2024-onward variant is the one in the text, so that the site figure and the pharmacy figure cover the same period. Clock starts run 2024-05-01 to 2026-02-03 and agreement dates 2024-09-17 to 2026-04-24. Clock start is the later of HRA approval and site selection. The end date is `Date of C&C`, which is the Capability and Confirmation Agreement signed after SIV, and not the site-confirmation milestone that ends the 60-day window. `Sources/Data/CT-Excel-README.md:236` separates the two, and the tracker carries no column for the latter.

**The 77-day upstream-lag sentence was deleted rather than corrected.** It was measured from HRA approval alone on a superseded file. On the settled clock the gap from clock start to pharmacy start has a median of 4 days across 23 trials, so the claim that "a second delay sits upstream of the first" is not supported and could not sit beside a headline that starts from the same clock. If the upstream interval is wanted back, the defensible sentence is that pharmacy starts a median of 4 days after the clock, with a right-skewed tail reaching 318 days.

**Why the medians cannot be added. Kept here, deliberately out of the text.** The paragraph now carries one median only, on the site measure, and gives pharmacy's performance as a count. With a single median in play there is nothing for a reader to add, so the caveat that previously closed the paragraph was removed as an answer to a question the text no longer raises. Restore it only if a second duration is ever reported alongside the first. On the 23 trials carrying all three dates, clock to pharmacy start has a median of 7 days and a mean of 50, pharmacy start to green light a median of 95 and a mean of 106, and clock to green light a median of 135 and a mean of 156. The means add exactly; the medians do not, because the clock-to-start distribution is heavily right-skewed and the slow-to-start trials are not the slow-to-review ones. Five of the 23 have a negative clock-to-start, meaning pharmacy began before the clock, which is the segment A case from the August meetings and matches the 6-of-28 count recorded there.

**[edit] Pharmacy performance restated as 2 of 23, 2026-08-12.** The previous 5 of 27 at 18.5 per cent came from `01-Plan.md:89-97`, computed 2026-06-26 against `CT-Excel-LTHTR-25-06-2026.xlsx`, which `Sources/Data/CT-Excel-README.md` records as superseded and whose percentages used 118 rows against a true distinct-trial count of about 104. Recomputed on `Sources/Data/CTIMP_tracker_cleaned_2026-08-02.xlsx`, taking trials holding both a pharmacy start and a green light: n = 23, median 95 days unchanged, 2 within 60 days at 8.7 per cent, spanning pharmacy starts from 2024-05-16 to green lights on 2026-04-15. The period is therefore 2024 to 2026 and is now stated in the text. To be recomputed again once the 16 to 20 complete cases arrive, which is the point of that data request.

**[edit] The 77-day upstream lag is disputed and has NOT been changed, 2026-08-12.** The same recomputation puts two problems in that sentence. It rests on the same superseded file, and it measures from HRA approval alone when the window runs from the later of HRA approval and site selection, which `Chapter3_Problem_Description.md:87` records as the later date in roughly three quarters of studies. On the cleaned tracker the two measures diverge sharply:

| Interval | n | Median |
|---|---|---|
| HRA approval to pharmacy start | 28 | 141 days, range −55 to 2468 |
| Later of HRA approval and site selection, to pharmacy start | 23 | **4 days** |

On the settled clock the upstream gap is about four days, not 77, which matches Jaya's account that RSG passes the trial to pharmacy the same day as the green light in roughly 90 per cent of cases (`Model/Meeting_Findings_2026-08_Field_and_Model_Changes.md:154`). If that holds, "a second delay sits upstream of the first" is wrong as written and §3.1 loses one of its two delay claims. The HRA-only figure is skewed by long-closed trials, its range reaching 2468 days.

This is the recomputation deliberately deferred on 2026-07-29 and recorded in `Chapter1_Introduction.md`. It also bears on the segment B question from the August meetings: segment B, clock start to set-up start, has a median of four days on this data, so the pre-queue loss is small. Both need deciding before §3.1 is next revised, and both should be checked again against the 16 to 20 complete cases.

**Oncology replaced by the prescription-build team, 2026-08-12.** Source: `Model/Meeting_Findings_2026-08_Field_and_Model_Changes.md:23-27`, 6 August 2026. Oncology was a proxy for whether an electronic prescription had to be built; trials on the inpatient prescribing system go through the ePMA pharmacy team on comparable timelines. Three changes: §3.1 names the prescription-build team and identifies both teams inside it; the team set in §3.3 and the notation table are renamed from $\mathrm{Onc}$ to $\mathrm{Rx}$; and the concurrency sentence in §3.1 now says explicitly that the one-trial-at-a-time limit is Oncology's. That limit comes from LTHTR answer Q3-2 and no equivalent figure is held for the ePMA team, so the $\mathrm{Rx}$ concurrency parameter $cap_{\mathrm{Rx}}$ currently rests on the oncology figure alone. It is in the 16-to-20-case data request as `Prescribing system`.

**Figures.** 18.5 per cent, 5 of 27, median 95 days, median 77 days across 30 trials: CT Excel Report sheet, computed 2026-06-26, recorded at `01-Plan.md:89-97`. Roughly 60 per cent requiring aseptics: LTHTR answer Q6, `Question_list_3006.docx`. Oncology one trial at a time (Q3-2) and the 80 per cent aseptic utilisation ceiling (Q3-1): same source. The 24-of-24 versus 2-of-24 comparison: `docs/Model1_IO_Specification.md:182`. The 12.5-day variance: `docs/Model1_IO_Specification.md:113-118`.

**Citations.** Kearney et al. 2014 (ER-008) uses the allowed wording recorded in `Knowledge/Claim Map.md`, Claim A3. Blake and Carter 2002 is **ER-030**, European Journal of Operational Research 140(3):541–561, DOI 10.1016/S0377-2217(01)00219-3. Note that `Experiments/Stage1_GP_Model_Design.md:16` cites this paper as ER-024, but ER-024 is Oddoye 2009. Full Harvard reference entries still need generating into the bibliography from the source notes.

**Cut from this chapter, by the focusing test.** EDGE field mechanics, solver choice, and the rolling re-plan and manual-override machinery were removed because they do not help explain the core problem. They belong in Background, Implementation, and Research Design respectively. The broader NHS set-up delay literature (Claims A1 and A2, covering Salman 2007, Hackshaw 2008 and Duley 2018) was cut to avoid duplicating Chapter 2; only the Kearney finding, which speaks directly to preparation activity, was retained.
