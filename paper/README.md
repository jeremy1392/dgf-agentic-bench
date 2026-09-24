# Research paper

## Title

**The Last Human Gate: Forward Deployed Engineering and the Automation of Enterprise Governance**

Author: Jeremy Canale  
Date: September 2026

Revised 24 September 2026: the original theoretical manuscript now incorporates the completed rules control, all-model evidence audit, approval behavior, and 135 repeated runs. These are the same data analyzed in the focused second paper, not an independent replication. The 2033 FTE hypothesis and synthetic scenarios are retained; testing the original date requires auditable records for the already closed 2026 baseline year.

Contact: [contact@jeremycanale.com](mailto:contact@jeremycanale.com) · [LinkedIn](https://www.linkedin.com/in/jcanale13)

The LaTeX source is contained in this directory. The paper provides the theoretical framework that DGF-Bench operationalizes: governance gates as information-transforming contracts, complete execution, route composition, handoff effects, labor accounting, the implementation role of Forward Deployed Engineers, and the hypothesis of 80% fewer required FTE by 2033 at comparable governed output. Complete automation is a stronger, undated conjecture.

DGF-Bench itself lives at the repository root and is the **experimental companion**. It generates controlled synthetic governance cases and evaluates whether an AI agent can investigate evidence, identify findings, produce gate dispositions, respect authorization boundaries, and execute route-aware handoffs.

See [`../docs/PAPER_AND_BENCHMARK.md`](../docs/PAPER_AND_BENCHMARK.md) for a detailed explanation of what benchmark results can and cannot establish relative to the paper.

## Build

From the repository root:

```bash
make paper
```

or directly:

```bash
cd paper
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
cp main.pdf The_Last_Human_Gate.pdf
```

The repository includes a verified compiled copy at:

`The_Last_Human_Gate.pdf`

The `anc/` directory contains the reproducibility scripts and synthetic calculations used by the paper.

## Measured benchmark results

The experimental section is written as a standalone account: research questions, generated business scenarios and evidence, the six-step agent workflow, actual route sequences, exact model identifiers and settings, scoring definitions, results, and conclusions. Two recorded cases explain a justified conditional approval and a correct decision that fails the exact-evidence rule. An experiment diagram and an actual generated architecture illustrate the inputs and process. These examples were selected after evaluation to explain the method.

The manuscript also reports the September 2026 evaluation on 300 synthetic dossiers: 899 of 900 model/case runs are evaluable. Gemini, Luna, and DeepSeek achieve 94.98%, 83.29%, and 74.18% strict gate success, respectively. These are measured agent outcomes on synthetic cases, distinct from the workforce scenarios.

The [research directory](../research/2026-09-dgf-bench/) contains final tables, diagnostics, figures, checksums, and an offline reproduction script. The [complete experiment release](https://github.com/jeremy1392/dgf-agentic-bench/releases/tag/dgf-bench-300-20260923) provides every file of the recorded run and dataset, plus the exact benchmark source snapshot. One Gemini infrastructure failure is excluded; historical partial exports remain in the archive and are clearly distinguished from final results.

The [follow-up analyses](../research/2026-09-followup/) add a deterministic control with 1,700/1,700 gates, structural evidence sensitivity across all three models, Procurement source checks, and exact conditional-approval behavior. The completed repetitions comprise 135 runs and 765 gates on 15 existing dossiers. Original and repeated inference total **$99.5757161948**. The source-coverage inventory and three development dossiers are offline diagnostics; the prepared General replay has not run.

## arXiv preparation

The revised source uses one-inch margins, includes an AI-assistance statement, and distinguishes measured results from the workforce conjectures. See [submission-readiness notes](ARXIV_READINESS.md) for current official requirements, the recommended classification, the relation between the two manuscripts, and the source-upload instructions. Local compilation and packaging do not guarantee arXiv moderation or constitute a submission.

The minimal [LaTeX source package](https://github.com/jeremy1392/dgf-agentic-bench/releases/download/dgf-bench-300-20260923/The_Last_Human_Gate_arXiv_source.zip) contains only compilation dependencies. The earlier 59-page version remains available in [the preceding repository revision](https://github.com/jeremy1392/dgf-agentic-bench/blob/fc3d1882a6b42a6ea0299e85131601da9382afef/paper/The_Last_Human_Gate.pdf).

To rebuild the benchmark tables, results chart, workflow diagram, and architecture specimen before compiling the paper:

```bash
python research/2026-09-dgf-bench/build_paper_assets.py
```

## Licensing

The repository's **MIT OR Apache-2.0** dual license applies to the original DGF-Bench software and benchmark documentation under the scope stated in the root [`LICENSE`](../LICENSE).

The manuscript, LaTeX source, figures, and compiled paper in this directory remain **Copyright (c) 2026 Jeremy Canale, all rights reserved**, unless a separate paper license is explicitly added later.
