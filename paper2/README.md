# From Governance Reviews to Task Substitution

**DGF-Bench and the Role of Forward Deployed Engineers**  
Jeremy Canale · September 2026

[Read the second paper](From_Governance_Reviews_to_Task_Substitution.pdf) · [LaTeX source](main.tex) · [Response to the review](REVIEW_RESPONSE.md)

**23 pages, revised with an executed deterministic comparator, an exhaustive structural evidence audit, and 135 completed repetition runs.**

This is a separate, shorter manuscript based on the **same September 2026 experiment** as [The Last Human Gate](../paper/The_Last_Human_Gate.pdf). It now adds three fresh trajectories per model on 15 existing dossiers. These repetitions assess within-sample stability, not independent dataset validation. The original paper remains available unchanged.

The second paper centers the 300-project benchmark, distinguishes decision quality from evidence conformity, gives FDE implementation work a concrete specification, and connects potential workforce substitution to measurable human labor. It replaces universal-law language with a conditional task-substitution hypothesis. The primary workforce proposal is now a seven-year, 80% FTE-reduction hypothesis anchored to a future registered baseline. No cohort has yet been enrolled; this does not retrospectively confirm the earlier 2033 prediction.

The human baseline, independent semantic evidence adjudication, scaffold-removal tests, and enterprise cohort are **proposed studies, not completed results**. No participants have been enrolled and no preregistration is claimed. A prospective study starting now cannot silently replace the original 2026 historical baseline.

## New executed controls

- **Rules comparator:** 1,700/1,700 strict gates and 300/300 routes, with zero model calls. It uses the executable policies and structured facts already supplied to agents. The task therefore does not establish incremental LLM value.
- **Gemini evidence audit:** of 85 failed gates, 69 have structurally matching excerpts, 9 contain flattened cross-object excerpts, and 7 lack a required evidence-tool read. This is structural analysis, not independent human semantic adjudication; original scores are preserved.
- **Related work:** ITBench, CI-Work, tau-bench, and agentic BPM added, with a task-level comparison.

[Complete follow-up measurements, scripts, and repetition plan](../research/2026-09-followup/). The repeats are complete: 135 evaluable runs, 765 gates, and $12.5598870228 including failed attempts. Gemini, Luna, and DeepSeek achieve 96.08%, 82.75%, and 73.33% pooled strict gate success; respectively 9/15, 3/15, and 0/15 dossiers pass all three times. [Per-repeat counts, case-cluster intervals, costs, and limitations](../research/2026-09-followup/REPETITION_RESULTS.md).

## Sources and reproduction

All original benchmark data, including Word documents and architectures, remain in the [complete experiment release](https://github.com/jeremy1392/dgf-agentic-bench/releases/tag/dgf-bench-300-20260923). The [research directory](../research/2026-09-dgf-bench/) contains final tables and offline reproduction instructions. The earlier [15-project pilot](../research/2026-09-pilot/SOURCE_DOCUMENTS.md) is separate from the main experiment.

Build from this directory with a standard LaTeX installation:

```sh
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

The output is `main.pdf`; the published copy is `From_Governance_Reviews_to_Task_Substitution.pdf`. Figures and table fragments are included, so compilation does not require Python or API access. From the repository root, `python paper2/verify_manuscript.py` checks table/figure provenance, headline counts, and scenario arithmetic against the released local research artifacts. It does not independently validate the governance rules.

## Follow-up protocols

- [Human and rules-engine comparison](protocols/human_baseline.md)
- [Independent semantic evidence audit](protocols/semantic_evidence.md)
- [Historical and prospective cohort calendar](protocols/field_cohort.md)

Author: [Jeremy Canale](https://www.jeremycanale.com) · contact@jeremycanale.com · [LinkedIn](https://www.linkedin.com/in/jcanale13)
