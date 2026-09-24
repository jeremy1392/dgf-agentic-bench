# The Last Human Gate

**Forward Deployed Engineering for Governance Automation**

Jeremy Canale · September 2026 · **25 pages**

[Read the concise paper](From_Governance_Reviews_to_Task_Substitution.pdf) · [LaTeX source](main.tex) · [arXiv package and metadata](ARXIV_SUBMISSION.md) · [Revision notes](REVIEW_RESPONSE.md)

This is the concise manuscript for readers and submission. It **replaces the former second paper**, *DGF-Bench: Rule Application and Evidence Reliability in Synthetic Governance Reviews*. It brings the task-substitution argument, FDE implementation, human-work accounting, and experimental evidence into one article. The [66-page original](../paper/The_Last_Human_Gate.pdf) remains available as an extended treatment. These versions share their evidence; they are not independent studies.

## The contribution

A governance function can remain necessary while agents and software take over tasks previously performed by people. The paper specifies when that transfer can count as a replacement: accessible information must suffice, outputs must meet the review contract and mandate, and exceptions, verification, correction, and support must leave less total human work.

- **Gate contracts:** a definition and an information-sufficiency proposition, grounded in a released document counterexample.
- **Human-work substitution:** a proved selection identity and reduction threshold, with all recurring human work counted.
- **FDE implementation:** evidence services, agent investigation, deterministic policy and mandate checks, shared handoffs, and escalation.
- **Controlled evidence:** 899 original evaluable runs on 300 synthetic dossiers, a deterministic control, evidence sensitivity, and 135 repeated runs.

The illustrative 140-FTE account can leave 43.52 or 168.92 FTE under different operating assumptions despite the same case partition. None of the four examples establishes an 80% reduction. With about 46.86% of baseline work in exceptions, even zero ordinary review and upkeep require an exception-effort multiplier no greater than about 0.427 to reach that target. These are calculations from declared assumptions, not measured enterprise outcomes.

The original **80% fewer required DGF FTE by 2033** hypothesis is retained in the discussion with its fixed accounting boundary and test conditions. It is not inferred from the benchmark. No enterprise cohort, human comparison, or new model experiment is claimed by this rewrite.

## Data and analyses

The complete [experiment release](https://github.com/jeremy1392/dgf-agentic-bench/releases/tag/dgf-bench-300-20260923) retains all original documents, Word files, architectures, traces, failures, scores, and source snapshots. Detailed tables and diagnostics remain in [original results](../research/2026-09-dgf-bench/) and [follow-up analyses](../research/2026-09-followup/). The 25-page PDF includes aggregate and gate-family results, a detailed protocol, two recorded examples, and a reproduction appendix. It does not alter the underlying measurements.

All original scores are unchanged. The rules control passes 1,700/1,700 gates; that structured condition establishes no incremental LLM advantage. The all-model evidence sensitivity remains a separate post-hoc criterion. The repetitions assess stability on 15 existing dossiers. Original and repeated inference total USD 99.5757161948.

## Sources and reproduction

Build from this directory:

```sh
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Three included image files and the inline bibliography make the source archive self-contained. A fourth figure is drawn directly in LaTeX with TikZ. The published PDF keeps the historical filename `From_Governance_Reviews_to_Task_Substitution.pdf` so links continue to work; its title is the one above.

From the repository root:

```sh
python paper2/verify_manuscript.py
python paper2/build_labor_figure.py
```

The verifier uses the standard library and checks the 80 numerical cells printed in the aggregate and gate-family results tables, abstract rates, confidence intervals, 14 citation keys, scenario calculations, and released supporting audit records. It checks consistency and provenance, not independent business validity. Rebuilding the workforce figure requires Matplotlib and reads the original `paper/anc/parameters.json`; compiling the paper does not require Python.

Some original benchmark figures and generated tables remain as supporting source artifacts and are checked against the original manuscript; they are not all included in the concise PDF. Its minimal [arXiv source ZIP](https://github.com/jeremy1392/dgf-agentic-bench/releases/download/dgf-bench-300-20260923/DGF_Bench_arXiv_source.zip) contains only actual compilation dependencies. See [technical verification](arxiv_verification.json) and the [submission guide](ARXIV_SUBMISSION.md). No submission or acceptance is claimed.

## Separate unexecuted protocols

- [Matched-information extraction and policy ablations](protocols/scaffold_ablation.md)
- [General-only comparison preparation](../research/2026-09-followup/GENERAL_REPLAY_PREPARATION.md)
- [Historical and prospective workforce calendar](protocols/field_cohort.md)

Author: [Jeremy Canale](https://www.jeremycanale.com) · contact@jeremycanale.com · [LinkedIn](https://www.linkedin.com/in/jcanale13)
