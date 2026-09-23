# Research paper

## Title

**The Last Human Gate: Forward Deployed Engineering and the Automation of Enterprise Governance**

Author: Jeremy Canale  
Date: September 2026

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

The manuscript also reports the September 2026 evaluation on 300 synthetic dossiers: 899 of 900 model/case runs are evaluable. Gemini, Luna, and DeepSeek achieve 94.98%, 83.29%, and 74.18% strict gate success, respectively. These are measured agent outcomes on synthetic cases, distinct from the workforce scenarios.

The [research directory](../research/2026-09-dgf-bench/) contains final tables, diagnostics, figures, checksums, and an offline reproduction script. The [complete experiment release](https://github.com/jeremy1392/dgf-agentic-bench/releases/tag/dgf-bench-300-20260923) provides every file of the recorded run and dataset, plus the exact benchmark source snapshot. One Gemini infrastructure failure is excluded; historical partial exports remain in the archive and are clearly distinguished from final results.

To rebuild the benchmark tables and figure from the published summaries before compiling the paper:

```bash
python research/2026-09-dgf-bench/build_paper_assets.py
```

## Licensing

The repository's **MIT OR Apache-2.0** dual license applies to the original DGF-Bench software and benchmark documentation under the scope stated in the root [`LICENSE`](../LICENSE).

The manuscript, LaTeX source, figures, and compiled paper in this directory remain **Copyright (c) 2026 Jeremy Canale, all rights reserved**, unless a separate paper license is explicitly added later.
