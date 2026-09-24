# DGF-Bench

**Rule Application and Evidence Reliability in Synthetic Governance Reviews**
Jeremy Canale · September 2026

[Read the second paper](From_Governance_Reviews_to_Task_Substitution.pdf) · [LaTeX source](main.tex) · [Response to the review](REVIEW_RESPONSE.md)

**21 pages: deterministic control, all-model evidence sensitivity, complete decision confusion matrices, Procurement diagnostics, 135 repeated runs, conditional-approval behavior, and source-coverage diagnostics.**

This is a separate, shorter manuscript based on the **same September 2026 experiment** as [The Last Human Gate](../paper/The_Last_Human_Gate.pdf). It now adds three fresh trajectories per model on 15 existing dossiers. These repetitions assess within-sample stability, not independent dataset validation. The first paper's 24 September revision includes a concise account of these same follow-up results while retaining its theoretical and workforce contribution; its earlier 59-page version remains in the repository history.

The second paper centers rule application and evidence reliability on the 300-project benchmark. It preserves original strict scores and reports the more permissive, post-hoc lexical-or-structural endpoint separately. The FDE and workforce argument remains in the first paper and project README; in this empirical manuscript it is a short discussion. The prospective seven-year 80% FTE hypothesis remains an untested proposal with no enrolled cohort. It does not confirm the historical 2033 forecast.

The current programme tests **LLM capability to perform governance-review decisions**, including evidence extraction, policy representation, and handoffs. Independent human evaluation is outside the programme; no human parity claim is made. No participants have been enrolled and no enterprise preregistration is claimed. The first manuscript retains its separate historical workforce hypothesis.

## New executed controls

- **Rules comparator:** 1,700/1,700 strict gates and 300/300 routes, with zero model calls. It uses the executable policies and structured facts already supplied to agents. The task therefore does not establish incremental LLM value.
- **All-model evidence audit:** all 690 evidence-failed gates are classified. Post-hoc gate success is 99.06% for Gemini, 85.53% for Luna, and 77.24% for DeepSeek, under the declared lexical-or-structural criterion. These are sensitivity measures, not independent semantic scores. [Full findings and item records](../research/2026-09-followup/ALL_MODELS_AUDIT.md).
- **Decision and Procurement diagnostics:** full confusion matrices, initial/effective reference agreement, and rule-level evidence defects.
- **Document-only preflight:** the same text in 26 Word documents can require GO or REWORK because a distinguishing fact lives in a CSV. [Protocol and blockers](protocols/scaffold_ablation.md).
- **Related work:** 16 references, including rule following, legal reasoning, process compliance, evidence attribution, agent benchmarks, costs, and automation bias.

[Complete follow-up measurements, scripts, and repetition plan](../research/2026-09-followup/). The repeats are complete: 135 evaluable runs, 765 gates, and $12.5598870228 including failed attempts. Gemini, Luna, and DeepSeek achieve 96.08%, 82.75%, and 73.33% pooled strict gate success; respectively 9/15, 3/15, and 0/15 dossiers pass all three times. [Per-repeat counts, case-cluster intervals, costs, and limitations](../research/2026-09-followup/REPETITION_RESULTS.md).

## Additional checks from the latest review

- **Conditional approval:** actual uses are 398 Gemini, 353 Luna and 202 DeepSeek. The matched specialist comparison has the same 391 eligible opportunities: 391, 347, 201 uses. Rejected calls are reported separately; 139 was only the Gemini approvals changing the initial label.
- **Procurement source provenance:** 25 exact observed CSV rows supplied by DeepSeek are excluded by the snapshot-only source contract. This does not establish complete semantic support or revise strict scores.
- **Repetitions:** the same structural audit now covers all 135 completed runs. Relaxed gate/route counts are reported alongside unchanged strict results.
- **Source sufficiency:** all 300 dossiers inspected with an explicit 76-field inventory. Two omissions are proved by counterfactuals and addressed in a development-only generation extension. Three new development cases are not held-out evidence.
- **Citation prototype:** source locations resolve to copied observed values. Unit tests cover provenance and invalid selectors; integration and semantic scoring remain future work.

[All added analyses and runnable scripts](../research/2026-09-followup/README.md).

## Sources and reproduction

All original benchmark data, including Word documents and architectures, remain in the [complete experiment release](https://github.com/jeremy1392/dgf-agentic-bench/releases/tag/dgf-bench-300-20260923). The [research directory](../research/2026-09-dgf-bench/) contains final tables and offline reproduction instructions. The earlier [15-project pilot](../research/2026-09-pilot/SOURCE_DOCUMENTS.md) is separate from the main experiment.

Build from this directory with a standard LaTeX installation:

```sh
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

The output is `main.pdf`; the published copy retains the stable filename `From_Governance_Reviews_to_Task_Substitution.pdf` so existing links keep working. Its title is now *DGF-Bench: Rule Application and Evidence Reliability in Synthetic Governance Reviews*. Figures and table fragments are included, so compilation does not require Python or API access. From the repository root, `python paper2/verify_manuscript.py` checks table/figure provenance, headline counts, all-model audit results, confusion matrices, and counterexample counts against the released local research artifacts. It does not independently validate the governance rules.

## Follow-up protocols

- [Matched-information scaffold and handoff ablations](protocols/scaffold_ablation.md)
- [Prepared General-only comparison and offline-tested runner](../research/2026-09-followup/GENERAL_REPLAY_PREPARATION.md) — 270 proposed executions, no new model results.
- [Historical and prospective cohort calendar](protocols/field_cohort.md)

Author: [Jeremy Canale](https://www.jeremycanale.com) · contact@jeremycanale.com · [LinkedIn](https://www.linkedin.com/in/jcanale13)
